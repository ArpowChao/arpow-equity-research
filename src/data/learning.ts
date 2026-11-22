import selection from './selection-14.json';
import revaluation from './revaluation-2026-11-22.json';
export const steps = [
  { title:'先懂生意', text:'誰付錢？買什麼？先看分部營收及利潤，拆開銷量、價格和組合。', where:'10-K／10-Q：業務說明、分部附註、管理層討論' },
  { title:'確認營收與利潤', text:'同季度或同年度比較。營收年增 = 本期營收 ÷ 去年同期 − 1；營益率 = 同口徑營業利益 ÷ 營收。分部營益不能當合併 GAAP 營益。', where:'損益表與分部附註；多一週、併購和一次性項目另列' },
  { title:'把利潤對回現金', text:'簡式自由現金流 = 營運現金流 − 資本支出（填支出正值）。營收變好但現金變差，就查應收、存貨和付款時點。', where:'現金流量表；兩項必須是相同起訖日，不混單季與累計' },
  { title:'確認股東分到多少', text:'先查現金與債務，再看股權薪酬、可轉債及股數。期末流通股數不等於計算 EPS 用的加權稀釋股數。', where:'資產負債表、EPS 附註與股權薪酬附註' },
  { title:'算三種價值，再跟股價比', text:'獲利穩定時可用正常化 EPS × 假設本益比；虧損時不要硬套 P/E。列悲觀／基準／樂觀，寫下什麼會推翻假設，再用同口徑快照比較。', where:'財報是已發生的事；成長率、倍數和安全折讓是你的假設' },
];
export const money = (v:number) => `$${v.toFixed(v < 1 ? 3 : 2)}`;
export function activeModel(ticker:string){
 const anchor=ticker.toLowerCase();
 const fresh=revaluation.models.find(r=>r.ticker===ticker);
 const row=selection.rows.find(r=>r.ticker===ticker);
 if(fresh) return {kind:'revalued', label:'新財報條件重估', date:revaluation.marketAsOf, price:fresh.market, cases:fresh.scenarios, stress:fresh.stress, url:`comparisons/revaluation-2026-11-22/#${anchor}`, formula:fresh.formula, source:fresh.source};
 if(row) return {kind:'condition', label:row.status, date:revaluation.marketAsOf, price:row.market, cases:row.cases.slice(0,3), stress:row.cases[3]?.value, url:`comparisons/selection-14/#${anchor}`, formula:row.formula, source:row.source};
 return null;
}

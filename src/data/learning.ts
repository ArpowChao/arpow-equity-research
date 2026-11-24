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
 if(row) return {kind:'condition', label:row.status, date:revaluation.marketAsOf, price:row.market, cases:row.cases.slice(0,3), stress:row.cases[3]?.value, url:`comparisons/selection-14/#${anchor}`, formula:chinese(row.formula), source:row.source};
 return null;
}

const terms: Record<string,string> = {
 'EV／營收':'企業價值除以營收的倍數', 'EV/Sales':'企業價值除以營收的倍數', 'EV/EBITDA':'企業價值／息稅折舊攤銷前盈餘', 'P/E':'本益比', 'EPS':'每股盈餘', 'FCF':'自由現金流', 'OCF':'營運現金流', 'CapEx':'資本支出', 'GAAP':'一般公認會計原則', 'RPO':'剩餘履約義務', 'SBC':'股權薪酬', 'EBITDA':'息稅折舊攤銷前盈餘', 'NTM':'未來十二個月', 'YoY':'年增率', 'SEC':'美國證券交易委員會', '10-K':'年度報告', '10-Q':'季度報告', 'EST':'美東標準時間', 'ARR':'年度經常性收入', 'ARPU':'每位使用者平均收入', 'TCV':'合約總價值', 'R&D':'研發', 'DCF':'折現現金流', 'ROIC':'投入資本報酬率', 'WACC':'加權平均資金成本', 'EV':'企業價值', 'NCI':'非控制權益', 'ADS':'美國存託股份', 'USD':'美元', 'IR':'投資人關係', 'FY':'財年', 'ASP':'平均售價', 'NAND':'快閃記憶體（NAND）', 'RSU':'限制型股票單位', 'CC':'固定匯率', 'TTM':'過去十二個月', 'QTD':'本季度至今', 'YTD':'本年至今', 'CEO':'執行長', 'D&A':'折舊與攤銷', 'SVOD':'訂閱制隨選影音', 'Bookings':'簽約額', 'bookings':'簽約額', 'backlog':'待履行訂單', 'GM':'毛利率', 'CAGR':'年複合成長率', 'DRAM':'動態隨機存取記憶體', 'GAI':'生成式人工智慧', 'AI':'人工智慧', 'GPU':'圖形處理器', 'CPU':'中央處理器', 'IPO':'首次公開發行', 'MW':'百萬瓦', 'GW':'十億瓦',
};
const termPattern = new RegExp(`(?<![A-Za-z])(?:${Object.keys(terms).sort((a,b)=>b.length-a.length).join('|')})(?![A-Za-z])`, 'g');
export const chinese = (text:string) => text.replace(termPattern,v=>terms[v]??v);
export const naturalProse = (text:string) => text;
export const termLabel = (t:string) => terms[t] ? `${t}（${terms[t]}）` : t;
const num=(v:number)=>v.toLocaleString('zh-TW',{maximumFractionDigits:8});
const usd=(v:number)=>`${v.toFixed(2)} 美元／股`;
export function baseWork(ticker:string, legacy?:{ snapshot:{baseFairValue:number}, valuation:{type:string, earnings?:number, forwardEbitda?:number, forwardRevenue?:number, baseMultiple:number, netCash?:number, discountFactor?:number,dilutedShares?:number} }){
 const fresh=revaluation.models.find(r=>r.ticker===ticker);
 const row=selection.rows.find(r=>r.ticker===ticker);
 const f=fresh?.scenarios.find(x=>x.label==='基準');
 const c=row?.cases.find(x=>x.label==='基準');
 if(f && "revenue" in f){
   const profits=f.revenue*f.margin*(1-f.tax), eps=profits/f.shares;
   return [`正常化稅後盈餘：${num(f.revenue)} 十億美元營收 × ${num(f.margin*100)}% 營業利益率 ×（1 − ${num(f.tax*100)}% 稅率）＝ ${num(profits)} 十億美元。`,`每股盈餘：${num(profits)} 十億美元 ÷ ${num(f.shares)} 十億稀釋股 ≈ ${num(eps)} 美元／股。`,`每股估值：${num(eps)} × ${num(f.multiple)} 倍本益比 ≈ ${usd(f.value)}。`];
 }
 if(!f && c && row?.model==='pe') return [`${ticker==='DIS'?'正常化每股盈餘：7.02 美元減第 53 週貢獻 0.17 美元，得到 6.85 美元／股；再乘（1 ＋ 11% 成長），得到 7.6035 美元／股。':`模型預估每股盈餘：${num(c.driver)} 美元／股。`}`,`每股估值：${num(c.driver)} 美元／股 × ${num(c.multiple)} 倍本益比 ＝ ${usd(c.value)}（四捨五入）。`];
 if(!f && c && row?.model==='op'){
   const profit=c.driver*c.margin*(1-c.tax), eps=profit/c.shares;
   return [`模型稅後盈餘：${num(c.driver)} 十億美元營收 × ${num(c.margin*100)}% 營業利益率 ×（1 − ${num(c.tax*100)}% 稅率）＝ ${num(profit)} 十億美元。`,`每股盈餘：${num(profit)} 十億美元 ÷ ${num(c.shares)} 十億稀釋股 ≈ ${num(eps)} 美元／股。`,`每股估值：${num(eps)} × ${num(c.multiple)} 倍本益比 ≈ ${usd(c.value)}。`];
 }
 if((f && "ebitda" in f) || (c && row)){
   const freshEv=f && "ebitda" in f ? f : undefined;
   const driver=freshEv?.ebitda ?? c!.driver, multiple=freshEv?.multiple ?? c!.multiple, shares=freshEv?.shares ?? c!.shares, cash=freshEv?.netCash ?? c!.netCash, factor=freshEv?1:c!.discount, target=freshEv?.value??c!.value;
   const economic=!f&&row!.model==='economic';
   const basis=economic?driver*c!.margin*(1-c!.tax):driver;
   const metric=economic?'稅後營業利益':f||row!.model==='ebitda'?'息稅折舊攤銷前盈餘':'營收';
   const ev=basis*multiple, equity=ev+cash, perShare=Math.max(0,equity/shares);
   return [ ...(economic?[`稅後營業利益：${num(driver)} 十億美元營收 × ${num(c!.margin*100)}% 營業利益率 ×（1 − ${num(c!.tax*100)}% 稅率）＝ ${num(basis)} 十億美元。`]:[]),`企業價值：${num(basis)} 十億美元${metric} × ${num(multiple)} 倍 ＝ ${num(ev)} 十億美元。`,`股東權益價值：${num(ev)} 十億美元 ${cash<0?'−':'＋'} ${num(Math.abs(cash))} 十億美元${cash<0?'淨負債':'淨現金'} ＝ ${num(equity)} 十億美元。`,`每股${factor===1?'估值':'遠期價值'}：${num(equity)} 十億美元 ÷ ${num(shares)} 十億稀釋股 ≈ ${factor===1?usd(target):`${num(perShare)} 美元／股`}。`,...(factor===1?[]:[`折回比較日：${num(perShare)} 美元／股 ÷ ${num(factor)}（折現除數）≈ ${usd(target)}。`])];
 }
 if(!legacy) return [];
 const v=legacy.valuation, target=legacy.snapshot.baseFairValue;
 const driver=v.earnings??v.forwardEbitda??v.forwardRevenue;
 if(driver==null) return [];
 const ev=driver*v.baseMultiple;
 const equity=ev+(v.netCash??0);
 const estimate=v.earnings!=null?ev:equity/(v.dilutedShares??1)*(v.discountFactor??1);
 if(Math.abs(estimate-target)>.011) return ['這份保存的基準與簡化試算欄位無法直接對上，先看原研究的假設與估值橋接；不將兩者當成同一數字。'];
 if(v.earnings!=null) return [`${num(driver)} 美元／股正常化盈餘 × ${num(v.baseMultiple)} 倍本益比 ≈ ${usd(target)}。`];
 return [`${num(driver)} 百萬美元${v.forwardEbitda!=null?'息稅折舊攤銷前盈餘':'營收'} × ${num(v.baseMultiple)} 倍 ＝ ${num(ev)} 百萬美元企業價值。`,`企業價值 ${num(ev)} 百萬美元 ${v.netCash!<0?'−':'＋'} ${num(Math.abs(v.netCash??0))} 百萬美元${v.netCash!<0?'淨負債':'淨現金'} ＝ ${num(equity)} 百萬美元股東權益價值。`,`每股估值：${num(equity)} 百萬美元 ÷ ${num(v.dilutedShares!)} 百萬稀釋股${v.discountFactor!=null && v.discountFactor!==1?` × ${num(v.discountFactor)} 折現係數`:''} ≈ ${usd(target)}。`];
}

export const gapLabel = '基準相對快照股價';
export const gapFormula = '（估值基準 ÷ 同版本快照股價 − 1）× 100%';
export function snapshotGap(benchmark:number, price:number){
 if(!Number.isFinite(benchmark) || !Number.isFinite(price) || price<=0) return '無可比快照';
 const change=Number(((benchmark/price-1)*100).toFixed(1));
 return `${change>0?'+':''}${change.toFixed(1)}%`;
}
const displayTerms: Record<string,string> = {
 '分部營業利益合計':'Total Segment Operating Income（分部營業利益合計）',
 '營收年增率':'Revenue Growth YoY（營收年增率）', '營收年增':'Revenue Growth YoY（營收年增）',
 '營收':'Revenue（營收）', '年增率':'YoY Growth（年增率）',
 '營業利益率':'Operating Margin（營業利益率）', '營益率':'Operating Margin（營益率）',
 '營業利益':'Operating Income（營業利益）', '營業虧損':'Operating Loss（營業虧損）',
 '營運現金流':'Operating Cash Flow（營運現金流）', '資本支出':'Capital Expenditures（資本支出）',
 '簡式自由現金流':'Free Cash Flow（簡式自由現金流）', '自由現金流':'Free Cash Flow（自由現金流）',
 '現金及約當現金':'Cash and Cash Equivalents（現金及約當現金）', '帳面現金':'Cash and Cash Equivalents（帳面現金）',
 '正常化每股盈餘':'Normalized EPS（正常化每股盈餘）', '調整後每股盈餘':'Adjusted EPS（調整後每股盈餘）', '稀釋每股盈餘':'Diluted EPS（稀釋每股盈餘）', '每股盈餘':'Earnings per Share（每股盈餘）',
 '每股估值':'Value per Share（每股估值）', '本益比':'Price-to-Earnings Ratio（本益比）', '倍本益比':'倍 Price-to-Earnings Ratio（本益比）',
 '企業價值除以營收的倍數':'EV/Revenue（企業價值／營收倍數）', '企業價值':'Enterprise Value（企業價值）',
 '股東權益價值':'Equity Value（股東權益價值）', '淨現金':'Net Cash（淨現金）', '淨負債':'Net Debt（淨負債）',
 '完全稀釋股數':'Fully Diluted Shares（完全稀釋股數）', '稀釋股數':'Diluted Shares（稀釋股數）', '稀釋股':'Diluted Shares（稀釋股）',
 '稅後營業利益':'After-tax Operating Income（稅後營業利益）', '稅後盈餘':'After-tax Earnings（稅後盈餘）',
 '息稅折舊攤銷前盈餘':'EBITDA（息稅折舊攤銷前盈餘）',
 '折現除數':'Discounting Denominator（折現除數）', '折現係數':'Discount Factor（折現係數）',
 '剩餘履約義務':'Remaining Performance Obligations（剩餘履約義務）', '股權薪酬':'Stock-Based Compensation（股權薪酬）',
 '一般公認會計原則':'GAAP（一般公認會計原則）', '毛利率':'Gross Margin（毛利率）', '毛利':'Gross Profit（毛利）', '淨利':'Net Income（淨利）',
};
const displayPattern=new RegExp(Object.keys(displayTerms).sort((a,b)=>b.length-a.length).join('|'),'g');
export const bilingual=(text:string)=>chinese(text).replace(displayPattern,word=>displayTerms[word]??word);

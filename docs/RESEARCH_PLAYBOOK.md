# Arpow Equity Research Playbook (v2 Buy-Side Standard)

這份文件定義了本網站（`ArpowChao/arpow-equity-research`）與自動化研究代理（Hermes + LLM）從 **v1「會計稽核機器人」升級至 v2「買方實戰決策分析師」** 的完整方法論、數學公式修正、資料契約與撰寫規範。

---

## 一、為何要從 v1 升級？（已驗證的 6 項結構缺陷）

| 編號 | v1 缺陷 | 實例證據（本庫現況） | v2 修正方案 |
| :--- | :--- | :--- | :--- |
| **1** | **Track B 蒸發了 4 年全部自由現金流** | `nvda-2026-11-18.json` 算出 4 年累計數千億美元獲利，卻只把第 4 年終值 `$120.50` 直接折現為 `$82.30`，同時計入股數稀釋 `0.5%/yr`，低估現值約 `20%–30%`（僅 4 年 FCF 現值就值 `$18.80/股`）。 | 改採 **含期間自由現金流折現公式**：$\text{PV} = \sum_{t=1}^4 \frac{\text{FCF}_t}{(1+r)^t} + \frac{\text{TerminalValue}}{(1+r)^4}$，保留保守轉化率（預設 85%）。 |
| **2** | **TTM 斷崖起點與固定單軸壓測失真** | `six-2026-11-14.json` 的 `AMD` 從過時 TTM 454 億起算、`10%` 成長，算出第 4 年營收比 NTM 基準還低（PV 僅 `$40.16`，-92%）；`tailored` 與 `common10` 在 NVDA 完全重複；僅砍毛利卻未連動營收增速。 | 區分 `ttm_conservative` 與 `ntm_base` 起點；強制輸出 **3×3「營收增速 × 毛利率」二維雙殺矩陣**，全面取代單一靜態壓測表。 |
| **3** | **合規法務車輪話與重複貼上** | `[ticker].astro` 與 JSON 重複跳針「不是已證實公平價／非買點／未指派機率」；`nvda-2026-11-18.json` 的 `Financial quality` 塞入 1,700 字分號流水帳，甚至同一段文字在 `analysis` 與 `modelNotes` 重複兩次。 | 網站頁尾已統一標示「不構成投資建議」；個股分析徹底刪除重複警語，聚焦 **結論分級、逆推預期差、量化確認／推翻門檻**。 |
| **4** | **缺席故事線（Setup）與總經利率約束** | 在 10Y 美債 `5.04%`、實質利率 `2.88%`、那斯達克單週重挫 10% 的環境下，v1 個股研究猶如真空孤島，未對比盈餘殖利率與無風險利率之權益風險溢酬（ERP）。 | 新增 `macroContext` 與 `storylineSetup`：區分 3–6 個月交易敘事與 10 年雜訊、評估 Setup 擁擠度，並計算 `ERP vs 10Y`。 |
| **5** | **未逆推市場定價、無同業錨點與分部淨額表** | `MU` 以峰值 75% 毛利算出 `+99%`、`ARM` 給 70x卻無同業與歷史 P/E 帶對照；`AMZN`／`MSFT` 被壓成單行總毛利，看不出哪個部門在扛風險。 | 強制 **Reverse Valuation（反推現價隱含 4Y 營收 CAGR 與 Forward P/E）**、至少 2 家同業橫向比對、至少 2 部門順逆風加減帳。 |
| **6** | **前端硬編碼義大利麵債與 `ZS` 漏網** | `[ticker].astro` 寫死 6 檔個股判斷、`index.astro` 寫死 `ZS`、`FilingEvidence.astro` 寫死 `IONQ`、`update_live_quotes.py` 只抓 `reports.generated.json` 導致 `ZS` 沒即時報價、`learning.ts` 全域把每個 `AI`/`EPS` 硬展成中英雙語。 | 收斂為宣告式 `src/data/ticker-overrides.json` 與 `src/data/buyside-v2.json`；`update_live_quotes.py` 跨全資料源自動偵測標的；長文改用 `naturalProse()`。 |

---

## 二、買方五大分析模組（吸收「投資TALK君」實戰精華）

每次撰寫或更新一檔標的至 `src/data/buyside-v2.json`，必須依序完成以下五個模組：

### 模組 1：市場故事線與 Setup 審計（Storyline & Macro）
1. **區分時間尺度**：說清楚「未來 3–6 個月市場真正交易的核心敘事」是什麼？什麼是「10 年遠期鬼故事雜訊」（例如短期利率折現 vs 十年後技術取代）？
2. **總經折現率標尺**：填入最新美國 10 年期公債殖利率（`us10yYieldPct`）、10 年實質利率（`real10yTipsPct`）與高收益債利差（`hyOasPct`）。當 10Y 超過 `4.8%–5.0%`，高倍數股的 ERP 空間將明顯壓縮。
3. **擁擠度與線性外推掃雷**：股價剛連漲半年、估值創 5 年新高（Crowded Setup），還是已經歷劇烈回撤？華爾街最可能在哪個指標做「無腦線性外推」（Peak Margin / Peak CapEx / GPU 永不跌價）？

### 模組 2：財報品質、分部加減帳與 Unit Economics
1. **三層獲利還原（保留真實成本）**：`GAAP Operating Income` → 剔除一次性損益（投資評價損益、認股權證負債評價、第 53 週、一次性退稅）→ `Economic Operating Income`（**明確保留持續性 SBC**）。
2. **現金流真實度**：比對 `TTM OCF`、`TTM FCF` 與 GAAP 淨利之轉化率；若獲利成長但現金流出，必須追查 DSO（應收天數）、存貨週轉、客戶延遲付款或供應鏈承諾/擔保。
3. **分部順逆風淨額表（Segment Bridge）**：多引擎企業嚴禁只看合併毛利，須拆出主要成長引擎與拖累引擎的營收比重、YoY 與抵銷結果（順風／逆風／中性）。
4. **上下游 Unit Economics 與法說追蹤層級**：檢查公司承諾（CapEx、RPO、客戶預算）與上下游營收對不對得上（例如算力客戶變現速度 vs 賣鏟子預估），並誠實標註法說取得深度（`full_qa` / `partial_clips` / `press_release_only`）與尚待驗證的 Q&A 盲點。

### 模組 3：逆推市場定價與三把估值尺（Reverse Valuation & Anchors）
1. **先反推，再評斷**：與其主觀給一個目標價，先算清楚 **「今天這口股價需要多好的未來才能合理？」**
   - `impliedForwardPe = price / ntmBaseEps`
   - `earningsYieldPct = 100 / impliedForwardPe`
   - `erpVs10yPct = earningsYieldPct - us10yYieldPct`
   - 呼叫 `scripts/valuation_math.py::solve_reverse_implied_cagr`，分別解出「基準毛利率下」與「壓力毛利率下」支撐現價所需的 **4 年營收年複合成長率（Implied 4Y CAGR）**。
2. **倍數不可拍腦袋**：必須同時對照 ① **公司自身 5Y/10Y 歷史 Forward P/E 區間** 與 ② **至少 2 檔直接同業（Peer Comps）** 的前瞻本益比、營收增速與毛利結構。

### 模組 4：修正版含 FCF 雙殺壓力測試（Stress V2）
1. **統一確定性引擎**：所有情境數值必須由 `scripts/valuation_math.py`（或前端同步實作 `src/lib/valuation.ts`）精算，禁止 LLM 心算或四捨五入錯位。
2. **對照舊版偏差**：同時紀錄 `fcfInclusiveResult`、`legacyExFcfPv` 與 `fcfPvDelta`，讓讀者一眼看清「把 4 年自由現金流算回來」與「僅看終值」的差距；針對高成長股亦須提供 `altNtmSeedResult` 對照，破除舊版 TTM 斷崖誤判。
3. **3×3 二維雙殺矩陣**：橫軸取低／中／高毛利率，縱軸取低／中／高 4 年營收 CAGR，標示每一格的 FCF 含權現值與相對現價折溢價（`gapPct`）。

### 模組 5：可證偽的買方定調與倉位紀律（Verdict）
- 四選一分級標籤：
  - `高勝率賠率`：現價隱含門檻保守、同業具明顯折價、現金流與 KPI 正向驗證。
  - `觀察待催化`：估值雖具緩衝或折價，但關鍵變數（毛利止穩／收現改善／治理或需求）仍待下一至兩季財報驗證。
  - `估值透支迴避`：現價隱含極高 CAGR 或峰值毛利永續，幾乎無容錯空間（低/負 ERP）。
  - `資訊缺口暫緩`：關鍵財報、客戶結構或法說證據不足，暫不建立方向性部位。
- 每檔必須列出 ≥ 2 項**明確量化翻多確認條件**（`confirmTriggers`）與 ≥ 2 項**明確量化推翻警訊**（`invalidateTriggers`），並給出倉位控管紀律（例如事件風險大者限縮追蹤倉位）。

---

## 三、Hermes 私有庫匯出與自動化檢核流程

1. 私有研究腳本完成 SEC 10-K/10-Q/8-K 數據抓取後，呼叫本庫的 `scripts/valuation_math.py` 計算 `stressV2`、`matrix2d`、`reverseValuation` 與 `erpVs10yPct`。
2. 產出符合 `schemas/equity-report.v2.schema.json` 的物件寫入 `src/data/buyside-v2.json`。
3. 絕不為了新增個股而修改任何 `.astro` 檔案；若有個股層級註記需顯示於既有卡片或資料證據框，請統一更新 `src/data/ticker-overrides.json`。
4. 執行 `python3 tests/validate_v2_methodology.py` 與 `npm test`，確保數學驗算誤差 $< 10^{-4}$ 且無違禁合規八股與敏感字串外洩。

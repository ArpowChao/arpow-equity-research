export type WatchItem = {
  name: string;
  why: string;
  good: string;
  warning: string;
};

export type BeginnerGuide = {
  industry: string;
  earns: string;
  keyQuestion: string;
  watch: WatchItem[];
  terms: string[];
};

export const glossary: Record<string, string> = {
  GAAP: '依法規會計準則呈現的原始成績，不能因為難看就跳過。',
  核心口徑: '公司自行排除某些項目後的成績。適合看營運趨勢，但被排除的股權薪酬、重整或權證仍可能是股東成本。',
  營收: '公司賣出產品或服務收到的收入；成長不代表一定賺錢。',
  毛利率: '每 100 元營收扣掉直接成本後剩多少。上升通常代表產品組合、價格或成本效率改善。',
  營業利益率: '扣除研發、行銷與管理費用後，本業每 100 元營收賺多少。',
  OCF: '營運現金流：本業實際帶進或用掉多少現金。',
  CapEx: '資本支出：蓋廠、買設備、資料中心或其他長期資產花掉的錢。',
  FCF: '自由現金流，簡化理解為 OCF 減 CapEx；是公司可用於還債、回購或再投資的現金。',
  SBC: '股權薪酬：用股票付員工。雖然不立即花現金，但會稀釋每位股東的持分。',
  RPO: '已簽約、尚未認列的履約義務；比一般意向訂單可靠，但仍要看多久才能轉成營收及是否集中單一客戶。',
  RDV: '剩餘交易價值，可能含客戶選擇權或可終止部分，不能全部視為已鎖定收入。',
  TCV: '合約潛在總價值，可能包含尚未執行的選擇權；不是當期營收。',
  稀釋股數: '把期權、RSU、認股權證等潛在新股算進來後的股數；股數越多，每股價值越薄。',
  有機成長: '排除併購與匯率後，原有業務自己長了多少。',
  ARPU: '每位使用者平均收入；訂戶增加但 ARPU 下滑，獲利未必改善。',
  TAC: '流量取得成本：Google 為取得搜尋流量付給合作夥伴的費用。',
  bookings: '新簽訂單或預約量；要繼續追蹤它能否轉成 RPO、營收與現金。',
  backlog: '已簽約、尚待履行的合約價值。要看取消條款、客戶集中與預計認列時間，不能直接當成現金。',
  ARR: '年度經常性收入或年化收入運行率。若以單月乘以 12 推算，代表當下速度，不等於全年已實現營收。',
  'Adjusted EBITDA': '公司加回折舊、股權薪酬、利息等項目後的非 GAAP 利潤；可能與自由現金流差很大。',
  EMA20: '近 20 個交易日價格的加權平均線，只描述短期價格趨勢，不代表公司價值。',
  'EV/Sales': '企業價值除以營收。常用於尚未成熟或虧損公司；倍數越高，市場要求的未來成長越高。',
  'P/E': '股價除以每股盈餘。只適合盈餘相對正常的公司；一次性利益或週期高峰會讓它失真。'
};

export const beginnerGuides: Record<string, BeginnerGuide> = {
  SPCX: {
    industry:'太空運輸＋衛星網路＋AI算力', earns:'Launch替客戶與政府發射火箭；Starlink向消費者、企業與政府收網路費；合併xAI後也出售AI算力、模型與X平台服務。', keyQuestion:'Starlink的現金利潤能否支撐Starship與AI的巨額CapEx，並把1000億美元年末ARR轉成可持續的GAAP收入與FCF？',
    watch:[
      {name:'Connectivity／Starlink',why:'目前唯一大型且GAAP營業獲利的分部，是整體現金引擎。',good:'訂戶、企業／政府收入與營業利益快於ARPU下滑。',warning:'ARPU、容量或監管限制使收入成長慢於衛星投資。'},
      {name:'Starship里程碑',why:'完整快速重複使用決定發射成本、V3衛星部署和長期太空經濟選擇權。',good:'軌道任務、船體／助推器回收與日常發射依序落地。',warning:'測試失敗、監管延誤或單位成本沒有下降。'},
      {name:'AI算力與合約',why:'目前成長最快，也占絕大多數CapEx；合約客戶集中。',good:'已簽合約按期認列、利用率與現金回收支持不到一年回收期。',warning:'GPU／電力延誤、價格回落、客戶不續約或AI仍GAAP虧損。'},
      {name:'CapEx／FCF／稀釋',why:'Adjusted EBITDA會加回巨額折舊與SBC，不能代表股東真正剩下的現金。',good:'OCF逐步覆蓋CapEx，淨現金不再快速消耗，每股收入快於股數。',warning:'靠IPO、發債或發股持續填補負FCF。'}
    ],terms:['GAAP','Adjusted EBITDA','ARR','backlog','OCF','CapEx','FCF','SBC','稀釋股數','EV/Sales']
  },
  GOOGL: {
    industry: '數位廣告＋雲端平台',
    earns: '主要靠搜尋與 YouTube 廣告賺錢，Google Cloud 是第二成長引擎；AI 目前同時帶來新產品與龐大資料中心支出。',
    keyQuestion: 'AI 搜尋能否守住廣告變現與市占，同時讓 Cloud／訂閱成長快過 CapEx？',
    watch: [
      {name:'搜尋與其他廣告', why:'Alphabet 最大現金來源；搜尋量、點擊價格與 AI 回答中的廣告變現決定整體獲利。', good:'廣告收入穩健成長，TAC 占比沒有惡化。', warning:'搜尋市占、查詢量或廣告定價下滑。'},
      {name:'YouTube', why:'同時有廣告與訂閱兩種收入，可降低只依賴搜尋的風險。', good:'廣告與訂閱收入同步成長。', warning:'觀看時數增加但變現或內容成本惡化。'},
      {name:'Google Cloud', why:'雲端營收與營益率決定 Alphabet 是否有第二個大型獲利引擎。', good:'營收快於公司整體、營益率持續提高。', warning:'成長降速且 AI 基礎設施折舊壓低利潤。'},
      {name:'AI CapEx 與 FCF', why:'買 GPU、伺服器與資料中心會先花現金，之後才可能產生收入。', good:'Cloud／AI 收入與營業利益成長快過 CapEx。', warning:'CapEx 大增，但 FCF 與增量利潤沒有跟上。'}
    ], terms:['GAAP','TAC','CapEx','FCF','P/E']
  },
  DIS: {
    industry: '娛樂內容＋串流＋主題樂園',
    earns: '靠主題樂園與郵輪的高現金流、Disney+／Hulu／ESPN 串流，以及電影、電視與授權內容賺錢。',
    keyQuestion: '樂園能否維持獲利，同時讓串流真正成為穩定利潤，而不是只追求訂戶？',
    watch: [
      {name:'Experiences 樂園與郵輪', why:'通常是 Disney 最穩定、最重要的獲利來源。', good:'入園人次、每人消費與飯店入住率穩健，營益率維持。', warning:'景氣轉弱、成本上升或大型 CapEx 先壓低現金流。'},
      {name:'串流 DTC', why:'Disney+、Hulu、ESPN 的成敗決定媒體轉型能否成功。', good:'營業利益改善，訂戶與 ARPU 同步健康。', warning:'靠降價買訂戶、流失率高或內容成本反彈。'},
      {name:'電影／電視／授權', why:'熱門作品會帶動票房、授權、商品與樂園 IP，但單片波動大。', good:'片單成功率提高且內容支出受控。', warning:'連續票房失利、線性電視廣告與訂閱加速衰退。'},
      {name:'ESPN 與體育權利', why:'體育內容黏著度高，但轉播權成本昂貴。', good:'串流轉型後收入覆蓋權利成本。', warning:'權利費漲幅長期高於訂閱與廣告收入。'}
    ], terms:['營業利益率','ARPU','CapEx','FCF','P/E']
  },
  AMD: {
    industry: '無晶圓廠半導體', earns:'設計資料中心 GPU／CPU、PC 處理器與遊戲晶片，由外部晶圓廠製造。', keyQuestion:'AI GPU 成長能否快過傳統業務波動，並在 NVIDIA 生態系壓力下守住毛利？',
    watch:[
      {name:'資料中心',why:'AI GPU 與 EPYC CPU 是成長及估值核心。',good:'營收、客戶數與毛利同步上升。',warning:'產品延遲、供應受限或價格競爭。'},
      {name:'Client PC',why:'PC 週期影響出貨、平均售價與庫存。',good:'市占提升且通路庫存正常。',warning:'需求下滑或降價清庫存。'},
      {name:'毛利率與產品組合',why:'高階資料中心產品占比提高才會真正創造利潤。',good:'非 GAAP 與 GAAP 毛利率共同改善。',warning:'營收增長但毛利率停滯。'}
    ],terms:['GAAP','核心口徑','毛利率','SBC','P/E']
  },
  INTC: {
    industry:'CPU＋晶圓代工', earns:'同時賣 PC／伺服器處理器並投資 Intel Foundry 替外部客戶製造晶片。', keyQuestion:'製程與產品能否準時，且 Foundry 的巨額 CapEx 最終能帶來足夠訂單與毛利？',
    watch:[
      {name:'Client／Data Center',why:'目前主要營收與現金來源。',good:'市占、平均售價與毛利止跌。',warning:'產品延遲或持續失去市占。'},
      {name:'Intel Foundry',why:'轉型成敗核心，但建廠前期虧損龐大。',good:'外部客戶、預付款與良率里程碑增加。',warning:'只有 CapEx，沒有可驗證外部訂單。'},
      {name:'製程節點與良率',why:'節點準時與良率決定成本和競爭力。',good:'節點按時量產且良率改善。',warning:'再次延期或需要昂貴外包。'},
      {name:'FCF 與資產負債表',why:'轉型需要多年資金。',good:'補助、營運現金與資產處分可覆蓋投資。',warning:'持續負 FCF、舉債或稀釋。'}
    ],terms:['毛利率','OCF','CapEx','FCF','P/E']
  },
  MU: {
    industry:'DRAM／NAND 記憶體', earns:'靠 DRAM、HBM 與 NAND 的價格、出貨量及產品組合賺錢，屬強週期產業。', keyQuestion:'HBM 的結構成長能否抵銷傳統記憶體價格循環，且新增供給不會再次壓垮毛利？',
    watch:[
      {name:'DRAM／NAND 售價',why:'價格小幅變動就會大幅影響利潤。',good:'平均售價上升且庫存天數下降。',warning:'供給成長快於需求、價格轉跌。'},
      {name:'HBM',why:'AI 伺服器的高價高階記憶體。',good:'認證、出貨與長約增加，產品組合提高毛利。',warning:'良率／認證延誤或競爭者擴產。'},
      {name:'CapEx 與供給',why:'景氣好時過度擴產常造成下一輪下跌。',good:'投資紀律、供給成長貼近需求。',warning:'同業同步大幅擴產。'},
      {name:'週期正常化 EPS',why:'高峰 EPS 不能永久年化。',good:'下行底部獲利與 FCF 高於前一循環。',warning:'只用單季高峰 P/E 判斷便宜。'}
    ],terms:['毛利率','CapEx','FCF','P/E']
  },
  SNDK: {
    industry:'NAND 快閃記憶體', earns:'靠 NAND 晶片與企業級／消費級 SSD，獲利受價格、bit 出貨與合資產能影響。', keyQuestion:'企業 SSD 成長能否提高產品組合，抵銷 NAND 供過於求的週期風險？',
    watch:[
      {name:'NAND 售價與 bit 出貨',why:'共同決定營收，但只衝出貨可能傷害價格。',good:'價格與出貨同步改善。',warning:'bit 增長靠降價換來。'},
      {name:'企業級 SSD',why:'資料中心產品通常比消費級產品更有價值。',good:'認證、市占與毛利提高。',warning:'客戶認證延誤或競爭加劇。'},
      {name:'庫存與 CapEx',why:'庫存與供給紀律決定 NAND 週期。',good:'庫存下降、產能投資克制。',warning:'庫存堆積、同業擴產。'}
    ],terms:['毛利率','CapEx','FCF','P/E']
  },
  NVDA: {
    industry:'AI 加速運算＋全棧資料中心', earns:'主要銷售資料中心 GPU／整機、NVLink／InfiniBand／Ethernet 網路與 CUDA 軟體生態；遊戲、工作站、車用與機器人歸入 Edge Computing。', keyQuestion:'Hyperscaler 與企業 AI 支出能否長期成長，讓 Blackwell／Rubin 的收入與現金流跑贏供應承諾、客戶自研晶片與出口限制？',
    watch:[
      {name:'Data Center：Hyperscale／ACIE',why:'占營收絕大多數；前者是大型雲端與網路公司，後者含 AI cloud、企業、工業與主權 AI。',good:'兩類客戶同步成長，單一客戶集中下降。',warning:'CSP CapEx 降速、專案延後或中國收入受限。'},
      {name:'Compute＋Networking 全棧',why:'GPU 之外，NVLink、InfiniBand、Spectrum-X 與軟體共同形成平台護城河。',good:'運算與網路收入同步成長，Blackwell／Rubin 轉換順利。',warning:'新平台延期、良率問題或客戶改用自研 ASIC。'},
      {name:'Edge Computing',why:'包含遊戲、工作站、汽車、機器人與邊緣 AI，可降低只依賴大型資料中心的風險。',good:'RTX、車用與機器人收入多元成長。',warning:'PC／遊戲週期疲弱，邊緣 AI 仍只有展示沒有量產。'},
      {name:'毛利、庫存與資本承諾',why:'高毛利來自稀缺與平台定價，但公司也提前鎖定大量供應、雲端與資料中心容量。',good:'毛利約75%、庫存周轉健康且 FCF 快速成長。',warning:'供給承諾、庫存或擔保增加，終端需求與現金回收跟不上。'}
    ],terms:['GAAP','核心口徑','毛利率','FCF','SBC','P/E']
  },
  ARM: {
    industry:'半導體 IP 授權', earns:'先收架構／核心設計授權費，再依客戶晶片出貨收 royalty；不直接製造多數晶片。', keyQuestion:'v9 與高價值資料中心／AI 晶片能否提高每顆 royalty，同時控制 SBC 與直接做晶片的資本風險？',
    watch:[
      {name:'Royalty revenue',why:'跟客戶實際晶片出貨連動，是長期複利核心。',good:'v9 占比與每顆費率提高。',warning:'手機出貨疲弱或客戶自研替代。'},
      {name:'License revenue',why:'大單波動較大，但預示未來 royalty。',good:'新客戶、CSS／資料中心授權增加。',warning:'單季大單被誤當持續收入。'},
      {name:'ACV／RPO／pipeline',why:'代表不同程度的未來機會，不能互相替代。',good:'已簽合約與實際認列共同成長。',warning:'只有 pipeline 宣傳，沒有收入。'},
      {name:'SBC 與稀釋',why:'GAAP 與非 GAAP 差異的重要來源。',good:'SBC 占營收下降。',warning:'股數持續上升侵蝕每股價值。'}
    ],terms:['核心口徑','RPO','SBC','稀釋股數','P/E']
  },
  PLTR: {
    industry:'AI 軟體平台', earns:'向政府與企業收取長期軟體平台及部署服務費，AIP 是目前主要成長引擎。', keyQuestion:'美國商業高速成長能否維持，並足以支撐極高估值與股權薪酬？',
    watch:[
      {name:'美國商業收入',why:'AIP 民間採用最直接的證據。',good:'收入、客戶與大額合約同步成長。',warning:'bootcamp 多但 production 合約轉換放慢。'},
      {name:'政府收入',why:'穩定但受預算與大型合約時點影響。',good:'合約多元且續約穩定。',warning:'單一大單造成基期與季度波動。'},
      {name:'TCV／RDV／RPO',why:'可靠程度不同，只有 RPO 較接近不可取消收入。',good:'RPO 與實際收入共同成長。',warning:'只強調含選擇權的 TCV／RDV。'},
      {name:'估值與 SBC',why:'好公司若價格太高仍可能沒有好報酬。',good:'成長與 FCF 消化倍數，SBC 占比下降。',warning:'成長降速造成營運與倍數雙殺。'}
    ],terms:['GAAP','TCV','RDV','RPO','SBC','EV/Sales']
  },
  CBRS: {
    industry:'AI 晶片＋推論雲端', earns:'銷售 wafer-scale AI 系統，也用自建／租用資料中心向客戶提供高速推論算力。', keyQuestion:'OpenAI 的巨大 RPO 能否按時轉成具毛利的收入，而不是先變成資料中心支出與股東稀釋？',
    watch:[
      {name:'OpenAI RPO 與 MW 交付',why:'未來收入最大來源，也是最大集中風險。',good:'容量按期上線、RPO 轉成收入且服務達標。',warning:'延誤、終止條款或容量閒置。'},
      {name:'GAAP／核心收入橋接',why:'核心口徑加回客戶權證並排除 pass-through，數字較好看。',good:'GAAP 收入、毛利與核心口徑一起改善。',warning:'只有核心成長，GAAP 與現金流沒有跟上。'},
      {name:'CapEx／FCF／租約',why:'AI 雲端是重資產生意，簽約同時也帶來建置義務。',good:'容量利用率與現金回收快過投資。',warning:'CapEx、租約與借款增速快過毛利。'},
      {name:'客戶權證與股數',why:'OpenAI、AWS 權證與員工股權會稀釋每股價值。',good:'每股收入成長快過完全稀釋股數。',warning:'只用基本股數估值。'}
    ],terms:['GAAP','核心口徑','RPO','CapEx','FCF','SBC','稀釋股數','EV/Sales']
  },
  MP: {
    industry:'稀土材料＋磁鐵供應鏈', earns:'從 Mountain Pass 生產稀土精礦，正往 NdPr 分離與美國磁鐵製造延伸。', keyQuestion:'10X／磁鐵專案能否按期量產，把政策與承購支持轉成真實 EBITDA 與 FCF？',
    watch:[
      {name:'NdPr 產量與價格',why:'決定目前材料業務收入與毛利。',good:'產量、回收率與實現價格改善。',warning:'中國供給壓價或成本上升。'},
      {name:'10X／磁鐵爬坡',why:'未來價值主要來自高附加價值產品。',good:'建廠、認證、良率與出貨按期。',warning:'延誤、超支或低利用率。'},
      {name:'合約與政策支持',why:'價格底線、承購與政府資金降低部分風險。',good:'支持條款實際覆蓋現金需求。',warning:'把政策支持誤當施工零風險。'},
      {name:'CapEx 與稀釋',why:'大型專案可能需要可轉債、優先股或權證。',good:'專案現金回報高於資金成本。',warning:'成本超支導致再融資與每股稀釋。'}
    ],terms:['CapEx','FCF','稀釋股數','EV/Sales']
  },
  FISV: {
    industry:'支付處理＋金融科技', earns:'Clover 與商戶收單處理支付，也為銀行提供帳務、發卡與支付網路服務。', keyQuestion:'有機營收能否恢復成長、管理層能否達成指引並用 FCF 降低高負債？',
    watch:[
      {name:'Merchant／Clover',why:'商戶交易量、服務收入與競爭力的核心。',good:'交易量、商戶數與每商戶收入改善。',warning:'商戶流失、價格壓力或成長轉負。'},
      {name:'Financial Solutions',why:'銀行科技具經常性，但轉換週期長。',good:'新客戶轉換、經常性收入與利潤改善。',warning:'專案延遲或客戶削減支出。'},
      {name:'有機成長與指引',why:'低 P/E 只有在盈餘不再下修時才有意義。',good:'連續達標並恢復正成長。',warning:'再次下修收入或 EPS。'},
      {name:'FCF／淨負債／回購',why:'高負債下，現金應優先創造每股價值。',good:'FCF 去槓桿且回購價格合理。',warning:'高價回購後仍需維持高負債。'}
    ],terms:['有機成長','核心口徑','OCF','CapEx','FCF','P/E']
  },
  QBTS: {
    industry:'量子運算商業化', earns:'銷售量子系統並提供雲端量子運算服務，目前營收仍小、價值主要來自未來商業化。', keyQuestion:'bookings 能否依序轉成 RPO、收入與毛利，且現金能撐到規模化？',
    watch:[
      {name:'bookings → RPO → revenue',why:'每一步都比前一步更接近真實收入。',good:'三者連續成長且轉換期縮短。',warning:'只有新聞訂單，收入沒有增加。'},
      {name:'商業客戶與 production 使用',why:'研究示範不等於可重複生意。',good:'付費客戶、續約與正式工作負載增加。',warning:'一次性系統銷售造成假性高成長。'},
      {name:'現金消耗與稀釋',why:'虧損公司可能靠發新股生存。',good:'現金 runway 延長且每股收入提升。',warning:'營收很小但股數快速增加。'}
    ],terms:['bookings','RPO','OCF','FCF','稀釋股數','EV/Sales']
  },
  LAES: {
    industry:'資安晶片／後量子安全', earns:'提供安全晶片、PKI 與後量子密碼相關方案，仍處早期商業化階段。', keyQuestion:'技術合作與 pipeline 能否轉成可重複的產品收入，而非持續靠融資？',
    watch:[
      {name:'產品收入與客戶多元化',why:'驗證技術是否真正被市場採用。',good:'付費客戶、重複訂單與毛利增加。',warning:'收入集中或合作公告沒有營收。'},
      {name:'研發里程碑',why:'認證與量產是商業化前提。',good:'認證完成並進入量產。',warning:'只有概念驗證與遠期 pipeline。'},
      {name:'現金 runway／稀釋',why:'小型虧損公司最常見的股東風險。',good:'現金足以覆蓋關鍵里程碑。',warning:'持續增發、權證或關聯交易。'}
    ],terms:['營收','毛利率','OCF','FCF','稀釋股數','EV/Sales']
  }
};

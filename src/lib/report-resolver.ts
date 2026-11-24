import fundamentals from '../data/fundamentals.generated.json';
import { activeModel, chinese, snapshotGap } from '../data/learning';
import { splits } from '../data/splits';
import overrides from '../data/ticker-overrides.json';
import buysideV2 from '../data/buyside-v2.json';

type OverrideRule = (typeof overrides.modelOverrides)[number];

export type BuySideV2Item = (typeof buysideV2.items)[number];

export interface ResolvedReportMeta {
  dualEconomic: boolean;
  dual: any;
  conditionalModel: boolean;
  isAudit: boolean;
  isNtmEconomic: boolean;
  split: { ratio: number; tradingDate: string; source: string } | undefined;
  latestFiling: (typeof fundamentals.items)[number] | undefined;
  activeModel: ReturnType<typeof activeModel>;
  olderModel: boolean;
  historic: boolean;
  preSplit: boolean;
  originalGap: string;
  methodSlug: string;
  snapshotDateLabel: string;
  cardPillLabel: string;
  cardBaseLabel: string;
  detailBaseLabel: string;
  scenarioBaseLabel: string;
  fairRangeLabel: string;
  mosLabel: string;
  sourceLinkLabel: string;
  calcFieldLabel: string;
  priceVerdict: string;
  buysideV2: BuySideV2Item | undefined;
}

export const pinnedTickers: string[] = [...overrides.pinnedTickers];

export const filingCaveats = overrides.filingCaveats as Record<
  string,
  { dataAttr: string; operatingIncomeLabel: string; summary: string; detailSuffix: string }
>;

export function getBuySideV2(ticker: string): BuySideV2Item | undefined {
  return buysideV2.items.find((item) => item.ticker === ticker);
}

export function resolveReportViewModel(report: {
  ticker: string;
  asOf: string;
  status: string;
  snapshot: {
    price: number;
    baseFairValue: number;
    bull: number;
    marginOfSafety: number[];
  };
  valuation: { type: string };
  dualTrack?: any;
}): ResolvedReportMeta {
  const dualEconomic = Boolean(report.dualTrack);
  const dual = report.dualTrack;
  const matchedRule: OverrideRule | undefined = overrides.modelOverrides.find(
    (rule) => rule.ticker === report.ticker && report.asOf >= rule.minAsOf,
  );

  const isAudit = matchedRule?.snapshotClass === 'audit';
  const isNtmEconomic = dualEconomic || matchedRule?.snapshotClass === 'ntm';
  const conditionalModel = dualEconomic || Boolean(matchedRule?.conditionalModel);

  const split = splits[report.ticker];
  const latestFiling = fundamentals.items.find((i) => i.ticker === report.ticker);
  const model = activeModel(report.ticker);
  const olderModel = Boolean(latestFiling && latestFiling.statement.filed > report.asOf);
  const historic = Boolean(model || olderModel);
  const preSplit = Boolean(split && report.asOf < split.tradingDate);
  const originalGap = snapshotGap(report.snapshot.baseFairValue, report.snapshot.price);
  const v2 = getBuySideV2(report.ticker);

  const typeMethods = overrides.valuationTypeMethods as Record<string, string>;
  const methodSlug = dualEconomic
    ? dual.method
    : matchedRule?.methodSlug ?? typeMethods[report.valuation.type] ?? typeMethods.default;

  const snapshotDateLabel =
    matchedRule?.snapshotDateLabel ?? (dualEconomic ? '11/13正規盤收盤' : report.asOf);

  const cardPillLabel = model
    ? `${model.label} · ${model.date}`
    : historic
      ? `歷史模型 · ${report.asOf}`
      : `${
          dualEconomic
            ? '雙軌估值'
            : matchedRule?.cardPillPrefix ?? (report.status === 'current' ? '研究快照' : '封存快照')
        } · ${report.asOf}`;

  const cardBaseLabel = dualEconomic
    ? '未來十二個月獲利基準'
    : matchedRule?.baseLabel ?? (historic ? '歷史基準' : '基準合理價');

  const detailBaseLabel = dualEconomic
    ? 'NTM經濟基準'
    : matchedRule?.detailBaseLabel ?? (historic ? '歷史基準' : '基準合理價');

  const scenarioBaseLabel = dualEconomic
    ? 'NTM經濟基準'
    : matchedRule?.scenarioBaseLabel ?? '基準';

  const fairRangeLabel =
    matchedRule?.fairRangeLabel ?? (conditionalModel ? '基準倍數敏感度' : '一般合理區間');

  const mosLabel =
    matchedRule?.mosLabel ?? (conditionalModel ? '模型折讓區（非買點）' : '安全邊際區');

  const sourceLinkLabel =
    dualEconomic
      ? '查看本篇原始來源 ↗'
      : matchedRule?.sourceLinkLabel ??
        (conditionalModel ? '查看本篇Q3原始來源 ↗' : '查看最新 SEC 基本面核對 ↗');

  const calcFieldLabel = isNtmEconomic
    ? '含股權薪酬的未來十二個月每股盈餘'
    : report.valuation.type === 'cycle-pe'
      ? '週期正常化每股盈餘'
      : '正常化每股盈餘';

  const [mosLow, mosHigh] = report.snapshot.marginOfSafety;
  const fallbackVerdict =
    report.snapshot.price < (mosLow ?? 0)
      ? `目前價格低於模型折讓區下緣（$${mosLow}–$${mosHigh}）；需搭配上方「買方五大檢查」確認基本面與現金流是否同步改善。`
      : report.snapshot.price <= (mosHigh ?? 0)
        ? `目前價格落於模型折讓區（$${mosLow}–$${mosHigh}），應優先檢驗營收動能與自由現金流轉化率。`
        : report.snapshot.price < report.snapshot.baseFairValue
          ? `目前價格低於基準估值，但尚未進入高安全邊際折讓區，需依賴營運執行與利潤率支撐。`
          : report.snapshot.price <= report.snapshot.bull
            ? `目前價格高於基準估值，市場已預先反映相當比例的樂觀預期，須嚴防增速不如預期的倍數壓縮。`
            : `目前價格高於樂觀情境，市場要求多項利多同時兌現，容錯空間有限。`;

  const priceVerdict = dualEconomic
    ? chinese(dual.verdict)
    : matchedRule?.priceVerdict ?? fallbackVerdict;

  return {
    dualEconomic,
    dual,
    conditionalModel,
    isAudit,
    isNtmEconomic,
    split,
    latestFiling,
    activeModel: model,
    olderModel,
    historic,
    preSplit,
    originalGap,
    methodSlug,
    snapshotDateLabel,
    cardPillLabel,
    cardBaseLabel,
    detailBaseLabel,
    scenarioBaseLabel,
    fairRangeLabel,
    mosLabel,
    sourceLinkLabel,
    calcFieldLabel,
    priceVerdict,
    buysideV2: v2,
  };
}

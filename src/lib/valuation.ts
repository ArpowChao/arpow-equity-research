export interface StressInputs {
  seedRevenueM: number;
  years: number;
  annualRevenueGrowth: number;
  grossMargin: number;
  opexRatio: number;
  netOtherM: number;
  taxRate: number;
  initialSharesM: number;
  annualDilution: number;
  terminalPe: number;
  discountRate: number;
  fcfConversion?: number;
}

export interface StressYearRow {
  year: number;
  revenueM: number;
  grossProfitM: number;
  opexM: number;
  operatingIncomeM: number;
  netIncomeM: number;
  sharesM: number;
  eps: number;
  fcfM: number;
  fcfPerShare: number;
  pvFcfPerShare: number;
}

export interface StressResult {
  years: StressYearRow[];
  terminalValue: number;
  cumFcfPerShare: number;
  totalExitValue: number;
  pvTerminal: number;
  pvInterimFcf: number;
  presentValue: number;
  annualReturnExFcf: number | null;
  annualReturnTotal: number | null;
  gapPctVsPrice: number | null;
}

export interface MatrixCell {
  growth: number;
  grossMargin: number;
  year4Eps: number;
  terminalValue: number;
  pvTerminal: number;
  pvInterimFcf: number;
  presentValue: number;
  gapPct: number | null;
  annualReturnTotal: number | null;
}

export interface StressMatrix2D {
  growthRates: number[];
  grossMargins: number[];
  cells: MatrixCell[][];
}

export interface ImpliedCagrResult {
  impliedAnnualRevCagr: number;
  achievedPv: number;
  impliedYear4RevenueM: number;
  impliedYear4Eps: number;
  bounded: 'ok' | 'below_min' | 'above_max';
}

export function calcFcfInclusiveStress(
  inputs: StressInputs,
  currentPrice?: number,
  includeInterimFcf = true,
): StressResult {
  const yearsCount = Math.max(1, Math.round(inputs.years || 4));
  const conv = inputs.fcfConversion ?? 0.85;
  let rev = inputs.seedRevenueM;
  let shares = inputs.initialSharesM;
  let cumFcfPerShare = 0;
  let pvInterimFcf = 0;
  let lastEps = 0;
  const rows: StressYearRow[] = [];

  for (let yr = 1; yr <= yearsCount; yr++) {
    rev *= 1 + inputs.annualRevenueGrowth;
    shares *= 1 + inputs.annualDilution;
    const grossProfitM = rev * inputs.grossMargin;
    const opexM = rev * inputs.opexRatio;
    const operatingIncomeM = grossProfitM - opexM;
    const netIncomeM = (operatingIncomeM + inputs.netOtherM) * (1 - inputs.taxRate);
    const eps = netIncomeM / shares;
    const rawFcfM = netIncomeM > 0 ? netIncomeM * conv : netIncomeM;
    const fcfM = includeInterimFcf ? rawFcfM : 0;
    const fcfPerShare = fcfM / shares;
    const pvFcfPerShare = fcfPerShare / Math.pow(1 + inputs.discountRate, yr);

    cumFcfPerShare += fcfPerShare;
    pvInterimFcf += pvFcfPerShare;
    lastEps = eps;

    rows.push({
      year: yr,
      revenueM: rev,
      grossProfitM,
      opexM,
      operatingIncomeM,
      netIncomeM,
      sharesM: shares,
      eps,
      fcfM,
      fcfPerShare,
      pvFcfPerShare,
    });
  }

  const terminalValue = lastEps * inputs.terminalPe;
  const pvTerminal = terminalValue / Math.pow(1 + inputs.discountRate, yearsCount);
  const presentValue = pvTerminal + pvInterimFcf;
  const totalExitValue = terminalValue + cumFcfPerShare;

  let annualReturnExFcf: number | null = null;
  let annualReturnTotal: number | null = null;
  let gapPctVsPrice: number | null = null;

  if (currentPrice && Number.isFinite(currentPrice) && currentPrice > 0) {
    if (terminalValue > 0) {
      annualReturnExFcf = Math.pow(terminalValue / currentPrice, 1 / yearsCount) - 1;
    }
    if (totalExitValue > 0) {
      annualReturnTotal = Math.pow(totalExitValue / currentPrice, 1 / yearsCount) - 1;
    }
    gapPctVsPrice = presentValue / currentPrice - 1;
  }

  return {
    years: rows,
    terminalValue,
    cumFcfPerShare,
    totalExitValue,
    pvTerminal,
    pvInterimFcf,
    presentValue,
    annualReturnExFcf,
    annualReturnTotal,
    gapPctVsPrice,
  };
}

export function calc2DStressMatrix(
  baseInputs: StressInputs,
  growthRates: number[],
  grossMargins: number[],
  currentPrice: number,
): StressMatrix2D {
  const cells = growthRates.map((growth) =>
    grossMargins.map((grossMargin) => {
      const res = calcFcfInclusiveStress(
        { ...baseInputs, annualRevenueGrowth: growth, grossMargin },
        currentPrice,
        true,
      );
      return {
        growth,
        grossMargin,
        year4Eps: res.years[res.years.length - 1]!.eps,
        terminalValue: res.terminalValue,
        pvTerminal: res.pvTerminal,
        pvInterimFcf: res.pvInterimFcf,
        presentValue: res.presentValue,
        gapPct: res.gapPctVsPrice,
        annualReturnTotal: res.annualReturnTotal,
      };
    }),
  );
  return { growthRates, grossMargins, cells };
}

export function solveImpliedCagr(
  currentPrice: number,
  baseInputs: StressInputs,
  low = -0.4,
  high = 1.5,
  tol = 1e-7,
): ImpliedCagrResult {
  const evalG = (g: number) =>
    calcFcfInclusiveStress({ ...baseInputs, annualRevenueGrowth: g }, currentPrice, true);

  const resLow = evalG(low);
  if (resLow.presentValue >= currentPrice) {
    const last = resLow.years[resLow.years.length - 1]!;
    return {
      impliedAnnualRevCagr: low,
      achievedPv: resLow.presentValue,
      impliedYear4RevenueM: last.revenueM,
      impliedYear4Eps: last.eps,
      bounded: 'below_min',
    };
  }
  const resHigh = evalG(high);
  if (resHigh.presentValue < currentPrice) {
    const last = resHigh.years[resHigh.years.length - 1]!;
    return {
      impliedAnnualRevCagr: high,
      achievedPv: resHigh.presentValue,
      impliedYear4RevenueM: last.revenueM,
      impliedYear4Eps: last.eps,
      bounded: 'above_max',
    };
  }

  let lo = low;
  let hi = high;
  let midRes = resLow;
  for (let iter = 0; iter < 80; iter++) {
    const mid = 0.5 * (lo + hi);
    midRes = evalG(mid);
    const diff = midRes.presentValue - currentPrice;
    if (Math.abs(diff) <= tol || hi - lo <= tol) {
      const last = midRes.years[midRes.years.length - 1]!;
      return {
        impliedAnnualRevCagr: mid,
        achievedPv: midRes.presentValue,
        impliedYear4RevenueM: last.revenueM,
        impliedYear4Eps: last.eps,
        bounded: 'ok',
      };
    }
    if (diff < 0) lo = mid;
    else hi = mid;
  }

  const last = midRes.years[midRes.years.length - 1]!;
  return {
    impliedAnnualRevCagr: 0.5 * (lo + hi),
    achievedPv: midRes.presentValue,
    impliedYear4RevenueM: last.revenueM,
    impliedYear4Eps: last.eps,
    bounded: 'ok',
  };
}

export function computeErpSpread(
  currentPrice: number,
  ntmEps: number,
  riskFree10yPct: number,
): { impliedForwardPe: number; earningsYieldPct: number; erpVs10yPct: number } {
  const impliedForwardPe = currentPrice / ntmEps;
  const earningsYieldPct = (ntmEps / currentPrice) * 100;
  const erpVs10yPct = earningsYieldPct - riskFree10yPct;
  return { impliedForwardPe, earningsYieldPct, erpVs10yPct };
}

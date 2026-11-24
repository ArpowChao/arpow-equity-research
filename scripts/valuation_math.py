#!/usr/bin/env python3
"""Deterministic buy-side valuation and FCF-inclusive stress math engine.

Single source of truth for NTM scenario EPS, FCF-inclusive 4-year valuation,
2D Revenue Growth x Gross Margin stress matrices, Reverse Valuation implied CAGR,
and Equity Risk Premium (ERP) vs 10Y US Treasury spreads.
"""
from __future__ import annotations

import argparse
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 28

ROOT = Path(__file__).resolve().parents[1]


def _d(value: float | int | str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def calc_ntm_scenario(
    revenue_m: float,
    gross_margin: float,
    opex_m: float,
    net_other_m: float,
    tax_rate: float,
    shares_m: float,
    pe: float,
) -> dict[str, float]:
    """Compute exact NTM economic EPS and target value from unit inputs."""
    rev = _d(revenue_m)
    gm = _d(gross_margin)
    opex = _d(opex_m)
    other = _d(net_other_m)
    tax = _d(tax_rate)
    shares = _d(shares_m)
    mult = _d(pe)
    if shares <= 0:
        raise ValueError("shares_m must be positive")

    gp = rev * gm
    op_inc = gp - opex
    ni = (op_inc + other) * (Decimal("1") - tax)
    eps = ni / shares
    val = eps * mult
    return {
        "revenueM": float(rev),
        "grossProfitM": float(gp),
        "opexM": float(opex),
        "operatingIncomeM": float(op_inc),
        "netIncomeM": float(ni),
        "sharesM": float(shares),
        "eps": float(eps),
        "pe": float(mult),
        "value": float(val),
    }


def calc_fcf_inclusive_stress(
    seed_revenue_m: float,
    annual_revenue_growth: float,
    gross_margin: float,
    opex_ratio: float,
    net_other_m: float,
    tax_rate: float,
    initial_shares_m: float,
    annual_dilution: float,
    terminal_pe: float,
    discount_rate: float,
    years: int = 4,
    fcf_conversion: float = 0.85,
    current_price: float | None = None,
    include_interim_fcf: bool = True,
) -> dict[str, Any]:
    """Compute 4-year stress valuation including discounted interim FCF per share.

    Fixes v1 Track B's structural omission where 4 years of intermediate free cash
    flow were evaporated before discounting Year-4 terminal equity value back to today.
    """
    if years < 1:
        raise ValueError("years must be >= 1")
    rev = _d(seed_revenue_m)
    g = _d(annual_revenue_growth)
    gm = _d(gross_margin)
    opex_r = _d(opex_ratio)
    other = _d(net_other_m)
    tax = _d(tax_rate)
    shares = _d(initial_shares_m)
    dil = _d(annual_dilution)
    t_pe = _d(terminal_pe)
    dr = _d(discount_rate)
    conv = _d(fcf_conversion)

    if shares <= 0 or (Decimal("1") + dr) <= 0:
        raise ValueError("initial_shares_m and (1 + discount_rate) must be positive")

    year_rows: list[dict[str, float]] = []
    cum_fcf_ps = Decimal("0")
    pv_interim_fcf = Decimal("0")
    last_eps = Decimal("0")

    for yr in range(1, years + 1):
        rev = rev * (Decimal("1") + g)
        shares = shares * (Decimal("1") + dil)
        gp = rev * gm
        opex = rev * opex_r
        op_inc = gp - opex
        ni = (op_inc + other) * (Decimal("1") - tax)
        eps = ni / shares
        # Apply FCF conversion only to positive net income; losses reflect 100% burn.
        fcf = (ni * conv) if ni > 0 else ni
        fcf_ps = fcf / shares if include_interim_fcf else Decimal("0")
        discount_factor = (Decimal("1") + dr) ** yr
        pv_fcf_ps = fcf_ps / discount_factor

        cum_fcf_ps += fcf_ps
        pv_interim_fcf += pv_fcf_ps
        last_eps = eps

        year_rows.append(
            {
                "year": yr,
                "revenueM": float(rev),
                "grossProfitM": float(gp),
                "opexM": float(opex),
                "operatingIncomeM": float(op_inc),
                "netIncomeM": float(ni),
                "sharesM": float(shares),
                "eps": float(eps),
                "fcfM": float(fcf if include_interim_fcf else Decimal("0")),
                "fcfPerShare": float(fcf_ps),
                "pvFcfPerShare": float(pv_fcf_ps),
            }
        )

    terminal_value = last_eps * t_pe
    pv_terminal = terminal_value / ((Decimal("1") + dr) ** years)
    present_value = pv_terminal + pv_interim_fcf
    total_exit_value = terminal_value + cum_fcf_ps

    annual_return_ex_fcf: float | None = None
    annual_return_total: float | None = None
    gap_pct: float | None = None

    if current_price is not None and current_price > 0:
        p = float(current_price)
        tv_f = float(terminal_value)
        tot_f = float(total_exit_value)
        pv_f = float(present_value)
        if tv_f > 0:
            annual_return_ex_fcf = (tv_f / p) ** (1.0 / years) - 1.0
        if tot_f > 0:
            annual_return_total = (tot_f / p) ** (1.0 / years) - 1.0
        gap_pct = (pv_f / p) - 1.0

    return {
        "years": year_rows,
        "terminalValue": float(terminal_value),
        "cumFcfPerShare": float(cum_fcf_ps),
        "totalExitValue": float(total_exit_value),
        "pvTerminal": float(pv_terminal),
        "pvInterimFcf": float(pv_interim_fcf),
        "presentValue": float(present_value),
        "annualReturnExFcf": annual_return_ex_fcf,
        "annualReturnTotal": annual_return_total,
        "gapPctVsPrice": gap_pct,
    }


def _strip_stress_kwargs(base_inputs: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "seedRevenueM": "seed_revenue_m",
        "annualRevenueGrowth": "annual_revenue_growth",
        "grossMargin": "gross_margin",
        "opexRatio": "opex_ratio",
        "netOtherM": "net_other_m",
        "taxRate": "tax_rate",
        "initialSharesM": "initial_shares_m",
        "annualDilution": "annual_dilution",
        "terminalPe": "terminal_pe",
        "discountRate": "discount_rate",
        "years": "years",
        "fcfConversion": "fcf_conversion",
    }
    out: dict[str, Any] = {}
    for k_src, k_dst in allowed.items():
        if k_src in base_inputs:
            out[k_dst] = base_inputs[k_src]
        elif k_dst in base_inputs:
            out[k_dst] = base_inputs[k_dst]
    return out


def calc_2d_stress_matrix(
    base_inputs: dict[str, Any],
    growth_rates: list[float],
    gross_margins: list[float],
    current_price: float,
) -> dict[str, Any]:
    """Generate a Revenue Growth x Gross Margin 2D matrix (FCF-inclusive PV)."""
    kwargs = _strip_stress_kwargs(base_inputs)
    cells: list[list[dict[str, Any]]] = []
    for g in growth_rates:
        row: list[dict[str, Any]] = []
        for gm in gross_margins:
            cell_kwargs = dict(kwargs)
            cell_kwargs["annual_revenue_growth"] = g
            cell_kwargs["gross_margin"] = gm
            res = calc_fcf_inclusive_stress(
                current_price=current_price,
                include_interim_fcf=True,
                **cell_kwargs,
            )
            row.append(
                {
                    "growth": float(g),
                    "grossMargin": float(gm),
                    "year4Eps": res["years"][-1]["eps"],
                    "terminalValue": res["terminalValue"],
                    "pvTerminal": res["pvTerminal"],
                    "pvInterimFcf": res["pvInterimFcf"],
                    "presentValue": res["presentValue"],
                    "gapPct": res["gapPctVsPrice"],
                    "annualReturnTotal": res["annualReturnTotal"],
                }
            )
        cells.append(row)
    return {
        "growthRates": [float(x) for x in growth_rates],
        "grossMargins": [float(x) for x in gross_margins],
        "cells": cells,
    }


def solve_reverse_implied_cagr(
    current_price: float,
    base_inputs: dict[str, Any],
    low: float = -0.40,
    high: float = 1.50,
    tol: float = 1e-7,
) -> dict[str, Any]:
    """Solve for the 4-year annual revenue CAGR whose FCF-inclusive PV equals current_price."""
    if current_price <= 0:
        raise ValueError("current_price must be positive")
    kwargs = _strip_stress_kwargs(base_inputs)

    def eval_g(g_val: float) -> dict[str, Any]:
        k = dict(kwargs)
        k["annual_revenue_growth"] = g_val
        return calc_fcf_inclusive_stress(current_price=current_price, include_interim_fcf=True, **k)

    res_low = eval_g(low)
    if res_low["presentValue"] >= current_price:
        return {
            "impliedAnnualRevCagr": low,
            "achievedPv": res_low["presentValue"],
            "impliedYear4RevenueM": res_low["years"][-1]["revenueM"],
            "impliedYear4Eps": res_low["years"][-1]["eps"],
            "bounded": "below_min",
        }
    res_high = eval_g(high)
    if res_high["presentValue"] < current_price:
        return {
            "impliedAnnualRevCagr": high,
            "achievedPv": res_high["presentValue"],
            "impliedYear4RevenueM": res_high["years"][-1]["revenueM"],
            "impliedYear4Eps": res_high["years"][-1]["eps"],
            "bounded": "above_max",
        }

    lo, hi = low, high
    mid_res = res_low
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        mid_res = eval_g(mid)
        diff = mid_res["presentValue"] - current_price
        if abs(diff) <= tol or (hi - lo) <= tol:
            return {
                "impliedAnnualRevCagr": mid,
                "achievedPv": mid_res["presentValue"],
                "impliedYear4RevenueM": mid_res["years"][-1]["revenueM"],
                "impliedYear4Eps": mid_res["years"][-1]["eps"],
                "bounded": "ok",
            }
        if diff < 0:
            lo = mid
        else:
            hi = mid

    return {
        "impliedAnnualRevCagr": 0.5 * (lo + hi),
        "achievedPv": mid_res["presentValue"],
        "impliedYear4RevenueM": mid_res["years"][-1]["revenueM"],
        "impliedYear4Eps": mid_res["years"][-1]["eps"],
        "bounded": "ok",
    }


def compute_erp_spread(current_price: float, ntm_eps: float, risk_free_10y_pct: float) -> dict[str, float]:
    """Compute implied forward P/E, earnings yield %, and ERP spread over 10Y US Treasury."""
    if current_price <= 0 or ntm_eps <= 0:
        raise ValueError("current_price and ntm_eps must be positive")
    fwd_pe = current_price / ntm_eps
    earnings_yield_pct = (ntm_eps / current_price) * 100.0
    erp_pct = earnings_yield_pct - risk_free_10y_pct
    return {
        "impliedForwardPe": fwd_pe,
        "earningsYieldPct": earnings_yield_pct,
        "erpVs10yPct": erp_pct,
    }


def verify_v2_file(path: Path) -> list[str]:
    """Verify every numeric calculation inside a buyside-v2 JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    for item in data.get("items", []):
        tk = item.get("ticker", "UNKNOWN")
        price = float(item["priceSnapshot"]["price"])
        rf = float(item["macroContext"]["us10yYieldPct"])
        rv = item["reverseValuation"]
        erp_calc = compute_erp_spread(price, float(rv["ntmBaseEps"]), rf)
        for field in ("impliedForwardPe", "earningsYieldPct", "erpVs10yPct"):
            if not math.isclose(float(rv[field]), erp_calc[field], rel_tol=1e-4, abs_tol=1e-3):
                errors.append(f"{tk} reverseValuation.{field}: got {rv[field]}, expected {erp_calc[field]}")

        sv2 = item["stressV2"]
        inp = sv2["inputs"]
        stress_kwargs = _strip_stress_kwargs(inp)
        calc_fcf = calc_fcf_inclusive_stress(current_price=price, include_interim_fcf=True, **stress_kwargs)
        calc_ex = calc_fcf_inclusive_stress(current_price=price, include_interim_fcf=False, **stress_kwargs)

        recorded_fcf = sv2["fcfInclusiveResult"]
        for key in ("terminalValue", "cumFcfPerShare", "totalExitValue", "pvTerminal", "pvInterimFcf", "presentValue"):
            if not math.isclose(float(recorded_fcf[key]), float(calc_fcf[key]), rel_tol=1e-5, abs_tol=1e-4):
                errors.append(f"{tk} fcfInclusiveResult.{key}: got {recorded_fcf[key]}, expected {calc_fcf[key]}")

        if not math.isclose(float(sv2["legacyExFcfPv"]), float(calc_ex["presentValue"]), rel_tol=1e-5, abs_tol=1e-4):
            errors.append(f"{tk} legacyExFcfPv: got {sv2['legacyExFcfPv']}, expected {calc_ex['presentValue']}")

        expected_delta = float(calc_fcf["presentValue"]) - float(calc_ex["presentValue"])
        if not math.isclose(float(sv2["fcfPvDelta"]), expected_delta, rel_tol=1e-5, abs_tol=1e-4):
            errors.append(f"{tk} fcfPvDelta: got {sv2['fcfPvDelta']}, expected {expected_delta}")

        if sv2.get("altNtmSeedRevenueM") is not None and sv2.get("altNtmSeedResult") is not None:
            alt_kwargs = dict(stress_kwargs)
            alt_kwargs["seed_revenue_m"] = float(sv2["altNtmSeedRevenueM"])
            calc_alt = calc_fcf_inclusive_stress(current_price=price, include_interim_fcf=True, **alt_kwargs)
            rec_alt = sv2["altNtmSeedResult"]
            for key in ("terminalValue", "cumFcfPerShare", "totalExitValue", "pvTerminal", "pvInterimFcf", "presentValue"):
                if not math.isclose(float(rec_alt[key]), float(calc_alt[key]), rel_tol=1e-5, abs_tol=1e-4):
                    errors.append(f"{tk} altNtmSeedResult.{key}: got {rec_alt[key]}, expected {calc_alt[key]}")

        # Verify reverse implied CAGRs (both at base gross margin and stress gross margin)
        rev_cagr_stress = solve_reverse_implied_cagr(price, inp)
        if not math.isclose(
            float(rv["implied4yRevCagrStressMargin"]),
            float(rev_cagr_stress["impliedAnnualRevCagr"]),
            rel_tol=1e-3,
            abs_tol=1e-4,
        ):
            errors.append(
                f"{tk} implied4yRevCagrStressMargin: got {rv['implied4yRevCagrStressMargin']}, expected {rev_cagr_stress['impliedAnnualRevCagr']}"
            )

        base_gm = rv.get("baseGrossMarginForReverse")
        if base_gm is not None:
            base_inp = dict(inp)
            base_inp["grossMargin"] = float(base_gm)
            rev_cagr_base = solve_reverse_implied_cagr(price, base_inp)
            if not math.isclose(
                float(rv["implied4yRevCagrBaseMargin"]),
                float(rev_cagr_base["impliedAnnualRevCagr"]),
                rel_tol=1e-3,
                abs_tol=1e-4,
            ):
                errors.append(
                    f"{tk} implied4yRevCagrBaseMargin: got {rv['implied4yRevCagrBaseMargin']}, expected {rev_cagr_base['impliedAnnualRevCagr']}"
                )
            if sv2.get("altNtmSeedRevenueM") is not None and rv.get("implied4yRevCagrFromNtmSeed") is not None:
                ntm_inp = dict(base_inp)
                ntm_inp["seedRevenueM"] = float(sv2["altNtmSeedRevenueM"])
                rev_cagr_ntm = solve_reverse_implied_cagr(price, ntm_inp)
                if not math.isclose(
                    float(rv["implied4yRevCagrFromNtmSeed"]),
                    float(rev_cagr_ntm["impliedAnnualRevCagr"]),
                    rel_tol=1e-3,
                    abs_tol=1e-4,
                ):
                    errors.append(
                        f"{tk} implied4yRevCagrFromNtmSeed: got {rv['implied4yRevCagrFromNtmSeed']}, expected {rev_cagr_ntm['impliedAnnualRevCagr']}"
                    )

        # Verify 2D matrix
        mat = sv2["matrix2d"]
        calc_mat = calc_2d_stress_matrix(inp, mat["growthRates"], mat["grossMargins"], price)
        for ri, row in enumerate(mat["cells"]):
            for ci, cell in enumerate(row):
                exp = calc_mat["cells"][ri][ci]
                for key in ("presentValue", "gapPct", "year4Eps", "pvInterimFcf"):
                    if not math.isclose(float(cell[key]), float(exp[key]), rel_tol=1e-4, abs_tol=1e-4):
                        errors.append(f"{tk} matrix[{ri}][{ci}].{key}: got {cell[key]}, expected {exp[key]}")
    return errors


def emit_nvda_calc() -> dict[str, Any]:
    """Emit exact verified v2 calculations for NVDA (2026-11-18 snapshot + 2026-11-20 macro)."""
    price = 155.46
    ntm_eps = 12.270351239669422
    rf = 5.04
    erp = compute_erp_spread(price, ntm_eps, rf)

    ttm_stress_inputs = {
        "seedRevenueM": 361808.0,
        "annualRevenueGrowth": 0.10,
        "grossMargin": 0.60,
        "opexRatio": 0.12,
        "netOtherM": 0.0,
        "taxRate": 0.22,
        "initialSharesM": 24200.0,
        "annualDilution": 0.005,
        "terminalPe": 15.0,
        "discountRate": 0.10,
        "years": 4,
        "fcfConversion": 0.85,
    }
    ntm_seed_inputs = dict(ttm_stress_inputs)
    ntm_seed_inputs["seedRevenueM"] = 575000.0

    ttm_fcf_res = calc_fcf_inclusive_stress(current_price=price, include_interim_fcf=True, **(_strip_stress_kwargs(ttm_stress_inputs)))
    ttm_legacy_res = calc_fcf_inclusive_stress(current_price=price, include_interim_fcf=False, **(_strip_stress_kwargs(ttm_stress_inputs)))
    ntm_fcf_res = calc_fcf_inclusive_stress(current_price=price, include_interim_fcf=True, **(_strip_stress_kwargs(ntm_seed_inputs)))

    growth_rates = [0.00, 0.10, 0.15]
    gross_margins = [0.60, 0.65, 0.715]
    matrix_ttm = calc_2d_stress_matrix(ttm_stress_inputs, growth_rates, gross_margins, price)

    rev_cagr_stress = solve_reverse_implied_cagr(price, ttm_stress_inputs)
    base_gm_inputs = dict(ttm_stress_inputs)
    base_gm_inputs["grossMargin"] = 0.715
    rev_cagr_base = solve_reverse_implied_cagr(price, base_gm_inputs)
    base_gm_ntm_inputs = dict(ntm_seed_inputs)
    base_gm_ntm_inputs["grossMargin"] = 0.715
    rev_cagr_ntm = solve_reverse_implied_cagr(price, base_gm_ntm_inputs)

    return {
        "erp": erp,
        "ttmStressFcf": ttm_fcf_res,
        "ttmLegacyExFcf": ttm_legacy_res,
        "fcfPvDelta": ttm_fcf_res["presentValue"] - ttm_legacy_res["presentValue"],
        "ntmSeedStressFcf": ntm_fcf_res,
        "matrix2d": matrix_ttm,
        "reverseStressMargin": rev_cagr_stress,
        "reverseBaseMarginFromTtm": rev_cagr_base,
        "reverseBaseMarginFromNtm": rev_cagr_ntm,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic buy-side equity math & verification.")
    parser.add_argument("--verify-v2", type=Path, help="Verify all calculations inside a buyside-v2 JSON file.")
    parser.add_argument("--emit-nvda-calc", action="store_true", help="Print computed NVDA v2 metrics as JSON.")
    args = parser.parse_args()

    if args.emit_nvda_calc:
        print(json.dumps(emit_nvda_calc(), ensure_ascii=False, indent=2))
        return 0
    if args.verify_v2:
        errs = verify_v2_file(args.verify_v2)
        if errs:
            for e in errs:
                print("FAIL:", e)
            return 1
        print(f"PASS: verified v2 math in {args.verify_v2}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

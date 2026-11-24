#!/usr/bin/env python3
"""Unit tests for deterministic buy-side valuation math and ticker discovery."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import update_live_quotes as ulq
import valuation_math as vm


def test_ex_fcf_matches_legacy_nvda() -> None:
    nvda_raw = json.loads((ROOT / "src/data/nvda-2026-11-18.json").read_text(encoding="utf-8"))["results"][0]
    tailored = nvda_raw["calculations"]["tailored"]
    inp = tailored["inputs"]

    ex_fcf = vm.calc_fcf_inclusive_stress(
        seed_revenue_m=inp["seedRevenueM"],
        annual_revenue_growth=inp["annualRevenueGrowth"],
        gross_margin=inp["grossMargin"],
        opex_ratio=inp["opexRatio"],
        net_other_m=inp["netOtherM"],
        tax_rate=inp["taxRate"],
        initial_shares_m=inp["initialSharesM"],
        annual_dilution=inp["annualDilution"],
        terminal_pe=inp["terminalPe"],
        discount_rate=inp["discountRate"],
        years=inp["years"],
        fcf_conversion=0.85,
        current_price=155.46,
        include_interim_fcf=False,
    )
    assert math.isclose(ex_fcf["terminalValue"], tailored["terminalValue"], rel_tol=1e-9)
    assert math.isclose(ex_fcf["presentValue"], tailored["presentValue"], rel_tol=1e-9)
    assert ex_fcf["pvInterimFcf"] == 0.0


def test_fcf_inclusive_adds_discounted_cashflow() -> None:
    with_fcf = vm.calc_fcf_inclusive_stress(
        seed_revenue_m=361808.0,
        annual_revenue_growth=0.10,
        gross_margin=0.60,
        opex_ratio=0.12,
        net_other_m=0.0,
        tax_rate=0.22,
        initial_shares_m=24200.0,
        annual_dilution=0.005,
        terminal_pe=15.0,
        discount_rate=0.10,
        years=4,
        fcf_conversion=0.85,
        current_price=155.46,
        include_interim_fcf=True,
    )
    assert with_fcf["pvInterimFcf"] > 15.0
    assert math.isclose(
        with_fcf["presentValue"],
        with_fcf["pvTerminal"] + with_fcf["pvInterimFcf"],
        rel_tol=1e-12,
    )
    assert with_fcf["annualReturnTotal"] > with_fcf["annualReturnExFcf"]


def test_2d_matrix_monotonic_and_reverse_cagr_roundtrip() -> None:
    inp = {
        "seedRevenueM": 361808.0,
        "years": 4,
        "annualRevenueGrowth": 0.10,
        "grossMargin": 0.60,
        "opexRatio": 0.12,
        "netOtherM": 0.0,
        "taxRate": 0.22,
        "initialSharesM": 24200.0,
        "annualDilution": 0.005,
        "terminalPe": 15.0,
        "discountRate": 0.10,
        "fcfConversion": 0.85,
    }
    price = 155.46
    mat = vm.calc_2d_stress_matrix(inp, [0.0, 0.10, 0.15], [0.60, 0.65, 0.715], price)
    cells = mat["cells"]
    assert len(cells) == 3 and all(len(r) == 3 for r in cells)
    for ri in range(3):
        assert cells[ri][0]["presentValue"] < cells[ri][1]["presentValue"] < cells[ri][2]["presentValue"]
    for ci in range(3):
        assert cells[0][ci]["presentValue"] < cells[1][ci]["presentValue"] < cells[2][ci]["presentValue"]

    solved = vm.solve_reverse_implied_cagr(price, inp)
    assert solved["bounded"] == "ok"
    assert abs(solved["achievedPv"] - price) < 1e-4


def test_quote_discovery_includes_zs_and_all_reports() -> None:
    reports = json.loads((ROOT / "src/data/reports.generated.json").read_text(encoding="utf-8"))
    expected_from_reports = {r["ticker"].upper() for r in reports}
    discovered = set(ulq.discover_tickers(ROOT))
    assert expected_from_reports <= discovered
    assert "ZS" in discovered
    assert "NVDA" in discovered


def main() -> int:
    test_ex_fcf_matches_legacy_nvda()
    test_fcf_inclusive_adds_discounted_cashflow()
    test_2d_matrix_monotonic_and_reverse_cagr_roundtrip()
    test_quote_discovery_includes_zs_and_all_reports()
    print("PASS: valuation_math parity, FCF PV addition, 2D monotonicity, reverse CAGR round-trip, ZS quote discovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

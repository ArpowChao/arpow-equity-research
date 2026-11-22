---
name: buy-side-equity-research
description: Buy-side 5-module equity & earnings research workflow for arpow-equity-research (Storyline & Setup audit, Segment Bridge & Unit Economics, Reverse Valuation & Multi-Anchor Comps, FCF-inclusive 2D Stress Matrix, Falsifiable Verdict) with deterministic Python math verification.
---

# Buy-Side Equity Research v2 Skill

Use this skill whenever adding, updating, or reviewing stock research in `arpow-equity-research` (or exporting sanitized research JSON from the private pipeline into this public repo).

## Mandatory Pre-Read
1. Read `docs/RESEARCH_PLAYBOOK.md` for financial methodology and style rules.
2. Inspect `schemas/equity-report.v2.schema.json` and the golden example (`NVDA`) in `src/data/buyside-v2.json`.
3. Never hand-calculate PV, EPS, 2D stress matrices, or implied CAGR in prose — always compute via `scripts/valuation_math.py`.

## Five-Module Workflow (Execute in Order)

### Module 1 — Market Storyline & Setup (`storylineSetup` + `macroContext`)
- Separate the **3–6 month trading narrative** from **10-year macro noise**.
- Record the current **Macro Hurdle Rate** (`us10yYieldPct`, `real10yTipsPct`, `hyOasPct` with `asOf` date). High-multiple growth stocks must justify their terminal multiple against real rates.
- Identify **Consensus Expectation**, **Setup Crowding** (is the stock crowded after a multi-month rally or washed out near lows?), and **Where Wall Street is Linearly Extrapolating** (e.g., peak gross margin, peak ASP, unverified multi-year capex announcements).

### Module 2 — Accounting Reality, Segment Bridge & Unit Economics (`earningsQuality`, `segmentBridge`, `unitEconomics`, `callCoverage`)
- **Three-Layer Earnings Reconciliation**: GAAP Operating Income → Strip one-offs (investment gains, warrants, extra 53rd week, one-time tax refunds) → Economic Operating Income **keeping recurring SBC as a real shareholder cost**.
- **Cash Conversion Check**: Compare `TTM OCF` and `TTM FCF` against GAAP net income; flag DSO spikes, inventory builds, customer financing/guarantees, or capex/capitalized-software surges.
- **Segment Headwind/Tailwind Bridge (Minimum 2 segments)**: Never collapse multi-engine companies (e.g., `AMZN`, `MSFT`, `GOOGL`, `NVDA`) into one blended margin without decomposing growing vs shrinking segments.
- **Unit Economics & Call Coverage**: Tie management's growth claim to downstream reality (e.g., ARR vs customer IT budget, RPO current vs non-current, CapEx-to-cloud 12–18m lag, capacity commitments vs balance sheet liquidity). Explicitly state `full_qa | partial_clips | press_release_only` and list concrete unanswered Q&A questions.

### Module 3 — Reverse Valuation & Three-Anchor Comps (`reverseValuation`, `valuationAnchors`)
- Start from **today's price** before asserting a target price:
  - `impliedForwardPe = currentPrice / ntmBaseEps`
  - `earningsYieldPct = (ntmBaseEps / currentPrice) * 100`
  - `erpVs10yPct = earningsYieldPct - us10yYieldPct`
- Solve the **Implied 4-Year Revenue CAGR** using `scripts/valuation_math.py::solve_reverse_implied_cagr` so the market's bar is quantified in growth % terms at both base gross margin and stressed gross margin.
- Anchor your exit multiple with **two objective rulers**:
  1. The company's own 5Y/10Y historical P/E or EV/FCF band;
  2. At least **2 direct peers** (`fwdPe`, growth note, margin note, relative conclusion).

### Module 4 — FCF-Inclusive 2D Stress Test (`stressV2`)
- **FIX THE v1 FLAW**: Always include 4 years of discounted interim Free Cash Flow (`fcfConversion`, default `0.85` for asset-light/chip leaders; adjust downward only for heavy reinvestment phases) PLUS discounted terminal value:
  `PV = sum_{t=1..4}(FCF_per_share_t / (1 + r)^t) + (Year4_EPS * Terminal_PE / (1 + r)^4)`
- Avoid TTM cliff distortion: explicitly document whether the stress seed is `ttm_conservative` or `ntm_base`. If high-growth transition makes TTM unrepresentative (e.g. `AMD`, `NVDA`), compute `altNtmSeedResult` alongside `ttm_conservative` so readers see the sensitivity cleanly.
- Compute the **3×3 2D Matrix (`Revenue Growth × Gross Margin`)** via `calc_2d_stress_matrix` — never stress only gross margin while keeping revenue constant!

### Module 5 — Falsifiable Buy-Side Verdict (`verdict` + `sources`)
- Choose exactly one `tier`: `高勝率賠率` | `觀察待催化` | `估值透支迴避` | `資訊缺口暫緩`.
- Write a crisp `oneLiner` (<= 180 chars) stating the exact trade-off between valuation cushion and execution/macro risk.
- Define at least 2 quantitative **Confirm Triggers** and 2 quantitative **Invalidate Triggers**, plus explicit **Position Discipline**.

## Data-Only Publishing Contract & Hard Prohibitions
1. **NO `.astro` edits per ticker**: Add/update entries in `src/data/buyside-v2.json` and `src/data/ticker-overrides.json` only. `scripts/update_live_quotes.py` auto-discovers tickers across all JSON data files.
2. **NO Compliance-Bot Clichés**: Do NOT fill `verdict.oneLiner` or analysis cards with repetitive legal padding (`不是已證實公平價`, `不是買點`, `未指派機率`, `不構成投資建議`, `保證下限`). Keep the single global disclaimer in `Base.astro` footer; keep stock analysis razor-sharp.
3. **NO Duplicate Text Strings**: Never repeat the exact same paragraph across `thesis`, `analysis`, and `modelNotes` (fix the v1 NVDA duplication bug).
4. **NO Symlink Edits**: Never touch `CLAUDE.md` (git symlink to `AGENTS.md`).
5. **Preserve Archived History**: Do NOT rewrite historical snapshot JSONs (`reports.generated.json`, `nvda-2026-11-18.json`, `six-2026-11-14.json`, `selection-14.json`, `revaluation-2026-11-22.json`) unless specifically migrating an old ticker cleanly without breaking `validate_public.py` and `verify_learning.py`.

## Mandatory Verification Sequence
Before pushing any commit or opening a PR:
```bash
npx astro check
python3 scripts/valuation_math.py --verify-v2 src/data/buyside-v2.json
npm test
```
All commands must exit with code `0`.

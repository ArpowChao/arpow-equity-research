# Arpow Equity Research — Agent & Hermes Operating Manual

> **NOTE TO HERMES / CODING AGENTS**: Every file listed in Section 1 is tracked in this repository and is your **mandatory curriculum** before generating, updating, or auditing any stock report. Never guess valuation math with LLM arithmetic and never copy v1 compliance-bot boilerplate.

## 1. Mandatory Reading Order (Read Before Acting)
1. **[docs/RESEARCH_PLAYBOOK.md](docs/RESEARCH_PLAYBOOK.md)** — Full Buy-Side v2 methodology (synthesizing Storyline & Setup audit, Segment Bridge, Unit Economics, Reverse Valuation, FCF-inclusive 2D Stress Matrix, and Taiwan Traditional Chinese tone guide).
2. **[.agents/skills/buy-side-equity-research/SKILL.md](.agents/skills/buy-side-equity-research/SKILL.md)** — Step-by-step execution checklist and publication contract.
3. **[schemas/equity-report.v2.schema.json](schemas/equity-report.v2.schema.json)** — Strict JSON contract for `src/data/buyside-v2.json`.
4. **[scripts/valuation_math.py](scripts/valuation_math.py)** — Deterministic Python (`Decimal`) math engine for NTM scenarios, FCF-inclusive 4Y PV, 2D matrices, Reverse Implied CAGR, and ERP spread.

## 2. Hard Rules & Anti-Patterns to Avoid
1. **No Evapored FCF in Track B**: Always calculate 4-year stress PV using `scripts/valuation_math.py::calc_fcf_inclusive_stress(..., include_interim_fcf=True)`. Record both `fcfInclusiveResult` and `legacyExFcfPv` so the cash flow bridge is transparent.
2. **No Backward-Looking TTM Cliffs Without Context**: When a company is in rapid inflection, tag `seedBasis` honestly and include `altNtmSeedResult` + the 3×3 `Revenue Growth × Gross Margin` `matrix2d` so users never confuse depressed TTM extrapolation with structural earnings power.
3. **No Compliance-Bot Repetition**: Global disclaimers already live in `src/layouts/Base.astro`. NEVER pad `verdict.oneLiner` or v2 sections with boilerplate (`不是已證實公平價`, `不是買點`, `未指派機率`, `不構成投資建議`).
4. **No Vacuum Valuations**: Every v2 report MUST include:
   - `macroContext` (`us10yYieldPct`, `real10yTipsPct`, `hyOasPct`) and `erpVs10yPct`
   - `reverseValuation` (implied Forward P/E and implied 4Y Revenue CAGR priced in right now)
   - `valuationAnchors` (company's own historical P/E band + ≥ 2 peers)
   - `segmentBridge` (≥ 2 segments with headwind/tailwind arithmetic)
5. **Strict Data-Only Updates**: Never modify `.astro` templates when adding a new ticker analysis. Put v2 analyses in `src/data/buyside-v2.json` and declarative overrides in `src/data/ticker-overrides.json`.
6. **Never Edit `CLAUDE.md` Directly**: `CLAUDE.md` is a git symlink (`120000`) pointing to `AGENTS.md`. Leave `CLAUDE.md` untouched in git status so Windows/Linux checkouts never corrupt its symlink mode.
7. **Privacy & Contract Preservation**: Never leak `/home/`, `password`, `cookie`, `token`, `paidSourceNotes`, or `workingNotes`. Do not mutate archived historical report fields tested by `tests/validate_public.py` and `tests/verify_learning.py`.

## 3. Mandatory Verification Gate Before Commit / PR
```bash
npx astro check
python3 scripts/valuation_math.py --verify-v2 src/data/buyside-v2.json
npm test
```

---

## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)

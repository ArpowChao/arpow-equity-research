#!/usr/bin/env python3
"""Contract & anti-pattern gate for Hermes and human-authored v2 equity research."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import valuation_math as vm

FORBIDDEN_COMPLIANCE_CLICHES = (
    "不是已證實公平價",
    "不是買點",
    "未指派機率",
    "不構成投資建議",
    "保證下限",
)
FORBIDDEN_PRIVACY_TOKENS = (
    "paidsourcenotes",
    "workingnotes",
    "password",
    "cookie",
    "access_token",
    "/home/",
)
ALLOWED_TIERS = {"高勝率賠率", "觀察待催化", "估值透支迴避", "資訊缺口暫緩"}


def main() -> int:
    required_docs = [
        ROOT / "AGENTS.md",
        ROOT / "docs/RESEARCH_PLAYBOOK.md",
        ROOT / ".agents/skills/buy-side-equity-research/SKILL.md",
        ROOT / "schemas/equity-report.v2.schema.json",
        ROOT / "src/data/buyside-v2.json",
        ROOT / "src/data/ticker-overrides.json",
    ]
    for path in required_docs:
        assert path.is_file(), f"Missing required v2 learning/contract file: {path}"

    schema = json.loads((ROOT / "schemas/equity-report.v2.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["version"]["const"] == "2.0"

    v2_path = ROOT / "src/data/buyside-v2.json"
    v2_data = json.loads(v2_path.read_text(encoding="utf-8"))
    raw_lower = json.dumps(v2_data, ensure_ascii=False).lower()
    for secret_tok in FORBIDDEN_PRIVACY_TOKENS:
        assert secret_tok not in raw_lower, f"Forbidden privacy token leaked in buyside-v2.json: {secret_tok}"

    assert v2_data.get("version") == "2.0"
    items = v2_data.get("items", [])
    assert len(items) >= 1

    # 1. Exact mathematical verification via deterministic Python engine
    errors = vm.verify_v2_file(v2_path)
    assert not errors, "Math verification failures:\n" + "\n".join(errors)

    # 2. Structural & anti-pattern enforcement per item
    for item in items:
        tk = item["ticker"]
        verdict = item["verdict"]
        assert verdict["tier"] in ALLOWED_TIERS, f"{tk}: invalid verdict tier {verdict['tier']}"
        assert 15 <= len(verdict["oneLiner"]) <= 180, f"{tk}: oneLiner length out of bounds"
        for cliche in FORBIDDEN_COMPLIANCE_CLICHES:
            assert cliche not in verdict["oneLiner"], f"{tk}: compliance cliché found in oneLiner: {cliche}"
        assert len(verdict["confirmTriggers"]) >= 2, f"{tk}: need >= 2 confirmTriggers"
        assert len(verdict["invalidateTriggers"]) >= 2, f"{tk}: need >= 2 invalidateTriggers"
        assert len(item["segmentBridge"]) >= 2, f"{tk}: need >= 2 segmentBridge items"
        assert len(item["unitEconomics"]) >= 2, f"{tk}: need >= 2 unitEconomics items"
        assert len(item["valuationAnchors"]["peers"]) >= 2, f"{tk}: need >= 2 peer comparisons"
        mat = item["stressV2"]["matrix2d"]
        assert len(mat["growthRates"]) == 3 and len(mat["grossMargins"]) == 3
        assert len(mat["cells"]) == 3 and all(len(r) == 3 for r in mat["cells"])
        assert len(item["sources"]) >= 3

    # 3. Verify built static output renders the v2 components and ZS live-quote hook
    dist_dir = ROOT / "dist"
    assert dist_dir.is_dir(), "dist/ not found; run npm run build first"

    nvda_html = (dist_dir / "research/nvda/index.html").read_text(encoding="utf-8")
    assert 'data-buyside-brief="NVDA"' in nvda_html
    assert "data-stress-matrix" in nvda_html
    assert "101.10" in nvda_html  # FCF-inclusive PV on NVDA

    zs_html = (dist_dir / "research/zs/index.html").read_text(encoding="utf-8")
    assert "data-live-quote" in zs_html
    assert 'data-ticker="ZS"' in zs_html

    index_html = (dist_dir / "index.html").read_text(encoding="utf-8")
    assert "v2 買方｜觀察待催化" in index_html

    playbook_html = (dist_dir / "methodology/buyside-v2-playbook/index.html").read_text(encoding="utf-8")
    assert "FCF_per_share_t" in playbook_html

    print(f"PASS: v2 contract, math parity, anti-pattern guards, and dist UI verified for {len(items)} item(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

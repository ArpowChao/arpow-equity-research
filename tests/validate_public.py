#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "/arpow-equity-research/"
reports = json.loads((ROOT / "src/data/reports.generated.json").read_text(encoding="utf-8"))
assert len(reports) >= 13
expected = {"DIS", "LAES", "QBTS", "INTC", "AMD", "MU", "SNDK", "MP", "GOOGL", "ARM", "FISV", "PLTR", "CBRS"}
assert {r["ticker"] for r in reports} >= expected
serialized = json.dumps(reports, ensure_ascii=False).lower()
for forbidden in ("paidsourcenotes", "workingnotes", "password", "cookie", "token"):
    assert forbidden not in serialized, f"private field leaked: {forbidden}"

pages = list((ROOT / "dist").rglob("*.html"))
assert len(pages) >= 8
for page in pages:
    html = page.read_text(encoding="utf-8")
    for link in re.findall(r'(?:href|src)="(/[^"]*)"', html):
        assert link.startswith(BASE), f"bad Pages path in {page}: {link}"

for ticker in (x.lower() for x in expected):
    html = (ROOT / f"dist/research/{ticker}/index.html").read_text(encoding="utf-8")
    assert "查看公式、理論與限制" in html
    assert "原始來源" in html
    assert "估值試算" in html
    assert "第一次看這家公司，先看這裡" in html
    assert "這家公司最該追蹤的業務引擎" in html
    assert "點開白話名詞表" in html
print(f"validated {len(reports)} reports and {len(pages)} pages")

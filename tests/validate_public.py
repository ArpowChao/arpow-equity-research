#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "/arpow-equity-research/"
reports = json.loads((ROOT / "src/data/reports.generated.json").read_text(encoding="utf-8"))
live_quotes = json.loads((ROOT / "public/data/live-quotes.json").read_text(encoding="utf-8"))
assert len(reports) >= 14
expected = {"DIS", "LAES", "QBTS", "INTC", "AMD", "MU", "SNDK", "MP", "GOOGL", "ARM", "FISV", "PLTR", "CBRS", "NVDA"}
assert {r["ticker"] for r in reports} >= expected
assert set(live_quotes["quotes"]) >= expected
for ticker, quote in live_quotes["quotes"].items():
    assert quote["ticker"] == ticker
    assert quote["price"] > 0
    assert quote["phase"] in {"pre-market", "regular", "post-market", "closed"}
    assert quote["observedAt"].endswith("Z")
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
    assert "最新可得行情" in html
    assert "本篇分析快照" in html
    assert "data-live-quote" in html
index_html = (ROOT / "dist/index.html").read_text(encoding="utf-8")
fundamentals = json.loads((ROOT / "src/data/fundamentals.generated.json").read_text(encoding="utf-8"))
items = fundamentals["items"]
assert len(items) == len(reports)
assert {item["ticker"] for item in items} == {report["ticker"] for report in reports}
assert len({item["ticker"] for item in items}) == len(items)
fundamentals_html = (ROOT / "dist/fundamentals/index.html").read_text(encoding="utf-8")
for item in items:
    assert item["statement"]["url"].startswith("https://www.sec.gov/Archives/")
    assert item["latestFiling"]["url"].startswith("https://www.sec.gov/Archives/")
    assert item["ticker"] in fundamentals_html
    assert (ROOT / f'dist/research/{item["ticker"].lower()}/index.html').is_file()
    assert item["analysisAsOf"] <= fundamentals["checkedAtUtc"][:10]
    for field in item["fields"].values():
        if field:
            assert field["end"] <= item["statement"]["periodEnd"]
            assert field["unit"] in {"USD", "shares"}
            assert field["accession"].replace('-', '') in item["statement"]["url"]
assert "全站基本面核對" in index_html
assert len(re.findall(r'<a[^>]+data-live-card', index_html)) == len(reports)
for marker in ("最新行情", "分析快照", "基準合理價", "data-live-grid", "約每15分鐘更新"):
    assert marker in index_html
print(f"validated {len(reports)} reports and {len(pages)} pages")

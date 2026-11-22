#!/usr/bin/env python3
"""Check all learning routes and matching values in dist, or on production."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
from sys import argv
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
def data(name):
    return json.loads((root / "src/data" / f"{name}.json").read_text())
reports = data("reports.generated")
selection = data("selection-14")
revaluation = data("revaluation-2026-11-22")
paths = ["", "learn/", "fundamentals/", "comparisons/selection-14/", "comparisons/revaluation-2026-11-22/"] + [f"research/{t.lower()}/" for t in [r["ticker"] for r in reports]+["ZS"]]
def fetch(path):
    if len(argv) == 1:
        return (root / "dist" / path / "index.html").read_text()
    with urlopen(argv[1].rstrip("/") + "/" + path + ("?v=" + argv[2] if len(argv) > 2 else ""), timeout=15) as r:
        return r.read().decode()
with ThreadPoolExecutor(max_workers=8) as pool:
    html = dict(zip(paths, pool.map(fetch, paths)))
for p, text in html.items():
    assert "data-analysis-steps" in text, p
    assert "先讀生意，再算股價" in text, p
    assert "營運現金流 − 資本支出" in text, p

def value(v):
    return f"${v:.{3 if v < 1 else 2}f}"

fresh = {r["ticker"]:r for r in revaluation["models"]}
for row in selection["rows"]:
    ticker = row["ticker"]
    lower = ticker.lower()
    article = html[f"research/{lower}/"]
    base = fresh[ticker]["scenarios"][1]["value"] if ticker in fresh else row["cases"][1]["value"]
    block = re.search(rf'<section[^>]*data-active-model="{ticker}".*?</section>', article, re.S)
    assert block and value(base) in block.group(), ticker
    expected = f"comparisons/{'revaluation-2026-11-22' if ticker in fresh else 'selection-14'}/#{lower}"
    assert expected in block.group(), ticker
    if ticker != "ZS":
        card = re.search(rf'<a[^>]*data-ticker="{ticker}".*?</a>', html[""], re.S)
        assert card and value(base) in card.group() and "最新研究" not in card.group(), ticker
        assert f'data-base-work="{ticker}"' in card.group() and "把數字代進去" in card.group(), ticker
        assert "歷史模型｜原分析股價" in article, ticker
    else:
        zs_card = re.search(r'<a[^>]*data-active-model="ZS".*?</a>', html[""], re.S)
        assert zs_card and value(base) in zs_card.group(), ticker
    assert f'id="{lower}"' in html["comparisons/selection-14/"]
    assert value(base) in html[expected.split("#")[0]], ticker

for text in ("符號怎麼讀", "79.19", "56.73%", "105.72", "121.66", "192.70", "53 週", "eps-lab", "不看答案"):
    assert text in html["learn/"], text
print(f"verified {len(paths)} routes, {len(selection['rows'])} model summaries and the Disney lab")

for t in [r["ticker"] for r in reports]+["ZS"]:
    assert f'data-base-work="{t}"' in html[""], t
assert html[""].index('data-ticker="IONQ"') < html[""].index('data-ticker="AMD"')

filings = data("fundamentals.generated")["items"]
for i in filings:
    ticker=i["ticker"]
    assert f'data-filing-evidence="{ticker}"' in html[""]
    assert f'data-filing-evidence="{ticker}"' in html[f"research/{ticker.lower()}/"]
    assert i["statement"]["url"] in html[f"research/{ticker.lower()}/"]
assert "8.962 億美元" in html["research/ionq/"]

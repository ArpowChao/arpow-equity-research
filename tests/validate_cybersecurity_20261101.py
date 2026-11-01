"""Deterministic scope, citation, classification and built-output checks."""
from pathlib import Path
import json
import math
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
r = json.loads((ROOT/'src/data/cybersecurity-2026-11-01.json').read_text())
rows = r['companies']
assert len(rows) == 11
assert len({c['ticker'] for c in rows}) == len(rows)
assert Counter(c['size'] for c in rows) == r['counts'] == {'大型':6,'中型':3,'小型':2}
assert not {'VRNS','CYBR'} & {c['ticker'] for c in rows}
assert {'VRNS','CYBR'} == {c['ticker'] for c in r['corporateActions']}
sources = {s['id']:s for s in r['sources']}
for action in r['corporateActions']:
    assert action['source'] in sources, (action['ticker'], 'source')
for c in rows:
    expected = '大型' if c['marketCapUsdApprox'] >= 1e10 else '中型' if c['marketCapUsdApprox'] >= 2e9 else '小型'
    assert c['size'] == expected
    assert c['priceSnapshotTime'].startswith('2026-10-30')
    assert c['priceSnapshotUsd'] > 0
    assert math.isclose(c['marketCapUsdApprox'] / 1e8, c['marketCapYiUsdApprox'], rel_tol=1e-12), c['ticker']
    assert c['quoteSource'].startswith('https://'), (c['ticker'], 'quoteSource')
    assert '初篩' in c['valuationStatus']
    assert 'fairValue' not in c and 'targetPrice' not in c
    for key in ('financialSource','productSource','marketCapSource'):
        assert c[key] in sources, (c['ticker'],key)
    assert 'scheduleSource' in c, (c['ticker'], 'scheduleSource')
    if c['scheduleSource'] is not None:
        assert c['scheduleSource'] in sources, (c['ticker'], 'scheduleSource')
    if '預定' in c['period']:
        assert c['scheduleSource'] is not None, (c['ticker'], 'scheduleSource')
    for key in ('thesis','risk','watch','growth','quality','period','financialAccess'):
        assert c[key].strip()
assert '年減1.5%' in next(c['growth'] for c in rows if c['ticker']=='RPD')
assert '2026 Q3' in next(c['period'] for c in rows if c['ticker']=='FTNT')
assert '2026 Q3' in next(c['period'] for c in rows if c['ticker']=='TENB')
for source in sources.values():
    assert source['url'].startswith('https://')
    assert source['title']
    assert source['accessed'] == '2026-11-01'
page = ROOT/'dist/sectors/cybersecurity-2026-11-01/index.html'
assert page.exists(), page
html = page.read_text()
assert html.count('data-company') >= 11
for c in rows:
    assert f'id="{c["ticker"].lower()}"' in html
    assert c['company'] in html
for term in ('不是買入清單','49.75','2027上半年','原站全文','尚未完成逐家10-Q'):
    assert term in html, term
assert '/arpow-equity-research/sectors/cybersecurity-2026-11-01/' in (ROOT/'dist/index.html').read_text()
assert '<html lang="zh-Hant"' in html
assert 'ghp_' not in html and 'github_pat_' not in html
print(json.dumps({'passed':True,'companyCount':len(rows),'sizeCounts':r['counts'],'sourceCount':len(sources),'path':str(page)},ensure_ascii=False))

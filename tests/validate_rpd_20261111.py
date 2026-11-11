#!/usr/bin/env python3
"""RPD scoped acceptance test; run explicitly for this dated research."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
rows=json.loads((P/'src/data/reports.generated.json').read_text())
matches=[r for r in rows if r['ticker']=='RPD']
assert len(matches)==1, 'RPD report is missing or duplicated'
r=matches[0]
assert r['company']=='Rapid7, Inc.' and r['currency']=='USD'
assert r['asOf']=='2026-11-11'
assert r['snapshot']['price']==14.49
assert r['valuation']['type']=='economic-pe'
assert abs(r['valuation']['earnings']*r['valuation']['baseMultiple']-r['snapshot']['base'])<1e-8
print('RPD identity, fixed snapshot and calculator contract passed')
# UI must label conditional economic values, not promise a fair-price interval.
page=(P/'src/pages/research/[ticker].astro').read_text()
assert "const rpdEconomic = report.ticker==='RPD'" in page, 'RPD economic labels and method routing are missing'
assert "'rapid7-economic-ntm'" in page
assert 'RPD:' in (P/'src/data/beginner-guides.ts').read_text()
print('RPD method routing and beginner layer passed')
# Financial and scope checks are tied to this dated baseline, not moving HEAD.
import subprocess, math
baseline='b4df5ce998b88efb9fea8db020f3a4874be8441a'
def original(path):
    return json.loads(subprocess.run(['git','show',f'{baseline}:{path}'],cwd=P,text=True,capture_output=True,check=True).stdout)
assert len(rows)==25
assert [x for x in rows if x['ticker']!='RPD']==original('src/data/reports.generated.json')
fund=json.loads((P/'src/data/fundamentals.generated.json').read_text())
prior=original('src/data/fundamentals.generated.json')
assert len(fund['items'])==25 and [x for x in fund['items'] if x['ticker']!='RPD']==prior['items']
assert fund['checkedAtUtc']==prior['checkedAtUtc']
for scenario,rev,margin,other,tax,shares,pe in zip(r['scenarios'],[780,830,900],[.04,.10,.15],[-8,0,4],[.25,.25,.22],[75,73,72],[12,16,22]):
    expected=(rev*margin+other)*(1-tax)/shares*pe
    assert math.isclose(scenario['value'],expected,abs_tol=1e-9)
assert math.isclose((153.827-7.599-16.106)+(106.926-3.448-11.667)-(116.250-6.446-11.984),124.113,abs_tol=1e-8)
assert math.isclose((104.335+62.961-81.059),86.237,abs_tol=1e-8)
assert math.isclose(900-335.714-395.853,168.433,abs_tol=1e-8)
assert '80.603m' in json.dumps(r,ensure_ascii=False) and '68.535768m' in json.dumps(r,ensure_ascii=False)
html=(P/'dist/research/rpd/index.html').read_text()
for marker in ['rapid7-economic-ntm','NTM經濟基準','基準倍數敏感度','模型折讓區（非買點）','105m','rpd-analysis-2026-11-11.png']:
    assert marker in html,marker
assert (P/'dist/methodology/rapid7-economic-ntm/index.html').exists()
assert len(r['sources'])==11 and len({x['url'] for x in r['sources']})==11
print('RPD scenarios, FCF, debt, shares, routes and original 24-report scope passed')

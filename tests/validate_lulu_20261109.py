#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,math
P=Path(__file__).resolve().parents[1]
reports=json.loads((P/'src/data/reports.generated.json').read_text());assert len(reports)==24
r=next(x for x in reports if x['ticker']=='LULU');assert r['asOf']=='2026-11-09' and r['snapshot']['price']==110.79
assert r['priceMeta']['observedAtUtc']=='2026-11-06T21:00:01+00:00'
assert r['priceMeta']['marketState']=='closed' and '11-06' in r['priceMeta']['asOf']
expected=[((9400*.09+10)*.69)/112*10,((10300*.13+20)*.70)/110*14,((11200*.16+25)*.71)/108*18]
for key,value in zip(['bear','base','bull'],expected):assert math.isclose(r['snapshot'][key],value,abs_tol=1e-9)
assert math.isclose(r['valuation']['earnings']*r['valuation']['baseMultiple'],r['snapshot']['base'],abs_tol=1e-9)
assert r['snapshot']['fairRange']==[103.78,138.37] and r['snapshot']['marginOfSafety']==[90.81,102.91]
assert len(r['sources'])==16 and len(r['analysis'])>=15 and len(r['metrics'])==8
body=' '.join(x['body'] for x in r['analysis']);assert all(s in body for s in ['exchangeable','special voting','54.9495','1354.336','49.7','50.275','未聽完整官方音訊','不是FY2027全年'])
base='0b9262128f5ea9bb9c1d0e4896de4d434ce74026'
old=json.loads(subprocess.check_output(['git','show',base+':src/data/reports.generated.json'],cwd=P));assert {x['ticker']:x for x in reports if x['ticker']!='LULU'}=={x['ticker']:x for x in old if x['ticker']!='LULU'}
f=json.loads((P/'src/data/fundamentals.generated.json').read_text());oldf=json.loads(subprocess.check_output(['git','show',base+':src/data/fundamentals.generated.json'],cwd=P));assert f['checkedAtUtc']==oldf['checkedAtUtc'];assert [x for x in f['items'] if x['ticker']!='LULU']==[x for x in oldf['items'] if x['ticker']!='LULU']
i=next(x for x in f['items'] if x['ticker']=='LULU');assert i['fields']['shares']['concept']=='WeightedAverageNumberOfDilutedSharesOutstanding' and i['fields']['shares']['value']==112919000
assert i['fields']['operatingCashFlow']['start']=='2026-02-02';assert i['statement']['periodEnd']=='2026-08-02';assert i['checkedAtUtc'].startswith('2026-11-09')
page=(P/'dist/research/lulu/index.html').read_text();assert all(s in page for s in ['lululemon-normalized-ntm','查看本篇Q2原始來源','模型折讓區（非買點）','基準倍數敏感度','含SBC的NTM經濟EPS','第一次看這家公司','分析者核心','54.95%'])
assert '查看本篇Q3原始來源' not in page
assert (P/'dist/methodology/lululemon-normalized-ntm/index.html').is_file();assert (P/'dist/charts/lulu-analysis-2026-11-09.png').is_file()
assert 'LULU' in (P/'dist/fundamentals/index.html').read_text()
quotes=json.loads((P/'public/data/live-quotes.json').read_text());assert len(quotes['quotes'])==24 and 'LULU' in quotes['quotes']
assert "throw new Error('stale quote')" in (P/'src/pages/research/[ticker].astro').read_text()
print('LULU contract passed: 24 reports; other 23 unchanged; 16 sources; normalisation, shares, quote timestamp, model, Q2 labels, route and chart verified.')

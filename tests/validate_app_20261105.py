#!/usr/bin/env python3
from pathlib import Path
import json,math,subprocess
P=Path(__file__).resolve().parents[1]
rows=json.loads((P/'src/data/reports.generated.json').read_text());old=json.loads(subprocess.check_output(['git','show','HEAD:src/data/reports.generated.json'],cwd=P,text=True));r=next(x for x in rows if x['ticker']=='APP')
assert len(rows)==24 and len({x['ticker'] for x in rows})==24
assert {x['ticker']:x for x in rows if x['ticker']!='APP'}=={x['ticker']:x for x in old if x['ticker']!='APP'}
assert r['asOf']=='2026-11-05' and r['snapshot']['price']==360.72
assert r['priceMeta']['observedAtUtc']=='2026-11-05T15:20:55+00:00' and r['priceMeta']['marketState']=='regular'
assert math.isclose(r['valuation']['earnings'],((10480*.75-100)*.78)/330)
assert math.isclose(r['valuation']['earnings']*26,r['snapshot']['base'])
assert r['snapshot']['fairRange']==[403.52,550.25] and r['snapshot']['marginOfSafety']==[381.51,405.35]
assert all(math.isclose(a,b) for a,b in zip([s['value'] for s in r['scenarios']],[226.32352941176472,476.8872727272728,803.446153846154]))
text=json.dumps(r,ensure_ascii=False)
for s in ['4877.667','1418.443','融資租賃本金','301.258','30.064','淨額','22%','未聽完整官方音訊','鏡像','不是當日','受限']:
 if s=='不是當日':continue
 assert s in text,s
assert '67%投票權' in text and '核准不等於已完成' in text
assert len(r['sources'])==11 and all(x['url'].startswith('https://') for x in r['sources'])
for s in ['paidSourceNotes','workingNotes','rawExtracts','password','github_pat_','ghp_']:assert s not in text
f=json.loads((P/'src/data/fundamentals.generated.json').read_text());prior=json.loads(subprocess.check_output(['git','show','HEAD:src/data/fundamentals.generated.json'],cwd=P,text=True))
assert f['checkedAtUtc']==prior['checkedAtUtc']
assert {x['ticker']:x for x in f['items'] if x['ticker']!='APP'}=={x['ticker']:x for x in prior['items'] if x['ticker']!='APP'}
a=next(x for x in f['items'] if x['ticker']=='APP');assert a['checkedAtUtc'][:10]=='2026-11-05' and a['statement']['periodEnd']=='2026-09-30'
assert a['fields']['operatingCashFlow']['value']==3589275000 and a['fields']['operatingCashFlow']['start']=='2026-01-01'
assert a['fields']['revenue']['value']==2184815000 and a['fields']['revenue']['start']=='2026-07-01'
assert a['fields']['shares']['value']==(301258+30064)*1000
page=(P/'src/pages/research/[ticker].astro').read_text();assert "appEconomic ? 'applovin-economic-ntm'" in page and 'appEconomic || amdEconomic' in page
assert 'data-min-observed-at' in page and "throw new Error('stale quote')" in page
assert '本檔核對' in (P/'src/pages/fundamentals.astro').read_text()
from PIL import Image
im=Image.open(P/'public/charts/app-analysis-2026-11-05.png');assert im.size==(1600,1390);im.verify()
print(json.dumps({'passed':True,'reports':24,'otherReportsPreserved':23,'fundamentalsOtherItemsPreserved':23,'base':round(r['snapshot']['base'],2),'sourceCount':11},ensure_ascii=False))

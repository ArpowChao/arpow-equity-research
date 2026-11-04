#!/usr/bin/env python3
"""AMD contract, scope and economics tests. Inputs are not recommendations."""
from pathlib import Path
import json,math,subprocess
P=Path(__file__).resolve().parents[1];rows=json.loads((P/'src/data/reports.generated.json').read_text());r=next(x for x in rows if x['ticker']=='AMD')
assert len(rows)==23 and len({x['ticker'] for x in rows})==23
prior=json.loads(subprocess.check_output(['git','show','HEAD:src/data/reports.generated.json'],cwd=P,text=True))
assert {x['ticker']:x for x in prior if x['ticker']!='AMD'}=={x['ticker']:x for x in rows if x['ticker']!='AMD'}
assert r['asOf']=='2026-11-04' and r['priceMeta']['marketState']=='post-market'
assert r['priceMeta']['observedAtUtc']=='2026-11-04T00:59:58+00:00'
assert r['snapshot']['price']==508.2 and math.isclose(r['snapshot']['baseFairValue'],459.34)
assert r['valuation']['type']=='economic-pe' and r['valuation']['baseMultiple']==36
assert math.isclose(r['valuation']['earnings'],((82000*.56-19000+100)*.85)/1800)
assert math.isclose(r['valuation']['earnings']*36,r['snapshot']['base'])
assert r['snapshot']['fairRange']==[408.3,510.38] and r['snapshot']['marginOfSafety']==[367.47,390.44]
assert all(math.isclose(a,b) for a,b in zip([s['value'] for s in r['scenarios']],[253.61325581395346,459.34,707.0109375]))
text=json.dumps(r,ensure_ascii=False)
for s in ['5.54億','10.97億','86.97億','16.68億','未聽完整官方音訊','最新完整已取得10-Q仍是Q2','已扣權證對價的淨營收','全部SBC於費用中保留','並非2027全年','502.60']:
 assert s in text,s
for s in ['rawExtracts','paidSourceNotes','workingNotes','password','github_pat_','ghp_']:assert s not in text
assert len(r['sources'])==9 and all(x['url'].startswith('https://') for x in r['sources'])
page=(P/'src/pages/research/[ticker].astro').read_text();home=(P/'src/pages/index.astro').read_text();methods=(P/'src/data/methods.ts').read_text();guide=(P/'src/data/beginner-guides.ts').read_text()
for s in ['amd-economic-ntm','NTM經濟基準','模型折讓區（非買點）','含SBC的NTM經濟EPS','conditionalModel','data-min-observed-at',"throw new Error('stale quote')"]:
 assert s in page,s
assert '11/03盤後19:59 EST' in home and 'NTM經濟基準' in home
assert "slug:'amd-economic-ntm'" in methods and '1668＋25＋107＝1800' in methods
assert '客戶權證:' in guide and '存貨／應收與現金流' in guide
from PIL import Image
im=Image.open(P/'public/charts/amd-analysis-2026-11-04.png');assert im.size==(1600,1390);im.verify()
print(json.dumps({'passed':True,'reports':len(rows),'unchangedOtherReports':22,'sourceCount':len(r['sources']),'baseline':round(r['snapshot']['base'],2)},ensure_ascii=False))

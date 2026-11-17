#!/usr/bin/env python3
from pathlib import Path
from decimal import Decimal as D
import json,math,subprocess
P=Path(__file__).resolve().parents[1]
r=json.loads((P/'src/data/reports.generated.json').read_text());f=json.loads((P/'src/data/fundamentals.generated.json').read_text());b=json.loads(subprocess.check_output(['git','show','03de338ce65c893e0e9e7808714c9cb717367f02:src/data/reports.generated.json'],cwd=P,text=True));bf=json.loads(subprocess.check_output(['git','show','03de338ce65c893e0e9e7808714c9cb717367f02:src/data/fundamentals.generated.json'],cwd=P,text=True))
assert len(r)==len({x['ticker'] for x in r})==26
assert [x for x in r if x['ticker']!='NVDA']==[x for x in b if x['ticker']!='NVDA']
assert [x for x in f['items'] if x['ticker']!='NVDA']==[x for x in bf['items'] if x['ticker']!='NVDA'] and f['checkedAtUtc']==bf['checkedAtUtc']
n=next(x for x in r if x['ticker']=='NVDA');assert n['asOf']=='2026-11-18' and n['snapshot']['price']==155.46 and n['priceMeta']['observedAtUtc']=='2026-11-17T21:00:00+00:00'
raw=json.loads((P/'src/data/nvda-2026-11-18.json').read_text())['results'][0];c=raw['calculations']
for s in c['scenarios']:
 eps=(D(str(s['revenueM']))*D(str(s['grossMargin']))-D(str(s['opexM']))+D(str(s['netOtherM'])))*(1-D(str(s['taxRate'])))/D(str(s['sharesM']))
 assert abs(float(eps)-s['eps'])<1e-10 and abs(float(eps*D(str(s['pe'])))-s['value'])<1e-9
for key in ['tailored','common10','zeroGrowth','uniform10x','uniform15x']:
 z=c[key];i=z['inputs'];rev=D(str(i['seedRevenueM']));shares=D(str(i['initialSharesM']));ni=D(0);assert len(z['years'])==4
 for y in z['years']:
  rev*=1+D(str(i['annualRevenueGrowth']));shares*=1+D(str(i['annualDilution']));ni=(rev*(D(str(i['grossMargin']))-D(str(i['opexRatio'])))+D(str(i['netOtherM'])))*(1-D(str(i['taxRate'])))
  assert math.isclose(float(rev),y['revenueM'],rel_tol=1e-12) and math.isclose(float(ni),y['netIncomeM'],rel_tol=1e-12) and math.isclose(float(ni/shares),y['eps'],rel_tol=1e-12)
 terminal=ni/shares*D(str(i['terminalPe']));pv=terminal/(1+D(str(i['discountRate'])))**4
 assert abs(float(terminal)-z['terminalValue'])<1e-8 and abs(float(pv)-z['presentValue'])<1e-8
 assert abs((z['terminalValue']/155.46)**.25-1-z['annualReturn'])<1e-12
assert abs(n['valuation']['earnings']*n['valuation']['baseMultiple']-n['snapshot']['baseFairValue'])<1e-10
methods=(P/'src/data/methods.batch.generated.ts').read_text();assert all(x in methods for x in ['mu-dual-track-20261114','nvda-dual-track-20261114','nvda-dual-track-20261118','amzn-dual-track-20261114'])
assert (P/'public/charts/nvda-analysis-2026-11-18.png').exists()
assert not any(s in json.dumps(raw).lower() for s in ['/home/','password','cookie','access_token','paidSourceNotes'.lower()])
print('PASS: 26 reports, other 25 unchanged, global date unchanged, Decimal scenario/stress recalculation, old/new method routes, source/privacy contract.')

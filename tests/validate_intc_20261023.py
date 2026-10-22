#!/usr/bin/env python3
"""INTC research snapshot regression checks; no fabricated remote fixtures."""
from pathlib import Path
import json,subprocess,math,re
R=Path(__file__).resolve().parents[1]
reports=json.loads((R/'src/data/reports.generated.json').read_text())
old=json.loads(subprocess.check_output(['git','show','origin/main:src/data/reports.generated.json'],cwd=R))
old_by={x['ticker']:x for x in old};new_by={x['ticker']:x for x in reports}
assert old_by.keys()==new_by.keys()
assert all(old_by[k]==new_by[k] for k in old_by if k!='INTC'),'Unrelated research changed'
r=new_by['INTC'];v=r['valuation'];s=r['snapshot']
assert r['asOf']=='2026-10-23' and '2026-10-22' in r['priceMeta']['asOf']
assert s['price']==85.49
assert abs((v['forwardRevenue']*v['baseMultiple']+v['netCash'])/v['dilutedShares']-s['baseFairValue'])<.01
for scenario,nums in zip(r['scenarios'],[(60000,2,-35000,5900),(70000,3.5,-25000,5700),(85000,6,-15000,5600)]):
 rev,m,c,sh=nums
 assert abs((rev*m+c)/sh-scenario['value'])<.01
assert s['bear']<s['base']<s['bull']
assert s['marginOfSafety']==[round(s['base']*.70,2),round(s['base']*.75,2)]
assert all(x['url'].startswith('https://') for x in r['sources'])
text=json.dumps(r,ensure_ascii=False)
assert all(k not in text.lower() for k in ['password','cookie','token','workingnotes','rawextracts'])
assert len(r['sources'])>=8
page=(R/'dist/research/intc/index.html').read_text()
for marker in ['2026-10-23','85.49','38.60','14.41','88.39','10/29','2.93億','20.89億','intel-turnaround','226.2億','142億']:
 assert marker in page,marker
assert (R/'dist/charts/intc-analysis-2026-10-23.svg').is_file()
assert (R/'dist/methodology/intel-turnaround/index.html').is_file()
print('PASS: one ticker changed; source/privacy schema, three scenario formulas, dated market snapshot, dilution, cash-flow bridge, chart and method routes verified.')

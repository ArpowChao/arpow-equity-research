from pathlib import Path
import json, math, hashlib
P=Path(__file__).resolve().parents[1]
T={'MU','FISV','AMD','NVDA','MSFT','AMZN'}
rows=json.loads((P/'src/data/reports.generated.json').read_text())
assert len(rows)==26 and len({r['ticker'] for r in rows})==26
assert {r['ticker'] for r in rows if r['asOf']=='2026-11-14'}==T
for r in rows:
 if r['ticker'] not in T:continue
 assert r['priceMeta']['observedAtUtc'].startswith('2026-11-13T21:00:')
 assert r['snapshot']['price']>0 and r['currency']=='USD'
 assert math.isclose(r['valuation']['earnings']*r['valuation']['baseMultiple'],r['snapshot']['base'],abs_tol=1e-8)
 assert len(r['scenarios'])==3 and len(r['beginner']['watch'])>=3 and len(r['sources'])>=4
 dt=r['dualTrack']
 for k in ['tailored','common10','zeroGrowth']:
  z=dt[k];i=z['inputs'];assert len(z['years'])==4
  for n,y in enumerate(z['years'],1):
   assert math.isclose(y['revenueM'],i['seedRevenueM']*(1+i['annualRevenueGrowth'])**n,abs_tol=1e-6)
   assert math.isclose(y['netIncomeM'],(y['revenueM']*(i['grossMargin']-i['opexRatio'])+i['netOtherM'])*(1-i['taxRate']),abs_tol=1e-6)
  assert math.isclose(z['presentValue'],z['terminalValue']/(1+i['discountRate'])**4,abs_tol=1e-8)
 assert dt['common10']['inputs']['annualRevenueGrowth']==.10
 assert dt['zeroGrowth']['inputs']['annualRevenueGrowth']==0
 assert (P/f"public/charts/{r['ticker'].lower()}-analysis-2026-11-14.png").exists()
 html=(P/f"dist/research/{r['ticker'].lower()}/index.html").read_text()
 for marker in ['退化成價值股','末期價值','折現現值','data-stress-calculator',dt['method'],'模型折讓區（非買點）']:
  assert marker in html,(r['ticker'],marker)
 assert (P/f"dist/methodology/{dt['method']}/index.html").exists()
assert (P/'dist/comparisons/six-2026-11-14/index.html').exists()
print('Six companies: common close, operational bridge, 3 normal scenarios, 3 stress sensitivities, PV, dilution, routes, charts passed')

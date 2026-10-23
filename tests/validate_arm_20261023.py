from pathlib import Path
import json,subprocess,math,re
ROOT=Path(__file__).resolve().parents[1]
reports=json.loads((ROOT/'src/data/reports.generated.json').read_text())
a=next(r for r in reports if r['ticker']=='ARM')
assert a['asOf']=='2026-10-23'
assert a['snapshot']['price']==212.03
assert '11:49:46 EDT' in a['priceMeta']['asOf'] and '盤中' in a['priceMeta']['asOf']
assert a['snapshot']['bear']==31.59 and a['snapshot']['base']==111.43 and a['snapshot']['bull']==233.01
assert a['snapshot']['marginOfSafety']==[78.0,83.57]
assert abs(a['valuation']['earnings']*a['valuation']['baseMultiple']-111.43)<.02
for s in a['scenarios']:assert s['value']>0 and s['condition'] and 'EPS' in s['assumption']
text=json.dumps(a,ensure_ascii=False)
for word in ['停止披露','11/4','97%','SBC','1.28億','6.65億','13.97億','10.68億','1.5918','403','完整場Q&A']:
 assert word in text,word
assert len([r for r in reports if r['ticker']=='ARM'])==1
prior=json.loads(subprocess.check_output(['git','show','HEAD:src/data/reports.generated.json'],cwd=ROOT))
assert {r['ticker']:r for r in reports if r['ticker']!='ARM'}=={r['ticker']:r for r in prior if r['ticker']!='ARM'},'unrelated reports changed'
assert all(k not in text for k in ['workingNotes','rawExtracts','password','token','/home/arpow'])
html=(ROOT/'dist/research/arm/index.html').read_text()
assert 'arm-economic-earnings' in html and '111.43' in html and '$78–$83.57' in html
chart=ROOT/'public'/a['chart'].lstrip('/')
assert chart.exists() and '含當日未收盤' in chart.read_text()
method=(ROOT/'dist/methodology/arm-economic-earnings/index.html').read_text()
assert '6500' in method and '1100' in method and '111.43' in method
print('ARM regression: finance bridge, snapshot, 3 scenarios, calculator, source limitations, private whitelist, unrelated reports, chart and method passed')

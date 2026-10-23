from pathlib import Path
import json,subprocess,hashlib
R=Path(__file__).resolve().parents[1]
reports=json.loads((R/'src/data/reports.generated.json').read_text());by={r['ticker']:r for r in reports}
old=json.loads(subprocess.check_output(['git','show','HEAD:src/data/reports.generated.json'],cwd=R))
assert {r['ticker']:r for r in reports if r['ticker'] not in ['NVDA','MU']}=={r['ticker']:r for r in old if r['ticker'] not in ['NVDA','MU']},'unrelated reports changed'
for t,values,method in [('NVDA',[160,325,492.15],'nvidia-economic-ntm'),('MU',[516.39,1239.72,2360.83],'memory-dual-horizon')]:
 a=by[t];assert a['asOf']=='2026-10-24';assert '2026-10-23 12:21:' in a['priceMeta']['asOf'];assert '盤中' in a['priceMeta']['asOf']
 assert [a['snapshot'][k] for k in ['bear','base','bull']]==values
 assert abs(a['valuation']['earnings']*a['valuation']['baseMultiple']-a['snapshot']['baseFairValue'])<.01
 assert len([r for r in reports if r['ticker']==t])==1
 s=json.dumps(a,ensure_ascii=False)
 for key in ['workingNotes','rawExtracts','password','token','/home/arpow']:assert key not in s
 for word in (['SBC','25倍','未來12個月','53','DSO','Hugging Face'] if t=='NVDA' else ['SCA','103.3104','152.10','耐久','589.63','623.08','361.97','317.93','存款']):assert word in s,(t,word)
 h=(R/f'dist/research/{t.lower()}/index.html').read_text();assert method in h
 assert (R/f'dist/methodology/{method}/index.html').exists()
 p=R/'public'/a['chart'].lstrip('/');assert p.exists() and '含當日未收盤' in p.read_text()
assert by['NVDA']['valuation']['earnings']==13 and by['MU']['valuation']['earnings']==103.3104
print('NVDA/MU regression passed: prices/time, 6 scenarios, calculator parity, dual horizon, SBC and FCF bridges, private whitelist, untouched other reports, methods and charts')

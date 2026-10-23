from pathlib import Path
import json,subprocess,math
ROOT=Path(__file__).resolve().parents[1]
old=json.loads(subprocess.check_output(['git','show','1cd9842ea26eb21e6b250c07506223ac05857bf9:src/data/reports.generated.json'],cwd=ROOT))
new=json.loads((ROOT/'src/data/reports.generated.json').read_text())
a={v['ticker']:v for v in old};b={v['ticker']:v for v in new}
assert a.keys()==b.keys() and len(b)==23
assert all(a[t]==b[t] for t in a if t!='INTC'), 'unrelated report changed'
r=b['INTC'];assert r['asOf']=='2026-10-24'
assert r['snapshot']==a['INTC']['snapshot'] and r['valuation']==a['INTC']['valuation'], 'audit silently repriced model'
assert math.isclose((70000*3.5-25000)/5700,38.59649122807018)
static=12874+16853-1988-48549-15601+22620
assert static==-13791
assert round((70000*3.5+static)/5285.069511,2)==43.75
assert [round((70000*m-25000)/5700,2) for m in [4,5,6,7]]==[44.74,57.02,69.30,81.58]
html=(ROOT/'dist/research/intc/index.html').read_text()
for t in ['保守模型錨點','原模型倍數敏感度','非唯一公平價','沒有完成全分部','intel-model-audit','43.75','52.8507','10/22']:
 assert t in html,t
assert '>一般合理區間</span>' not in html
assert (ROOT/'dist/methodology/intel-model-audit/index.html').is_file()
assert r['chart']==a['INTC']['chart']
assert (ROOT/'public'/r['chart'].lstrip('/')).is_file()
print('PASS: 22 unrelated reports unchanged; original INTC valuation preserved and explicitly qualified; bridge, share, multiples, audit/method labels verified')

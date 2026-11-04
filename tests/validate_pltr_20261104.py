"""Dated PLTR model, source/label contracts, and unchanged-ticker regressions."""
from pathlib import Path
import json,subprocess,math
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'src/data/reports.generated.json').read_text());p=next(x for x in rows if x['ticker']=='PLTR')
old=json.loads(subprocess.check_output(['git','show','origin/main:src/data/reports.generated.json'],cwd=R,text=True))
assert {x['ticker']:x for x in old if x['ticker']!='PLTR'}=={x['ticker']:x for x in rows if x['ticker']!='PLTR'}
assert len(rows)==len({x['ticker'] for x in rows})==23
assert p['asOf']=='2026-11-04' and p['snapshot']['price']==175.4
assert p['priceMeta']['marketState']=='regular-close' and p['priceMeta']['observedAtUtc']=='2026-11-03T21:00:00Z'
v=p['valuation'];assert v['type']=='ev-sales-diluted'
assert math.isclose((v['forwardRevenue']*v['baseMultiple']+v['netCash'])/v['dilutedShares'],p['snapshot']['baseFairValue'],abs_tol=1e-9)
assert [round(x['value'],2) for x in p['scenarios']]==[74.99,137.57,211.27]
assert p['snapshot']['fairRange']==[111.11,164.04] and p['snapshot']['marginOfSafety']==[110.06,116.94]
assert len(p['sources'])==7 and all(x['url'].startswith('https://') for x in p['sources'])
assert any('000132165526000048' in x['url'] for x in p['sources'])
assert any('0.341' in x['body'] and '1.18%' in x['body'] for x in p['analysis'])
assert any('上市股權1.85383' in x['body'] for x in p['analysis'])
assert any('TCV29.18億年增6%' in x['body'] and '44%預計未來十二個月內認列' in x['body'] for x in p['analysis'])
assert '十二月內認列' not in json.dumps(p,ensure_ascii=False)
assert any('10/26實際A+B+F約24.095億股' in x['note'] for x in p['metrics'])
assert any('10/26 A+B+F實際股數24.09497474億' in x['body'] for x in p['analysis'])
methods=(R/'src/data/methods.ts').read_text()
assert '原始期限十二個月或以下的合約可不揭露' in methods
html=(R/'dist/research/pltr/index.html').read_text()
for s in ['條件式基準','基準倍數敏感度','模型折讓區（非買點）','試算條件式價值','2026-11-03 16:00 EST','palantir-growth-valuation','filing-sources','未播放完整官方音訊','49億']:
 assert s in html,s
assert '一般合理區間' not in html
assert html.index('第一次看這家公司')<html.index('關鍵營運證據')
assert 'data-min-observed-at="2026-11-03T21:00:00Z"' in html
assert (R/'dist/methodology/palantir-growth-valuation/index.html').is_file()
assert (R/'dist/charts/pltr-analysis-2026-11-04.png').read_bytes().startswith(b'\x89PNG')
print(json.dumps({'passed':True,'reports':23,'unchangedOtherReports':22,'sources':7,'baseReproduced':round(p['snapshot']['baseFairValue'],2)}))

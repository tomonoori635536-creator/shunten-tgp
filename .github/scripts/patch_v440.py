from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

repls=[
("クリーン版 v4.39：騎手クラス別＋直前騎乗→次騎乗パターンを追加",
 "クリーン版 v4.40：馬能力は今回貼付の馬柱だけで評価"),
("function horseAbility(row,meta){\n  const all=horseHistoryBefore(row?.name,meta?.date).filter(r=>Number.isFinite(Number(r.rank)));",
 "function horseAbility(row,meta,sourceRuns=null){\n  const target=dateNumber(meta?.date);\n  const base=Array.isArray(sourceRuns)\n    ? sourceRuns.filter(r=>{\n        if(String(r.name||'')!==String(row?.name||''))return false;\n        if(!target)return true;\n        const d=dateNumber(r.date);\n        return d&&d<target;\n      })\n    : horseHistoryBefore(row?.name,meta?.date);\n  const all=base.filter(r=>Number.isFinite(Number(r.rank)));"),
("<th>馬履歴</th>","<th>今回馬柱</th>"),
("const hs=horseAbility(r,m);","const hs=horseAbility(r,m,p.pastRuns);"),
("const horseRuns=horseHistoryBefore(r.name,m.date).length;",
 "const horseRuns=(Array.isArray(p.pastRuns)?p.pastRuns:[]).filter(x=>String(x.name||'')===String(r.name||'')&&Number.isFinite(Number(x.rank))).length;")
]

for old,new in repls:
    n=s.count(old)
    assert n==1, f'anchor count {n}: {old[:80]}'
    s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

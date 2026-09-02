from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""  const seen=new Set();
  return out.filter(r=>{const k=horseHistoryKey(r);if(!k||seen.has(k))return false;seen.add(k);return true});
}
function scoreRows(rows){"""
new="""  // The copied netkeiba page can contain hidden 9-run text even when the 5-run tab is shown.
  // Canonicalize per horse, remove duplicate race dates, then keep only the latest 5 runs.
  const byHorse=new Map();
  for(const r of out){
    const horse=String(r.name||'').trim();
    if(!horse)continue;
    if(!byHorse.has(horse))byHorse.set(horse,[]);
    byHorse.get(horse).push(r);
  }
  const fixed=[];
  for(const [horse,rows] of byHorse){
    const seen=new Set();
    const clean=rows
      .sort((a,b)=>dateNumber(b.date)-dateNumber(a.date))
      .filter(r=>{
        const k=[r.date||'',r.venue||'',r.name||''].join('|');
        if(!r.date||seen.has(k))return false;
        seen.add(k);return true;
      })
      .slice(0,5);
    fixed.push(...clean);
  }
  return fixed;
}
function scoreRows(rows){"""
assert old in s, 'extract return anchor not found'
s=s.replace(old,new,1)
s=s.replace('クリーン版 v4.42：馬柱の馬別区切り＋外/内コース読取を修正','クリーン版 v4.43：5走版は馬ごとに最新5走へ固定',1)
s=s.replace('✓ クリーン版 v4.42 起動。馬柱の馬別区切りと外/内コース読取を修正しました。','✓ クリーン版 v4.43 起動。5走版は馬ごとに重複除去し最新5走へ固定しました。',1)
assert '.slice(0,5)' in s
assert 'クリーン版 v4.43' in s
p.write_text(s,encoding='utf-8')

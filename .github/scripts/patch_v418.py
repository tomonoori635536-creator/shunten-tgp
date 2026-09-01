from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('クリーン版 v4.17：騎手の並びパターン学習を追加','クリーン版 v4.18：安全復元した過去並びも学習',1)

old='''function completeRacesBefore(targetDate){\n  const target=dateNumber(targetDate);\n  return (state.races||[]).filter(r=>{\n    const d=dateNumber(r.meta?.date);\n    return !target||(!d?false:d<target);\n  });\n}\n'''
new=r'''function isGenericRecoveredClass(name){
  const s=String(name||'').trim();
  return /^(?:\d歳未勝利|\d歳新馬|\d歳以上\d勝クラス|\d歳以上未勝利|\d歳以上オープン|\d歳以上障害.*)$/.test(s);
}
function recoveredLineupRaces(){
  const groups=new Map();
  for(const r of (state.seedHistory||[])){
    if(!r?.date||!r?.venue||!r?.className||!r?.surface||!Number.isFinite(Number(r.distance))||!r?.going||!Number.isFinite(Number(r.fieldSize)))continue;
    const key=[r.date,r.venue,r.className,r.surface,Number(r.distance),r.going,Number(r.fieldSize)].join('|');
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(r);
  }
  const out=[];
  for(const rows of groups.values()){
    if(rows.length<3)continue;
    const first=rows[0];
    if(isGenericRecoveredClass(first.className))continue;
    if(new Set(rows.map(r=>Number(r.num))).size!==rows.length)continue;
    if(new Set(rows.map(r=>Number(r.rank))).size!==rows.length)continue;
    if(new Set(rows.map(r=>String(r.jockey||''))).size!==rows.length)continue;
    const field=Number(first.fieldSize);
    if(rows.length>field)continue;
    out.push({
      recovered:true,
      meta:{date:first.date,venue:first.venue,raceName:first.className,surface:first.surface,distance:Number(first.distance),going:first.going,fieldSize:field},
      rows:rows.map(r=>({...r}))
    });
  }
  return out;
}
function completeRacesBefore(targetDate){
  const target=dateNumber(targetDate);
  const live=(state.races||[]).filter(r=>{
    const d=dateNumber(r.meta?.date);
    return !target||(!d?false:d<target);
  });
  const recovered=recoveredLineupRaces().filter(r=>{
    const d=dateNumber(r.meta?.date);
    return !target||(!d?false:d<target);
  });
  return [...live,...recovered];
}
'''
assert old in s, 'completeRacesBefore target missing'
s=s.replace(old,new,1)
old_text='並び補正は、完全保存された過去レースだけを使い「内・中・外」と同乗騎手に対する内側/外側の先着傾向を学習します。補正は最大±8点で、データが少ない間は主スコアを動かしすぎません。'
new_text='並び補正は、完全保存された結果に加え、過去馬柱から安全に同一レースと復元できた組だけを使い「内・中・外」と同乗騎手に対する内側/外側の先着傾向を学習します。曖昧な組は除外し、補正は最大±8点です。'
assert old_text in s, 'preview note target missing'
s=s.replace(old_text,new_text,1)
p.write_text(s,encoding='utf-8')

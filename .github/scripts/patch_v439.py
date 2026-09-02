from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

rep('<p>クリーン版 v4.38：Q→Bで救った勝ち馬診断を追加</p>',
    '<p>クリーン版 v4.39：騎手クラス別＋直前騎乗→次騎乗パターンを追加</p>',
    'header')

rep("goings:{},popRides:0", "goings:{},classes:{},popRides:0", 'jockey class storage')
rep("bucketAdd(x.goings,r.going||'不明',rank);const pop=Number(r.pop);",
    "bucketAdd(x.goings,r.going||'不明',rank);const cls=horseClassKey(r);if(cls)bucketAdd(x.classes,cls,rank);const pop=Number(r.pop);",
    'jockey class accumulation')

helpers=r'''
function jockeyClassPattern(row,meta){
  const cls=horseClassKey(meta);
  if(!row?.jockey||!cls)return {label:'クラス不明',n:0,wins:0,places:0,note:'クラス判定なし'};
  const rows=jockeyHistoryBefore(row.jockey,meta?.date).filter(r=>horseClassKey(r)===cls);
  const n=rows.length,wins=rows.filter(r=>Number(r.rank)===1).length,places=rows.filter(r=>Number(r.rank)<=3).length;
  let label=n===0?'未学習':n<3?'サンプル少':n<6?'参考':'蓄積あり';
  return {label,n,wins,places,note:`${cls} 過去${n}鞍 / 1着${wins}（${pct(wins,n)}） / 3着内${places}（${pct(places,n)}）`};
}
function emptyNextRideBucket(label){return {label,n:0,next1:0,next2:0,next3:0,next4plus:0,rankSum:0,gapSum:0}}
function addNextRideBucket(x,rank,gap){
  x.n++;x.rankSum+=rank;x.gapSum+=gap;
  if(rank===1)x.next1++;else if(rank===2)x.next2++;else if(rank===3)x.next3++;else x.next4plus++;
}
function mergeNextRideBuckets(a,b,label){
  const x=emptyNextRideBucket(label);
  for(const k of ['n','next1','next2','next3','next4plus','rankSum','gapSum'])x[k]=(a?.[k]||0)+(b?.[k]||0);
  return x;
}
function nextRideTransitionBuckets(name,beforeDate=''){
  const target=beforeDate?dateNumber(beforeDate):null;
  const base={win:emptyNextRideBucket('直前1着'),place23:emptyNextRideBucket('直前2-3着'),out:emptyNextRideBucket('直前4着以下')};
  const byDay=new Map();
  const races=[...(state.races||[])].sort((a,b)=>dateNumber(a.meta?.date)-dateNumber(b.meta?.date)||Number(a.meta?.raceNo||0)-Number(b.meta?.raceNo||0));
  for(const race of races){
    const d=dateNumber(race.meta?.date),rn=Number(race.meta?.raceNo),venue=String(race.meta?.venue||'');
    if(!d||!Number.isFinite(rn)||!venue||(target&&d>=target))continue;
    const rr=(race.rows||[]).find(x=>x.jockey===name&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    const key=`${race.meta.date}|${venue}`;
    if(!byDay.has(key))byDay.set(key,[]);
    byDay.get(key).push({raceNo:rn,rank:Number(rr.rank)});
  }
  for(const rides of byDay.values()){
    rides.sort((a,b)=>a.raceNo-b.raceNo);
    for(let i=0;i<rides.length-1;i++){
      const prev=rides[i],next=rides[i+1];
      const bucket=prev.rank===1?base.win:prev.rank<=3?base.place23:base.out;
      addNextRideBucket(bucket,next.rank,Math.max(1,next.raceNo-prev.raceNo));
    }
  }
  base.placeAll=mergeNextRideBuckets(base.win,base.place23,'直前3着内（合計）');
  return base;
}
function nextRideTransitionTable(name){
  const st=nextRideTransitionBuckets(name);
  const order=['win','place23','placeAll','out'];
  const rows=order.map(k=>{
    const x=st[k],place=x.next1+x.next2+x.next3,avg=x.n?(x.rankSum/x.n).toFixed(2):'-',gap=x.n?(x.gapSum/x.n).toFixed(1):'-';
    return `<tr><td>${esc(x.label)}</td><td>${x.n}</td><td>${x.next1}</td><td>${x.next2}</td><td>${x.next3}</td><td>${x.next4plus}</td><td>${pct(place,x.n)}</td><td>${avg}</td><td>${gap}R</td></tr>`;
  }).join('');
  return `<div class="patternCard"><h4>直前騎乗 → 次の騎乗</h4><div class="tablewrap"><table><tr><th>直前の状態</th><th>次騎乗</th><th>次1着</th><th>次2着</th><th>次3着</th><th>次4着以下</th><th>次3着内率</th><th>次平均着順</th><th>平均R間隔</th></tr>${rows}</table></div><p class="muted">同じ日・同じ競馬場で、その騎手の次の騎乗を追跡します。1着後と2〜3着後は分けて集計し、3着内合計も併記します。</p></div>`;
}
function latestEarlierRide(jockey,meta){
  const rn=Number(meta?.raceNo);if(!jockey||!meta?.date||!meta?.venue||!Number.isFinite(rn))return null;
  let best=null;
  for(const race of (state.races||[])){
    if(String(race.meta?.date||'')!==String(meta.date)||String(race.meta?.venue||'')!==String(meta.venue))continue;
    const rno=Number(race.meta?.raceNo);if(!Number.isFinite(rno)||rno>=rn)continue;
    const rr=(race.rows||[]).find(x=>x.jockey===jockey&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    if(!best||rno>best.raceNo)best={raceNo:rno,rank:Number(rr.rank)};
  }
  return best;
}
function nextRidePatternBefore(row,meta){
  const prev=latestEarlierRide(row?.jockey,meta);
  if(!prev)return {label:'当日履歴なし',note:'このRより前の同日騎乗結果が未保存、または当日初騎乗'};
  const key=prev.rank===1?'win':prev.rank<=3?'place23':'out';
  const hist=nextRideTransitionBuckets(row.jockey,meta?.date)[key];
  const place=hist.next1+hist.next2+hist.next3;
  const prevLabel=prev.rank===1?'直前1着':prev.rank<=3?'直前2-3着':'直前4着以下';
  let label=hist.n===0?'未学習':hist.n<3?'サンプル少':hist.n<6?'参考':'蓄積あり';
  return {label,n:hist.n,prevRank:prev.rank,note:`${prev.raceNo}R ${prevLabel} → 過去${hist.n}回 / 次1着${hist.next1} / 次3着内${place}（${pct(place,hist.n)}）`};
}
'''
rep('function avgRankText(x){',helpers+'\nfunction avgRankText(x){','next ride helpers')

rep("騎手名をクリックすると、競馬場・コース距離・馬場・人気別のパターンを確認できます。",
    "騎手名をクリックすると、競馬場・コース距離・馬場・クラス・人気・当日R・直前騎乗→次騎乗のパターンを確認できます。",
    'jockey view guide')

rep("平均着順 ${avgRankText(st)}</p><div class=\"patternGrid\">",
    "平均着順 ${avgRankText(st)}</p><p class=\"muted\">現在の学習内容：競馬場 / コース距離 / 馬場 / 人気順位 / クラス / 当日成績×R / 位置 / 相手比較 / 直前騎乗→次騎乗。クラスと直前騎乗パターンは現在は参考表示のみで、最終騎手点にはまだ加算しません。</p><div class=\"patternGrid\">",
    'learning memo')

rep("${patternTable('馬場別',Object.entries(st.goings),'馬場')}${patternTable('人気帯別',popEntries,'人気帯')}",
    "${patternTable('馬場別',Object.entries(st.goings),'馬場')}${patternTable('クラス別',Object.entries(st.classes||{}),'クラス')}${patternTable('人気帯別',popEntries,'人気帯')}",
    'class table')
rep("${patternTable('当日成績 × R',dailyPatternEntries(name),'状態')}${popularityExpectationCard(st)}",
    "${patternTable('当日成績 × R',dailyPatternEntries(name),'状態')}${nextRideTransitionTable(name)}${popularityExpectationCard(st)}",
    'next ride table')

rep("騎手は適性＋並び補正を採用し、当日Rは参考表示・学習継続です。",
    "騎手は適性＋並び補正を採用し、当日R・クラス別・直前騎乗→次騎乗は参考表示・学習継続です。",
    'card guide')
rep("<th>騎手適性</th><th>並び補正</th><th>当日R参考</th><th>最終騎手</th>",
    "<th>騎手適性</th><th>クラス参考</th><th>並び補正</th><th>当日R参考</th><th>直前騎乗参考</th><th>最終騎手</th>",
    'card headers')
rep("      const dp=jockeyDayRacePattern(r,m);\n      const hs=horseAbility(r,m);",
    "      const dp=jockeyDayRacePattern(r,m);\n      const cp=jockeyClassPattern(r,m);\n      const nx=nextRidePatternBefore(r,m);\n      const hs=horseAbility(r,m);",
    'card calculations')
rep("<td class=\"scoreCell ${scoreClass(base)}\">${scoreText}</td><td class=\"scoreCell ${scoreClass(50+lp.adj)}\">${adjText}</td><td class=\"scoreCell ${scoreClass(50+dp.adj)}\">${dayAdjText}</td><td class=\"scoreCell ${scoreClass(finalScore)}\">${finalText}</td>",
    "<td class=\"scoreCell ${scoreClass(base)}\">${scoreText}</td><td class=\"scoreNote\"><span class=\"scoreFlag\">${esc(cp.label)}</span><div class=\"muted\">${esc(cp.note)}</div></td><td class=\"scoreCell ${scoreClass(50+lp.adj)}\">${adjText}</td><td class=\"scoreCell ${scoreClass(50+dp.adj)}\">${dayAdjText}</td><td class=\"scoreNote\"><span class=\"scoreFlag\">${esc(nx.label)}</span><div class=\"muted\">${esc(nx.note)}</div></td><td class=\"scoreCell ${scoreClass(finalScore)}\">${finalText}</td>",
    'card reference cells')

rep("setStatus('✓ クリーン版 v4.38 起動。Q→Bで救った勝ち馬診断を追加しました。','ok');",
    "setStatus('✓ クリーン版 v4.39 起動。騎手クラス別と直前騎乗→次騎乗パターンを追加しました。','ok');",
    'boot status')

for required in ['クラス別','直前騎乗 → 次の騎乗','jockeyClassPattern','nextRidePatternBefore','v4.39']:
    if required not in s: raise SystemExit(f'missing output marker: {required}')
p.write_text(s,encoding='utf-8')

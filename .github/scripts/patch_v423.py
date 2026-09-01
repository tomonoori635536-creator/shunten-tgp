from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_header='クリーン版 v4.22：騎手人気1〜12位を個別学習'
new_header='クリーン版 v4.23：騎手の当日成績×Rパターン学習'
assert old_header in s, 'v4.22 header not found'
s=s.replace(old_header,new_header,1)

marker="function scoreClass(score){if(score==null)return '';return score>=60?'scoreGood':score>=45?'scoreMid':'scoreLow'}"
assert marker in s, 'scoreClass marker not found'

daily_code=r'''function dayJockeyContext(jockey,date,raceNo,venue=''){
  const rn=Number(raceNo);
  const ctx={rides:0,wins:0,places:0};
  if(!jockey||!date||!Number.isFinite(rn))return ctx;
  for(const race of (state.races||[])){
    if(String(race.meta?.date||'')!==String(date))continue;
    if(venue&&race.meta?.venue&&String(race.meta.venue)!==String(venue))continue;
    const rno=Number(race.meta?.raceNo);
    if(!Number.isFinite(rno)||rno>=rn)continue;
    const rr=(race.rows||[]).find(x=>x.jockey===jockey&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    const rank=Number(rr.rank);
    ctx.rides++;
    if(rank===1)ctx.wins++;
    if(rank<=3)ctx.places++;
  }
  return ctx;
}
function dailyPatternRate(rows){
  const n=rows.length;if(!n)return {n:0,wins:0,places:0,winRate:0,placeRate:0};
  const wins=rows.filter(x=>Number(x.rank)===1).length;
  const places=rows.filter(x=>Number(x.rank)<=3).length;
  return {n,wins,places,winRate:wins/n,placeRate:places/n};
}
function jockeyDayRacePattern(row,meta){
  const jockey=String(row?.jockey||'');
  const targetDate=dateNumber(meta?.date);
  const targetRace=Number(meta?.raceNo);
  const venue=String(meta?.venue||'');
  const current=dayJockeyContext(jockey,meta?.date,targetRace,venue);
  if(!jockey||!targetDate||!Number.isFinite(targetRace))return {adj:0,label:'未学習',current,n:0,wins:0,places:0,sameRN:0,note:'日付またはR不明'};
  const sameR=[];
  const exact=[];
  for(const race of (state.races||[])){
    const d=dateNumber(race.meta?.date);
    if(!d||d>=targetDate||Number(race.meta?.raceNo)!==targetRace)continue;
    const rr=(race.rows||[]).find(x=>x.jockey===jockey&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    const field=(race.rows||[]).filter(x=>Number.isFinite(Number(x.rank))).length;
    const enriched={...rr,fieldSize:field};
    sameR.push(enriched);
    const hist=dayJockeyContext(jockey,race.meta?.date,targetRace,race.meta?.venue||'');
    if(hist.wins===current.wins&&hist.places===current.places)exact.push(enriched);
  }
  const exactStat=dailyPatternRate(exact);
  const baseStat=dailyPatternRate(sameR);
  let adj=0;
  if(exactStat.n&&baseStat.n){
    const edge=(exactStat.winRate-baseStat.winRate)*14+(exactStat.placeRate-baseStat.placeRate)*18;
    const shrink=exactStat.n/(exactStat.n+5);
    adj=clampValue(edge*shrink,-6,6);
  }
  let label='蓄積あり';
  if(exactStat.n===0)label='未学習';
  else if(exactStat.n<3)label='サンプル少';
  else if(exactStat.n<6)label='参考';
  const note=`${targetRace}R前 ${current.wins}勝・3着内${current.places}回（当日${current.rides}鞍） → 過去${exactStat.n}回 / 1着${exactStat.wins}回 / 3着内${exactStat.places}回`;
  return {adj,label,current,n:exactStat.n,wins:exactStat.wins,places:exactStat.places,sameRN:baseStat.n,note};
}
function dailyPatternEntries(name){
  const map=new Map();
  const races=[...(state.races||[])].sort((a,b)=>dateNumber(a.meta?.date)-dateNumber(b.meta?.date)||Number(a.meta?.raceNo||0)-Number(b.meta?.raceNo||0));
  for(const race of races){
    const rn=Number(race.meta?.raceNo);
    if(!Number.isFinite(rn))continue;
    const rr=(race.rows||[]).find(x=>x.jockey===name&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    const ctx=dayJockeyContext(name,race.meta?.date,rn,race.meta?.venue||'');
    const key=`${rn}R / 前${ctx.wins}勝・3着内${ctx.places}回`;
    if(!map.has(key))map.set(key,{rides:0,wins:0,places:0,rankSum:0,raceNo:rn,preWins:ctx.wins,prePlaces:ctx.places});
    const x=map.get(key),rank=Number(rr.rank);
    x.rides++;x.rankSum+=rank;if(rank===1)x.wins++;if(rank<=3)x.places++;
  }
  return [...map.entries()].sort((a,b)=>a[1].raceNo-b[1].raceNo||a[1].preWins-b[1].preWins||a[1].prePlaces-b[1].prePlaces);
}
'''
s=s.replace(marker,daily_code+marker,1)

old_desc='騎手適性は過去履歴から計算。並び補正は、完全保存された結果に加え、過去馬柱から安全に同一レースと復元できた組だけを使い「内・中・外」と同乗騎手に対する内側/外側の先着傾向を学習します。曖昧な組は除外し、補正は最大±8点です。'
new_desc='騎手適性は過去履歴から計算。並び補正は最大±8点。当日R補正は、対象Rより前の当日成績（勝数・3着内数）と同じ状態で、そのRに騎乗した過去開催日の成績を騎手ごとに学習します。未来のRや同日の後続結果は使わず、補正は最大±6点です。'
assert old_desc in s, 'preview description not found'
s=s.replace(old_desc,new_desc,1)

old_head='<th>騎手適性</th><th>並び補正</th><th>最終騎手</th><th>信頼度</th><th>並び学習</th><th>今回の一致データ</th>'
new_head='<th>騎手適性</th><th>並び補正</th><th>当日R補正</th><th>最終騎手</th><th>信頼度</th><th>当日パターン</th><th>並び学習</th><th>今回の一致データ</th>'
assert old_head in s, 'preview table header not found'
s=s.replace(old_head,new_head,1)

old_calc=r'''      const q=jockeySuitability(r,m);
      const lp=jockeyLineupPattern(r,m,p.rows);
      const base=q.score==null?null:q.score;
      const finalScore=base==null?null:clampValue(base+lp.adj,0,100);
      const scoreText=base==null?'--':Math.round(base);
      const finalText=finalScore==null?'--':Math.round(finalScore);
      const adjText=lp.label==='未学習'?'--':`${lp.adj>0?'+':''}${lp.adj.toFixed(1)}`;
      const reason=q.reasons.length?q.reasons.join(' / '):`過去 ${q.total}鞍・条件一致なし`;
      const lineupText=lp.notes.length?lp.notes.slice(0,3).join(' / '):`位置 ${lp.posN}鞍 / 相手比較 ${lp.pairMatches}回`;
      const horseRuns=horseHistoryBefore(r.name,m.date).length; return `<tr><td>${r.num??''}</td><td>${esc(r.name)}</td><td>${horseRuns}走</td><td>${esc(r.jockey)}</td><td>${r.pop??'-'}</td><td>${r.odds??'-'}</td><td class="scoreCell ${scoreClass(base)}">${scoreText}</td><td class="scoreCell ${scoreClass(50+lp.adj)}">${adjText}</td><td class="scoreCell ${scoreClass(finalScore)}">${finalText}</td><td><span class="scoreFlag">${esc(q.label)}</span><div class="muted">過去${q.total}鞍 / 一致${q.matchCount}鞍</div></td><td class="scoreNote"><span class="scoreFlag">${esc(lp.label)}</span><div class="muted">${esc(lineupText)}</div></td><td class="scoreNote">${esc(reason)}</td></tr>`;'''
new_calc=r'''      const q=jockeySuitability(r,m);
      const lp=jockeyLineupPattern(r,m,p.rows);
      const dp=jockeyDayRacePattern(r,m);
      const base=q.score==null?null:q.score;
      const finalScore=base==null?null:clampValue(base+lp.adj+dp.adj,0,100);
      const scoreText=base==null?'--':Math.round(base);
      const finalText=finalScore==null?'--':Math.round(finalScore);
      const adjText=lp.label==='未学習'?'--':`${lp.adj>0?'+':''}${lp.adj.toFixed(1)}`;
      const dayAdjText=dp.label==='未学習'?'--':`${dp.adj>0?'+':''}${dp.adj.toFixed(1)}`;
      const reason=q.reasons.length?q.reasons.join(' / '):`過去 ${q.total}鞍・条件一致なし`;
      const lineupText=lp.notes.length?lp.notes.slice(0,3).join(' / '):`位置 ${lp.posN}鞍 / 相手比較 ${lp.pairMatches}回`;
      const horseRuns=horseHistoryBefore(r.name,m.date).length; return `<tr><td>${r.num??''}</td><td>${esc(r.name)}</td><td>${horseRuns}走</td><td>${esc(r.jockey)}</td><td>${r.pop??'-'}</td><td>${r.odds??'-'}</td><td class="scoreCell ${scoreClass(base)}">${scoreText}</td><td class="scoreCell ${scoreClass(50+lp.adj)}">${adjText}</td><td class="scoreCell ${scoreClass(50+dp.adj)}">${dayAdjText}</td><td class="scoreCell ${scoreClass(finalScore)}">${finalText}</td><td><span class="scoreFlag">${esc(q.label)}</span><div class="muted">過去${q.total}鞍 / 一致${q.matchCount}鞍</div></td><td class="scoreNote"><span class="scoreFlag">${esc(dp.label)}</span><div class="muted">${esc(dp.note)}</div></td><td class="scoreNote"><span class="scoreFlag">${esc(lp.label)}</span><div class="muted">${esc(lineupText)}</div></td><td class="scoreNote">${esc(reason)}</td></tr>`;'''
assert old_calc in s, 'preview row calculation not found'
s=s.replace(old_calc,new_calc,1)

old_detail="${patternTable('人気順位別',exactPopEntries,'人気')}${popularityExpectationCard(st)}</div>`}"
new_detail="${patternTable('人気順位別',exactPopEntries,'人気')}${patternTable('当日成績 × R',dailyPatternEntries(name),'状態')}${popularityExpectationCard(st)}</div>`}"
assert old_detail in s, 'jockey detail pattern insertion point not found'
s=s.replace(old_detail,new_detail,1)

old_boot="setStatus('✓ クリーン版 v4.20 起動。保存確認とJSON自動バックアップに対応しました。','ok')"
new_boot="setStatus('✓ クリーン版 v4.23 起動。当日ここまでの勝数・3着内数 × Rを騎手別に学習します。','ok')"
assert old_boot in s, 'boot message not found'
s=s.replace(old_boot,new_boot,1)

p.write_text(s,encoding='utf-8')

from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_header='クリーン版 v4.25：当日Rは学習継続・最終点から一時除外'
new_header='クリーン版 v4.26：馬能力スコア土台＋時系列検証'
assert old_header in s, 'v4.25 header not found'
s=s.replace(old_header,new_header,1)

old_hint='A=騎手適性 / B=＋並び / C=＋当日R / D=＋並び＋当日R'
new_hint='A=騎手適性 / B=＋並び / C=＋当日R / D=＋並び＋当日R / H=馬能力のみ（未混合）'
assert old_hint in s, 'backtest hint not found'
s=s.replace(old_hint,new_hint,1)

old_bt_desc='保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で4方式を比較します。取消・除外など結果に存在しない馬は評価対象から外します。'
new_bt_desc='保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で騎手4方式と馬能力のみを比較します。馬と騎手はまだ混ぜません。取消・除外など結果に存在しない馬は評価対象から外します。'
assert old_bt_desc in s, 'backtest description not found'
s=s.replace(old_bt_desc,new_bt_desc,1)

insert_marker='function backtestKey(meta){'
assert insert_marker in s, 'backtest marker not found'
horse_code=r'''function normalizeGoingValue(g){
  const s=String(g||'').trim();
  if(s==='稍')return '稍重';
  if(s==='不')return '不良';
  return s;
}
function horseClassKey(x){
  const s=String(typeof x==='string'?x:(x?.className||x?.raceName||'')).trim();
  if(!s)return '';
  if(/(?:Jpn|G)1|重賞.*(?:1|Ⅰ)/i.test(s))return '重賞1';
  if(/(?:Jpn|G)2|重賞.*(?:2|Ⅱ)/i.test(s))return '重賞2';
  if(/(?:Jpn|G)3|重賞.*(?:3|Ⅲ)/i.test(s))return '重賞3';
  let m=s.match(/([ABC])\s*\d*\s*組?/i);
  if(m)return m[1].toUpperCase();
  m=s.match(/(\d+)勝クラス/);
  if(m)return `${m[1]}勝クラス`;
  if(/未勝利/.test(s))return '未勝利';
  if(/新馬/.test(s))return '新馬';
  if(/オープン|\bOP\b/i.test(s))return 'オープン';
  if(/3歳/.test(s))return '3歳';
  if(/2歳/.test(s))return '2歳';
  return '';
}
function horseRunPerformance(r){
  const rank=Number(r?.rank),field=Number(r?.fieldSize);
  if(!Number.isFinite(rank)||rank<1)return null;
  if(Number.isFinite(field)&&field>=2){
    const safeRank=clampValue(rank,1,field);
    return clampValue(100*(field-safeRank)/(field-1),0,100);
  }
  if(rank===1)return 85;
  if(rank===2)return 75;
  if(rank===3)return 68;
  return clampValue(68-(rank-3)*6,15,62);
}
function horseAverageScore(rows,shrinkBase=3){
  const vals=(rows||[]).map(horseRunPerformance).filter(Number.isFinite);
  if(!vals.length)return null;
  const raw=vals.reduce((a,b)=>a+b,0)/vals.length;
  const shrink=vals.length/(vals.length+shrinkBase);
  return 50+(raw-50)*shrink;
}
function horseRecentScore(rows){
  const recent=[...(rows||[])].sort((a,b)=>dateNumber(b.date)-dateNumber(a.date)).slice(0,3);
  if(!recent.length)return null;
  const weights=[0.50,0.30,0.20];
  let sum=0,w=0,n=0;
  for(let i=0;i<recent.length;i++){
    const v=horseRunPerformance(recent[i]);
    if(!Number.isFinite(v))continue;
    sum+=v*weights[i];w+=weights[i];n++;
  }
  if(!w)return null;
  const raw=sum/w;
  const shrink=n/(n+1.5);
  return {score:50+(raw-50)*shrink,n};
}
function horseAbility(row,meta){
  const all=horseHistoryBefore(row?.name,meta?.date).filter(r=>Number.isFinite(Number(r.rank)));
  if(!all.length)return {score:null,label:'未学習',total:0,reasons:[]};
  const factors=[];
  const recent=horseRecentScore(all);
  if(recent)factors.push({label:'直近3走',weight:40,score:recent.score,n:recent.n});
  const courseRows=all.filter(r=>String(r.surface||'')===String(meta?.surface||'')&&Number(r.distance)===Number(meta?.distance));
  const courseScore=horseAverageScore(courseRows,3);
  if(Number.isFinite(courseScore))factors.push({label:`${meta?.surface||'?'}${meta?.distance||'?'}m`,weight:25,score:courseScore,n:courseRows.length});
  const targetGoing=normalizeGoingValue(meta?.going);
  const goingRows=targetGoing?all.filter(r=>normalizeGoingValue(r.going)===targetGoing):[];
  const goingScore=horseAverageScore(goingRows,3);
  if(Number.isFinite(goingScore))factors.push({label:targetGoing,weight:15,score:goingScore,n:goingRows.length});
  const cls=horseClassKey(meta);
  const classRows=cls?all.filter(r=>horseClassKey(r)===cls):[];
  const classScore=horseAverageScore(classRows,3);
  if(Number.isFinite(classScore))factors.push({label:`クラス${cls}`,weight:20,score:classScore,n:classRows.length});
  if(!factors.length)return {score:null,label:'未学習',total:all.length,reasons:[]};
  const weightSum=factors.reduce((a,x)=>a+x.weight,0);
  const score=factors.reduce((a,x)=>a+x.score*x.weight,0)/weightSum;
  let label='蓄積あり';
  if(all.length<2)label='サンプル少';
  else if(all.length<5)label='参考';
  return {score:clampValue(score,0,100),label,total:all.length,reasons:factors.map(x=>`${x.label} ${x.n}走`),factors};
}
'''
s=s.replace(insert_marker,horse_code+insert_marker,1)

# Replace chronological backtest and renderer so horse-only can have its own sample count.
start=s.index('function runChronologicalBacktest(){')
end=s.index('\nfunction scoreClass(score)',start)
new_bt=r'''function runChronologicalBacktest(){
  state=loadState();
  if(!Array.isArray(state.races))state.races=[];
  if(!Array.isArray(state.raceCards))state.raceCards=[];
  if(!Array.isArray(state.history))rebuildHistory();
  rebuildHorseHistory();
  const variants=[
    {key:'a',name:'A 騎手適性のみ',score:'scoreA'},
    {key:'b',name:'B ＋並び（現在採用）',score:'scoreB'},
    {key:'c',name:'C ＋当日R',score:'scoreC'},
    {key:'d',name:'D ＋並び＋当日R',score:'scoreD'},
    {key:'h',name:'H 馬能力のみ',score:'scoreH'}
  ];
  const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0}]));
  const details=[];
  let skipped=0;
  for(const pair of backtestRacePairs()){
    const result=pair.result,card=pair.card;
    if(!card){skipped++;continue}
    const resultRows=(result.rows||[]).filter(x=>Number.isFinite(Number(x.rank)));
    const resultByNum=new Map(resultRows.map(x=>[Number(x.num),x]));
    const winner=resultRows.find(x=>Number(x.rank)===1);
    if(!winner){skipped++;continue}
    const cardRows=(card.rows||[]).filter(x=>resultByNum.has(Number(x.num)));
    if(cardRows.length<3){skipped++;continue}
    const meta={...(card.meta||{}),date:result.meta?.date||card.meta?.date,venue:result.meta?.venue||card.meta?.venue,raceNo:result.meta?.raceNo||card.meta?.raceNo};
    const scored=cardRows.map(row=>{
      const h=horseAbility(row,meta);
      const q=jockeySuitability(row,meta);
      let scoreA=null,scoreB=null,scoreC=null,scoreD=null;
      if(q.score!=null){
        const lp=jockeyLineupPattern(row,meta,cardRows);
        const dp=jockeyDayRacePattern(row,meta);
        const base=Number(q.score);
        scoreA=base;
        scoreB=clampValue(base+lp.adj,0,100);
        scoreC=clampValue(base+dp.adj,0,100);
        scoreD=clampValue(base+lp.adj+dp.adj,0,100);
      }
      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score};
    });
    const actualTop3=new Set(resultRows.filter(x=>Number(x.rank)>=1&&Number(x.rank)<=3).map(x=>Number(x.num)));
    const rowDetail={date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',winnerNum:Number(winner.num),winnerName:winner.name||'',tops:{}};
    let anyEvaluated=false;
    for(const v of variants){
      const ranked=backtestRankRows(scored,v.score);
      if(ranked.length<3){rowDetail.tops[v.key]=null;continue}
      anyEvaluated=true;
      const st=stats[v.key],top1=ranked[0],top3=ranked.slice(0,3);
      const top1Result=resultByNum.get(Number(top1.row.num));
      st.n++;
      if(Number(top1Result?.rank)===1)st.top1Win++;
      if(Number(top1Result?.rank)<=3)st.top1Place++;
      if(top3.some(x=>Number(x.row.num)===Number(winner.num)))st.winnerTop3++;
      const predTop3=new Set(top3.map(x=>Number(x.row.num)));
      if(actualTop3.size===3&&[...actualTop3].every(n=>predTop3.has(n)))st.exactTop3++;
      rowDetail.tops[v.key]={num:Number(top1.row.num),name:top1.row.name||'',hit:Number(top1Result?.rank)===1,place:Number(top1Result?.rank)<=3};
    }
    if(anyEvaluated)details.push(rowDetail);else skipped++;
  }
  return {variants,stats,details,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};
}
function renderBacktest(){
  const bt=runChronologicalBacktest();
  $('btResultCount').textContent=bt.totalResults;
  $('btCardCount').textContent=bt.totalCards;
  $('btEvalCount').textContent=bt.details.length;
  $('btSkipCount').textContent=bt.skipped;
  if(!bt.details.length){
    $('backtestStatus').textContent='評価できる「出馬表→結果」の組がまだありません。日付・競馬場・Rが一致した保存データが必要です。';
    $('backtestSummary').innerHTML='';$('backtestDetail').innerHTML='';return;
  }
  const horseN=bt.stats.h?.n||0;
  $('backtestStatus').textContent=`✓ ${bt.details.length}レースを時系列評価しました。後の開催日・同日後続Rは予測に使っていません。馬能力は${horseN}レース評価。除外 ${bt.skipped}レース。`;
  const metrics=['top1Win','top1Place','winnerTop3','exactTop3'];
  const best={};
  for(const m of metrics){
    const rates=bt.variants.filter(v=>bt.stats[v.key].n>0).map(v=>bt.stats[v.key][m]/bt.stats[v.key].n);
    best[m]=rates.length?Math.max(...rates):0;
  }
  const cell=(v,m)=>{const st=bt.stats[v.key];if(!st.n)return '<td>-</td>';const rate=st[m]/st.n,cls=Math.abs(rate-best[m])<1e-12?' class="bestCell"':'';return `<td${cls}>${backtestPct(st[m],st.n)} <span class="muted">(${st[m]}/${st.n})</span></td>`};
  $('backtestSummary').innerHTML=`<div class="tablewrap"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}</tr>`}).join('')}</tbody></table></div><p class="muted">Hは馬能力だけの独立テストです。まだ騎手とは混ぜません。Hの評価Rが少ない場合は、馬の過去走が十分保存されていないレースがあるためです。</p>`;
  $('backtestDetail').innerHTML=`<div class="tablewrap"><table><thead><tr><th>日付</th><th>競馬場</th><th>R</th><th>勝ち馬</th><th>A 1位</th><th>B 1位</th><th>C 1位</th><th>D 1位</th><th>H 馬1位</th></tr></thead><tbody>${bt.details.map(d=>`<tr><td>${esc(d.date)}</td><td>${esc(d.venue)}</td><td>${d.raceNo}R</td><td><b>${d.winnerNum} ${esc(d.winnerName)}</b></td>${bt.variants.map(v=>{const x=d.tops[v.key];if(!x)return '<td class="muted">--</td>';return `<td class="${x.hit?'hit':'miss'}">${x.hit?'✓':'・'} ${x.num} ${esc(x.name)}</td>`}).join('')}</tr>`).join('')}</tbody></table></div>`;
}
'''
s=s[:start]+new_bt+s[end:]

old_desc='騎手適性は過去履歴から計算。並び補正は最大±8点。当日Rパターンは、対象Rより前の当日成績（勝数・3着内数）と同じ状態で、そのRに騎乗した過去開催日の成績を騎手ごとに学習します。未来のRや同日の後続結果は使いません。現在はバックテスト結果により当日Rは参考表示のみとし、最終騎手点には加算しません。'
new_desc='馬能力は直近3走40%・同コース距離25%・同馬場15%・クラス20%の土台で、対象日より前の馬成績だけから計算します。該当データがない項目は残りの項目へ再配分します。騎手は適性＋並び補正を採用し、当日Rは参考表示・学習継続です。馬能力と騎手はまだ混ぜません。'
assert old_desc in s, 'preview description not found'
s=s.replace(old_desc,new_desc,1)

old_head='<th>馬履歴</th><th>騎手</th>'
new_head='<th>馬履歴</th><th>馬能力</th><th>騎手</th>'
assert old_head in s, 'horse preview header not found'
s=s.replace(old_head,new_head,1)

old_dp='''      const dp=jockeyDayRacePattern(r,m);\n      const base=q.score==null?null:q.score;'''
new_dp='''      const dp=jockeyDayRacePattern(r,m);\n      const hs=horseAbility(r,m);\n      const base=q.score==null?null:q.score;'''
assert old_dp in s, 'preview dp insertion point not found'
s=s.replace(old_dp,new_dp,1)

old_return="""      const horseRuns=horseHistoryBefore(r.name,m.date).length; return `<tr><td>${r.num??''}</td><td>${esc(r.name)}</td><td>${horseRuns}走</td><td>${esc(r.jockey)}</td>"""
new_return="""      const horseRuns=horseHistoryBefore(r.name,m.date).length;\n      const horseText=hs.score==null?'--':Math.round(hs.score);\n      const horseReason=hs.reasons?.length?hs.reasons.slice(0,3).join(' / '):'過去走なし';\n      return `<tr><td>${r.num??''}</td><td>${esc(r.name)}</td><td>${horseRuns}走</td><td class=\"scoreCell ${scoreClass(hs.score)}\">${horseText}<div class=\"muted\">${esc(horseReason)}</div></td><td>${esc(r.jockey)}</td>"""
assert old_return in s, 'horse preview row not found'
s=s.replace(old_return,new_return,1)

# Update stale boot line.
s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.26 起動。馬能力は馬だけで独立採点し、バックテストで騎手系と比較します。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

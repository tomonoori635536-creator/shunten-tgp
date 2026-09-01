from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.23：騎手の当日成績×Rパターン学習'
new='クリーン版 v4.24：51レース時系列バックテスト'
assert old in s, 'v4.23 header not found'
s=s.replace(old,new,1)

old_css='.scoreFlag{display:inline-block;padding:2px 7px;border-radius:999px;background:#eef3f7;font-size:12px;font-weight:700}'
new_css=old_css+'.bestCell{background:#edf8f1;font-weight:800}.hit{color:#0d6b3f;font-weight:800}.miss{color:#8a3333}.btNote{white-space:normal;min-width:180px}'
assert old_css in s, 'css marker not found'
s=s.replace(old_css,new_css,1)

old_tabs='''<button class="btn tab active" data-view="inputView">データ入力</button>\n<button class="btn tab" data-view="jockeyView">騎手一覧</button>\n<button class="btn tab" data-view="manageView">保存データ</button>'''
new_tabs='''<button class="btn tab active" data-view="inputView">データ入力</button>\n<button class="btn tab" data-view="jockeyView">騎手一覧</button>\n<button class="btn tab" data-view="backtestView">バックテスト</button>\n<button class="btn tab" data-view="manageView">保存データ</button>'''
assert old_tabs in s, 'tab marker not found'
s=s.replace(old_tabs,new_tabs,1)

manage_marker='''<section class="panel view" id="manageView">\n<h2>保存データ</h2>'''
backtest_section='''<section class="panel view" id="backtestView">\n<h2>時系列バックテスト</h2>\n<p>保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で4方式を比較します。取消・除外など結果に存在しない馬は評価対象から外します。</p>\n<div class="row"><button class="btn primary" id="backtestBtn">バックテスト再計算</button><span class="muted">A=騎手適性 / B=＋並び / C=＋当日R / D=＋並び＋当日R</span></div>\n<div class="summary" style="margin-top:14px"><div class="chip"><b>保存結果</b><div class="big" id="btResultCount">0</div></div><div class="chip"><b>保存出馬表</b><div class="big" id="btCardCount">0</div></div><div class="chip"><b>評価対象</b><div class="big" id="btEvalCount">0</div></div><div class="chip"><b>除外</b><div class="big" id="btSkipCount">0</div></div></div>\n<div id="backtestStatus" class="status">バックテストタブを開くと計算します。</div>\n<div id="backtestSummary"></div>\n<h3>レース別</h3>\n<div id="backtestDetail"></div>\n</section>\n\n<section class="panel view" id="manageView">\n<h2>保存データ</h2>'''
assert manage_marker in s, 'manage section marker not found'
s=s.replace(manage_marker,backtest_section,1)

insert_before='''function scoreClass(score){if(score==null)return '';return score>=60?'scoreGood':score>=45?'scoreMid':'scoreLow'}'''
backtest_js=r'''function backtestKey(meta){return [meta?.date||'',meta?.venue||'',Number(meta?.raceNo)||''].join('|')}
function backtestPct(n,d){return d?`${(100*n/d).toFixed(1)}%`:'0.0%'}
function backtestRankRows(scored,key){
  return scored.filter(x=>Number.isFinite(Number(x[key]))).sort((a,b)=>Number(b[key])-Number(a[key])||Number(a.row?.num||99)-Number(b.row?.num||99));
}
function backtestRacePairs(){
  const cards=new Map();
  for(const c of (state.raceCards||[]))cards.set(backtestKey(c.meta),c);
  return [...(state.races||[])].sort((a,b)=>dateNumber(a.meta?.date)-dateNumber(b.meta?.date)||Number(a.meta?.raceNo||0)-Number(b.meta?.raceNo||0)).map(result=>({result,card:cards.get(backtestKey(result.meta))||null}));
}
function runChronologicalBacktest(){
  state=loadState();
  if(!Array.isArray(state.races))state.races=[];
  if(!Array.isArray(state.raceCards))state.raceCards=[];
  if(!Array.isArray(state.history))rebuildHistory();
  rebuildHorseHistory();
  const variants=[
    {key:'a',name:'A 騎手適性のみ',score:'scoreA'},
    {key:'b',name:'B ＋並び',score:'scoreB'},
    {key:'c',name:'C ＋当日R',score:'scoreC'},
    {key:'d',name:'D ＋並び＋当日R',score:'scoreD'}
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
      const q=jockeySuitability(row,meta);
      if(q.score==null)return {row,scoreA:null,scoreB:null,scoreC:null,scoreD:null};
      const lp=jockeyLineupPattern(row,meta,cardRows);
      const dp=jockeyDayRacePattern(row,meta);
      const base=Number(q.score);
      return {row,scoreA:base,scoreB:clampValue(base+lp.adj,0,100),scoreC:clampValue(base+dp.adj,0,100),scoreD:clampValue(base+lp.adj+dp.adj,0,100)};
    });
    const rankings={};
    let usable=true;
    for(const v of variants){
      const ranked=backtestRankRows(scored,v.score);
      if(ranked.length<3){usable=false;break}
      rankings[v.key]=ranked;
    }
    if(!usable){skipped++;continue}
    const actualTop3=new Set(resultRows.filter(x=>Number(x.rank)>=1&&Number(x.rank)<=3).map(x=>Number(x.num)));
    const rowDetail={date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',winnerNum:Number(winner.num),winnerName:winner.name||'',tops:{}};
    for(const v of variants){
      const ranked=rankings[v.key],st=stats[v.key],top1=ranked[0],top3=ranked.slice(0,3);
      const top1Result=resultByNum.get(Number(top1.row.num));
      st.n++;
      if(Number(top1Result?.rank)===1)st.top1Win++;
      if(Number(top1Result?.rank)<=3)st.top1Place++;
      if(top3.some(x=>Number(x.row.num)===Number(winner.num)))st.winnerTop3++;
      const predTop3=new Set(top3.map(x=>Number(x.row.num)));
      if(actualTop3.size===3&&[...actualTop3].every(n=>predTop3.has(n)))st.exactTop3++;
      rowDetail.tops[v.key]={num:Number(top1.row.num),name:top1.row.name||'',hit:Number(top1Result?.rank)===1,place:Number(top1Result?.rank)<=3};
    }
    details.push(rowDetail);
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
  $('backtestStatus').textContent=`✓ ${bt.details.length}レースを時系列評価しました。後の開催日・同日後続Rは予測に使っていません。除外 ${bt.skipped}レース。`;
  const metrics=['top1Win','top1Place','winnerTop3','exactTop3'];
  const best={};
  for(const m of metrics)best[m]=Math.max(...bt.variants.map(v=>bt.stats[v.key][m]/Math.max(1,bt.stats[v.key].n)));
  const cell=(v,m)=>{const st=bt.stats[v.key],rate=st[m]/Math.max(1,st.n),cls=Math.abs(rate-best[m])<1e-12?' class="bestCell"':'';return `<td${cls}>${backtestPct(st[m],st.n)} <span class="muted">(${st[m]}/${st.n})</span></td>`};
  $('backtestSummary').innerHTML=`<div class="tablewrap"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}</tr>`}).join('')}</tbody></table></div><p class="muted">緑のセルはその指標の最高値です。まずは「補正を足したことで改善したか」をAと比較してください。</p>`;
  $('backtestDetail').innerHTML=`<div class="tablewrap"><table><thead><tr><th>日付</th><th>競馬場</th><th>R</th><th>勝ち馬</th><th>A 1位</th><th>B 1位</th><th>C 1位</th><th>D 1位</th></tr></thead><tbody>${bt.details.map(d=>`<tr><td>${esc(d.date)}</td><td>${esc(d.venue)}</td><td>${d.raceNo}R</td><td><b>${d.winnerNum} ${esc(d.winnerName)}</b></td>${bt.variants.map(v=>{const x=d.tops[v.key];return `<td class="${x.hit?'hit':'miss'}">${x.hit?'✓':'・'} ${x.num} ${esc(x.name)}</td>`}).join('')}</tr>`).join('')}</tbody></table></div>`;
}
'''
assert insert_before in s, 'scoreClass marker not found'
s=s.replace(insert_before,backtest_js+'\n'+insert_before,1)

old_click="document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));btn.classList.add('active');$(btn.dataset.view).classList.add('active');if(btn.dataset.view!=='inputView')renderDashboard()}));"
new_click="document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));btn.classList.add('active');$(btn.dataset.view).classList.add('active');if(btn.dataset.view==='backtestView')renderBacktest();else if(btn.dataset.view!=='inputView')renderDashboard()}));\n$('backtestBtn').addEventListener('click',renderBacktest);"
assert old_click in s, 'tab click handler not found'
s=s.replace(old_click,new_click,1)

for old_boot in [
    "setStatus('✓ クリーン版 v4.20 起動。保存確認とJSON自動バックアップに対応しました。','ok')",
    "setStatus('✓ クリーン版 v4.21 起動。取消・除外・中止・失格は着順学習から除外します。','ok')",
    "setStatus('✓ クリーン版 v4.22 起動。騎手人気1〜12位を個別学習します。','ok')",
    "setStatus('✓ クリーン版 v4.23 起動。当日成績×Rパターンを学習します。','ok')",
]:
    if old_boot in s:
        s=s.replace(old_boot,"setStatus('✓ クリーン版 v4.24 起動。51レース時系列バックテストに対応しました。','ok')",1)
        break

p.write_text(s,encoding='utf-8')

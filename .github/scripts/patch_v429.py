from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.28：馬55×騎手45も仮比較'
new='クリーン版 v4.29：単勝回収率も仮検証'
assert old in s, 'v4.28 header not found'
s=s.replace(old,new,1)

old_desc='保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で比較します。馬能力Hと現在採用中の騎手Bを50:50・55:45・60:40・70:30・80:20で仮合成します。ここで最良でも正式採用にはせず、データ増加後に再検証します。取消・除外など結果に存在しない馬は評価対象から外します。'
new_desc='保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で比較します。馬能力Hと現在採用中の騎手Bを50:50・55:45・60:40・70:30・80:20で仮合成します。さらに各方式の1位評価馬を単勝100円固定で買った場合の確定単勝オッズ回収率も仮検証します。ここで最良でも正式採用にはせず、データ増加後に再検証します。取消・除外など結果に存在しない馬は評価対象から外します。'
assert old_desc in s, 'backtest description not found'
s=s.replace(old_desc,new_desc,1)

old_stats="const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0}]));"
new_stats="const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0,roiN:0,stake:0,returnYen:0}]));"
assert old_stats in s, 'stats init not found'
s=s.replace(old_stats,new_stats,1)

old_block="""      st.n++;
      if(Number(top1Result?.rank)===1)st.top1Win++;
      if(Number(top1Result?.rank)<=3)st.top1Place++;
      if(top3.some(x=>Number(x.row.num)===Number(winner.num)))st.winnerTop3++;
      const predTop3=new Set(top3.map(x=>Number(x.row.num)));"""
new_block="""      st.n++;
      if(Number(top1Result?.rank)===1)st.top1Win++;
      if(Number(top1Result?.rank)<=3)st.top1Place++;
      if(top3.some(x=>Number(x.row.num)===Number(winner.num)))st.winnerTop3++;
      const winOdds=Number(top1Result?.odds);
      if(Number.isFinite(winOdds)&&winOdds>0){
        st.roiN++;
        st.stake+=100;
        if(Number(top1Result?.rank)===1)st.returnYen+=Math.round(winOdds*100);
      }
      const predTop3=new Set(top3.map(x=>Number(x.row.num)));"""
assert old_block in s, 'backtest result block not found'
s=s.replace(old_block,new_block,1)

old_metrics="""  const metrics=['top1Win','top1Place','winnerTop3','exactTop3'];
  const best={};
  for(const m of metrics){
    const rates=bt.variants.filter(v=>bt.stats[v.key].n>0).map(v=>bt.stats[v.key][m]/bt.stats[v.key].n);
    best[m]=rates.length?Math.max(...rates):0;
  }
  const cell=(v,m)=>{const st=bt.stats[v.key];if(!st.n)return '<td>-</td>';const rate=st[m]/st.n,cls=Math.abs(rate-best[m])<1e-12?' class=\"bestCell\"':'';return `<td${cls}>${backtestPct(st[m],st.n)} <span class=\"muted\">(${st[m]}/${st.n})</span></td>`};"""
new_metrics="""  const metrics=['top1Win','top1Place','winnerTop3','exactTop3'];
  const best={};
  for(const m of metrics){
    const rates=bt.variants.filter(v=>bt.stats[v.key].n>0).map(v=>bt.stats[v.key][m]/bt.stats[v.key].n);
    best[m]=rates.length?Math.max(...rates):0;
  }
  const roiRates=bt.variants.filter(v=>bt.stats[v.key].stake>0).map(v=>bt.stats[v.key].returnYen/bt.stats[v.key].stake);
  const bestRoi=roiRates.length?Math.max(...roiRates):0;
  const cell=(v,m)=>{const st=bt.stats[v.key];if(!st.n)return '<td>-</td>';const rate=st[m]/st.n,cls=Math.abs(rate-best[m])<1e-12?' class=\"bestCell\"':'';return `<td${cls}>${backtestPct(st[m],st.n)} <span class=\"muted\">(${st[m]}/${st.n})</span></td>`};
  const roiCell=(v)=>{const st=bt.stats[v.key];if(!st.stake)return '<td>-</td>';const rate=st.returnYen/st.stake,cls=Math.abs(rate-bestRoi)<1e-12?' class=\"bestCell\"':'';const profit=st.returnYen-st.stake;return `<td${cls}><b>${(rate*100).toFixed(1)}%</b><div class=\"muted\">${st.roiN}R / 投資${st.stake.toLocaleString()}円 / 払戻${st.returnYen.toLocaleString()}円 / 収支${profit>=0?'+':''}${profit.toLocaleString()}円</div></td>`};"""
assert old_metrics in s, 'metrics block not found'
s=s.replace(old_metrics,new_metrics,1)

old_summary="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">50:50・55:45・60:40・70:30・80:20は暫定比較です。今回の最高値を固定せず、100R・150Rなどデータ増加時に再検証します。B=騎手適性＋並び、H=馬能力のみです。</p>`;"""
new_summary="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th><th>確定単勝回収率</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}${roiCell(v)}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">単勝回収率は各方式の1位評価馬へ100円固定投資し、結果ページに保存された確定単勝オッズで計算します。オッズが保存されていない選択は回収率対象から除外します。これはモデル比較用の事後検証で、実戦時に同じオッズで買えたことを意味しません。50:50・55:45・60:40・70:30・80:20は引き続き暫定比較です。</p>`;"""
assert old_summary in s, 'backtest summary not found'
s=s.replace(old_summary,new_summary,1)

# Add selected horse odds to race detail for auditing ROI.
old_detail="""      rowDetail.tops[v.key]={num:Number(top1.row.num),name:top1.row.name||'',hit:Number(top1Result?.rank)===1,place:Number(top1Result?.rank)<=3};"""
new_detail="""      rowDetail.tops[v.key]={num:Number(top1.row.num),name:top1.row.name||'',hit:Number(top1Result?.rank)===1,place:Number(top1Result?.rank)<=3,odds:Number.isFinite(Number(top1Result?.odds))?Number(top1Result.odds):null};"""
assert old_detail in s, 'row detail assignment not found'
s=s.replace(old_detail,new_detail,1)

old_render_detail="""return `<td class=\"${x.hit?'hit':'miss'}\">${x.hit?'✓':'・'} ${x.num} ${esc(x.name)}</td>`"""
new_render_detail="""return `<td class=\"${x.hit?'hit':'miss'}\">${x.hit?'✓':'・'} ${x.num} ${esc(x.name)}<div class=\"muted\">単勝 ${x.odds??'-'}</div></td>`"""
assert old_render_detail in s, 'detail cell render not found'
s=s.replace(old_render_detail,new_render_detail,1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.29 起動。確定単勝オッズの回収率を仮検証できます。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

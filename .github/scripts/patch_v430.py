from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.29：単勝回収率も仮検証'
new='クリーン版 v4.30：単勝回収率の安定性を分解検証'
assert old in s, 'v4.29 header not found'
s=s.replace(old,new,1)

old_stats="const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0,roiN:0,stake:0,returnYen:0}]));"
new_stats="const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0,roiN:0,stake:0,returnYen:0,winOdds:[],oddsBands:{low:{n:0,stake:0,ret:0,wins:0},mid:{n:0,stake:0,ret:0,wins:0},high:{n:0,stake:0,ret:0,wins:0},long:{n:0,stake:0,ret:0,wins:0}}}]));"
assert old_stats in s, 'stats init not found'
s=s.replace(old_stats,new_stats,1)

old_roi="""      if(Number.isFinite(winOdds)&&winOdds>0){
        st.roiN++;
        st.stake+=100;
        if(Number(top1Result?.rank)===1)st.returnYen+=Math.round(winOdds*100);
      }"""
new_roi="""      if(Number.isFinite(winOdds)&&winOdds>0){
        st.roiN++;
        st.stake+=100;
        const band=winOdds<3?'low':winOdds<5?'mid':winOdds<10?'high':'long';
        const ob=st.oddsBands[band];
        ob.n++;ob.stake+=100;
        if(Number(top1Result?.rank)===1){
          const ret=Math.round(winOdds*100);
          st.returnYen+=ret;
          st.winOdds.push(winOdds);
          ob.ret+=ret;ob.wins++;
        }
      }"""
assert old_roi in s, 'ROI accumulation block not found'
s=s.replace(old_roi,new_roi,1)

old_after_roi="""  const roiCell=(v)=>{const st=bt.stats[v.key];if(!st.stake)return '<td>-</td>';const rate=st.returnYen/st.stake,cls=Math.abs(rate-bestRoi)<1e-12?' class=\"bestCell\"':'';const profit=st.returnYen-st.stake;return `<td${cls}><b>${(rate*100).toFixed(1)}%</b><div class=\"muted\">${st.roiN}R / 投資${st.stake.toLocaleString()}円 / 払戻${st.returnYen.toLocaleString()}円 / 収支${profit>=0?'+':''}${profit.toLocaleString()}円</div></td>`};"""
new_after_roi="""  const roiCell=(v)=>{const st=bt.stats[v.key];if(!st.stake)return '<td>-</td>';const rate=st.returnYen/st.stake,cls=Math.abs(rate-bestRoi)<1e-12?' class=\"bestCell\"':'';const profit=st.returnYen-st.stake;return `<td${cls}><b>${(rate*100).toFixed(1)}%</b><div class=\"muted\">${st.roiN}R / 投資${st.stake.toLocaleString()}円 / 払戻${st.returnYen.toLocaleString()}円 / 収支${profit>=0?'+':''}${profit.toLocaleString()}円</div></td>`};
  const bandCell=(b)=>{if(!b||!b.stake)return '-';return `${(100*b.ret/b.stake).toFixed(1)}% <span class=\"muted\">(${b.wins}/${b.n})</span>`};
  const roiDiagnostic=(v)=>{
    const st=bt.stats[v.key],wins=[...(st.winOdds||[])].sort((a,b)=>b-a);
    const avg=wins.length?wins.reduce((a,b)=>a+b,0)/wins.length:null;
    const max=wins.length?wins[0]:null;
    let trimmed='-';
    if(max!=null&&st.roiN>1){
      const ts=st.stake-100,tr=st.returnYen-Math.round(max*100);
      trimmed=ts>0?`${(100*tr/ts).toFixed(1)}%`:'-';
    }
    return `<tr><td><b>${esc(v.name)}</b></td><td>${wins.length}</td><td>${avg==null?'-':avg.toFixed(2)+'倍'}</td><td>${max==null?'-':max.toFixed(1)+'倍'}</td><td>${trimmed}</td><td>${bandCell(st.oddsBands.low)}</td><td>${bandCell(st.oddsBands.mid)}</td><td>${bandCell(st.oddsBands.high)}</td><td>${bandCell(st.oddsBands.long)}</td></tr>`;
  };"""
assert old_after_roi in s, 'roiCell block not found'
s=s.replace(old_after_roi,new_after_roi,1)

old_summary="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th><th>確定単勝回収率</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}${roiCell(v)}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">単勝回収率は各方式の1位評価馬へ100円固定投資し、結果ページに保存された確定単勝オッズで計算します。オッズが保存されていない選択は回収率対象から除外します。これはモデル比較用の事後検証で、実戦時に同じオッズで買えたことを意味しません。50:50・55:45・60:40・70:30・80:20は引き続き暫定比較です。</p>`;"""
new_summary="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th><th>確定単勝回収率</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}${roiCell(v)}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">単勝回収率は各方式の1位評価馬へ100円固定投資し、結果ページに保存された確定単勝オッズで計算します。オッズが保存されていない選択は回収率対象から除外します。これはモデル比較用の事後検証で、実戦時に同じオッズで買えたことを意味しません。50:50・55:45・60:40・70:30・80:20は引き続き暫定比較です。</p><h3>回収率の安定性診断</h3><div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>単勝的中</th><th>的中平均単勝</th><th>最大単勝</th><th>最大配当1頭除外ROI</th><th>1.0〜2.9倍</th><th>3.0〜4.9倍</th><th>5.0〜9.9倍</th><th>10倍以上</th></tr></thead><tbody>${bt.variants.map(roiDiagnostic).join('')}</tbody></table></div><p class=\"muted\">最大配当1頭除外ROIは、その最高配当の的中レース1件を投資100円ごと除いて再計算します。各オッズ帯は「的中数/購入数」も併記します。1頭の大穴だけで全体回収率が上がっていないかを見るための診断です。</p>`;"""
assert old_summary in s, 'summary block not found'
s=s.replace(old_summary,new_summary,1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.30 起動。単勝回収率を最大配当除外・オッズ帯別まで分解できます。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

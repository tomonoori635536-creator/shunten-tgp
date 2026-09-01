from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.30：単勝回収率の安定性を分解検証'
new='クリーン版 v4.31：高配当1位の要因を分解診断'
assert old in s, 'v4.30 header not found'
s=s.replace(old,new,1)

old="""  const details=[];
  let skipped=0;"""
new="""  const details=[];
  const highPayoutDiagnostics=[];
  let skipped=0;"""
assert old in s, 'details init not found'
s=s.replace(old,new,1)

old="""      const h=horseAbility(row,meta);
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
      const horse=Number.isFinite(Number(h.score))?Number(h.score):null;
      const jockey=Number.isFinite(Number(scoreB))?Number(scoreB):null;
      const blend=(hw)=>horse==null||jockey==null?null:clampValue(horse*hw+jockey*(1-hw),0,100);
      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score,
        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
new="""      const h=horseAbility(row,meta);
      const q=jockeySuitability(row,meta);
      let scoreA=null,scoreB=null,scoreC=null,scoreD=null,lineupAdj=0,dayAdj=0;
      if(q.score!=null){
        const lp=jockeyLineupPattern(row,meta,cardRows);
        const dp=jockeyDayRacePattern(row,meta);
        const base=Number(q.score);
        lineupAdj=Number(lp.adj)||0;
        dayAdj=Number(dp.adj)||0;
        scoreA=base;
        scoreB=clampValue(base+lineupAdj,0,100);
        scoreC=clampValue(base+dayAdj,0,100);
        scoreD=clampValue(base+lineupAdj+dayAdj,0,100);
      }
      const horse=Number.isFinite(Number(h.score))?Number(h.score):null;
      const jockey=Number.isFinite(Number(scoreB))?Number(scoreB):null;
      const blend=(hw)=>horse==null||jockey==null?null:clampValue(horse*hw+jockey*(1-hw),0,100);
      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score,jockeyBase:scoreA,lineupAdj,dayAdj,horseScore:horse,
        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
assert old in s, 'scored row block not found'
s=s.replace(old,new,1)

old="""    const actualTop3=new Set(resultRows.filter(x=>Number(x.rank)>=1&&Number(x.rank)<=3).map(x=>Number(x.num)));
    const rowDetail={date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',winnerNum:Number(winner.num),winnerName:winner.name||'',tops:{}};"""
new="""    const actualTop3=new Set(resultRows.filter(x=>Number(x.rank)>=1&&Number(x.rank)<=3).map(x=>Number(x.num)));
    const rankOf=(key,num)=>{const arr=backtestRankRows(scored,key);const i=arr.findIndex(x=>Number(x.row?.num)===Number(num));return i>=0?i+1:null};
    const winnerScored=scored.find(x=>Number(x.row?.num)===Number(winner.num));
    const winnerOdds=Number(winner?.odds);
    if(winnerScored&&Number.isFinite(winnerOdds)&&winnerOdds>=10){
      const rankA=rankOf('scoreA',winner.num),rankB=rankOf('scoreB',winner.num),rankC=rankOf('scoreC',winner.num),rankD=rankOf('scoreD',winner.num),rankH=rankOf('scoreH',winner.num),rankM55=rankOf('scoreM55',winner.num);
      if(rankB===1||rankD===1){
        highPayoutDiagnostics.push({
          date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',num:Number(winner.num),name:winner.name||'',odds:winnerOdds,
          pop:Number.isFinite(Number(winner.pop))?Number(winner.pop):Number.isFinite(Number(winnerScored.row?.pop))?Number(winnerScored.row.pop):null,
          jockey:winnerScored.row?.jockey||winner.jockey||'',
          jockeyBase:winnerScored.jockeyBase,lineupAdj:winnerScored.lineupAdj,dayAdj:winnerScored.dayAdj,horseScore:winnerScored.horseScore,
          scoreB:winnerScored.scoreB,scoreD:winnerScored.scoreD,scoreM55:winnerScored.scoreM55,
          rankA,rankB,rankC,rankD,rankH,rankM55
        });
      }
    }
    const rowDetail={date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',winnerNum:Number(winner.num),winnerName:winner.name||'',tops:{}};"""
assert old in s, 'actualTop3 insertion point not found'
s=s.replace(old,new,1)

old="""  return {variants,stats,details,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};"""
new="""  highPayoutDiagnostics.sort((a,b)=>b.odds-a.odds||String(a.date).localeCompare(String(b.date))||Number(a.raceNo)-Number(b.raceNo));
  return {variants,stats,details,highPayoutDiagnostics,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};"""
assert old in s, 'backtest return not found'
s=s.replace(old,new,1)

old="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th><th>確定単勝回収率</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}${roiCell(v)}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">単勝回収率は各方式の1位評価馬へ100円固定投資し、結果ページに保存された確定単勝オッズで計算します。オッズが保存されていない選択は回収率対象から除外します。これはモデル比較用の事後検証で、実戦時に同じオッズで買えたことを意味しません。50:50・55:45・60:40・70:30・80:20は引き続き暫定比較です。</p><h3>回収率の安定性診断</h3><div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>単勝的中</th><th>的中平均単勝</th><th>最大単勝</th><th>最大配当1頭除外ROI</th><th>1.0〜2.9倍</th><th>3.0〜4.9倍</th><th>5.0〜9.9倍</th><th>10倍以上</th></tr></thead><tbody>${bt.variants.map(roiDiagnostic).join('')}</tbody></table></div><p class=\"muted\">最大配当1頭除外ROIは、その最高配当の的中レース1件を投資100円ごと除いて再計算します。各オッズ帯は「的中数/購入数」も併記します。1頭の大穴だけで全体回収率が上がっていないかを見るための診断です。</p>`;"""
new="""  const signed=n=>Number.isFinite(Number(n))?`${Number(n)>0?'+':''}${Number(n).toFixed(1)}`:'-';
  const rankText=n=>Number.isFinite(Number(n))?`${n}位`:'-';
  const scoreText=n=>Number.isFinite(Number(n))?Number(n).toFixed(1):'-';
  const highReason=x=>{
    const bits=[];
    if(x.rankA!==1&&x.rankB===1&&Math.abs(Number(x.lineupAdj)||0)>=0.1)bits.push(`並び${signed(x.lineupAdj)}でA${rankText(x.rankA)}→B1位`);
    else if(x.rankB===1&&x.rankA===1)bits.push('元の騎手適性Aから1位');
    if(x.rankB!==1&&x.rankD===1&&Math.abs(Number(x.dayAdj)||0)>=0.1)bits.push(`当日R${signed(x.dayAdj)}でB${rankText(x.rankB)}→D1位`);
    else if(x.rankD===1&&x.rankB===1&&Math.abs(Number(x.dayAdj)||0)>=0.1)bits.push(`Dは当日R${signed(x.dayAdj)}を追加`);
    if(x.rankH===1)bits.push('馬能力Hも1位');
    if(x.rankM55===1)bits.push('55:45でも1位');
    return bits.join(' / ')||'複合要因';
  };
  const highDiag=(bt.highPayoutDiagnostics||[]).length?`<h3>高配当1位の要因診断</h3><div class=\"tablewrap\"><table><thead><tr><th>レース</th><th>勝ち馬</th><th>単勝</th><th>人気</th><th>騎手</th><th>A騎手適性</th><th>並び補正</th><th>B点 / 順位</th><th>当日R補正</th><th>D点 / 順位</th><th>H馬能力 / 順位</th><th>55:45 / 順位</th><th>なぜ拾えたか</th></tr></thead><tbody>${bt.highPayoutDiagnostics.map(x=>`<tr><td>${esc(x.date)} ${esc(x.venue)} ${x.raceNo}R</td><td><b>${x.num} ${esc(x.name)}</b></td><td><b>${x.odds.toFixed(1)}倍</b></td><td>${x.pop??'-'}</td><td>${esc(x.jockey)}</td><td>${scoreText(x.jockeyBase)} / ${rankText(x.rankA)}</td><td>${signed(x.lineupAdj)}</td><td>${scoreText(x.scoreB)} / ${rankText(x.rankB)}</td><td>${signed(x.dayAdj)}</td><td>${scoreText(x.scoreD)} / ${rankText(x.rankD)}</td><td>${scoreText(x.horseScore)} / ${rankText(x.rankH)}</td><td>${scoreText(x.scoreM55)} / ${rankText(x.rankM55)}</td><td class=\"btNote\">${esc(highReason(x))}</td></tr>`).join('')}</tbody></table></div><p class=\"muted\">10倍以上の勝ち馬のうち、B（騎手適性＋並び）またはD（B＋当日R）が1位評価できたレースだけを表示します。順位変化を見ることで、高配当を拾った主因が並び・当日R・元の騎手適性・馬能力のどこにあったか確認できます。</p>`:`<h3>高配当1位の要因診断</h3><p class=\"muted\">10倍以上の勝ち馬をBまたはDで1位評価したレースはまだありません。</p>`;
  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th><th>確定単勝回収率</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}${roiCell(v)}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">単勝回収率は各方式の1位評価馬へ100円固定投資し、結果ページに保存された確定単勝オッズで計算します。オッズが保存されていない選択は回収率対象から除外します。これはモデル比較用の事後検証で、実戦時に同じオッズで買えたことを意味しません。50:50・55:45・60:40・70:30・80:20は引き続き暫定比較です。</p><h3>回収率の安定性診断</h3><div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>単勝的中</th><th>的中平均単勝</th><th>最大単勝</th><th>最大配当1頭除外ROI</th><th>1.0〜2.9倍</th><th>3.0〜4.9倍</th><th>5.0〜9.9倍</th><th>10倍以上</th></tr></thead><tbody>${bt.variants.map(roiDiagnostic).join('')}</tbody></table></div><p class=\"muted\">最大配当1頭除外ROIは、その最高配当の的中レース1件を投資100円ごと除いて再計算します。各オッズ帯は「的中数/購入数」も併記します。1頭の大穴だけで全体回収率が上がっていないかを見るための診断です。</p>${highDiag}`;"""
assert old in s, 'backtest summary block not found'
s=s.replace(old,new,1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.31 起動。高配当1位を拾った要因を順位変化まで分解できます。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

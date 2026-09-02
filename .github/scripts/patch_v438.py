from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing anchor: {label}')
    s=s.replace(old,new,1)

rep('<p>クリーン版 v4.37：Q→B順位悪化の的中馬診断を追加</p>',
    '<p>クリーン版 v4.38：Q→Bで救った勝ち馬診断を追加</p>',
    'header')

rep('  const highPayoutDiagnostics=[];\n  const qToBRegressions=[];\n  let skipped=0;',
    '  const highPayoutDiagnostics=[];\n  const qToBRegressions=[];\n  const bRescuedWinners=[];\n  let skipped=0;',
    'diagnostic arrays')

old="""    if(winnerScored&&winnerRankQ===1&&Number.isFinite(winnerRankB)&&winnerRankB>1){
      qToBRegressions.push({
        date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',num:Number(winner.num),name:winner.name||'',
        odds:Number.isFinite(winnerOdds)?winnerOdds:null,
        pop:Number.isFinite(Number(winner.pop))?Number(winner.pop):Number.isFinite(Number(winnerScored.row?.pop))?Number(winnerScored.row.pop):null,
        jockey:winnerScored.row?.jockey||winner.jockey||'',
        scoreQ:winnerScored.scoreQ,scoreB:winnerScored.scoreB,rankQ:winnerRankQ,rankB:winnerRankB,
        posAdj:Number(winnerScored.lineupDetail?.posAdj)||0,pairAdj:Number(winnerScored.lineupDetail?.pairAdj)||0,
        posN:Number(winnerScored.lineupDetail?.posN)||0,posLiveN:Number(winnerScored.lineupDetail?.posLiveN)||0,posRecoveredN:Number(winnerScored.lineupDetail?.posRecoveredN)||0,
        pairMatches:Number(winnerScored.lineupDetail?.pairMatches)||0,pairOpponents:Number(winnerScored.lineupDetail?.pairOpponents)||0,
        pairLiveMatches:Number(winnerScored.lineupDetail?.pairLiveMatches)||0,pairRecoveredMatches:Number(winnerScored.lineupDetail?.pairRecoveredMatches)||0
      });
    }
    if(winnerScored&&Number.isFinite(winnerOdds)&&winnerOdds>=10){"""
new="""    if(winnerScored&&winnerRankQ===1&&Number.isFinite(winnerRankB)&&winnerRankB>1){
      qToBRegressions.push({
        date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',num:Number(winner.num),name:winner.name||'',
        odds:Number.isFinite(winnerOdds)?winnerOdds:null,
        pop:Number.isFinite(Number(winner.pop))?Number(winner.pop):Number.isFinite(Number(winnerScored.row?.pop))?Number(winnerScored.row.pop):null,
        jockey:winnerScored.row?.jockey||winner.jockey||'',
        scoreQ:winnerScored.scoreQ,scoreB:winnerScored.scoreB,rankQ:winnerRankQ,rankB:winnerRankB,
        posAdj:Number(winnerScored.lineupDetail?.posAdj)||0,pairAdj:Number(winnerScored.lineupDetail?.pairAdj)||0,
        posN:Number(winnerScored.lineupDetail?.posN)||0,posLiveN:Number(winnerScored.lineupDetail?.posLiveN)||0,posRecoveredN:Number(winnerScored.lineupDetail?.posRecoveredN)||0,
        pairMatches:Number(winnerScored.lineupDetail?.pairMatches)||0,pairOpponents:Number(winnerScored.lineupDetail?.pairOpponents)||0,
        pairLiveMatches:Number(winnerScored.lineupDetail?.pairLiveMatches)||0,pairRecoveredMatches:Number(winnerScored.lineupDetail?.pairRecoveredMatches)||0
      });
    }
    if(winnerScored&&winnerRankB===1&&Number.isFinite(winnerRankQ)&&winnerRankQ>1){
      bRescuedWinners.push({
        date:meta.date||'',venue:meta.venue||'',raceNo:meta.raceNo||'',num:Number(winner.num),name:winner.name||'',
        odds:Number.isFinite(winnerOdds)?winnerOdds:null,
        pop:Number.isFinite(Number(winner.pop))?Number(winner.pop):Number.isFinite(Number(winnerScored.row?.pop))?Number(winnerScored.row.pop):null,
        jockey:winnerScored.row?.jockey||winner.jockey||'',
        scoreQ:winnerScored.scoreQ,scoreB:winnerScored.scoreB,rankQ:winnerRankQ,rankB:winnerRankB,
        posAdj:Number(winnerScored.lineupDetail?.posAdj)||0,pairAdj:Number(winnerScored.lineupDetail?.pairAdj)||0,
        posN:Number(winnerScored.lineupDetail?.posN)||0,posLiveN:Number(winnerScored.lineupDetail?.posLiveN)||0,posRecoveredN:Number(winnerScored.lineupDetail?.posRecoveredN)||0,
        pairMatches:Number(winnerScored.lineupDetail?.pairMatches)||0,pairOpponents:Number(winnerScored.lineupDetail?.pairOpponents)||0,
        pairLiveMatches:Number(winnerScored.lineupDetail?.pairLiveMatches)||0,pairRecoveredMatches:Number(winnerScored.lineupDetail?.pairRecoveredMatches)||0
      });
    }
    if(winnerScored&&Number.isFinite(winnerOdds)&&winnerOdds>=10){"""
rep(old,new,'rescued winners capture')

rep("  qToBRegressions.sort((a,b)=>(Number(b.odds)||0)-(Number(a.odds)||0)||String(a.date).localeCompare(String(b.date))||Number(a.raceNo)-Number(b.raceNo));\n  return {variants,stats,details,highPayoutDiagnostics,qToBRegressions,positionBuckets,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};",
    "  qToBRegressions.sort((a,b)=>(Number(b.odds)||0)-(Number(a.odds)||0)||String(a.date).localeCompare(String(b.date))||Number(a.raceNo)-Number(b.raceNo));\n  bRescuedWinners.sort((a,b)=>(Number(b.odds)||0)-(Number(a.odds)||0)||String(a.date).localeCompare(String(b.date))||Number(a.raceNo)-Number(b.raceNo));\n  return {variants,stats,details,highPayoutDiagnostics,qToBRegressions,bRescuedWinners,positionBuckets,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};",
    'return rescued winners')

anchor="""  const qbDiag=(bt.qToBRegressions||[]).length?`<h3>Q→B順位悪化の的中馬診断</h3><div class=\"tablewrap\"><table><thead><tr><th>レース</th><th>勝ち馬</th><th>単勝</th><th>人気</th><th>騎手</th><th>Q点 / 順位</th><th>位置補正</th><th>相手比較補正</th><th>B点 / 順位</th><th>位置サンプル</th><th>相手比較</th><th>データ由来</th></tr></thead><tbody>${bt.qToBRegressions.map(x=>`<tr><td>${esc(x.date)} ${esc(x.venue)} ${x.raceNo}R</td><td><b>${x.num} ${esc(x.name)}</b></td><td>${x.odds==null?'-':x.odds.toFixed(1)+'倍'}</td><td>${x.pop??'-'}</td><td>${esc(x.jockey)}</td><td>${scoreText(x.scoreQ)} / ${rankText(x.rankQ)}</td><td><b>${signed(x.posAdj)}</b></td><td>${signed(x.pairAdj)}</td><td>${scoreText(x.scoreB)} / ${rankText(x.rankB)}</td><td>${x.posN}鞍</td><td>${x.pairOpponents}人 / ${x.pairMatches}回</td><td class=\"btNote\">位置 実${x.posLiveN}/復${x.posRecoveredN}<br>相手比較 実${x.pairLiveMatches}/復${x.pairRecoveredMatches}</td></tr>`).join('')}</tbody></table></div><p class=\"muted\">実際の勝ち馬をQ（騎手適性＋相手比較）が1位評価したのに、位置補正を足したBでは1位から落ちたレースだけを表示します。位置補正がQの勝ち馬選択を邪魔しているケースを直接確認する診断で、重みは変更していません。</p>`:`<h3>Q→B順位悪化の的中馬診断</h3><p class=\"muted\">該当レースはありません。現在の保存データでは、Qが1位で実際に勝った馬を位置補正がBの1位から落とした例はありません。</p>`;
  const positionOrder=['p3','p1','mid','m1','m3'];"""
replacement="""  const qbDiag=(bt.qToBRegressions||[]).length?`<h3>Q→B順位悪化の的中馬診断</h3><div class=\"tablewrap\"><table><thead><tr><th>レース</th><th>勝ち馬</th><th>単勝</th><th>人気</th><th>騎手</th><th>Q点 / 順位</th><th>位置補正</th><th>相手比較補正</th><th>B点 / 順位</th><th>位置サンプル</th><th>相手比較</th><th>データ由来</th></tr></thead><tbody>${bt.qToBRegressions.map(x=>`<tr><td>${esc(x.date)} ${esc(x.venue)} ${x.raceNo}R</td><td><b>${x.num} ${esc(x.name)}</b></td><td>${x.odds==null?'-':x.odds.toFixed(1)+'倍'}</td><td>${x.pop??'-'}</td><td>${esc(x.jockey)}</td><td>${scoreText(x.scoreQ)} / ${rankText(x.rankQ)}</td><td><b>${signed(x.posAdj)}</b></td><td>${signed(x.pairAdj)}</td><td>${scoreText(x.scoreB)} / ${rankText(x.rankB)}</td><td>${x.posN}鞍</td><td>${x.pairOpponents}人 / ${x.pairMatches}回</td><td class=\"btNote\">位置 実${x.posLiveN}/復${x.posRecoveredN}<br>相手比較 実${x.pairLiveMatches}/復${x.pairRecoveredMatches}</td></tr>`).join('')}</tbody></table></div><p class=\"muted\">実際の勝ち馬をQ（騎手適性＋相手比較）が1位評価したのに、位置補正を足したBでは1位から落ちたレースだけを表示します。位置補正がQの勝ち馬選択を邪魔しているケースを直接確認する診断で、重みは変更していません。</p>`:`<h3>Q→B順位悪化の的中馬診断</h3><p class=\"muted\">該当レースはありません。現在の保存データでは、Qが1位で実際に勝った馬を位置補正がBの1位から落とした例はありません。</p>`;
  const bqDiag=(bt.bRescuedWinners||[]).length?`<h3>Q→Bで救った勝ち馬診断</h3><div class=\"tablewrap\"><table><thead><tr><th>レース</th><th>勝ち馬</th><th>単勝</th><th>人気</th><th>騎手</th><th>Q点 / 順位</th><th>位置補正</th><th>相手比較補正</th><th>B点 / 順位</th><th>位置サンプル</th><th>相手比較</th><th>データ由来</th></tr></thead><tbody>${bt.bRescuedWinners.map(x=>`<tr><td>${esc(x.date)} ${esc(x.venue)} ${x.raceNo}R</td><td><b>${x.num} ${esc(x.name)}</b></td><td>${x.odds==null?'-':x.odds.toFixed(1)+'倍'}</td><td>${x.pop??'-'}</td><td>${esc(x.jockey)}</td><td>${scoreText(x.scoreQ)} / ${rankText(x.rankQ)}</td><td><b>${signed(x.posAdj)}</b></td><td>${signed(x.pairAdj)}</td><td>${scoreText(x.scoreB)} / ${rankText(x.rankB)}</td><td>${x.posN}鞍</td><td>${x.pairOpponents}人 / ${x.pairMatches}回</td><td class=\"btNote\">位置 実${x.posLiveN}/復${x.posRecoveredN}<br>相手比較 実${x.pairLiveMatches}/復${x.pairRecoveredMatches}</td></tr>`).join('')}</tbody></table></div><p class=\"muted\">Qでは1位ではなかった実際の勝ち馬を、位置補正を加えたBが1位まで押し上げたレースだけを表示します。上の「Q→B順位悪化」と対にして、位置補正が失った勝ち馬と救った勝ち馬を比較します。重みは変更していません。</p>`:`<h3>Q→Bで救った勝ち馬診断</h3><p class=\"muted\">該当レースはありません。現在の保存データでは、Qで1位でなかった勝ち馬をBが1位まで押し上げた例はありません。</p>`;
  const positionOrder=['p3','p1','mid','m1','m3'];"""
rep(anchor,replacement,'rescued winners render')

rep('${splitDiag}${qbDiag}${highDiag}${positionDiag}`;',
    '${splitDiag}${qbDiag}${bqDiag}${highDiag}${positionDiag}`;',
    'summary insertion')

rep("setStatus('✓ クリーン版 v4.37 起動。Q→B順位悪化の的中馬診断を追加しました。','ok');",
    "setStatus('✓ クリーン版 v4.38 起動。Q→Bで救った勝ち馬診断を追加しました。','ok');",
    'boot status')

p.write_text(s,encoding='utf-8')

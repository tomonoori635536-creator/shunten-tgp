from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.31：高配当1位の要因を分解診断'
new='クリーン版 v4.32：並び補正の中身とデータ由来を分解'
assert old in s, 'v4.31 header not found'
s=s.replace(old,new,1)

old_early="""  if(!row?.jockey||!races.length)return {adj:0,pairAdj:0,posAdj:0,pairMatches:0,pairOpponents:0,posN:0,label:'未学習',notes:[]};"""
new_early="""  if(!row?.jockey||!races.length)return {adj:0,pairAdj:0,posAdj:0,pairMatches:0,pairOpponents:0,posN:0,posLiveN:0,posRecoveredN:0,pairLiveMatches:0,pairRecoveredMatches:0,label:'未学習',notes:[]};"""
assert old_early in s, 'lineup early return not found'
s=s.replace(old_early,new_early,1)

old_self="""  const selfAll=[];
  const selfBand=[];
  for(const race of races){
    const rr=(race.rows||[]).find(x=>x.jockey===row.jockey&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    const field=(race.rows||[]).filter(x=>Number.isFinite(Number(x.rank))).length;
    const enriched={...rr,fieldSize:field};
    selfAll.push(enriched);
    if(currentBand&&gateBandByNumber(rr.num,field)===currentBand)selfBand.push(enriched);
  }"""
new_self="""  const selfAll=[];
  const selfBand=[];
  let posLiveN=0,posRecoveredN=0;
  for(const race of races){
    const rr=(race.rows||[]).find(x=>x.jockey===row.jockey&&Number.isFinite(Number(x.rank)));
    if(!rr)continue;
    const field=(race.rows||[]).filter(x=>Number.isFinite(Number(x.rank))).length;
    const enriched={...rr,fieldSize:field};
    selfAll.push(enriched);
    if(currentBand&&gateBandByNumber(rr.num,field)===currentBand){
      selfBand.push(enriched);
      if(race.recovered)posRecoveredN++;else posLiveN++;
    }
  }"""
assert old_self in s, 'lineup self block not found'
s=s.replace(old_self,new_self,1)

old_pair_start="""  let pairWeighted=0,pairWeight=0,pairMatches=0,pairOpponents=0;
  const notes=[];"""
new_pair_start="""  let pairWeighted=0,pairWeight=0,pairMatches=0,pairOpponents=0,pairLiveMatches=0,pairRecoveredMatches=0;
  const notes=[];"""
assert old_pair_start in s, 'pair accumulator not found'
s=s.replace(old_pair_start,new_pair_start,1)

old_pair_loop="""    let n=0,ahead=0;
    for(const race of races){
      const rows=(race.rows||[]).filter(x=>Number.isFinite(Number(x.rank)));
      const me=rows.find(x=>x.jockey===row.jockey),other=rows.find(x=>x.jockey===opp.jockey);
      if(!me||!other)continue;
      if(relativeSide(me.num,other.num)!==targetSide)continue;
      n++;
      if(Number(me.rank)<Number(other.rank))ahead++;
    }
    if(n<2)continue;"""
new_pair_loop="""    let n=0,ahead=0,liveN=0,recoveredN=0;
    for(const race of races){
      const rows=(race.rows||[]).filter(x=>Number.isFinite(Number(x.rank)));
      const me=rows.find(x=>x.jockey===row.jockey),other=rows.find(x=>x.jockey===opp.jockey);
      if(!me||!other)continue;
      if(relativeSide(me.num,other.num)!==targetSide)continue;
      n++;
      if(race.recovered)recoveredN++;else liveN++;
      if(Number(me.rank)<Number(other.rank))ahead++;
    }
    if(n<2)continue;"""
assert old_pair_loop in s, 'pair loop not found'
s=s.replace(old_pair_loop,new_pair_loop,1)

old_pair_count="""    pairMatches+=n;
    pairOpponents++;
    if(n>=3)notes.push(`${opp.jockey}に${targetSide} ${ahead}/${n}先着`);"""
new_pair_count="""    pairMatches+=n;
    pairLiveMatches+=liveN;
    pairRecoveredMatches+=recoveredN;
    pairOpponents++;
    if(n>=3)notes.push(`${opp.jockey}に${targetSide} ${ahead}/${n}先着（実${liveN}/復${recoveredN}）`);"""
assert old_pair_count in s, 'pair count block not found'
s=s.replace(old_pair_count,new_pair_count,1)

old_return="""  return {adj,pairAdj,posAdj,pairMatches,pairOpponents,posN:selfBand.length,label,notes};"""
new_return="""  return {adj,pairAdj,posAdj,pairMatches,pairOpponents,posN:selfBand.length,posLiveN,posRecoveredN,pairLiveMatches,pairRecoveredMatches,label,notes};"""
assert old_return in s, 'lineup return not found'
s=s.replace(old_return,new_return,1)

old_scored_decl="""      let scoreA=null,scoreB=null,scoreC=null,scoreD=null,lineupAdj=0,dayAdj=0;"""
new_scored_decl="""      let scoreA=null,scoreB=null,scoreC=null,scoreD=null,lineupAdj=0,dayAdj=0,lineupDetail=null;"""
assert old_scored_decl in s, 'scored decl not found'
s=s.replace(old_scored_decl,new_scored_decl,1)

old_lp_assign="""        const lp=jockeyLineupPattern(row,meta,cardRows);
        const dp=jockeyDayRacePattern(row,meta);
        const base=Number(q.score);
        lineupAdj=Number(lp.adj)||0;"""
new_lp_assign="""        const lp=jockeyLineupPattern(row,meta,cardRows);
        const dp=jockeyDayRacePattern(row,meta);
        const base=Number(q.score);
        lineupDetail=lp;
        lineupAdj=Number(lp.adj)||0;"""
assert old_lp_assign in s, 'lp assignment not found'
s=s.replace(old_lp_assign,new_lp_assign,1)

old_scored_return="""      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score,jockeyBase:scoreA,lineupAdj,dayAdj,horseScore:horse,
        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
new_scored_return="""      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score,jockeyBase:scoreA,lineupAdj,dayAdj,horseScore:horse,lineupDetail,
        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
assert old_scored_return in s, 'scored return not found'
s=s.replace(old_scored_return,new_scored_return,1)

old_diag_fields="""          jockeyBase:winnerScored.jockeyBase,lineupAdj:winnerScored.lineupAdj,dayAdj:winnerScored.dayAdj,horseScore:winnerScored.horseScore,
          scoreB:winnerScored.scoreB,scoreD:winnerScored.scoreD,scoreM55:winnerScored.scoreM55,"""
new_diag_fields="""          jockeyBase:winnerScored.jockeyBase,lineupAdj:winnerScored.lineupAdj,dayAdj:winnerScored.dayAdj,horseScore:winnerScored.horseScore,
          posAdj:Number(winnerScored.lineupDetail?.posAdj)||0,pairAdj:Number(winnerScored.lineupDetail?.pairAdj)||0,
          posN:Number(winnerScored.lineupDetail?.posN)||0,posLiveN:Number(winnerScored.lineupDetail?.posLiveN)||0,posRecoveredN:Number(winnerScored.lineupDetail?.posRecoveredN)||0,
          pairMatches:Number(winnerScored.lineupDetail?.pairMatches)||0,pairOpponents:Number(winnerScored.lineupDetail?.pairOpponents)||0,
          pairLiveMatches:Number(winnerScored.lineupDetail?.pairLiveMatches)||0,pairRecoveredMatches:Number(winnerScored.lineupDetail?.pairRecoveredMatches)||0,
          scoreB:winnerScored.scoreB,scoreD:winnerScored.scoreD,scoreM55:winnerScored.scoreM55,"""
assert old_diag_fields in s, 'high payout diag fields not found'
s=s.replace(old_diag_fields,new_diag_fields,1)

old_highdiag='''  const highDiag=(bt.highPayoutDiagnostics||[]).length?`<h3>高配当1位の要因診断</h3><div class="tablewrap"><table><thead><tr><th>レース</th><th>勝ち馬</th><th>単勝</th><th>人気</th><th>騎手</th><th>A騎手適性</th><th>並び補正</th><th>B点 / 順位</th><th>当日R補正</th><th>D点 / 順位</th><th>H馬能力 / 順位</th><th>55:45 / 順位</th><th>なぜ拾えたか</th></tr></thead><tbody>${bt.highPayoutDiagnostics.map(x=>`<tr><td>${esc(x.date)} ${esc(x.venue)} ${x.raceNo}R</td><td><b>${x.num} ${esc(x.name)}</b></td><td><b>${x.odds.toFixed(1)}倍</b></td><td>${x.pop??'-'}</td><td>${esc(x.jockey)}</td><td>${scoreText(x.jockeyBase)} / ${rankText(x.rankA)}</td><td>${signed(x.lineupAdj)}</td><td>${scoreText(x.scoreB)} / ${rankText(x.rankB)}</td><td>${signed(x.dayAdj)}</td><td>${scoreText(x.scoreD)} / ${rankText(x.rankD)}</td><td>${scoreText(x.horseScore)} / ${rankText(x.rankH)}</td><td>${scoreText(x.scoreM55)} / ${rankText(x.rankM55)}</td><td class="btNote">${esc(highReason(x))}</td></tr>`).join('')}</tbody></table></div><p class="muted">10倍以上の勝ち馬のうち、B（騎手適性＋並び）またはD（B＋当日R）が1位評価できたレースだけを表示します。順位変化を見ることで、高配当を拾った主因が並び・当日R・元の騎手適性・馬能力のどこにあったか確認できます。</p>`:`<h3>高配当1位の要因診断</h3><p class="muted">10倍以上の勝ち馬をBまたはDで1位評価したレースはまだありません。</p>`;'''
new_highdiag='''  const highDiag=(bt.highPayoutDiagnostics||[]).length?`<h3>高配当1位の要因診断</h3><div class="tablewrap"><table><thead><tr><th>レース</th><th>勝ち馬</th><th>単勝</th><th>人気</th><th>騎手</th><th>A騎手適性</th><th>並び合計</th><th>位置補正</th><th>相手比較補正</th><th>比較相手</th><th>過去比較</th><th>データ由来</th><th>B点 / 順位</th><th>当日R補正</th><th>D点 / 順位</th><th>H馬能力 / 順位</th><th>55:45 / 順位</th><th>なぜ拾えたか</th></tr></thead><tbody>${bt.highPayoutDiagnostics.map(x=>`<tr><td>${esc(x.date)} ${esc(x.venue)} ${x.raceNo}R</td><td><b>${x.num} ${esc(x.name)}</b></td><td><b>${x.odds.toFixed(1)}倍</b></td><td>${x.pop??'-'}</td><td>${esc(x.jockey)}</td><td>${scoreText(x.jockeyBase)} / ${rankText(x.rankA)}</td><td><b>${signed(x.lineupAdj)}</b></td><td>${signed(x.posAdj)}</td><td>${signed(x.pairAdj)}</td><td>${x.pairOpponents}人</td><td>${x.pairMatches}回</td><td class="btNote">位置 ${x.posN}鞍（実${x.posLiveN}/復${x.posRecoveredN}）<br>相手比較 ${x.pairMatches}回（実${x.pairLiveMatches}/復${x.pairRecoveredMatches}）</td><td>${scoreText(x.scoreB)} / ${rankText(x.rankB)}</td><td>${signed(x.dayAdj)}</td><td>${scoreText(x.scoreD)} / ${rankText(x.rankD)}</td><td>${scoreText(x.horseScore)} / ${rankText(x.rankH)}</td><td>${scoreText(x.scoreM55)} / ${rankText(x.rankM55)}</td><td class="btNote">${esc(highReason(x))}</td></tr>`).join('')}</tbody></table></div><p class="muted">並び合計は「位置補正＋相手比較補正」（最終的に±8点で制限）です。実=保存済みの実結果レース、復=過去馬柱から安全復元した並び学習データ。相手比較回数は、今回一緒に乗る騎手との過去の内外関係が一致した比較の合計です。重み自体は変更していません。</p>`:`<h3>高配当1位の要因診断</h3><p class="muted">10倍以上の勝ち馬をBまたはDで1位評価したレースはまだありません。</p>`;'''
assert old_highdiag in s, 'highDiag render not found'
s=s.replace(old_highdiag,new_highdiag,1)

old_lineup_text="""      const lineupText=lp.notes.length?lp.notes.slice(0,3).join(' / '):`位置 ${lp.posN}鞍 / 相手比較 ${lp.pairMatches}回`;"""
new_lineup_text="""      const sourceLine=`位置 ${lp.posN}鞍（実${lp.posLiveN||0}/復${lp.posRecoveredN||0}） / 相手${lp.pairOpponents||0}人・比較${lp.pairMatches}回（実${lp.pairLiveMatches||0}/復${lp.pairRecoveredMatches||0}）`;
      const lineupText=lp.notes.length?`${lp.notes.slice(0,3).join(' / ')} / ${sourceLine}`:sourceLine;"""
assert old_lineup_text in s, 'preview lineup text not found'
s=s.replace(old_lineup_text,new_lineup_text,1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.32 起動。並び補正を位置・相手比較・実結果/安全復元まで分解表示します。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

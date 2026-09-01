from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.32：並び補正の中身とデータ由来を分解'
new='クリーン版 v4.33：位置補正の強さ別に成績を検証'
assert old in s, 'v4.32 header not found'
s=s.replace(old,new,1)

old_stats="""  const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0,roiN:0,stake:0,returnYen:0,winOdds:[],oddsBands:{low:{n:0,stake:0,ret:0,wins:0},mid:{n:0,stake:0,ret:0,wins:0},high:{n:0,stake:0,ret:0,wins:0},long:{n:0,stake:0,ret:0,wins:0}}}]));
  const details=[];
  const highPayoutDiagnostics=[];"""
new_stats="""  const stats=Object.fromEntries(variants.map(v=>[v.key,{name:v.name,n:0,top1Win:0,top1Place:0,winnerTop3:0,exactTop3:0,roiN:0,stake:0,returnYen:0,winOdds:[],oddsBands:{low:{n:0,stake:0,ret:0,wins:0},mid:{n:0,stake:0,ret:0,wins:0},high:{n:0,stake:0,ret:0,wins:0},long:{n:0,stake:0,ret:0,wins:0}}}]));
  const positionBuckets={
    p3:{label:'+3以上',n:0,wins:0,places:0,adjSum:0,oddsN:0,oddsSum:0,stake:0,ret:0},
    p1:{label:'+1〜+3',n:0,wins:0,places:0,adjSum:0,oddsN:0,oddsSum:0,stake:0,ret:0},
    mid:{label:'-1〜+1',n:0,wins:0,places:0,adjSum:0,oddsN:0,oddsSum:0,stake:0,ret:0},
    m1:{label:'-3〜-1',n:0,wins:0,places:0,adjSum:0,oddsN:0,oddsSum:0,stake:0,ret:0},
    m3:{label:'-3以下',n:0,wins:0,places:0,adjSum:0,oddsN:0,oddsSum:0,stake:0,ret:0}
  };
  const positionBucketKey=(adj)=>adj>=3?'p3':adj>=1?'p1':adj>-1?'mid':adj>-3?'m1':'m3';
  const details=[];
  const highPayoutDiagnostics=[];"""
assert old_stats in s, 'stats block not found'
s=s.replace(old_stats,new_stats,1)

anchor="""    const actualTop3=new Set(resultRows.filter(x=>Number(x.rank)>=1&&Number(x.rank)<=3).map(x=>Number(x.num)));
    const rankOf=(key,num)=>{const arr=backtestRankRows(scored,key);const i=arr.findIndex(x=>Number(x.row?.num)===Number(num));return i>=0?i+1:null};"""
insert="""    const actualTop3=new Set(resultRows.filter(x=>Number(x.rank)>=1&&Number(x.rank)<=3).map(x=>Number(x.num)));
    const bRankedForPosition=backtestRankRows(scored,'scoreB');
    if(bRankedForPosition.length>=3){
      const bTop=bRankedForPosition[0];
      const bResult=resultByNum.get(Number(bTop.row?.num));
      const posAdj=Number(bTop.lineupDetail?.posAdj);
      if(Number.isFinite(posAdj)&&bResult){
        const pb=positionBuckets[positionBucketKey(posAdj)];
        pb.n++;pb.adjSum+=posAdj;
        const rank=Number(bResult.rank);
        if(rank===1)pb.wins++;
        if(rank<=3)pb.places++;
        const odds=Number(bResult.odds);
        if(Number.isFinite(odds)&&odds>0){
          pb.oddsN++;pb.oddsSum+=odds;pb.stake+=100;
          if(rank===1)pb.ret+=Math.round(odds*100);
        }
      }
    }
    const rankOf=(key,num)=>{const arr=backtestRankRows(scored,key);const i=arr.findIndex(x=>Number(x.row?.num)===Number(num));return i>=0?i+1:null};"""
assert anchor in s, 'actualTop3 anchor not found'
s=s.replace(anchor,insert,1)

old_return="""  return {variants,stats,details,highPayoutDiagnostics,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};"""
new_return="""  return {variants,stats,details,highPayoutDiagnostics,positionBuckets,skipped,totalResults:(state.races||[]).length,totalCards:(state.raceCards||[]).length};"""
assert old_return in s, 'backtest return not found'
s=s.replace(old_return,new_return,1)

summary_anchor="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th><th>確定単勝回収率</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}${roiCell(v)}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">単勝回収率は各方式の1位評価馬へ100円固定投資し、結果ページに保存された確定単勝オッズで計算します。オッズが保存されていない選択は回収率対象から除外します。これはモデル比較用の事後検証で、実戦時に同じオッズで買えたことを意味しません。50:50・55:45・60:40・70:30・80:20は引き続き暫定比較です。</p><h3>回収率の安定性診断</h3><div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>単勝的中</th><th>的中平均単勝</th><th>最大単勝</th><th>最大配当1頭除外ROI</th><th>1.0〜2.9倍</th><th>3.0〜4.9倍</th><th>5.0〜9.9倍</th><th>10倍以上</th></tr></thead><tbody>${bt.variants.map(roiDiagnostic).join('')}</tbody></table></div><p class=\"muted\">最大配当1頭除外ROIは、その最高配当の的中レース1件を投資100円ごと除いて再計算します。各オッズ帯は「的中数/購入数」も併記します。1頭の大穴だけで全体回収率が上がっていないかを見るための診断です。</p>${highDiag}`;"""
assert summary_anchor in s, 'summary assignment not found'

position_def="""  const positionOrder=['p3','p1','mid','m1','m3'];
  const positionRow=(key)=>{
    const x=bt.positionBuckets?.[key];
    if(!x||!x.n)return `<tr><td><b>${esc(x?.label||key)}</b></td><td>0</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>`;
    const avgAdj=x.adjSum/x.n;
    const avgOdds=x.oddsN?x.oddsSum/x.oddsN:null;
    const roi=x.stake?100*x.ret/x.stake:null;
    return `<tr><td><b>${esc(x.label)}</b></td><td>${x.n}</td><td>${signed(avgAdj)}</td><td>${backtestPct(x.wins,x.n)} <span class=\"muted\">(${x.wins}/${x.n})</span></td><td>${backtestPct(x.places,x.n)} <span class=\"muted\">(${x.places}/${x.n})</span></td><td>${roi==null?'-':roi.toFixed(1)+'%'}<div class=\"muted\">ROI対象 ${x.oddsN}R / 投資${x.stake.toLocaleString()}円 / 払戻${x.ret.toLocaleString()}円</div></td><td>${avgOdds==null?'-':avgOdds.toFixed(2)+'倍'}</td></tr>`;
  };
  const positionDiag=`<h3>位置補正の強さ別診断（B 1位評価馬）</h3><div class=\"tablewrap\"><table><thead><tr><th>位置補正帯</th><th>該当R</th><th>平均位置補正</th><th>1着率</th><th>3着内率</th><th>単勝回収率</th><th>平均選択単勝</th></tr></thead><tbody>${positionOrder.map(positionRow).join('')}</tbody></table></div><p class=\"muted\">各レースでB（騎手適性＋並び）が1位評価した馬を、その馬の「位置補正」だけで5区分に分けた診断です。+3以上が本当に好成績か、位置補正が強すぎないかを確認します。境界は +3以上 / +1以上3未満 / -1より大きく+1未満 / -3より大きく-1以下 / -3以下 として重複なく集計します。重みは変更していません。</p>`;
"""
s=s.replace(summary_anchor,position_def+summary_anchor.replace("</p>${highDiag}`;","</p>${highDiag}${positionDiag}`;"),1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.33 起動。Bの1位評価馬を位置補正の強さ別に検証できます。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

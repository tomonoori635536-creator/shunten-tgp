from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.33：位置補正の強さ別に成績を検証'
new='クリーン版 v4.34：位置補正と相手比較を分離バックテスト'
assert old in s, 'v4.33 header not found'
s=s.replace(old,new,1)

old_help='A=騎手適性 / B=＋並び / C=＋当日R / D=＋並び＋当日R / H=馬能力 / 仮=馬:騎手 50:50 / 55:45 / 60:40 / 70:30 / 80:20'
new_help='A=騎手適性 / P=＋位置だけ / Q=＋相手比較だけ / B=＋位置＋相手比較 / C=＋当日R / D=＋並び＋当日R / H=馬能力 / 仮=馬:騎手 50:50 / 55:45 / 60:40 / 70:30 / 80:20'
assert old_help in s, 'backtest help not found'
s=s.replace(old_help,new_help,1)

old_variants="""  const variants=[
    {key:'a',name:'A 騎手適性のみ',score:'scoreA'},
    {key:'b',name:'B ＋並び（現在採用）',score:'scoreB'},
    {key:'c',name:'C ＋当日R',score:'scoreC'},"""
new_variants="""  const variants=[
    {key:'a',name:'A 騎手適性のみ',score:'scoreA'},
    {key:'p',name:'P ＋位置だけ',score:'scoreP'},
    {key:'q',name:'Q ＋相手比較だけ',score:'scoreQ'},
    {key:'b',name:'B ＋位置＋相手比較（現在採用）',score:'scoreB'},
    {key:'c',name:'C ＋当日R',score:'scoreC'},"""
assert old_variants in s, 'variants block not found'
s=s.replace(old_variants,new_variants,1)

old_decl="""      let scoreA=null,scoreB=null,scoreC=null,scoreD=null,lineupAdj=0,dayAdj=0,lineupDetail=null;"""
new_decl="""      let scoreA=null,scoreP=null,scoreQ=null,scoreB=null,scoreC=null,scoreD=null,lineupAdj=0,dayAdj=0,lineupDetail=null;"""
assert old_decl in s, 'score declaration not found'
s=s.replace(old_decl,new_decl,1)

old_scores="""        scoreA=base;
        scoreB=clampValue(base+lineupAdj,0,100);
        scoreC=clampValue(base+dayAdj,0,100);
        scoreD=clampValue(base+lineupAdj+dayAdj,0,100);"""
new_scores="""        scoreA=base;
        scoreP=clampValue(base+(Number(lp.posAdj)||0),0,100);
        scoreQ=clampValue(base+(Number(lp.pairAdj)||0),0,100);
        scoreB=clampValue(base+lineupAdj,0,100);
        scoreC=clampValue(base+dayAdj,0,100);
        scoreD=clampValue(base+lineupAdj+dayAdj,0,100);"""
assert old_scores in s, 'score calculation block not found'
s=s.replace(old_scores,new_scores,1)

old_return="""      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score,jockeyBase:scoreA,lineupAdj,dayAdj,horseScore:horse,lineupDetail,
        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
new_return="""      return {row,scoreA,scoreP,scoreQ,scoreB,scoreC,scoreD,scoreH:h.score,jockeyBase:scoreA,lineupAdj,dayAdj,horseScore:horse,lineupDetail,
        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
assert old_return in s, 'scored return not found'
s=s.replace(old_return,new_return,1)

# Add a dedicated compact comparison table before the position-bucket diagnostic.
anchor="""  const positionOrder=['p3','p1','mid','m1','m3'];"""
insert="""  const splitKeys=['a','p','q','b'];
  const splitRow=(key)=>{
    const v=bt.variants.find(x=>x.key===key),st=bt.stats[key];
    if(!v||!st||!st.n)return '';
    const roi=st.stake?100*st.returnYen/st.stake:null;
    const profit=st.returnYen-st.stake;
    return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td><td>${backtestPct(st.top1Win,st.n)} <span class=\"muted\">(${st.top1Win}/${st.n})</span></td><td>${backtestPct(st.top1Place,st.n)} <span class=\"muted\">(${st.top1Place}/${st.n})</span></td><td>${backtestPct(st.winnerTop3,st.n)} <span class=\"muted\">(${st.winnerTop3}/${st.n})</span></td><td>${roi==null?'-':roi.toFixed(1)+'%'}<div class=\"muted\">収支${profit>=0?'+':''}${profit.toLocaleString()}円</div></td></tr>`;
  };
  const splitDiag=`<h3>位置 vs 相手比較 分離診断</h3><div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位→1着</th><th>1位→3着内</th><th>勝ち馬TOP3</th><th>単勝回収率</th></tr></thead><tbody>${splitKeys.map(splitRow).join('')}</tbody></table></div><p class=\"muted\">A=騎手適性だけ、P=位置補正だけ追加、Q=相手比較補正だけ追加、B=位置＋相手比較。すべて同じ時系列条件で比較します。ここでは重みを変更せず、どの要素が改善に寄与しているかだけを確認します。</p>`;
  const positionOrder=['p3','p1','mid','m1','m3'];"""
assert anchor in s, 'positionOrder anchor not found'
s=s.replace(anchor,insert,1)

old_summary_end="""</p>${highDiag}${positionDiag}`;"""
new_summary_end="""</p>${splitDiag}${highDiag}${positionDiag}`;"""
assert old_summary_end in s, 'summary tail not found'
s=s.replace(old_summary_end,new_summary_end,1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.34 起動。位置補正と相手比較補正を分離して時系列検証できます。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

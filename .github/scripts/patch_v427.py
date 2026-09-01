from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.26：馬能力スコア土台＋時系列検証'
new='クリーン版 v4.27：馬×騎手の比率を仮比較'
assert old in s
s=s.replace(old,new,1)

old='保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で騎手4方式と馬能力のみを比較します。馬と騎手はまだ混ぜません。取消・除外など結果に存在しない馬は評価対象から外します。'
new='保存済みの「出馬表→結果」を使って、対象レースより後の結果を見ない真の時系列で比較します。馬能力Hと現在採用中の騎手Bを50:50〜80:20で仮合成します。ここで最良でも正式採用にはせず、データ増加後に再検証します。取消・除外など結果に存在しない馬は評価対象から外します。'
assert old in s
s=s.replace(old,new,1)

old='A=騎手適性 / B=＋並び / C=＋当日R / D=＋並び＋当日R / H=馬能力のみ（未混合）'
new='A=騎手適性 / B=＋並び / C=＋当日R / D=＋並び＋当日R / H=馬能力 / 仮=馬:騎手 50:50〜80:20'
assert old in s
s=s.replace(old,new,1)

old="""    {key:'h',name:'H 馬能力のみ',score:'scoreH'}
  ];"""
new="""    {key:'h',name:'H 馬能力のみ',score:'scoreH'},
    {key:'m50',name:'仮 50:50 馬50＋騎手50',score:'scoreM50'},
    {key:'m60',name:'仮 60:40 馬60＋騎手40',score:'scoreM60'},
    {key:'m70',name:'仮 70:30 馬70＋騎手30',score:'scoreM70'},
    {key:'m80',name:'仮 80:20 馬80＋騎手20',score:'scoreM80'}
  ];"""
assert old in s
s=s.replace(old,new,1)

old="""      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score};"""
new="""      const horse=Number.isFinite(Number(h.score))?Number(h.score):null;
      const jockey=Number.isFinite(Number(scoreB))?Number(scoreB):null;
      const blend=(hw)=>horse==null||jockey==null?null:clampValue(horse*hw+jockey*(1-hw),0,100);
      return {row,scoreA,scoreB,scoreC,scoreD,scoreH:h.score,
        scoreM50:blend(0.50),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
assert old in s
s=s.replace(old,new,1)

old="""  $('backtestStatus').textContent=`✓ ${bt.details.length}レースを時系列評価しました。後の開催日・同日後続Rは予測に使っていません。馬能力は${horseN}レース評価。除外 ${bt.skipped}レース。`;"""
new="""  const blendN=bt.stats.m50?.n||0;
  $('backtestStatus').textContent=`✓ ${bt.details.length}レースを時系列評価しました。未来データは不使用。馬能力${horseN}R、仮合成${blendN}Rを評価。比率はまだ仮です。除外 ${bt.skipped}レース。`;"""
assert old in s
s=s.replace(old,new,1)

old="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">Hは馬能力だけの独立テストです。まだ騎手とは混ぜません。Hの評価Rが少ない場合は、馬の過去走が十分保存されていないレースがあるためです。</p>`;"""
new="""  $('backtestSummary').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>方式</th><th>評価R</th><th>1位評価の1着率</th><th>1位評価の3着内率</th><th>勝ち馬TOP3率</th><th>実着1〜3が評価TOP3内</th></tr></thead><tbody>${bt.variants.map(v=>{const st=bt.stats[v.key];return `<tr><td><b>${esc(v.name)}</b></td><td>${st.n}</td>${cell(v,'top1Win')}${cell(v,'top1Place')}${cell(v,'winnerTop3')}${cell(v,'exactTop3')}</tr>`}).join('')}</tbody></table></div><p class=\"muted\">50:50〜80:20は暫定比較です。今回の最高値を固定せず、100R・150Rなどデータ増加時に再検証します。B=騎手適性＋並び、H=馬能力のみです。</p>`;"""
assert old in s
s=s.replace(old,new,1)

old="""  $('backtestDetail').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>日付</th><th>競馬場</th><th>R</th><th>勝ち馬</th><th>A 1位</th><th>B 1位</th><th>C 1位</th><th>D 1位</th><th>H 馬1位</th></tr></thead><tbody>${bt.details.map(d=>`<tr><td>${esc(d.date)}</td><td>${esc(d.venue)}</td><td>${d.raceNo}R</td><td><b>${d.winnerNum} ${esc(d.winnerName)}</b></td>${bt.variants.map(v=>{const x=d.tops[v.key];if(!x)return '<td class=\"muted\">--</td>';return `<td class=\"${x.hit?'hit':'miss'}\">${x.hit?'✓':'・'} ${x.num} ${esc(x.name)}</td>`}).join('')}</tr>`).join('')}</tbody></table></div>`;"""
new="""  $('backtestDetail').innerHTML=`<div class=\"tablewrap\"><table><thead><tr><th>日付</th><th>競馬場</th><th>R</th><th>勝ち馬</th>${bt.variants.map(v=>`<th>${esc(v.name)} 1位</th>`).join('')}</tr></thead><tbody>${bt.details.map(d=>`<tr><td>${esc(d.date)}</td><td>${esc(d.venue)}</td><td>${d.raceNo}R</td><td><b>${d.winnerNum} ${esc(d.winnerName)}</b></td>${bt.variants.map(v=>{const x=d.tops[v.key];if(!x)return '<td class=\"muted\">--</td>';return `<td class=\"${x.hit?'hit':'miss'}\">${x.hit?'✓':'・'} ${x.num} ${esc(x.name)}</td>`}).join('')}</tr>`).join('')}</tbody></table></div>`;"""
assert old in s
s=s.replace(old,new,1)

# Keep live preview unblended for now and make that explicit.
old='馬能力と騎手はまだ混ぜません。'
new='馬能力と騎手の合成はバックテスト上の仮比較だけで、実戦表示の最終点にはまだ採用しません。'
assert old in s
s=s.replace(old,new,1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.27 起動。馬×騎手比率はバックテスト上の仮比較のみです。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

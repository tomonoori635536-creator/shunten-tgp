from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="<p>クリーン版 v4.40：馬能力は今回貼付の馬柱だけで評価</p>"
new="<p>クリーン版 v4.41：貼付5走を読取時に固定し馬能力へ使用</p>"
assert old in s, 'header anchor missing'
s=s.replace(old,new,1)

old="function parseAll(raw){const lines=linesOf(raw);if(!lines.length)return {error:'入力が空です'};const meta=parseMeta(lines),markdownRows=parseMarkdownResultRows(raw),resultRows=markdownRows.length>=3?markdownRows:parseResultRows(lines);if(resultRows.length>=3)return {meta,mode:'result',rows:resultRows,lines,debug:{result:resultRows.length,markdown:markdownRows.length,past:0,card:0}};const pastRows=parsePastCard(lines);if(pastRows.length>=3)return {meta,mode:'card',rows:pastRows,lines,debug:{result:resultRows.length,markdown:markdownRows.length,past:pastRows.length,card:0}};const cardRows=parseRaceCard(lines);const mode=cardRows.length?'card':'unknown';return {meta,mode,rows:cardRows,lines,debug:{result:resultRows.length,markdown:markdownRows.length,past:pastRows.length,card:cardRows.length}};}"
new="""function parseAll(raw){
  const lines=linesOf(raw);
  if(!lines.length)return {error:'入力が空です'};
  const meta=parseMeta(lines),markdownRows=parseMarkdownResultRows(raw),resultRows=markdownRows.length>=3?markdownRows:parseResultRows(lines);
  if(resultRows.length>=3)return {meta,mode:'result',rows:resultRows,lines,pastRuns:[],debug:{result:resultRows.length,markdown:markdownRows.length,past:0,card:0}};
  const pastRows=parsePastCard(lines);
  if(pastRows.length>=3){
    const pastRuns=extractHorsePastRuns(lines,pastRows);
    return {meta,mode:'card',rows:pastRows,lines,pastRuns,debug:{result:resultRows.length,markdown:markdownRows.length,past:pastRows.length,card:0,horsePast:pastRuns.length}};
  }
  const cardRows=parseRaceCard(lines);
  const mode=cardRows.length?'card':'unknown';
  const pastRuns=mode==='card'?extractHorsePastRuns(lines,cardRows):[];
  return {meta,mode,rows:cardRows,lines,pastRuns,debug:{result:resultRows.length,markdown:markdownRows.length,past:pastRows.length,card:cardRows.length,horsePast:pastRuns.length}};
}"""
assert old in s, 'parseAll anchor missing'
s=s.replace(old,new,1)

old="const scored=cardRows.map(row=>{\n      const h=horseAbility(row,meta);"
new="const scored=cardRows.map(row=>{\n      const h=horseAbility(row,meta,Array.isArray(card.pastRuns)&&card.pastRuns.length?card.pastRuns:null);"
assert old in s, 'backtest horse anchor missing'
s=s.replace(old,new,1)

old="const obj={meta:m,rows:parsed.rows,savedAt:new Date().toISOString()};const idx=state.raceCards.findIndex"
new="const obj={meta:m,rows:parsed.rows,pastRuns:Array.isArray(parsed.pastRuns)?parsed.pastRuns:[],savedAt:new Date().toISOString()};const idx=state.raceCards.findIndex"
assert old in s, 'card object anchor missing'
s=s.replace(old,new,1)

old="const past=extractHorsePastRuns(parsed.lines||[],parsed.rows||[]);const before=(state.horseHistory||[]).length;"
new="const past=Array.isArray(parsed.pastRuns)?parsed.pastRuns:extractHorsePastRuns(parsed.lines||[],parsed.rows||[]);parsed.pastRuns=past;const before=(state.horseHistory||[]).length;"
assert old in s, 'save past anchor missing'
s=s.replace(old,new,1)

old="setStatus('✓ クリーン版 v4.39 起動。騎手クラス別と直前騎乗→次騎乗パターンを追加しました。','ok')"
new="setStatus('✓ クリーン版 v4.41 起動。今回貼った馬柱5走を読取時に固定して馬能力へ使います。','ok')"
assert old in s, 'boot anchor missing'
s=s.replace(old,new,1)

assert 'p.pastRuns' in s
assert 'pastRuns:Array.isArray(parsed.pastRuns)?parsed.pastRuns:[]' in s
assert "horseAbility(row,meta,Array.isArray(card.pastRuns)&&card.pastRuns.length?card.pastRuns:null)" in s

p.write_text(s,encoding='utf-8')

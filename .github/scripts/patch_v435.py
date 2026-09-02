from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')

old_header = '<p>クリーン版 v4.34：位置補正と相手比較を分離バックテスト</p>'
new_header = '<p>クリーン版 v4.35：v4.34分離BT＋netkeiba結果横表対応</p>'
assert old_header in s, 'v4.34 header not found'
s = s.replace(old_header, new_header, 1)

needle = "function looksJockey(s){return s&&!/^\\d/.test(s)&&!/(映像を見る|着差|タイム|人気|馬体重)/.test(s)}\nfunction parseResultRows(lines){"
insert = r'''function looksJockey(s){return s&&!/^\d/.test(s)&&!/(映像を見る|着差|タイム|人気|馬体重)/.test(s)}
function parseMarkdownResultRows(raw){
  const out=[];
  const rawLines=String(raw||'').replace(/\r/g,'').split('\n');
  for(const rawLine of rawLines){
    const line=rawLine.trim();
    if(/^##\s*払戻/.test(line)) break;
    if(!line.startsWith('|')) continue;
    const cells=line.split('|').slice(1,-1).map(cleanPasteToken);
    if(cells.length<11) continue;
    const rank=Number(cells[0]),frame=Number(cells[1]),num=Number(cells[2]);
    const name=cells[3],sexAge=cells[4],burden=cells[5],jockey=cells[6],time=cells[7];
    const pop=Number(cells[9]),odds=Number(cells[10]);
    if(!Number.isInteger(rank)||rank<1||rank>30) continue;
    if(!Number.isInteger(frame)||frame<1||frame>8) continue;
    if(!Number.isInteger(num)||num<1||num>30) continue;
    if(!name||!isSexAge(sexAge)) continue;
    if(!/^\d{2,3}(?:\.\d)?$/.test(burden)||!looksJockey(jockey)) continue;
    if(!/^\d+:\d{2}(?:\.\d)?$/.test(time)) continue;
    out.push({rank,frame,num,name,jockey,pop:Number.isInteger(pop)&&pop>=1?pop:null,odds:Number.isFinite(odds)&&odds>0?odds:null,time});
  }
  return dedupe(out,r=>`${r.rank}|${r.num}|${r.name}`);
}
function parseResultRows(lines){'''
assert needle in s, 'result parser insertion point not found'
s = s.replace(needle, insert, 1)

old_parse_all = "function parseAll(raw){const lines=linesOf(raw);if(!lines.length)return {error:'入力が空です'};const meta=parseMeta(lines),resultRows=parseResultRows(lines);if(resultRows.length>=3)return {meta,mode:'result',rows:resultRows,lines,debug:{result:resultRows.length,past:0,card:0}};const pastRows=parsePastCard(lines);if(pastRows.length>=3)return {meta,mode:'card',rows:pastRows,lines,debug:{result:resultRows.length,past:pastRows.length,card:0}};const cardRows=parseRaceCard(lines);const mode=cardRows.length?'card':'unknown';return {meta,mode,rows:cardRows,lines,debug:{result:resultRows.length,past:pastRows.length,card:cardRows.length}};}"
new_parse_all = "function parseAll(raw){const lines=linesOf(raw);if(!lines.length)return {error:'入力が空です'};const meta=parseMeta(lines),markdownRows=parseMarkdownResultRows(raw),resultRows=markdownRows.length>=3?markdownRows:parseResultRows(lines);if(resultRows.length>=3)return {meta,mode:'result',rows:resultRows,lines,debug:{result:resultRows.length,markdown:markdownRows.length,past:0,card:0}};const pastRows=parsePastCard(lines);if(pastRows.length>=3)return {meta,mode:'card',rows:pastRows,lines,debug:{result:resultRows.length,markdown:markdownRows.length,past:pastRows.length,card:0}};const cardRows=parseRaceCard(lines);const mode=cardRows.length?'card':'unknown';return {meta,mode,rows:cardRows,lines,debug:{result:resultRows.length,markdown:markdownRows.length,past:pastRows.length,card:cardRows.length}};}"
assert old_parse_all in s, 'parseAll target not found'
s = s.replace(old_parse_all, new_parse_all, 1)

assert 'function parseMarkdownResultRows(raw)' in s
assert 'markdownRows=parseMarkdownResultRows(raw)' in s
assert 'クリーン版 v4.35' in s
path.write_text(s, encoding='utf-8')

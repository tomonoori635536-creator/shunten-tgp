from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

start=s.index('function extractHorsePastRuns(lines,cardRows){')
end=s.index('\nfunction scoreRows(rows){',start)
new_func=r'''function extractHorsePastRuns(lines,cardRows){
  const out=[];
  const names=[...new Set((cardRows||[]).map(r=>String(r.name||'').trim()).filter(Boolean))];
  if(!names.length)return out;
  const nameSet=new Set(names);
  const dateRe=new RegExp(`^(20\\d{2})[./](\\d{1,2})[./](\\d{1,2})\\s+(${venues.join('|')})(\\d{1,2})$`);
  // netkeiba can show turf courses as 芝2400(外) / 芝1600(内).
  const courseRe=/^(芝|ダ|障)(\d{3,4})(?:\((?:外|内)\))?\s+([0-9]+:[0-9]{2}(?:\.[0-9])?|[0-9]+(?:\.[0-9])?)\s+(良|稍重|稍|重|不良|稍|不)$/;
  const fieldRe=/^(\d+)頭\s+(\d+)番\s+(\d+)人\s+(.+?)\s+(\d{2,3}(?:\.\d)?)$/;

  // Find only the horse's own profile header. Do not switch horses when a current
  // runner merely appears as an opponent at the end of another horse's past race.
  const anchors=[];
  for(let i=0;i<lines.length;i++){
    const line=String(lines[i]||'').trim();
    if(!nameSet.has(line))continue;
    const near=lines.slice(i+1,Math.min(lines.length,i+16)).map(x=>String(x||'').trim());
    const joined=near.join(' ');
    const hasProfile=/(?:牡|牝|セ)\d/.test(joined)&&/\(\d{1,2}人気\)/.test(joined)&&near.some(x=>dateRe.test(x));
    if(hasProfile)anchors.push({index:i,name:line});
  }

  for(let a=0;a<anchors.length;a++){
    const start=anchors[a].index;
    const stop=a+1<anchors.length?anchors[a+1].index:lines.length;
    const horseName=anchors[a].name;
    for(let i=start;i<stop;i++){
      const line=String(lines[i]||'').trim();
      const dm=line.match(dateRe);
      if(!dm||i+3>=stop)continue;
      const cm=String(lines[i+2]||'').trim().match(courseRe);
      const fm=String(lines[i+3]||'').trim().match(fieldRe);
      if(!cm||!fm)continue;
      let going=cm[4];if(going==='稍')going='稍重';if(going==='不')going='不良';
      out.push({
        name:horseName,
        date:`${dm[1]}/${String(dm[2]).padStart(2,'0')}/${String(dm[3]).padStart(2,'0')}`,
        venue:dm[4],raceNo:null,raceName:String(lines[i+1]||'').trim(),className:String(lines[i+1]||'').trim(),
        surface:cm[1],distance:Number(cm[2]),time:cm[3],going,
        rank:Number(dm[5]),fieldSize:Number(fm[1]),num:Number(fm[2]),pop:Number(fm[3]),jockey:fm[4],burden:Number(fm[5]),
        source:'pasted_horse_card'
      });
    }
  }
  const seen=new Set();
  return out.filter(r=>{const k=horseHistoryKey(r);if(!k||seen.has(k))return false;seen.add(k);return true});
}'''
s=s[:start]+new_func+s[end:]
s=s.replace('クリーン版 v4.41：貼付5走を読取時に固定し馬能力へ使用','クリーン版 v4.42：馬柱の馬別区切り＋外/内コース読取を修正')
s=s.replace("✓ クリーン版 v4.39 起動。騎手クラス別と直前騎乗→次騎乗パターンを追加しました。","✓ クリーン版 v4.42 起動。馬柱の馬別区切りと外/内コース読取を修正しました。")

assert "line.startsWith(`${n}(`)" not in s
assert "(?:\\((?:外|内)\\))?" in s
assert 'クリーン版 v4.42' in s
p.write_text(s,encoding='utf-8')

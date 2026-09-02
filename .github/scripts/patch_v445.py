from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace(
"const dateRe=new RegExp(`^(20\\\\d{2})[./](\\\\d{1,2})[./](\\\\d{1,2})\\\\s+(${venues.join('|')})(\\\\d{1,2})$`);",
"const dateRe=new RegExp(`^(20\\\\d{2})[./](\\\\d{1,2})[./](\\\\d{1,2})\\\\s+(${venues.join('|')})(\\\\d{1,2}|取|取消|除|除外|中止)$`);",
1)

old="""      const dm=line.match(dateRe);
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
      });"""
new="""      const dm=line.match(dateRe);
      if(!dm)continue;
      const date=`${dm[1]}/${String(dm[2]).padStart(2,'0')}/${String(dm[3]).padStart(2,'0')}`;
      const status=String(dm[5]||'');
      const rank=/^\\d+$/.test(status)?Number(status):null;
      if(rank==null){
        // Keep cancel/exclude/non-finish rows as part of the visible 5-run card,
        // but horseAbility ignores them because rank is null.
        out.push({name:horseName,date,venue:dm[4],raceNo:null,raceName:'',className:'',surface:'',distance:null,time:'',going:'',rank:null,status,fieldSize:null,num:null,pop:null,jockey:'',burden:null,source:'pasted_horse_card'});
        continue;
      }
      // Race names can wrap over multiple lines. Search forward for the course line
      // instead of assuming it is always exactly two lines after the date.
      let courseIdx=-1,cm=null;
      for(let j=i+1;j<Math.min(stop,i+8);j++){
        const hit=String(lines[j]||'').trim().match(courseRe);
        if(hit){courseIdx=j;cm=hit;break}
      }
      if(courseIdx<0||!cm)continue;
      let fieldIdx=-1,fm=null;
      for(let j=courseIdx+1;j<Math.min(stop,courseIdx+5);j++){
        const hit=String(lines[j]||'').trim().match(fieldRe);
        if(hit){fieldIdx=j;fm=hit;break}
      }
      if(fieldIdx<0||!fm)continue;
      let going=cm[4];if(going==='稍')going='稍重';if(going==='不')going='不良';
      const raceName=lines.slice(i+1,courseIdx).map(x=>String(x||'').trim()).filter(x=>x&&x!=='映像を見る').join(' ');
      out.push({
        name:horseName,date,venue:dm[4],raceNo:null,raceName,className:raceName,
        surface:cm[1],distance:Number(cm[2]),time:cm[3],going,
        rank,fieldSize:Number(fm[1]),num:Number(fm[2]),pop:Number(fm[3]),jockey:fm[4],burden:Number(fm[5]),
        source:'pasted_horse_card'
      });"""
assert old in s, 'past-run parse block not found'
s=s.replace(old,new,1)

old_render="""      const horseRuns=(Array.isArray(p.pastRuns)?p.pastRuns:[]).filter(x=>String(x.name||'')===String(r.name||'')&&Number.isFinite(Number(x.rank))).length;
      const horseText=hs.score==null?'--':Math.round(hs.score);
      const horseReason=hs.reasons?.length?hs.reasons.slice(0,3).join(' / '):'過去走なし';
      return `<tr><td>${r.num??''}</td><td>${esc(r.name)}</td><td>${horseRuns}走</td>"""
new_render="""      const horseCards=(Array.isArray(p.pastRuns)?p.pastRuns:[]).filter(x=>String(x.name||'')===String(r.name||''));
      const horseRuns=horseCards.filter(x=>Number.isFinite(Number(x.rank))).length;
      const nonFinish=horseCards.length-horseRuns;
      const horseRunText=nonFinish>0?`${horseCards.length}件<div class=\"muted\">評価${horseRuns}走 / 取消等${nonFinish}</div>`:`${horseRuns}走`;
      const horseText=hs.score==null?'--':Math.round(hs.score);
      const horseReason=hs.reasons?.length?hs.reasons.slice(0,3).join(' / '):'過去走なし';
      return `<tr><td>${r.num??''}</td><td>${esc(r.name)}</td><td>${horseRunText}</td>"""
assert old_render in s, 'render horse run block not found'
s=s.replace(old_render,new_render,1)

s=s.replace('クリーン版 v4.44：馬柱プロフィール開始判定を強化','クリーン版 v4.45：馬柱5件と評価対象走を分離＋折返し対応',1)
s=s.replace('✓ クリーン版 v4.44 起動。馬柱プロフィール開始判定を強化しました。','✓ クリーン版 v4.45 起動。馬柱5件と評価対象走を分離し、折返しレース名にも対応しました。',1)

assert '取消等${nonFinish}' in s
assert 'courseIdx' in s
assert 'クリーン版 v4.45' in s
p.write_text(s,encoding='utf-8')

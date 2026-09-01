from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace('クリーン版 v4.18：安全復元した過去並びも学習','クリーン版 v4.19：馬の成績も自動蓄積',1)

marker='function scoreRows(rows){'
assert marker in s, 'scoreRows marker missing'
helpers=r'''function normalizeHorseHistoryRecord(r){
  const name=String(r?.name||r?.horseName||'').trim();
  if(!name)return null;
  const rank=Number(r?.rank);
  const pop=Number(r?.pop);
  const distance=Number(r?.distance);
  const fieldSize=Number(r?.fieldSize);
  const num=Number(r?.num);
  const raceNo=Number(r?.raceNo);
  const burden=Number(r?.burden);
  return {
    name,
    date:String(r?.date||''),
    venue:String(r?.venue||''),
    raceNo:Number.isFinite(raceNo)&&raceNo>0?raceNo:null,
    raceName:String(r?.raceName||r?.className||''),
    className:String(r?.className||r?.raceName||''),
    surface:String(r?.surface||''),
    distance:Number.isFinite(distance)?distance:null,
    going:String(r?.going||''),
    rank:Number.isFinite(rank)?rank:null,
    pop:Number.isFinite(pop)&&pop>0?pop:null,
    odds:r?.odds==null||r?.odds===''?null:Number(r.odds),
    time:String(r?.time||''),
    jockey:String(r?.jockey||''),
    num:Number.isFinite(num)&&num>0?num:null,
    fieldSize:Number.isFinite(fieldSize)&&fieldSize>0?fieldSize:null,
    burden:Number.isFinite(burden)?burden:null,
    source:String(r?.source||'')
  };
}
function horseHistoryKey(r){
  const x=normalizeHorseHistoryRecord(r);if(!x)return '';
  if(x.date&&x.venue)return `${x.date}|${x.venue}|${x.name}`;
  return [x.date,x.venue,x.raceName,x.surface,x.distance??'',x.name,x.rank??''].join('|');
}
function mergeHorseRecords(a,b){
  const out={...(a||{})};
  for(const [k,v] of Object.entries(b||{})){
    if(v!==null&&v!==''&&v!==undefined)out[k]=v;
  }
  return out;
}
function rebuildHorseHistory(extra=[]){
  const existing=Array.isArray(state.horseHistory)?state.horseHistory:[];
  const recovered=(state.seedHistory||[]).filter(r=>r?.name&&Number.isFinite(Number(r?.rank))).map(r=>({...r,source:r.source||'recovered_horse_card'}));
  const live=(state.races||[]).flatMap(r=>(r.rows||[]).map(x=>({...x,...(r.meta||{}),fieldSize:(r.rows||[]).length,source:'saved_result'})));
  const map=new Map();
  for(const raw of [...recovered,...existing,...live,...(extra||[])]){
    const x=normalizeHorseHistoryRecord(raw);if(!x)continue;
    const k=horseHistoryKey(x);if(!k)continue;
    map.set(k,mergeHorseRecords(map.get(k),x));
  }
  state.horseHistory=[...map.values()].sort((a,b)=>String(b.date||'').localeCompare(String(a.date||''))||String(a.name||'').localeCompare(String(b.name||''),'ja'));
  persist();
  return state.horseHistory.length;
}
function horseHistoryBefore(name,targetDate){
  const target=dateNumber(targetDate);
  return (state.horseHistory||[]).filter(r=>{
    if(String(r.name||'')!==String(name||''))return false;
    if(!target)return true;
    const d=dateNumber(r.date);
    return d&&d<target;
  });
}
function extractHorsePastRuns(lines,cardRows){
  const out=[];
  const names=[...new Set((cardRows||[]).map(r=>String(r.name||'').trim()).filter(Boolean))];
  if(!names.length)return out;
  let currentHorse='';
  const dateRe=new RegExp(`^(20\\d{2})[./](\\d{1,2})[./](\\d{1,2})\\s+(${venues.join('|')})(\\d{1,2})$`);
  const courseRe=/^(芝|ダ|障)(\d{3,4})\s+([0-9]+:[0-9]{2}(?:\.[0-9])?|[0-9]+(?:\.[0-9])?)\s+(良|稍重|稍|重|不良|不)$/;
  const fieldRe=/^(\d+)頭\s+(\d+)番\s+(\d+)人\s+(.+?)\s+(\d{2,3}(?:\.\d)?)$/;
  for(let i=0;i<lines.length;i++){
    const line=String(lines[i]||'').trim();
    const matchedName=names.find(n=>line===n||line.startsWith(`${n}(`));
    if(matchedName)currentHorse=matchedName;
    const dm=line.match(dateRe);
    if(!dm||!currentHorse||i+3>=lines.length)continue;
    const cm=String(lines[i+2]||'').trim().match(courseRe);
    const fm=String(lines[i+3]||'').trim().match(fieldRe);
    if(!cm||!fm)continue;
    let going=cm[4];if(going==='稍')going='稍重';if(going==='不')going='不良';
    out.push({
      name:currentHorse,
      date:`${dm[1]}/${String(dm[2]).padStart(2,'0')}/${String(dm[3]).padStart(2,'0')}`,
      venue:dm[4],raceNo:null,raceName:String(lines[i+1]||'').trim(),className:String(lines[i+1]||'').trim(),
      surface:cm[1],distance:Number(cm[2]),time:cm[3],going,
      rank:Number(dm[5]),fieldSize:Number(fm[1]),num:Number(fm[2]),pop:Number(fm[3]),jockey:fm[4],burden:Number(fm[5]),
      source:'pasted_horse_card'
    });
  }
  const seen=new Set();
  return out.filter(r=>{const k=horseHistoryKey(r);if(!k||seen.has(k))return false;seen.add(k);return true});
}
'''
s=s.replace(marker,helpers+marker,1)

old="function saveParsedResult(auto=false){if(!parsed||parsed.mode!=='result'||!parsed.rows.length)return false;const m=parsed.meta||{};if(!m.venue||!m.raceNo||!m.date)return false;const key=[m.date,m.venue,m.raceNo].join('|');const obj={meta:m,rows:parsed.rows,savedAt:new Date().toISOString()};const idx=(state.races||[]).findIndex(r=>[r.meta?.date,r.meta?.venue,r.meta?.raceNo].join('|')===key);if(idx>=0)state.races[idx]=obj;else state.races.push(obj);rebuildHistory();renderDashboard();setStatus(`✓ ${auto?'自動保存・騎手反映':'保存'}しました: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭`,'ok');return true}"
new="function saveParsedResult(auto=false){if(!parsed||parsed.mode!=='result'||!parsed.rows.length)return false;const m=parsed.meta||{};if(!m.venue||!m.raceNo||!m.date)return false;const key=[m.date,m.venue,m.raceNo].join('|');const obj={meta:m,rows:parsed.rows,savedAt:new Date().toISOString()};const idx=(state.races||[]).findIndex(r=>[r.meta?.date,r.meta?.venue,r.meta?.raceNo].join('|')===key);if(idx>=0)state.races[idx]=obj;else state.races.push(obj);rebuildHistory();const horseTotal=rebuildHorseHistory();renderDashboard();setStatus(`✓ ${auto?'自動保存・騎手反映':'保存'}しました: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭\\n馬成績も ${parsed.rows.length}頭分反映 / 馬履歴 合計${horseTotal}走`,'ok');return true}"
assert old in s, 'saveParsedResult target missing'
s=s.replace(old,new,1)

old="function saveParsedCard(){if(!parsed||parsed.mode!=='card'||!parsed.rows.length)return false;const m=parsed.meta||{};if(!m.venue||!m.raceNo||!m.date)return false;if(!Array.isArray(state.raceCards))state.raceCards=[];const key=[m.date,m.venue,m.raceNo].join('|');const obj={meta:m,rows:parsed.rows,savedAt:new Date().toISOString()};const idx=state.raceCards.findIndex(r=>[r.meta?.date,r.meta?.venue,r.meta?.raceNo].join('|')===key);if(idx>=0)state.raceCards[idx]=obj;else state.raceCards.push(obj);persist();renderDashboard();const names=[...new Set(parsed.rows.map(r=>r.jockey).filter(Boolean))];setStatus(`✓ 出馬表として読取・騎手登録: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭 / ${names.length}名\\n成績は結果を読み取った時だけ加算します。`,'ok');return true}"
new="function saveParsedCard(){if(!parsed||parsed.mode!=='card'||!parsed.rows.length)return false;const m=parsed.meta||{};if(!m.venue||!m.raceNo||!m.date)return false;if(!Array.isArray(state.raceCards))state.raceCards=[];const key=[m.date,m.venue,m.raceNo].join('|');const obj={meta:m,rows:parsed.rows,savedAt:new Date().toISOString()};const idx=state.raceCards.findIndex(r=>[r.meta?.date,r.meta?.venue,r.meta?.raceNo].join('|')===key);if(idx>=0)state.raceCards[idx]=obj;else state.raceCards.push(obj);const past=extractHorsePastRuns(parsed.lines||[],parsed.rows||[]);const before=(state.horseHistory||[]).length;const horseTotal=rebuildHorseHistory(past);const added=Math.max(0,horseTotal-before);renderDashboard();const names=[...new Set(parsed.rows.map(r=>r.jockey).filter(Boolean))];setStatus(`✓ 出馬表として読取・騎手登録: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭 / ${names.length}名\\n馬柱の過去走: 検出${past.length}走 / 新規${added}走 / 馬履歴 合計${horseTotal}走`,'ok');return true}"
assert old in s, 'saveParsedCard target missing'
s=s.replace(old,new,1)

old='<th>馬番</th><th>馬名</th><th>騎手</th><th>人気</th>'
new='<th>馬番</th><th>馬名</th><th>馬履歴</th><th>騎手</th><th>人気</th>'
assert old in s, 'card header target missing'
s=s.replace(old,new,1)

old='return `<tr><td>${r.num??\'\'}</td><td>${esc(r.name)}</td><td>${esc(r.jockey)}</td><td>${r.pop??\'-\'}</td>'
new='const horseRuns=horseHistoryBefore(r.name,m.date).length; return `<tr><td>${r.num??\'\'}</td><td>${esc(r.name)}</td><td>${horseRuns}走</td><td>${esc(r.jockey)}</td><td>${r.pop??\'-\'}</td>'
assert old in s, 'card row target missing'
s=s.replace(old,new,1)

old="function renderDashboard(){state=loadState();if(!Array.isArray(state.races))state.races=[];if(!Array.isArray(state.history))rebuildHistory();if(!Array.isArray(state.raceCards))state.raceCards=[];const stats=jockeyStats();"
new="function renderDashboard(){state=loadState();if(!Array.isArray(state.races))state.races=[];if(!Array.isArray(state.history))rebuildHistory();if(!Array.isArray(state.raceCards))state.raceCards=[];rebuildHorseHistory();const stats=jockeyStats();"
assert old in s, 'renderDashboard start missing'
s=s.replace(old,new,1)

old="$('manageStatus').textContent=`保存レース: ${state.races.length} / 学習騎乗: ${(state.history||[]).length}（復元 ${(state.seedHistory||[]).length}） / 出馬表: ${state.raceCards.length}`"
new="const horseCount=new Set((state.horseHistory||[]).map(r=>r.name).filter(Boolean)).size;$('manageStatus').textContent=`保存レース: ${state.races.length} / 学習騎乗: ${(state.history||[]).length}（復元 ${(state.seedHistory||[]).length}） / 馬成績: ${(state.horseHistory||[]).length}走・${horseCount}頭 / 出馬表: ${state.raceCards.length}`"
assert old in s, 'manage status target missing'
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

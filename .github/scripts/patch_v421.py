from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_header='クリーン版 v4.20：保存確認＋JSON自動バックアップ'
new_header='クリーン版 v4.21：取消・除外の結果誤読を修正'
assert old_header in s, 'v4.20 header not found'
s=s.replace(old_header,new_header,1)

old_start="""function parseResultRows(lines){
  const out=[];
  for(let i=0;i<lines.length-7;i++){
    if(!/^\\d{1,2}$/.test(lines[i])) continue;
    const rank=Number(lines[i]);if(rank<1||rank>30) continue;
"""
new_start="""function parseResultRows(lines){
  const out=[];
  const boundary=lines.findIndex(s=>/^(?:レース映像|払戻金|払戻し|コーナー通過順位)$/.test(String(s||'').trim()));
  const limit=boundary>0?boundary:lines.length;
  for(let i=0;i<limit-7;i++){
    if(!/^\\d{1,2}$/.test(lines[i])) continue;
    const prev=String(lines[i-1]||'').trim();
    if(/^(?:取|取消|除|除外|中|中止|失|失格)$/.test(prev)) continue;
    const rank=Number(lines[i]);if(rank<1||rank>30) continue;
"""
assert old_start in s, 'parseResultRows start not found'
s=s.replace(old_start,new_start,1)

old_end='    const end=Math.min(lines.length,p+18);'
new_end='    const end=Math.min(limit,p+18);'
assert old_end in s, 'parseResultRows scan limit not found'
s=s.replace(old_end,new_end,1)

old_existing="const existing=Array.isArray(state.horseHistory)?state.horseHistory:[];"
new_existing="const existing=(Array.isArray(state.horseHistory)?state.horseHistory:[]).filter(r=>r?.source!=='saved_result');"
assert old_existing in s, 'horseHistory existing line not found'
s=s.replace(old_existing,new_existing,1)

old_boot="setStatus('✓ クリーン版 v4.14 起動。通常出馬表と馬柱(5走/9走)の両方に対応しました。','ok')"
new_boot="setStatus('✓ クリーン版 v4.21 起動。取消・除外・中止・失格は着順学習から除外します。','ok')"
if old_boot in s:
    s=s.replace(old_boot,new_boot,1)

p.write_text(s,encoding='utf-8')

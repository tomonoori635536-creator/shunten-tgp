from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

s=s.replace('クリーン版 v4.19：馬の成績も自動蓄積','クリーン版 v4.20：保存確認＋JSON自動バックアップ',1)

# input receipt
old='<div id="status" class="status">待機中</div><div id="preview"></div>'
new='<div id="status" class="status">待機中</div><div id="saveReceipt" class="status ok" style="display:none;font-size:18px;font-weight:800"></div><div id="preview"></div>'
assert old in s
s=s.replace(old,new,1)

# manage UI
old='''<div class="row"><button class="btn secondary" id="exportBtn">JSON書き出し</button><label class="btn secondary" style="display:inline-block">JSON読込<input type="file" id="importFile" accept="application/json,.json" style="display:none"></label><button class="btn secondary" id="deleteLastBtn">最後のレースを削除</button></div>\n<div id="manageStatus" class="status">保存データを確認できます。</div>\n<div class="tablewrap"><table><thead><tr><th>日付</th><th>競馬場</th><th>R</th><th>レース名</th><th>頭数</th></tr></thead><tbody id="raceBody"></tbody></table></div>'''
new='''<div class="row"><button class="btn primary" id="autoBackupBtn">自動JSON保存を設定</button><span id="autoBackupState" class="muted">未設定</span></div>\n<p class="muted">最初に1回だけ保存先のJSONファイルを選びます。以後、出馬表・結果を保存するたびに同じファイルへ自動上書きします。</p>\n<div class="row"><button class="btn secondary" id="exportBtn">JSON書き出し</button><label class="btn secondary" style="display:inline-block">JSON読込<input type="file" id="importFile" accept="application/json,.json" style="display:none"></label><button class="btn secondary" id="deleteLastBtn">最後のレースを削除</button></div>\n<div id="manageStatus" class="status">保存データを確認できます。</div>\n<h3>保存済み出馬表</h3>\n<div class="tablewrap"><table><thead><tr><th>保存</th><th>日付</th><th>競馬場</th><th>R</th><th>レース名</th><th>頭数</th></tr></thead><tbody id="cardBody"></tbody></table></div>\n<h3>保存済み結果</h3>\n<div class="tablewrap"><table><thead><tr><th>日付</th><th>競馬場</th><th>R</th><th>レース名</th><th>頭数</th></tr></thead><tbody id="raceBody"></tbody></table></div>'''
assert old in s
s=s.replace(old,new,1)

# insert auto backup helpers before cleanPasteToken
marker="const $=id=>document.getElementById(id);\n"
assert marker in s
helpers=r'''const AUTO_DB='shunten_auto_json_db';
const AUTO_STORE='handles';
const AUTO_HANDLE_KEY='backup';
let autoJsonHandle=null;
function openAutoDb(){
  return new Promise((resolve,reject)=>{
    const req=indexedDB.open(AUTO_DB,1);
    req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains(AUTO_STORE))req.result.createObjectStore(AUTO_STORE)};
    req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);
  });
}
async function getStoredAutoHandle(){
  try{const db=await openAutoDb();return await new Promise((resolve,reject)=>{const tx=db.transaction(AUTO_STORE,'readonly');const q=tx.objectStore(AUTO_STORE).get(AUTO_HANDLE_KEY);q.onsuccess=()=>resolve(q.result||null);q.onerror=()=>reject(q.error)})}catch(e){return null}
}
async function storeAutoHandle(h){
  try{const db=await openAutoDb();await new Promise((resolve,reject)=>{const tx=db.transaction(AUTO_STORE,'readwrite');tx.objectStore(AUTO_STORE).put(h,AUTO_HANDLE_KEY);tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error)})}catch(e){}
}
function autoBackupUi(text,good=false){const el=$('autoBackupState');if(!el)return;el.textContent=text;el.className=good?'ok':'muted'}
async function writeAutoJsonBackup(forcePermission=false){
  if(!autoJsonHandle)return false;
  try{
    let perm=await autoJsonHandle.queryPermission({mode:'readwrite'});
    if(perm!=='granted'&&forcePermission)perm=await autoJsonHandle.requestPermission({mode:'readwrite'});
    if(perm!=='granted'){autoBackupUi('要再許可：自動JSON保存を設定を押してください');return false}
    const writable=await autoJsonHandle.createWritable();
    await writable.write(JSON.stringify(state,null,2));
    await writable.close();
    const now=new Date();
    autoBackupUi(`自動保存ON ✓ ${now.toLocaleTimeString('ja-JP',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}`,true);
    return true;
  }catch(e){autoBackupUi('自動保存エラー：設定し直してください');return false}
}
async function chooseAutoJsonBackup(){
  if(!window.showSaveFilePicker){autoBackupUi('このブラウザは同一JSONへの自動保存に未対応');return}
  try{
    const h=await window.showSaveFilePicker({suggestedName:'shunten_auto_backup.json',types:[{description:'JSON',accept:{'application/json':['.json']}}]});
    autoJsonHandle=h;await storeAutoHandle(h);await writeAutoJsonBackup(true);
  }catch(e){if(e?.name!=='AbortError')autoBackupUi('設定できませんでした')}
}
async function initAutoJsonBackup(){
  autoJsonHandle=await getStoredAutoHandle();
  if(!autoJsonHandle){autoBackupUi('未設定');return}
  try{const perm=await autoJsonHandle.queryPermission({mode:'readwrite'});autoBackupUi(perm==='granted'?'自動保存ON ✓':'保存先あり・再許可待ち',perm==='granted')}catch(e){autoBackupUi('未設定')}
}
function triggerAutoJsonBackup(){void writeAutoJsonBackup(false)}
'''
s=s.replace(marker,marker+helpers,1)

# status receipts + automatic backup hooks
old="setStatus(`✓ ${auto?'自動保存・騎手反映':'保存'}しました: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭\\n馬成績も ${parsed.rows.length}頭分反映 / 馬履歴 合計${horseTotal}走`,'ok');return true}"
new="setStatus(`✓ ${auto?'自動保存・騎手反映':'保存'}しました: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭\\n馬成績も ${parsed.rows.length}頭分反映 / 馬履歴 合計${horseTotal}走`,'ok');$('saveReceipt').style.display='block';$('saveReceipt').textContent=`✅ 結果 保存済み　${m.date} ${m.venue} ${m.raceNo}R`;triggerAutoJsonBackup();return true}"
assert old in s
s=s.replace(old,new,1)

old="setStatus(`✓ 出馬表として読取・騎手登録: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭 / ${names.length}名\\n馬柱の過去走: 検出${past.length}走 / 新規${added}走 / 馬履歴 合計${horseTotal}走`,'ok');return true}"
new="setStatus(`✓ 出馬表として読取・騎手登録: ${m.date} ${m.venue} ${m.raceNo}R / ${parsed.rows.length}頭 / ${names.length}名\\n馬柱の過去走: 検出${past.length}走 / 新規${added}走 / 馬履歴 合計${horseTotal}走`,'ok');$('saveReceipt').style.display='block';$('saveReceipt').textContent=`✅ 出馬表 保存済み　${m.date} ${m.venue} ${m.raceNo}R`;triggerAutoJsonBackup();return true}"
assert old in s
s=s.replace(old,new,1)

# render saved card list
needle="$('raceBody').innerHTML=state.races.length?"
idx=s.index(needle)
insert="$('cardBody').innerHTML=state.raceCards.length?[...state.raceCards].sort((a,b)=>String(b.meta?.date||'').localeCompare(String(a.meta?.date||''))||Number(b.meta?.raceNo||0)-Number(a.meta?.raceNo||0)).map(r=>`<tr><td>✅</td><td>${esc(r.meta?.date||'')}</td><td>${esc(r.meta?.venue||'')}</td><td>${r.meta?.raceNo??''}</td><td>${esc(r.meta?.raceName||'')}</td><td>${(r.rows||[]).length}</td></tr>`).join(''):'<tr><td colspan=\"6\">保存済み出馬表はありません。</td></tr>';"
s=s[:idx]+insert+s[idx:]

# register button, backup after import/delete; clear receipt on clear
old="$('exportBtn').addEventListener('click',downloadJSON);"
new="$('autoBackupBtn').addEventListener('click',chooseAutoJsonBackup);\n$('exportBtn').addEventListener('click',downloadJSON);"
assert old in s
s=s.replace(old,new,1)

old="state=Object.assign(emptyState(),x);rebuildHistory();renderDashboard();$('manageStatus').textContent='✓ JSONを読み込みました。'"
new="state=Object.assign(emptyState(),x);rebuildHistory();renderDashboard();triggerAutoJsonBackup();$('manageStatus').textContent='✓ JSONを読み込みました。'"
assert old in s
s=s.replace(old,new,1)

old="const r=state.races.pop();rebuildHistory();renderDashboard();$('manageStatus').textContent=`最後のレースを削除しました: ${r.meta?.date||''} ${r.meta?.venue||''} ${r.meta?.raceNo??''}R`"
new="const r=state.races.pop();rebuildHistory();renderDashboard();triggerAutoJsonBackup();$('manageStatus').textContent=`最後のレースを削除しました: ${r.meta?.date||''} ${r.meta?.venue||''} ${r.meta?.raceNo??''}R`"
assert old in s
s=s.replace(old,new,1)

old="$('clearBtn').addEventListener('click',()=>{$('raw').value='';$('preview').innerHTML='';parsed=null;$('saveBtn').disabled=true;setStatus('入力欄だけ消しました')});"
new="$('clearBtn').addEventListener('click',()=>{$('raw').value='';$('preview').innerHTML='';$('saveReceipt').style.display='none';$('saveReceipt').textContent='';parsed=null;$('saveBtn').disabled=true;setStatus('入力欄だけ消しました')});"
assert old in s
s=s.replace(old,new,1)

# boot text + init
old="setStatus('✓ クリーン版 v4.14 起動。通常出馬表と馬柱(5走/9走)の両方に対応しました。','ok');renderDashboard()"
new="setStatus('✓ クリーン版 v4.20 起動。保存確認とJSON自動バックアップに対応しました。','ok');renderDashboard();void initAutoJsonBackup()"
assert old in s
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

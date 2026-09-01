from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_header='クリーン版 v4.21：取消・除外の結果誤読を修正'
new_header='クリーン版 v4.22：騎手人気1〜12位を個別学習'
assert old_header in s, 'v4.21 header not found'
s=s.replace(old_header,new_header,1)

old="function popularityBand(pop){const n=Number(pop);if(!Number.isFinite(n)||n<1)return '';return n===1?'1人気':n<=3?'2-3人気':n<=6?'4-6人気':'7人気以下'}"
new="function popularityBand(pop){const n=Number(pop);if(!Number.isFinite(n)||n<1)return '';return n===1?'1人気':n<=3?'2-3人気':n<=6?'4-6人気':'7人気以下'}\nfunction exactPopularity(pop){const n=Number(pop);if(!Number.isInteger(n)||n<1)return '';return `${n}人気`}"
assert old in s, 'popularityBand not found'
s=s.replace(old,new,1)

old_js="function jockeySuitability(row,meta){if(!row?.jockey)return {score:null,label:'騎手不明',matchCount:0,total:0,reasons:[]};const all=jockeyHistoryBefore(row.jockey,meta?.date);if(!all.length)return {score:null,label:'未学習',matchCount:0,total:0,reasons:[]};const course=(meta?.surface||meta?.distance)?`${meta?.surface||'?'}${meta?.distance||'?'}m`:'';const band=popularityBand(row.pop);const factors=[{label:'競馬場',value:meta?.venue||'',weight:30,test:r=>(r.venue||'')===(meta?.venue||'')},{label:'コース',value:course,weight:30,test:r=>((r.surface||r.distance)?`${r.surface||'?'}${r.distance||'?'}m`:'')===course},{label:'馬場',value:meta?.going||'',weight:15,test:r=>(r.going||'')===(meta?.going||'')},{label:'人気帯',value:band,weight:15,test:r=>popularityBand(r.pop)===band},{label:'総合',value:'',weight:10,test:()=>true}];let weighted=0,weightSum=0;const matched=new Set();const reasons=[];for(const f of factors){if(f.label!=='総合'&&!f.value)continue;const rows=f.label==='総合'?all:all.filter(f.test);if(!rows.length)continue;const q=scoreRows(rows);if(!q)continue;weighted+=q.score*f.weight;weightSum+=f.weight;if(f.label!=='総合'){rows.forEach(x=>matched.add(x));reasons.push(`${f.value} ${rows.length}鞍`)}}if(!weightSum)return {score:null,label:'未学習',matchCount:0,total:all.length,reasons:[]};const score=weighted/weightSum;const matchCount=matched.size;let label='蓄積あり';if(all.length<3||matchCount<2)label='サンプル少';else if(all.length<10||matchCount<5)label='参考';return {score,label,matchCount,total:all.length,reasons}}"
new_js="function jockeySuitability(row,meta){if(!row?.jockey)return {score:null,label:'騎手不明',matchCount:0,total:0,reasons:[]};const all=jockeyHistoryBefore(row.jockey,meta?.date);if(!all.length)return {score:null,label:'未学習',matchCount:0,total:0,reasons:[]};const course=(meta?.surface||meta?.distance)?`${meta?.surface||'?'}${meta?.distance||'?'}m`:'';const exactPop=exactPopularity(row.pop);const factors=[{label:'競馬場',value:meta?.venue||'',weight:30,test:r=>(r.venue||'')===(meta?.venue||'')},{label:'コース',value:course,weight:30,test:r=>((r.surface||r.distance)?`${r.surface||'?'}${r.distance||'?'}m`:'')===course},{label:'馬場',value:meta?.going||'',weight:15,test:r=>(r.going||'')===(meta?.going||'')},{label:'人気順位',value:exactPop,weight:15,test:r=>exactPopularity(r.pop)===exactPop},{label:'総合',value:'',weight:10,test:()=>true}];let weighted=0,weightSum=0;const matched=new Set();const reasons=[];for(const f of factors){if(f.label!=='総合'&&!f.value)continue;const rows=f.label==='総合'?all:all.filter(f.test);if(!rows.length)continue;const q=scoreRows(rows);if(!q)continue;weighted+=q.score*f.weight;weightSum+=f.weight;if(f.label!=='総合'){rows.forEach(x=>matched.add(x));reasons.push(`${f.value} ${rows.length}鞍`)}}if(!weightSum)return {score:null,label:'未学習',matchCount:0,total:all.length,reasons:[]};const score=weighted/weightSum;const matchCount=matched.size;let label='蓄積あり';if(all.length<3||matchCount<2)label='サンプル少';else if(all.length<10||matchCount<5)label='参考';return {score,label,matchCount,total:all.length,reasons}}"
assert old_js in s, 'jockeySuitability old function not found'
s=s.replace(old_js,new_js,1)

old_detail="const exactPopEntries=Object.entries(st.popExact).sort((a,b)=>Number(a[0].replace('人気',''))-Number(b[0].replace('人気','')));"
new_detail="const zeroPop=()=>({rides:0,wins:0,places:0,rankSum:0});const exactPopEntries=Array.from({length:12},(_,i)=>{const k=`${i+1}人気`;return [k,st.popExact[k]||zeroPop()]});"
assert old_detail in s, 'exactPopEntries line not found'
s=s.replace(old_detail,new_detail,1)

old_boot="setStatus('✓ クリーン版 v4.21 起動。取消・除外・中止・失格は着順学習から除外します。','ok')"
new_boot="setStatus('✓ クリーン版 v4.22 起動。騎手の人気順位は1人気〜12人気を個別に学習します。','ok')"
if old_boot in s:
    s=s.replace(old_boot,new_boot,1)

p.write_text(s,encoding='utf-8')

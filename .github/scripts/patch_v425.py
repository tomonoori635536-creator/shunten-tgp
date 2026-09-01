from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old_header='クリーン版 v4.24：51レース時系列バックテスト'
new_header='クリーン版 v4.25：当日Rは学習継続・最終点から一時除外'
assert old_header in s, 'v4.24 header not found'
s=s.replace(old_header,new_header,1)

old_desc='騎手適性は過去履歴から計算。並び補正は最大±8点。当日R補正は、対象Rより前の当日成績（勝数・3着内数）と同じ状態で、そのRに騎乗した過去開催日の成績を騎手ごとに学習します。未来のRや同日の後続結果は使わず、補正は最大±6点です。'
new_desc='騎手適性は過去履歴から計算。並び補正は最大±8点。当日Rパターンは、対象Rより前の当日成績（勝数・3着内数）と同じ状態で、そのRに騎乗した過去開催日の成績を騎手ごとに学習します。未来のRや同日の後続結果は使いません。現在はバックテスト結果により当日Rは参考表示のみとし、最終騎手点には加算しません。'
assert old_desc in s, 'card description not found'
s=s.replace(old_desc,new_desc,1)

old_head='<th>当日R補正</th>'
new_head='<th>当日R参考</th>'
assert old_head in s, 'daily R table header not found'
s=s.replace(old_head,new_head,1)

old_final="const finalScore=base==null?null:clampValue(base+lp.adj+dp.adj,0,100);"
new_final="const finalScore=base==null?null:clampValue(base+lp.adj,0,100);"
assert old_final in s, 'live final score expression not found'
s=s.replace(old_final,new_final,1)

# Keep the daily pattern value visible, but label it as reference-only.
old_day="const dayAdjText=dp.label==='未学習'?'--':`${dp.adj>0?'+':''}${dp.adj.toFixed(1)}`;"
new_day="const dayAdjText=dp.label==='未学習'?'--':`${dp.adj>0?'+':''}${dp.adj.toFixed(1)} 参考`;"
assert old_day in s, 'daily R text expression not found'
s=s.replace(old_day,new_day,1)

# Update stale boot message if present.
import re
s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.25 起動。当日Rは学習・表示を継続し、最終騎手点は騎手適性＋並び補正で計算します。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

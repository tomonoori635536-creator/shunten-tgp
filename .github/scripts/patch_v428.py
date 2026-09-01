from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old='クリーン版 v4.27：馬×騎手の比率を仮比較'
new='クリーン版 v4.28：馬55×騎手45も仮比較'
assert old in s, 'v4.27 header not found'
s=s.replace(old,new,1)

s=s.replace('馬能力Hと現在採用中の騎手Bを50:50〜80:20で仮合成します。','馬能力Hと現在採用中の騎手Bを50:50・55:45・60:40・70:30・80:20で仮合成します。',1)
s=s.replace('仮=馬:騎手 50:50〜80:20','仮=馬:騎手 50:50 / 55:45 / 60:40 / 70:30 / 80:20',1)

old_variants="""    {key:'m50',name:'仮 50:50 馬50＋騎手50',score:'scoreM50'},
    {key:'m60',name:'仮 60:40 馬60＋騎手40',score:'scoreM60'},"""
new_variants="""    {key:'m50',name:'仮 50:50 馬50＋騎手50',score:'scoreM50'},
    {key:'m55',name:'仮 55:45 馬55＋騎手45',score:'scoreM55'},
    {key:'m60',name:'仮 60:40 馬60＋騎手40',score:'scoreM60'},"""
assert old_variants in s, 'variant insertion point not found'
s=s.replace(old_variants,new_variants,1)

old_scores="""        scoreM50:blend(0.50),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
new_scores="""        scoreM50:blend(0.50),scoreM55:blend(0.55),scoreM60:blend(0.60),scoreM70:blend(0.70),scoreM80:blend(0.80)};"""
assert old_scores in s, 'blend score insertion point not found'
s=s.replace(old_scores,new_scores,1)

s=s.replace('50:50〜80:20は暫定比較です。','50:50・55:45・60:40・70:30・80:20は暫定比較です。',1)

s=re.sub(r"setStatus\('✓ クリーン版 v[0-9.]+ 起動。[^']*','ok'\)","setStatus('✓ クリーン版 v4.28 起動。55:45を追加しました。比率はまだ仮比較です。','ok')",s,count=1)

p.write_text(s,encoding='utf-8')

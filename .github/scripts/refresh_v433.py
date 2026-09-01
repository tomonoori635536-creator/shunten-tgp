from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='<!-- deploy-refresh-v433-20260902 -->'
assert 'クリーン版 v4.33：位置補正の強さ別に成績を検証' in s
if marker not in s:
    s=s.replace('<body>','<body>\n'+marker,1)
p.write_text(s,encoding='utf-8')

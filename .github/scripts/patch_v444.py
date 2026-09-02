from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""    const near=lines.slice(i+1,Math.min(lines.length,i+16)).map(x=>String(x||'').trim());
    const joined=near.join(' ');
    const hasProfile=/(?:牡|牝|セ)\\d/.test(joined)&&/\\(\\d{1,2}人気\\)/.test(joined)&&near.some(x=>dateRe.test(x));
    if(hasProfile)anchors.push({index:i,name:line});"""
new="""    const near=lines.slice(i+1,Math.min(lines.length,i+30)).map(x=>String(x||'').trim());
    const joined=near.join(' ');
    // Horse profile layout is sire -> horse -> dam -> (broodmare sire) -> stable ... -> sex/age.
    // Opponent names at the end of a past race are followed by '映像を見る', so requiring
    // the pedigree parenthesis immediately after the dam avoids false horse switches.
    const dam=String(lines[i+1]||'').trim();
    const broodmareSire=String(lines[i+2]||'').trim();
    const hasPedigree=!!dam&&/^\\(.+\\)$/.test(broodmareSire);
    const hasSexAge=/(?:牡|牝|セ)\\d/.test(joined);
    const hasBurden=near.some(x=>/^\\d{2,3}(?:\\.\\d)?$/.test(x));
    const hasProfile=hasPedigree&&hasSexAge&&hasBurden;
    if(hasProfile)anchors.push({index:i,name:line});"""
assert old in s, 'profile anchor block not found'
s=s.replace(old,new,1)
s=s.replace('クリーン版 v4.43：5走版は馬ごとに最新5走へ固定','クリーン版 v4.44：馬柱プロフィール開始判定を強化',1)
s=s.replace('✓ クリーン版 v4.43 起動。5走版は馬ごとに重複除去し最新5走へ固定しました。','✓ クリーン版 v4.44 起動。馬柱プロフィール開始判定を強化しました。',1)
assert 'hasPedigree&&hasSexAge&&hasBurden' in s
assert 'クリーン版 v4.44' in s
p.write_text(s,encoding='utf-8')

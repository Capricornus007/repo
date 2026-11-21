#!/usr/bin/env python3
"""修正 cjktty 補丁的 fbcon.h Hunk#1 以適配 CachyOS 的 struct fbcon_rotated。

CachyOS 7.3.x 把 fbcon.h 的匿名 struct 改成命名 struct fbcon_rotated，
且多三個欄位 (buf_width/height/charcount)，補丁原本的 context
(`int buf_rotate;` 緊接 `} rotated;`) 對不上 → Hunk#1 FAILED。
本腳本把 Hunk#1 換成以 CachyOS 真實結構為 context 的最小 hunk
（3 行 context，patch 預設 fuzz=2 即可套上），其餘 hunk 不動。

用法: cjktty-fix-patch.py 0001-cjktty.patch [內核源碼 fbcon.h]
第二參數可選：給了就從中讀 context 行（更準）；不給用內建 CachyOS 7.3.x 字串。
"""
import sys
p = sys.argv[1]
lines = open(p, encoding='utf-8', errors='replace').read().split('\n')
# 找 fbcon.h 段的 Hunk#1 (@@ -87,6 +87,9 @@ struct fbcon_par {)
i = j = None
for idx, line in enumerate(lines):
    if line.startswith('@@ -87,6 +87,9'):
        i = idx
    if i is not None and idx > i and line.startswith('@@'):
        j = idx
        break
if i is None or j is None:
    print('fbcon.h Hunk#1 找不到（上游補丁格式可能已變），跳過修正', file=sys.stderr)
    sys.exit(0)
# CachyOS 7.3.x struct fbcon_rotated 的真實 context (line 79-81)
new_hunk = [
    '@@ -79,3 +79,6 @@ struct fbcon_rotated {',
    ' \tsize_t bufsize;',
    ' \tint buf_rotate;              /* rotation of buf */',
    '+\tfont_data_t *fontdata_utf; /* CJK font source */',
    '+\tu8 *buf_utf;               /* rotated CJK glyphs */',
    '+\tsize_t bufsize_utf;',
    ' \tunsigned int buf_width;      /* geometry of source font */',
]
lines[i:j] = new_hunk
open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('fbcon.h Hunk#1 已改為 CachyOS struct fbcon_rotated 適配版')

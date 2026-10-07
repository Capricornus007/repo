#!/usr/bin/env python3
"""把 PySolFC 的說明頁 HTML 樹依 gettext 目錄改寫成語系版。

用法：localize-help.py <htmldir> <lang> <mo>
  htmldir  例 <pkg>/usr/share/PySolFC/html
  lang     例 zh_TW
  mo       例 zh_TW_help.mo（msgid = 文字節點原文，msgstr = 譯文）

只動 >...< 之間的文字節點：標籤、屬性、HTML 實體、檔名、圖片路徑一律原樣保留。
輸出 <htmldir>/<lang>/<相對路徑>，並將 images 目錄 symlink 過去，讓譯文裡
`../images/x.png` 這種相對引用照舊解析得到。
"""
import gettext
import os
import re
import sys

NODE = re.compile(r'>([^<>]+)<', re.S)
MARKER = '.pysol-localized'


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    htmldir, lang, mopath = sys.argv[1:4]
    with open(mopath, 'rb') as fh:
        cat = gettext.GNUTranslations(fh)

    root = os.path.abspath(htmldir)
    out_root = os.path.join(root, lang)
    stat = {'total': 0, 'hit': 0, 'miss': 0, 'files': 0}

    def rep(m):
        text = m.group(1)
        key = ' '.join(text.split())
        if len(key) < 3 or not re.search(r'[A-Za-z]{2}', key):
            return m.group(0)
        stat['total'] += 1
        t = cat.gettext(key)
        if t == key:
            stat['miss'] += 1
            return m.group(0)
        stat['hit'] += 1
        lead = text[:len(text) - len(text.lstrip())]
        trail = text[len(text.rstrip()):]
        return '>%s%s%s<' % (lead, t, trail)

    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel != '.' and os.path.exists(os.path.join(dirpath, MARKER)):
            dirnames[:] = []          # 別把已生成的語系樹當英文來源再翻一遍
            continue
        for fn in sorted(filenames):
            if not fn.endswith('.html'):
                continue
            s = open(os.path.join(dirpath, fn), encoding='utf-8').read()
            dst = os.path.join(out_root, rel, fn)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'w', encoding='utf-8').write(NODE.sub(rep, s))
            stat['files'] += 1

    img, src_img = os.path.join(out_root, 'images'), os.path.join(root, 'images')
    if os.path.isdir(src_img) and not os.path.lexists(img):
        os.symlink('../images', img)
    open(os.path.join(out_root, MARKER), 'w').write(
        '本目錄由 localize-help.py 產生（來源 = 上層英文 html + %s）\n'
        % os.path.basename(mopath))

    print('localize-help %s: %d 頁、文字節點 %d、命中 %d、未譯 %d'
          % (lang, stat['files'], stat['total'], stat['hit'], stat['miss']))
    if stat['hit'] == 0:
        sys.exit('ERROR: 一個字都沒翻譯——.mo 或 htmldir 給錯了，別發沒中文的說明頁')


main()

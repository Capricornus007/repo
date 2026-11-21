#!/usr/bin/env python3
"""從 KDE invent GitLab tags JSON(stdin) 輸出最高版 pkgver（去 v 前綴）。

三個 KDE -git 包（kpat-git/kmahjongg-git/kdeconnect-git）共用。
"""
import json, sys, re
d = json.load(sys.stdin)
vers = []
for t in d:
    name = t.get('name', '').lstrip('v')
    if re.match(r'^\d+(\.\d+)*$', name):
        vers.append(tuple(int(x) for x in name.split('.')))
if not vers:
    sys.exit(1)
print('.'.join(str(x) for x in max(vers)))

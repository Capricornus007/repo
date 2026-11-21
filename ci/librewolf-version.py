#!/usr/bin/env python3
# 從 librewolf.dev Forgejo source tags 讀入 JSON(stdin)，輸出最高版 pkgver。
# tag 160.0.1-1 -> 160.0.1_1；round 160.0-1 -> 160.0.0_1（補 .0 避免 vercmp 問題）
import json, sys, re
d = json.load(sys.stdin)
best = None
for t in d:
    m = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?-(\d+)$", t["name"])
    if not m:
        continue
    maj, minor, patch, rel = [int(x) if x else 0 for x in m.groups()]
    key = (maj, minor, patch, rel)
    if best is None or key > best[0]:
        best = (key, (maj, minor, patch, rel))
if not best:
    sys.exit(1)
maj, minor, patch, rel = best[1]
print(f"{maj}.{minor}.{patch}_{rel}")

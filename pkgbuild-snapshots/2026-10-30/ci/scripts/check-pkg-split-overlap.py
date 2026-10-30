#!/usr/bin/env python3
"""靜態檢查分割包（pkgbase + 多個 package_X()）的 _pick 清單有無重疊。

為什麼要它：makepkg 只在跑到 package() 階段才發現「同一檔案被兩個包聲有」，
而 llvm 這種要編一兩小時的包，等到那步才炸等於白燒一輪 CI。重疊與否其實是
「兩份 glob 樣式能否命中同一路徑」，可以在寫完的當下用字串判出來。

演算法（逐段，因為 glob 的 * 不跨 /）：
  · 樣式切成路徑段。
  · 兩樣式若段數相同：逐段都要「可命中同一字串」才算重疊。
  · 若一段數是另一段的**前綴**：短的那個最後一段若能命中長的那個的下一段，
    就算重疊 —— 因為 `cp -a usr/share/clang` 是把整棵子目錄搬走。
  · 段與段「可命中同一字串」= 兩者的字面前綴互为前綴、且字面後綴互为後綴
    （`libclang*` 與 `libclang-cpp*` → 是；`*.a` 與 `cmake` → 否）。

⚠️ 已知不覆蓋：靠 _drop 才不重疊的寫法（clang-git 先收 usr/bin/clang-*
再剔掉 extra 工具名）。那種「先搶再讓」太脆，出現時應該改成明確清單；
本工具刻意不去模擬 _drop，免得給自己假安全感。
"""
import fnmatch
import re
import sys
from pathlib import Path

FUNC = re.compile(r"^package_([A-Za-z0-9_.@-]+)\(\)")


def seg_compat(a, b):
    """兩個路徑段能否命中同一個字串。"""
    if a == b:
        return True
    if a == "*" or b == "*":
        return True

    def has_glob(s):
        return any(c in s for c in "*?[")

    ga, gb = has_glob(a), has_glob(b)
    if not ga and not gb:
        return False				# 兩個字面段，a != b 就是不相交
    if ga != gb:
        # 一literal一 glob：字面段要真能被那個 glob 命中才算
        lit, pat = (b, a) if ga else (a, b)
        if "[" in pat or "?" in pat:
            return True			# 少見形式一律保守當會重疊
        return fnmatch.fnmatchcase(lit, pat)

    def split_glob(s):
        # 只處理我們實際會寫的形式：前綴*、*後綴、*、字面
        if s == "*":
            return "", ""
        if "?" in s or "[" in s:
            return None
        if s.startswith("*") and s.endswith("*"):
            return s[1:-1], s[1:-1]
        if s.endswith("*"):
            return s[:-1], ""
        if s.startswith("*"):
            return "", s[1:]
        return s, s			# 字面段

    ap, asf = split_glob(a)
    bp, bsf = split_glob(b)
    if ap is None or bp is None:
        return True
    return (ap.startswith(bp) or bp.startswith(ap)) and (asf.endswith(bsf) or bsf.endswith(asf))


def patterns(text):
    """回傳 {package 名: [glob 樣式, …]}，含跨行（行尾 \\）的 _pick。"""
    out, cur = {}, None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = FUNC.match(line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, [])
            i += 1
            continue
        m = re.match(r"^\s*_pick\s+(.*)$", line) if cur else None
        if m:
            buf = m.group(1)
            while buf.rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1
                buf = buf.rstrip()[:-1] + " " + lines[i].strip()
            for tok in re.findall(r"'([^']+)'", buf):
                out[cur].append(tok)
        i += 1
    return out


def clash(pa, pb):
    a, b = pa.strip("/").split("/"), pb.strip("/").split("/")
    n, m = len(a), len(b)
    k = min(n, m)
    for x, y in zip(a[:k], b[:k]):
        if not seg_compat(x, y):
            return False
    # 共有的前 k 段全部可命中同一字串。段數不同時，短的那個已被完整匹配，
    # 而 `cp -a usr/share/clang` 是把整棵子目錄搬走 → 一律算重疊。
    # （不必再拿短樣式的末段去比長樣式的下一段：那個末段就是共有段的最後一個，
    #   上面已經比過了；多比一次反而會漏判父子路徑。）
    return True


def main(paths):
    bad = 0
    for path in paths:
        pkgs = patterns(Path(path).read_text(encoding="utf-8"))
        names = [k for k, v in pkgs.items() if v]
        if len(names) < 2:
            continue
        print(f"== {path}：{len(names)} 個有 _pick 的分割包 ==")
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                p, q = names[i], names[j]
                for x in pkgs[p]:
                    for y in pkgs[q]:
                        if clash(x, y):
                            bad += 1
                            print(f"  重疊  {p}: {x}")
                            print(f"        {q}: {y}")
    if bad:
        print(f"FAIL: {bad} 對重疊樣式")
        return 1
    print("OK: 未發現跨包重疊樣式")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or [str(Path.cwd() / "PKGBUILD")]))

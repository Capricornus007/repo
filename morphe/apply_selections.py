#!/usr/bin/env python3
"""把 Morphe Manager 匯出的 selections JSON 套用到 options-create 產生的 options 檔。

用法: apply_selections.py <export.json> <options.json> <package> [<options.json> <package> ...]
每組 options.json + package 對應一個要修補的 app。
"""
import json, sys

def load_export(path):
    with open(path) as f:
        return json.load(f)

def decode_value(v):
    # Manager 把 option 值 JSON 編碼後再嵌進匯出檔，解一層
    try:
        return json.loads(v)
    except Exception:
        return v

def bundle_matches(bundle_patches, selected):
    if not selected:
        return 0
    return sum(1 for p in selected if p in bundle_patches)

def apply(export, options_path, package):
    with open(options_path) as f:
        bundles = json.load(f)
    # 收集匯出檔裡這個 package 的所有 bundle 選擇
    wanted = []  # (bundleName, [patches], {patch: {opt: val}})
    for b in export.get('bundles', []):
        sel = b.get('selections', {}).get(package)
        if not sel:
            continue
        opts = b.get('options', {}).get(package, {})
        wanted.append((b.get('bundleName', '?'), sel, opts))
    if not wanted:
        print('!! 匯出檔裡沒有 %s 的選擇' % package)
        return 1
    used = set()
    missing_total = []
    for name, sel, opts in wanted:
        # 找包含最多所選 patch 的 options bundle
        best_i, best_score = None, 0
        for i, ob in enumerate(bundles):
            if i in used:
                continue
            score = bundle_matches(ob['patches'], sel)
            if score > best_score:
                best_i, best_score = i, score
        if best_i is None or best_score == 0:
            print('!! 找不到對應的 options bundle（%s，%d 個 patch）' % (name, len(sel)))
            missing_total.extend(sel)
            continue
        used.add(best_i)
        ob = bundles[best_i]
        sel_set = set(sel)
        # 先全部關掉，再開所選的（匯出檔是完整選擇）
        for pname, pdata in ob['patches'].items():
            pdata['enabled'] = pname in sel_set
        # 套 option 值
        for pname, popts in opts.items():
            if pname not in ob['patches']:
                print('!! option 對應的 patch 不存在: %s' % pname)
                continue
            tgt = ob['patches'][pname].setdefault('options', {})
            for k, v in popts.items():
                tgt[k] = decode_value(v)
        missing = [p for p in sel if p not in ob['patches']]
        if missing:
            print('!! %s: %d 個所選 patch 在最新版不存在: %s' % (name, len(missing), ', '.join(missing)))
            missing_total.extend(missing)
        print('== %s -> bundle[%d] %s: 開 %d/%d 個 patch' % (name, best_i, ob['meta'].get('source'), len(sel) - len(missing), len(sel)))
    with open(options_path, 'w') as f:
        json.dump(bundles, f, indent=2, ensure_ascii=False)
    if missing_total:
        print('!! 共 %d 個 patch 未套用' % len(missing_total))
    return 0

def main():
    args = sys.argv[1:]
    export = load_export(args[0])
    rc = 0
    i = 1
    while i < len(args):
        options_path, package = args[i], args[i + 1]
        rc |= apply(export, options_path, package)
        i += 2
    sys.exit(rc)

if __name__ == '__main__':
    main()

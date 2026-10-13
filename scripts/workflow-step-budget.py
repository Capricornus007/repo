#!/usr/bin/env python3
"""GitHub Actions 的「含表達式 step ≤ 21000 位元組」本地守門。

為啥要這個：GitHub 的 parser 對**字串值裡帶 `${{ }}` 的模板**有 21000 位元組的硬
上限，踩過就整個 workflow 解析失敗、一個 job 都不起（連日誌都沒有，run 顯示成
`conclusion=failure`、`jobs=0`、名稱直接顯示檔案路徑）。PyYAML 與 actionlint
**都查不出來**，只有 GitHub 自己會講：
    failed to parse workflow: error parsing called workflow ...
    (Line: 49, Col: 14): Exceeded max expression length 21000
（2026-10-13 實測：f5aa969 那輪三條 workflow 全 0 秒紅，就是「初始化 Arch Linux
環境」那步從 20788 長到 21147 bytes。）

三個必須算對的細節：
  · 上限算的是**位元組**不是字元——繁中註解 1 字＝3 bytes。
  · `run: |` 區塊裡的 **shell 註解也計入**（它就是字串本體）。
  · **不含 `${{ }}` 的 step 不受這條限制**（同 job 的「检测目标版本」52249 bytes
    照跑），所以只對模板字串設閘，別亂報。
"""
import os
import subprocess
import sys

LIMIT = 21000
WARN = 19000

try:
    import yaml
except ImportError:
    print('FATAL: 需要 python-yaml（本腳本靠它拿到解析後的字串值）', file=sys.stderr)
    sys.exit(2)


def strings(node):
    """遞迴产出 (路徑, 字串) —— 只有字串值會被 GitHub 當模板展開。"""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)
    elif isinstance(node, str):
        yield node


def workflow_texts(path):
    with open(path, encoding='utf-8') as fh:
        doc = yaml.safe_load(fh)
    return list(strings(doc))


def check(path):
    bad = []
    for s in workflow_texts(path):
        if '${{' not in s:
            continue
        n = len(s.encode('utf-8'))
        if n >= LIMIT:
            bad.append((n, 'RED ', s[:70].replace('\n', '\\n')))
        elif n >= WARN:
            bad.append((n, 'WARN', s[:70].replace('\n', '\\n')))
    for n, level, head in sorted(bad, reverse=True):
        print(f'{level} {path}  模板字串 {n} bytes（上限 {LIMIT}）  開頭: {head}')
    return any(level == 'RED ' for _, level, _ in bad)


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        root = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                              capture_output=True, text=True).stdout.strip()
        wdir = os.path.join(root, '.github', 'workflows')
        files = [os.path.join(wdir, f) for f in sorted(os.listdir(wdir))] if os.path.isdir(wdir) else []
    failed = False
    for f in files:
        if not f.endswith(('.yml', '.yaml')):
            continue
        try:
            failed |= check(f)
        except FileNotFoundError:
            print(f'SKIP {f}（不存在）')
        except yaml.YAMLError as exc:
            print(f'RED {f} YAML 就解析不過：{exc}')
            failed = True
    if not files:
        print('沒找到任何 workflow 檔')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()

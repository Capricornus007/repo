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
import re
import shutil
import subprocess
import sys
import tempfile

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
        # 先驗表達式本體：`${{ }}` 這種空表達式在 **shell 註解裡一樣會被 GitHub 解析**
        # （2026-10-13 實測：我在拆步那段註解寫了「含 `${{ }}` 表達式的 step」，
        #  結果 dispatch 回 `(Line: 250, Col: 14): An expression was expected`，
        #  三條 workflow 又一次一個 job 都不起。PyYAML／actionlint 全綠。）
        for m in re.finditer(r'\$\{\{(.*?)\}\}', s, re.S):
            if not m.group(1).strip():
                print(f'RED {path}  有空表達式 ${{{{}}}}（註解裡也算）：…{s[max(0, m.start()-40):m.start()+20]!r}…')
                bad.append((0, 'RED ', 'empty-expression'))
        # 未閉合：以「每個 `${{` 往後都找得到一個 `}}`」為準。不能直接比對
        # `${{` 與 `}}` 的總數——shell／awk 裡本來就有一堆單獨的 `}}`（實測這樣會誤報）。
        opens = [m.start() for m in re.finditer(r'\$\{\{', s)]
        close_re = re.compile(r'\}\}')
        for pos in opens:
            if not close_re.search(s, pos):
                print(f'RED {path}  表達式沒閉合（offset {pos}）：…{s[pos:pos+40]!r}…')
                bad.append((0, 'RED ', 'unbalanced'))
                break
        if '${{' not in s:
            continue
        n = len(s.encode('utf-8'))
        if n >= LIMIT:
            bad.append((n, 'RED ', s[:70].replace('\n', '\\n')))
        elif n >= WARN:
            bad.append((n, 'WARN', s[:70].replace('\n', '\\n')))
    for n, level, head in sorted(bad, reverse=True):
        if level == 'RED ' and n == 0:
            continue          # 空／未閉合已在上面印過
        print(f'{level} {path}  模板字串 {n} bytes（上限 {LIMIT}）  開頭: {head}')
    return any(level == 'RED ' for _, level, _ in bad)


def check_shell(path):
    """把每個 `run:` 抽出來跑 `bash -n`。

    為啥要這一道：`run: |` 是 YAML **block scalar**，裡面的 shell 對 YAML 而言只是
    一大坨字串——所以「刪掉一個 `case` 分支後多留一個 `;;`」這種錯，PyYAML 綠、
    actionlint 也綠，只有 GitHub 真正把腳本丟給 bash 才炸，而且一炸就是**所有跑到
    該步驟的 job 全紅**（2026-10-19 實測：刪 xlibre 版號分支時把前一個 case 的收尾
    `;;` 多留一份，`/__w/_temp/….sh: line 263: syntax error near unexpected token ';;'`，
    一輪紅掉 8 個 job，日誌還要等 run 結束才取得到）。
    `${{ }}` 先換成佔位字串，否則 bash 會把 `${{` 當成非法參數展開。
    """
    bad = False
    with open(path, encoding='utf-8') as fh:
        doc = yaml.safe_load(fh)
    for jn, job in (doc.get('jobs') or {}).items():
        for st in (job.get('steps') or []):
            script = st.get('run')
            if not isinstance(script, str):
                continue
            shell = st.get('shell')
            if shell and 'bash' not in str(shell):
                continue            # python／sh 等另說，別用 bash 去判
            tmp = os.path.join(tempfile.mkdtemp(prefix='wfsh-'), 's.sh')
            with open(tmp, 'w', encoding='utf-8') as fh2:
                fh2.write(re.sub(r'\$\{\{.*?\}\}', 'X', script, flags=re.S))
            r = subprocess.run(['bash', '-n', tmp], capture_output=True, text=True)
            shutil.rmtree(os.path.dirname(tmp), ignore_errors=True)
            if r.returncode:
                line = (r.stderr.strip().splitlines() or ['(無訊息)'])[-1]
                print(f'RED {path}  job={jn} step={st.get("name", "?")!r} bash 語法錯：{line}')
                bad = True
    return bad


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
            failed |= check_shell(f)
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

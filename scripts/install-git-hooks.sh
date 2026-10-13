#!/usr/bin/env bash
# 把本倉自帶的 git hooks 裝進 .git/hooks。hook 不進版本控制，clone 後要跑一次。
# ⚠️ 本目錄是**多個 AI 代理共用的工作區**，裝 hook 會一起改掉別人的 commit 行為，
#    所以裝之前先 diff 給你看、裝完在溝通檔留一行。
set -euo pipefail
root=$(git rev-parse --show-toplevel)
dest="$root/.git/hooks"
mkdir -p "$dest"
cat > "$dest/pre-commit" <<'HOOK'
#!/usr/bin/env bash
# 1) PKGBUILD 有實質改動但 pkgver/pkgrel 沒動時，自動 pkgrel +1（見 scripts/bump-pkgrel）
"$(git rev-parse --show-toplevel)/scripts/bump-pkgrel" || exit 1

# 2) 改到 workflow 就驗 GitHub 的兩條解析地雷（21000 bytes 模板上限／空表達式）。
#    這條**PyYAML 與 actionlint 都查不出來**，只能自己擋：踩過兩次（2026-10-13 的
#    f5aa969 與 666c28c），症狀都是三條 workflow 0 秒紅、一個 job 都不起，
#    詳見 docs/in-tree-packages.md 文末「21000 上限的精確語意」。
if git diff --cached --name-only | grep -q '^\.github/workflows/.*\.ya?ml$'; then
  exec python3 "$(git rev-parse --show-toplevel)/scripts/workflow-step-budget.py"
fi
HOOK
chmod +x "$dest/pre-commit" "$root/scripts/bump-pkgrel" "$root/scripts/workflow-step-budget.py"
echo "已安裝 pre-commit → bump-pkgrel ＋（有改 workflow 時）workflow-step-budget.py"

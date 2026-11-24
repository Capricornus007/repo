#!/bin/bash
# 六最 setup：从本仓 master raw URL 抓 ci/ 配置、装编译器外掛、翻 makepkg.conf 预设 LTO。
# 抽成独立脚本是因为主 setup step 的 run 块已撞 GitHub 21000 表达式上限。
# 环境：GH_REPO（github.repository）。
set -uo pipefail

# 此處翻的是 /etc/makepkg.conf 的「預設值」——讓沒寫 options 的包默認開 LTO，安全：
# PKGBUILD 自己宣告的 !lto 仍會覆蓋它。與 68456a3 已撤銷的「PKGBUILD 級強制翻轉」
# 不同（後者 run 45062672105 實測 4 紅→11 紅），兩者不可混淆。
sed -i 's/!lto/lto/g' /etc/makepkg.conf
grep -qE '^OPTIONS=\(.*lto' /etc/makepkg.conf || echo 'OPTIONS+=(lto)' >> /etc/makepkg.conf

_ci_base="https://raw.githubusercontent.com/${GH_REPO}/master/ci"
for _try in 1 2 3; do
  curl -sfL --retry 2 "$_ci_base/makepkg-flags.conf" -o /tmp/makepkg-flags.conf \
    && curl -sfL --retry 2 "$_ci_base/gcc-znver3.sh" -o /tmp/gcc-znver3.sh \
    && curl -sfL --retry 2 "$_ci_base/clang-znver3.sh" -o /tmp/clang-znver3.sh \
    && curl -sfL --retry 2 "$_ci_base/pgo-train.sh" -o /tmp/pgo-train.sh \
    && curl -sfL --retry 2 "$_ci_base/pgo-build.sh" -o /tmp/pgo-build.sh \
    && [ -s /tmp/makepkg-flags.conf ] && [ -s /tmp/gcc-znver3.sh ] \
    && [ -s /tmp/clang-znver3.sh ] && [ -s /tmp/pgo-train.sh ] && [ -s /tmp/pgo-build.sh ] && break
  [ "$_try" = 3 ] && { echo "::error::抓不到 ci/ 六最配置（raw URL 3 次失敗）"; exit 1; }
  sleep $((_try * 10))
done
install -d /usr/local/bin
install -m755 /tmp/gcc-znver3.sh /usr/local/bin/gcc-znver3
for c in gcc g++ cc c++; do ln -sf /usr/local/bin/gcc-znver3 "/usr/local/bin/$c"; done
install -m755 /tmp/clang-znver3.sh /usr/local/bin/clang-znver3
for c in clang clang++; do ln -sf /usr/local/bin/clang-znver3 "/usr/local/bin/$c"; done
install -m755 /tmp/pgo-train.sh /usr/local/bin/pgo-train
install -m755 /tmp/pgo-build.sh /usr/local/bin/pgo-build
cat /tmp/makepkg-flags.conf >> /etc/makepkg.conf
sed -i 's/,--as-needed//g; s/ --as-needed//g' /etc/makepkg.conf
sed -i 's|^LDFLAGS="|LDFLAGS="-lm |' /etc/makepkg.conf

#!/usr/bin/env python3
# 六最 2026-11-25：base 納管配方批量生成器（任務#37）
# 鐵律25：MLFS 系統全部必須 pacman 管理。這些工具 LFS 源碼自建、命令在但無主，
# 配方釘系統同版本源碼構建，pacman 接管所有權（非升級）。
# 特例：gcc 用 LFS 式捆綁 gmp/mpfr/mpc/isl（解包進源碼樹改名，不單獨出包）。
import os, textwrap

REPO = "/home/avatar/Downloads/repo"

# (pkgname, version, source_url, depends, makedepends, extra_build, notes)
# source_url 中 {v} = version；None = 特殊處理
GNU = "https://ftp.gnu.org/gnu"
PKGS = [
    # --- GNU 核心工具（autotools 系，標準 configure）---
    ("bash", "5.3.20", f"{GNU}/bash/bash-5.3.20.tar.gz", "", "", ""),
    ("autoconf", "2.73", f"{GNU}/autoconf/autoconf-2.73.tar.xz", "", "", ""),
    ("automake", "1.19", f"{GNU}/automake/automake-1.19.tar.xz", "", "", ""),
    ("bison", "3.8.2", f"{GNU}/bison/bison-3.8.2.tar.xz", "", "", ""),
    ("findutils", "4.11.0", f"{GNU}/findutils/findutils-4.11.0.tar.xz", "", "", ""),
    ("flex", "2.6.4", f"{GNU}/flex/flex-2.6.4.tar.gz", "", "", ""),
    ("gawk", "5.4.1", f"{GNU}/gawk/gawk-5.4.1.tar.xz", "", "", ""),
    ("gettext", "1.0", f"{GNU}/gettext/gettext-1.0.tar.xz", "", "", ""),
    ("grep", "3.12", f"{GNU}/grep/grep-3.12.tar.xz", "", "", ""),
    ("groff", "1.24.2", f"{GNU}/groff/groff-1.24.2.tar.gz", "", "", ""),
    ("gzip", "1.15", f"{GNU}/gzip/gzip-1.15.tar.xz", "", "", ""),
    ("m4", "1.4.21", f"{GNU}/m4/m4-1.4.21.tar.xz", "", "", ""),
    ("make", "4.4.1", f"{GNU}/make/make-4.4.1.tar.gz", "", "", ""),
    ("patch", "2.8.1", f"{GNU}/patch/patch-2.8.1.tar.xz", "", "", ""),
    ("sed", "4.10", f"{GNU}/sed/sed-4.10.tar.xz", "", "", ""),
    ("tar", "1.35", f"{GNU}/tar/tar-1.35.tar.xz", "", "", ""),
    ("texinfo", "7.3", f"{GNU}/texinfo/texinfo-7.3.tar.xz", "", "", ""),
    ("which", "2.23", f"{GNU}/which/which-2.23.tar.gz", "", "", ""),
    ("libtool", "2.6.2", f"{GNU}/libtool/libtool-2.6.2.tar.xz", "", "", ""),
    # --- 非 GNU ---
    ("binutils", "2.47", "https://sourceware.org/pub/binutils/releases/binutils-2.47.tar.xz", "", "", ""),
    ("pkgconf", "3.0.10", "https://distfiles.amperecomputing.com/blfs/pkgconf-3.0.10.tar.gz", "", "", ""),
    ("procps-ng", "4.0.7", "https://sourceforge.net/projects/procps-ng/files/Production/procps-ng-4.0.7.tar.xz", "", "", ""),
    ("psmisc", "23.7", "https://sourceforge.net/projects/psmisc/files/psmisc/psmisc-23.7.tar.xz", "", "", ""),
    ("shadow", "4.19.2", "https://github.com/shadow-maint/shadow/releases/download/4.19.2/shadow-4.19.2.tar.xz", "", "", ""),
    ("iproute2", "7.3.0", "https://www.kernel.org/pub/linux/utils/net/iproute2/iproute2-7.3.0.tar.xz", "", "", ""),
    ("debugedit", "5.2", "https://sourceware.org/pub/debugedit/debugedit-5.2.tar.xz", "", "", ""),
]

TEMPLATE = """# 六最納管 2026-11-25（任務#37，鐵律25）：LFS 同源版本源碼構建，pacman 接管所有權。
# 系統現有同名無主命令（LFS 自建），本包版本釘系統現版本，裝即接管非升級。
pkgname={name}
pkgver={ver}
pkgrel=1
pkgdesc='{name} (LFS 同源構建，六最納管)'
arch=(x86_64)
url='{url}'
license=({license})
{depends_line}{makedepends_line}
source=("{src}")
sha256sums=('SKIP')

build() {{
  cd "{name}-{ver}"
{build}
}}

package() {{
  cd "{name}-{ver}"
  make DESTDIR="$pkgdir" install
}}
"""

def gen_standard(name, ver, url, depends, makedepends, extra):
    build = "  ./configure --prefix=/usr" + (f"\n  {extra}" if extra else "") + "\n  make"
    return TEMPLATE.format(
        name=name, ver=ver, url=url,
        license="GPL-3.0-or-later",
        depends_line=(f"depends=({depends})\n" if depends else ""),
        makedepends_line=(f"makedepends=({makedepends})\n" if makedepends else ""),
        src=url.split("/")[-1], build=build)

def gen_gcc():
    return """# 六最納管 2026-11-25（任務#37）：gcc 16.2.0，LFS 式捆綁 gmp/mpfr/mpc/isl。
# 構建時解包四個依賴進源碼樹改名（LFS 標準做法），不單獨出包。
pkgname=gcc
pkgver=16.2.0
pkgrel=1
pkgdesc='GNU Compiler Collection (LFS 同源構建，六最納管)'
arch=(x86_64)
url='https://gcc.gnu.org'
license=(GPL-3.0-or-later LGPL-3.0-or-later GFDL-1.3-or-later)
makedepends=(binutils)
source=("gcc-16.2.0.tar.xz::https://ftp.gnu.org/gnu/gcc/gcc-16.2.0/gcc-16.2.0.tar.xz"
        "gmp-6.3.0.tar.xz::https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz"
        "mpfr-4.2.2.tar.xz::https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.2.tar.xz"
        "mpc-1.3.1.tar.gz::https://ftp.gnu.org/gnu/mpc/mpc-1.3.1.tar.gz"
        "isl-0.27.tar.xz::https://libisl.sourceforge.io/isl-0.27.tar.xz")
sha256sums=('SKIP' 'SKIP' 'SKIP' 'SKIP' 'SKIP')

prepare() {
  cd gcc-16.2.0
  # LFS 標準：依賴解包進源碼樹改名，gcc 自動內部構建
  tar -xf "$srcdir/gmp-6.3.0.tar.xz" && mv gmp-6.3.0 gmp
  tar -xf "$srcdir/mpfr-4.2.2.tar.xz" && mv mpfr-4.2.2 mpfr
  tar -xf "$srcdir/mpc-1.3.1.tar.gz" && mv mpc-1.3.1 mpc
  tar -xf "$srcdir/isl-0.27.tar.xz" && mv isl-0.27 isl
}

build() {
  cd gcc-16.2.0
  mkdir -p build && cd build
  ../configure --prefix=/usr \
    --enable-languages=c,c++ \
    --disable-multilib \
    --disable-bootstrap \
    --with-system-zlib \
    --enable-default-pie \
    --enable-default-ssp
  make
}

package() {
  cd gcc-16.2.0/build
  make DESTDIR="$pkgdir" install
  # 去掉系統已有的 cc 鏈接衝突：make install 已建 gcc，補 cc → gcc
  ln -sf gcc "$pkgdir/usr/bin/cc"
}
"""

def gen_filesystem():
    return """# 六最納管 2026-11-25（任務#37）：filesystem —— 目錄樹與基礎帳號文件接管。
# 只接管已存在的路徑所有權，不動內容；/etc/passwd 等標記 backup（用戶編輯受保護）。
pkgname=filesystem
pkgver=20261125
pkgrel=1
pkgdesc='Base MLFS filesystem (六最納管：目錄樹所有權)'
arch=(x86_64)
url='https://www.linuxfromscratch.org/lfs/'
license=(custom)
backup=(etc/passwd etc/group etc/shadow etc/gshadow etc/fstab etc/hosts
        etc/hostname etc/hosts.equiv etc/shells)
source=()
sha256sums=()

package() {
  # 目錄樹所有權（已存在，pacman 接管；不存在的補建）
  for d in etc etc/profile.d usr usr/bin usr/lib usr/local var var/log var/spool \\
           run home root tmp mnt media srv opt srv/ftp; do
    install -dm755 "$pkgdir/$d"
  done
  install -dm1777 "$pkgdir/tmp" "$pkgdir/var/tmp"
  install -dm555 "$pkgdir/proc" "$pkgdir/sys" "$pkgdir/dev" 2>/dev/null || true
  # 基礎帳號文件接管（backup 標記保護用戶編輯）
  for f in passwd group shadow gshadow fstab hosts hostname shells; do
    [ -e "/etc/$f" ] && install -m644 "/etc/$f" "$pkgdir/etc/$f"
  done
}
"""

def gen_licenses():
    return """# 六最納管 2026-11-25（任務#37）：licenses —— 常見許可證文本集。
pkgname=licenses
pkgver=20261125
pkgrel=1
pkgdesc='Common licenses (六最納管)'
arch=(any)
url='https://www.gnu.org/licenses/'
license=(custom)
source=()
sha256sums=()

package() {
  install -dm755 "$pkgdir/usr/share/licenses/common"
  # GPL-3.0 全文（GNU 官方）
  curl -fsSL "https://www.gnu.org/licenses/gpl-3.0.txt" \\
    -o "$pkgdir/usr/share/licenses/common/GPL-3.0" || true
  curl -fsSL "https://www.gnu.org/licenses/lgpl-3.0.txt" \\
    -o "$pkgdir/usr/share/licenses/common/LGPL-3.0" || true
  curl -fsSL "https://www.gnu.org/licenses/fdl-1.3.txt" \\
    -o "$pkgdir/usr/share/licenses/common/GFDL-1.3" || true
}
"""

def main():
    os.makedirs(f"{REPO}/base-naguan", exist_ok=True)
    count = 0
    for name, ver, url, depends, makedepends, extra in PKGS:
        d = f"{REPO}/base-naguan/{name}"
        os.makedirs(d, exist_ok=True)
        content = gen_standard(name, ver, url, depends, makedepends, extra)
        with open(f"{d}/PKGBUILD", "w") as f:
            f.write(content)
        count += 1
    # 特殊包
    for name, content in (("gcc", gen_gcc()), ("filesystem", gen_filesystem()), ("licenses", gen_licenses())):
        d = f"{REPO}/base-naguan/{name}"
        os.makedirs(d, exist_ok=True)
        with open(f"{d}/PKGBUILD", "w") as f:
            f.write(content)
        count += 1
    print(f"生成 {count} 個配方於 {REPO}/base-naguan/")

if __name__ == "__main__":
    main()

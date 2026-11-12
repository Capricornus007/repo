# Maintainer: Evangelos Foutras <foutrelis@archlinux.org>
# Contributor: Jan Alexander Steffens (heftig) <heftig@archlinux.org>

pkgname=lib32-clang
pkgver=23.1.1
pkgrel=1
pkgdesc="C language family frontend for LLVM (32-bit)"
arch=('x86_64')
url="https://clang.llvm.org/"
license=('Apache-2.0 WITH LLVM-exception')
depends=('lib32-llvm-libs' 'clang')
makedepends=("lib32-llvm=1:$pkgver" 'cmake' 'ninja' 'python')
optdepends=('lib32-llvm: referenced by some clang headers')
_source_base=https://github.com/llvm/llvm-project/releases/download/llvmorg-$pkgver
source=($_source_base/llvm-project-$pkgver.src.tar.xz{,.sig}
        0001-Revert-clang-driver-When-fveclib-ArmPL-flag-is-in-us.patch
        enable-fstack-protector-strong-by-default.patch)
sha256sums=('ebe9be46fe8756d58c5b198ffad0fa2a766257add81a4dc52179bfacc7888ee6'
            'SKIP'
            '94baa1ca8b7f68c2c22b4d4c429d4560f81f882c00299f6b5398ffe6dc3a3913'
            '89e36fcc53383bbfa51da820c96d4ae136e060ac55ee53c914888a37e52be06c')
validpgpkeys=('474E22316ABF4785A88C6E8EA2C794A986419D8A'  # Tom Stellard <tstellar@redhat.com>
              'D574BD5D1D0E98895E3BF90044F2485E45D59042'  # Tobias Hieta <tobias@hieta.se>
              'FFB3368980F3E6BB5737145A316C56D064CACBA5'  # Douglas Yung <douglas.yung@sony.com>
              '71046D1E9C6656BDD61171873E83BABF4A4F9E85'  # Cullen Rhodes <cullen.rhodes@arm.com>
)

# Utilizing LLVM_DISTRIBUTION_COMPONENTS to avoid
# installing static libraries; inspired by Gentoo
_get_distribution_components() {
  local target
  ninja -t targets | grep -Po 'install-\K.*(?=-stripped:)' | while read -r target; do
    case $target in
      clang-libraries|distribution)
        continue
        ;;
      clang|clangd|clang-*)
        ;;
      clang*|findAllSymbols|scan-build-py)
        continue
        ;;
    esac
    echo $target
  done
}

prepare() {
  cd llvm-project-$pkgver.src/clang
  mkdir build
  patch -Np2 -i "$srcdir/enable-fstack-protector-strong-by-default.patch"

  # Revert always linking against libamath when -fveclib=ArmPL
  patch -Np2 -i "$srcdir/0001-Revert-clang-driver-When-fveclib-ArmPL-flag-is-in-us.patch"
}

build() {
  cd llvm-project-$pkgver.src/clang/build

  # Build only minimal debug info to reduce size
  CFLAGS=${CFLAGS/-g /-g1 }
  CXXFLAGS=${CXXFLAGS/-g /-g1 }

  local cmake_args=(
    -G Ninja
    -DCMAKE_BUILD_TYPE=Release
    -DCMAKE_INSTALL_PREFIX=/usr
    -DCMAKE_INSTALL_DOCDIR=share/doc
    -DCMAKE_SKIP_RPATH=ON
    -DCLANG_DEFAULT_PIE_ON_LINUX=ON
    -DCLANG_LINK_CLANG_DYLIB=ON
    -DENABLE_LINKER_BUILD_ID=ON
    -DLLVM_CONFIG=llvm-config32
    -DLLVM_ENABLE_RTTI=ON
    -DLLVM_EXTERNAL_CLANG_TOOLS_EXTRA_SOURCE_DIR=
    -DLLVM_INCLUDE_DOCS=OFF
    -DLLVM_INCLUDE_TESTS=OFF
    -DLLVM_LIBDIR_SUFFIX=32
    -DLLVM_LINK_LLVM_DYLIB=ON
    -DLLVM_THIRD_PARTY_DIR="$srcdir/llvm-project-$pkgver.src/third-party"
    -DLLVM_PACKAGE_BUGREPORT=https://gitlab.archlinux.org/archlinux/packaging/packages/lib32-clang/-/issues
  )

  export CFLAGS+=" -m32"
  export CXXFLAGS+=" -m32"
  export PKG_CONFIG="i686-pc-linux-gnu-pkg-config"

  cmake .. "${cmake_args[@]}"
  local distribution_components=$(_get_distribution_components | paste -sd\;)
  test -n "$distribution_components"
  cmake_args+=(-DLLVM_DISTRIBUTION_COMPONENTS="$distribution_components")

  cmake .. "${cmake_args[@]}"
  ninja
}

package() {
  cd llvm-project-$pkgver.src/clang/build

  DESTDIR="$pkgdir" ninja install-distribution
  rm -rf "$pkgdir"/usr/{bin,include,lib,libexec,share}

  install -Dm644 "$srcdir/llvm-project-$pkgver.src/clang/LICENSE.TXT" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}

# vim:set ts=2 sw=2 et:

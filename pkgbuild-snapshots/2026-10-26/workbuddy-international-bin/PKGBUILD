# Maintainer: local build
# Unofficial Linux port of the WorkBuddy AI international (workbuddy.ai) macOS client.
# Conversion toolchain vendored from the MIT-licensed workbuddy-linux community
# project (see LICENSE.port-tool). Not affiliated with Tencent. See DISCLAIMER.

pkgname=workbuddy-international-bin
_pkgver=5.8.4.41366630
_build=73952edb
_electronver=37.10.3
pkgver=${_pkgver}_${_build}
# pkgrel 2: the shipped app.asar now carries the workbuddyStorage at-rest shim
# (Fix 7 in lib-apply-linux-patches.js). Without it every agent session child
# exits within ~400ms on 5.8.x and the app looks "installed but unusable".
pkgrel=2
pkgdesc="AI Agent for everyday office work (international edition, unofficial Linux port)"
arch=('x86_64')
url="https://www.workbuddy.ai"
license=('custom')
depends=('libsecret' 'libappindicator-gtk3' 'nss' 'alsa-lib' 'gtk3' 'libxss')
makedepends=('nodejs' 'npm' 'p7zip' 'unzip' 'python' 'imagemagick' 'file')
optdepends=('nodejs-lts: frontend skills'
            'gnome-shell-extension-appindicator: tray icon support')
options=(!strip !debug)

# The international edition publishes no Linux package; the macOS x64 DMG is the
# canonical source. Version and DMG sha256 are published by the official update
# API:  curl 'https://www.workbuddy.ai/v2/update?platform=workbuddy-darwin-x64'
# The Electron runtime version matches the one bundled in the DMG.
_dmg="WorkBuddy-darwin-x64-${_pkgver}-${_build}.dmg"
_electronzip="electron-v${_electronver}-linux-x64.zip"
source=("${_dmg}::https://codebuddy-1328495429.cos.accelerate.myqcloud.com/workbuddy/saas/darwin-x64/WorkBuddy-darwin-x64-${_pkgver}-${_build}.dmg"
        "${_electronzip}::https://github.com/electron/electron/releases/download/v${_electronver}/${_electronzip}"
        "workbuddy-international.desktop")
sha256sums=('8404d7eeb2653ec49ca3f3bce4b69fd101ecf60bd1fd9f8472181108a11aa63e'
            'c0b4edd6bd9858cda4cf7ab299e69a2d3ecd2e5fcca78507bc0851ba35614660'
            '6fcbfa4cba8e730e603b68fcca484c7963aacdaf56a3f6c5c47ff320a5189e85')

prepare() {
    # Extract the .app bundle out of the DMG
    rm -rf "${srcdir}/dmg"
    mkdir -p "${srcdir}/dmg"
    7z x -o"${srcdir}/dmg" "${srcdir}/${_dmg}" -y >/dev/null
}

build() {
    # Run the vendored conversion toolchain: use the pre-seeded Linux Electron
    # runtime, rebuild native modules for Linux, apply runtime patches.
    # Fixes 1-6 are anchor-tolerant (5.8.x already carries the E2BIG/tray work
    # upstream, so they are no-ops here); Fix 7 (workbuddyStorage at-rest shim)
    # is mandatory on 5.8+ and aborts the build if its anchor drifts.
    export WORKBUDDY_APP_ID="WorkBuddy AI"
    export WORKBUDDY_APP_DISPLAY_NAME="WorkBuddy AI (International)"
    export WORKBUDDY_INSTALL_DIR="${srcdir}/workbuddy-app"
    export WORKBUDDY_ELECTRON_ZIP="${srcdir}/${_electronzip}"
    local app_bundle
    app_bundle="$(find "${srcdir}/dmg" -maxdepth 2 -name "*.app" -type d | head -1)"
    bash "${startdir}/install.sh" "${app_bundle}"
}

check() {
    # Two cheap, display-free assertions on the tree that is about to be
    # packaged. Both catch the class of bug that used to ship silently:
    # an archive that builds, installs and opens a window, but cannot start a
    # single agent session.
    local app="${srcdir}/workbuddy-app"
    local asar="${app}/resources/app.asar"
    local cli="${app}/resources/app.asar.unpacked/cli/bin/codebuddy"

    # 1. The CLI child the desktop app spawns for every conversation must boot
    #    under the shipped Linux Electron (same ELECTRON_RUN_AS_NODE invocation
    #    the sidecar uses). A rebuilt native module with the wrong ABI, or an
    #    asar header that lost an unpacked entry, fails right here.
    [[ -x "${cli}" ]] || { error "cli/bin/codebuddy is missing or not executable"; return 1; }
    local cli_version
    cli_version="$(ELECTRON_RUN_AS_NODE=1 "${app}/electron" "${cli}" --version 2>&1)" || {
        error "bundled agent CLI does not start: ${cli_version}"
        return 1
    }
    msg2 "bundled agent CLI reports ${cli_version}"

    # 2. 5.8+ demands the at-rest credential key from the *vendor's* patched
    #    Electron (electron.workbuddyStorage). Stock Linux Electron has no such
    #    API, so lib-apply-linux-patches.js must have injected a replacement
    #    provider; without it every session child is killed ~400ms after spawn
    #    with "credential bootstrap did not configure required capabilities".
    if grep -qa 'workbuddyStorage' "${asar}"; then
        grep -qa '__WB_LINUX_ATREST_SHIM_V1__' "${asar}" || {
            error "app.asar still calls the vendor-only electron.workbuddyStorage;"
            error "the Linux at-rest shim (Fix 7) was not applied"
            return 1
        }
        msg2 "workbuddyStorage at-rest shim present in app.asar"
    fi
    return 0
}

package() {
    install -dm755 "${pkgdir}/opt/workbuddy-international"
    cp -a "${srcdir}/workbuddy-app/." "${pkgdir}/opt/workbuddy-international/"

    # The helper desktop file written by install.sh embeds the build-time
    # srcdir in Exec=; point it at the final install location instead.
    sed -i "s|${srcdir}/workbuddy-app|/opt/workbuddy-international|g" \
        "${pkgdir}/opt/workbuddy-international/.workbuddy-linux/WorkBuddy AI.desktop" 2>/dev/null || true

    # Desktop entry: named exactly after the app's Wayland app_id ("WorkBuddy AI")
    # so the task manager associates windows with this entry and its icon.
    install -Dm644 "${startdir}/workbuddy-international.desktop" \
        "${pkgdir}/usr/share/applications/WorkBuddy AI.desktop"

    # Icons: theme-integrated hicolor entry plus pixmaps fallback
    install -Dm644 "${srcdir}/workbuddy-app/.workbuddy-linux/workbuddy.png" \
        "${pkgdir}/usr/share/icons/hicolor/256x256/apps/workbuddy-international.png"
    install -Dm644 "${srcdir}/workbuddy-app/.workbuddy-linux/workbuddy.png" \
        "${pkgdir}/usr/share/pixmaps/workbuddy-international.png"

    # Launcher
    install -dm755 "${pkgdir}/usr/bin"
    cat > "${pkgdir}/usr/bin/workbuddy-international" <<'EOF'
#!/usr/bin/env bash
exec /opt/workbuddy-international/start.sh "$@"
EOF
    chmod 755 "${pkgdir}/usr/bin/workbuddy-international"

    # Licenses / notices
    install -Dm644 "${startdir}/LICENSE.port-tool" \
        "${pkgdir}/usr/share/licenses/workbuddy-international/LICENSE.port-tool"
    install -Dm644 "${startdir}/DISCLAIMER" \
        "${pkgdir}/usr/share/licenses/workbuddy-international/DISCLAIMER"

    _verify_package_payload
}

# The conversion toolchain deletes every macOS/Windows binary and then has to
# replace the ones the app actually loads. If that replacement silently does
# not happen, the tarball is still produced and yay goes straight to "Install?"
# even though the app cannot start. Fail here instead, so makepkg aborts before
# the install prompt.
_verify_package_payload() {
    local appdir="${pkgdir}/opt/workbuddy-international"
    local asar="${appdir}/resources/app.asar"
    local upstream="${_pkgver%.*}"
    local f rel magic missing=0

    _fail() {
        error "payload verification failed: $*"
        exit 1
    }

    # `file(1)` crashes under fakeroot (invalid syscall), so sniff magic bytes
    # instead: 7f454c46=ELF, feedface/feedfacf/cefaedfe/cffaedfe=Mach-O,
    # cafebabe/bebafeca=fat Mach-O, 4d5a=PE/Windows.
    _magic() {
        od -An -tx1 -N4 "$1" 2>/dev/null | tr -d ' \n'
    }
    _is_elf() {
        [[ "$(_magic "$1")" == "7f454c46" ]]
    }

    # App payload present and plausible in size (5.5+/5.8.x are ~90 MB)
    [[ -s "${asar}" ]] || _fail "resources/app.asar missing or empty"
    (( $(stat -c%s "${asar}") > 20000000 )) \
        || _fail "resources/app.asar is only $(stat -c%s "${asar}") bytes"

    # The repack must not silently duplicate the sidecar back into the archive.
    # @electron/asar re-packs anything its glob does not match, and on 5.8.4
    # that inflated app.asar from 96 MB to 198 MB. Compare against the archive
    # that came out of the DMG: only the injected shim may be added on top.
    local upstream_asar upstream_asar_size asar_size
    upstream_asar="$(find "${srcdir}/dmg" -maxdepth 6 -path "*Contents/Resources/app.asar" -type f 2>/dev/null | head -1)"
    if [[ -n "${upstream_asar}" ]]; then
        upstream_asar_size=$(stat -c%s "${upstream_asar}")
        asar_size=$(stat -c%s "${asar}")
        (( asar_size <= upstream_asar_size * 11 / 10 )) \
            || _fail "packed app.asar is ${asar_size} bytes vs ${upstream_asar_size} upstream: repack churned the archive"
    fi

    # Launcher chain
    [[ -x "${appdir}/start.sh" ]] || _fail "start.sh missing or not executable"
    [[ -f "${appdir}/electron" ]] || _fail "electron runtime missing"
    _is_elf "${appdir}/electron" || _fail "electron runtime is not a Linux ELF binary"

    # Every native module the app loads must exist as a Linux ELF binary
    # (os-bridge is new in 5.8.x: the vendor prebuilds it per platform and the
    # darwin copy is deleted by the toolchain, so it is easy to lose silently).
    for rel in \
        resources/app.asar.unpacked/node_modules/better-sqlite3/build/Release/better_sqlite3.node \
        resources/app.asar.unpacked/node_modules/node-pty/build/Release/pty.node \
        resources/app.asar.unpacked/node_modules/koffi/build/koffi/linux_x64/koffi.node \
        resources/app.asar.unpacked/node_modules/@ban-dal/os-bridge-linux-x64-gnu/os-bridge.linux-x64-gnu.node \
        resources/app.asar.unpacked/cli/vendor/ripgrep/x64-linux/rg
    do
        f="${appdir}/${rel}"
        if [[ ! -s "${f}" ]]; then
            warning "missing: ${rel}"
            missing=1
        elif ! _is_elf "${f}"; then
            warning "not a Linux ELF binary: ${rel} (magic $(_magic "${f}"))"
            missing=1
        fi
    done
    (( missing == 0 )) || _fail "native payload incomplete (see warnings above)"

    # macOS/Windows leftovers are dead weight, not breakage: report them but do
    # not fail the build (node-pty's npm tarball ships them again after Phase 3).
    while IFS= read -r f; do
        magic="$(_magic "${f}")"
        case "${magic}" in
            feedface|feedfacf|cefaedfe|cffaedfe|cafebabe|bebafeca)
                warning "Mach-O binary packaged: ${f#"${appdir}/"}" ;;
            4d5a*)
                warning "PE binary packaged: ${f#"${appdir}/"}" ;;
        esac
    done < <(find "${appdir}" -type f \( -name '*.node' -o -name '*.so' -o -name '*.dylib' -o -name '*.dll' \) 2>/dev/null)

    # The Linux runtime patches are applied by repacking app.asar. If that
    # repack failed, install.sh only warns and the raw macOS asar is shipped
    # (no window / empty tray) - that must not be installed.
    [[ -s "${appdir}/.workbuddy-linux/patches-applied" ]] \
        || _fail "app.asar repack did not complete (Linux runtime patches not applied)"

    # The 5.8.x regression, checked against the file that actually ships:
    # the app reads the at-rest credential key from electron.workbuddyStorage,
    # an API that only exists in Tencent's own Electron fork. Upstream publishes
    # no Linux build past 5.5.2 (v2/update?platform=workbuddy-linux-x64-deb is
    # frozen), so this port always runs a stock runtime and must carry the
    # replacement provider. If it is missing the window opens but every agent
    # session child exits in ~400ms with "capability-missing".
    if grep -qa 'workbuddyStorage' "${asar}" && \
       ! grep -qa '__WB_LINUX_ATREST_SHIM_V1__' "${asar}"; then
        _fail "app.asar uses the vendor-only electron.workbuddyStorage without the Linux at-rest shim"
    fi
    if compgen -G "${appdir}/resources/app.asar.new*" >/dev/null \
        || compgen -G "${appdir}/resources/app.asar.prepatch" >/dev/null; then
        _fail "staging leftovers from a failed asar repack were packaged"
    fi

    # Metadata must describe the version we claim to build
    grep -q "\"upstreamVersion\": \"${upstream}\"" \
        "${appdir}/.workbuddy-linux/build-info.json" 2>/dev/null \
        || _fail "build-info.json does not report upstreamVersion ${upstream}"

    # Desktop integration
    [[ -s "${pkgdir}/usr/share/applications/WorkBuddy AI.desktop" ]] \
        || _fail "desktop entry missing"
    [[ -s "${pkgdir}/usr/share/icons/hicolor/256x256/apps/workbuddy-international.png" ]] \
        || _fail "icon missing"
    [[ -x "${pkgdir}/usr/bin/workbuddy-international" ]] \
        || _fail "launcher wrapper missing"
}

#!/usr/bin/env python3
"""In-tree fixes applied to nornzach/oh-my-pi-gui main HEAD before building.

Two independent things, both requested by the user on 2026-11-12:

1. GUI/CLI freeze when deleting a provider. ProviderConfigDialog used to
   `await refreshProviders(true)` after every delete AND every save. That sends
   `get_providers {forceRefresh:true}` to the bundled sidecar, which triggers a
   full discovery sweep over every configured provider (the user's models.yml
   has 41 providers / ~4000 models). The sidecar's RPC queue is serial, so the
   dialog, the rest of the GUI and the embedded CLI all sit there with no
   response until the sweep times out. We keep the cache-aware refresh but make
   it fire-and-forget; the catalog push / ProvidersWindow poll converges later.

2. Chinese was Simplified-only (`zh` -> zh-CN). Add a Taiwan Traditional
   Chinese (`zh-TW`) catalog as a first-class language, including the Electron
   native menus, tray, settings schema labels and schema enum labels. zh-TW is
   the base per the user's standing rule; the existing zh-CN file is untouched.

Every replacement is asserted to match exactly once: if upstream moves the
code, the build fails loudly instead of silently shipping a half-fixed app.
"""

import shutil
import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"FATAL [{label}]: expected 1 match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"  ok  {label}")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: omp-gui-fixes.py <source-root> <assets-dir>")
    root, assets = Path(sys.argv[1]), Path(sys.argv[2])
    print(f"omp-gui-fixes: root={root} assets={assets}")

    # ---- 1. shared language registry -------------------------------------
    lang = root / "src/shared/languages.ts"
    replace_once(
        lang,
        '''export const LANGUAGES = [
\t{ id: "en", name: "English", short: "EN", locale: "en-US" },
\t{ id: "ru", name: "Русский", short: "RU", locale: "ru-RU" },
\t{ id: "zh", name: "中文", short: "中文", locale: "zh-CN" },
] as const;''',
        '''export const LANGUAGES = [
\t{ id: "en", name: "English", short: "EN", locale: "en-US" },
\t{ id: "ru", name: "Русский", short: "RU", locale: "ru-RU" },
\t{ id: "zh", name: "简体中文", short: "简中", locale: "zh-CN" },
\t{ id: "zh-TW", name: "繁體中文", short: "繁中", locale: "zh-TW" },
] as const;''',
        "languages: add zh-TW",
    )
    replace_once(
        lang,
        '''export function languageFromLocale(locale: string): Language {
\tconst base = locale.toLowerCase().split(/[-_]/)[0];
\treturn isLanguage(base) ? base : "en";
}''',
        '''export function languageFromLocale(locale: string): Language {
\tconst lower = locale.toLowerCase();
\t// zh-TW / zh-HK / zh-Hant must land on the Traditional catalog. A bare
\t// "zh" still resolves to the Simplified one so older persisted prefs stay valid.
\tif (/^zh[-_](tw|hk|hant)/.test(lower)) return "zh-TW";
\tconst base = lower.split(/[-_]/)[0];
\treturn isLanguage(base) ? base : "en";
}''',
        "languages: locale detection",
    )

    # ---- 2. renderer i18n registry --------------------------------------
    i18n = root / "src/renderer/lib/i18n.tsx"
    replace_once(
        i18n,
        'import { zh } from "../locales/zh";',
        'import { zh } from "../locales/zh";\nimport { zhTW } from "../locales/zh-TW";',
        "i18n: import zh-TW",
    )
    replace_once(
        i18n,
        "const LOCALES: Record<Lang, Locale> = { en, ru, zh };",
        'const LOCALES: Record<Lang, Locale> = { en, ru, zh, "zh-TW": zhTW };',
        "i18n: register locale",
    )

    # ---- 3. settings schema localization --------------------------------
    (root / "src/renderer/components/settings/schema-localization.ts").write_text(
        '''import type { Language } from "../../../shared/languages";
import { RU_SCHEMA_OPTION_TEXT } from "./schema-option-ru";
import { ZH_SCHEMA_OPTION_TEXT } from "./schema-option-zh";
import { ZH_TW_SCHEMA_OPTION_TEXT } from "./schema-option-zh-TW";
import { RU_GROUP_TITLES, RU_SETTINGS } from "./schema-ru";
import { ZH_GROUP_TITLES, ZH_SETTINGS } from "./schema-zh";
import { ZH_TW_GROUP_TITLES, ZH_TW_SETTINGS } from "./schema-zh-TW";

export function settingTranslation(language: Language, path: string) {
\tif (language === "ru") return RU_SETTINGS[path];
\tif (language === "zh-TW") return ZH_TW_SETTINGS[path];
\tif (language === "zh") return ZH_SETTINGS[path];
\treturn undefined;
}

export function schemaGroupTitle(language: Language, title: string): string {
\tconst titles =
\t\tlanguage === "ru"
\t\t\t? RU_GROUP_TITLES
\t\t\t: language === "zh-TW"
\t\t\t\t? ZH_TW_GROUP_TITLES
\t\t\t\t: language === "zh"
\t\t\t\t\t? ZH_GROUP_TITLES
\t\t\t\t\t: undefined;
\treturn titles?.[title] ?? title;
}

export function schemaOptionText(language: Language, text: string): string {
\tconst options =
\t\tlanguage === "ru"
\t\t\t? RU_SCHEMA_OPTION_TEXT
\t\t\t: language === "zh-TW"
\t\t\t\t? ZH_TW_SCHEMA_OPTION_TEXT
\t\t\t\t: language === "zh"
\t\t\t\t\t? ZH_SCHEMA_OPTION_TEXT
\t\t\t\t\t: undefined;
\treturn options?.[text] ?? text;
}
''',
        encoding="utf-8",
    )
    print("  ok  schema-localization: zh-TW dictionaries")

    utils = root / "src/renderer/components/settings/settings-schema-utils.ts"
    replace_once(
        utils,
        'import { ZH_SETTINGS } from "./schema-zh";',
        'import { ZH_SETTINGS } from "./schema-zh";\nimport { ZH_TW_SETTINGS } from "./schema-zh-TW";',
        "settings search: import",
    )
    replace_once(
        utils,
        '''\tconst zh = ZH_SETTINGS[entry.path];
\tconst ru = RU_SETTINGS[entry.path];
\tconst haystack = [entry.path, entry.label, entry.description, zh?.label, zh?.description, ru?.label, ru?.description]''',
        '''\tconst zh = ZH_SETTINGS[entry.path];
\tconst zhTw = ZH_TW_SETTINGS[entry.path];
\tconst ru = RU_SETTINGS[entry.path];
\tconst haystack = [entry.path, entry.label, entry.description, zh?.label, zh?.description, zhTw?.label, zhTw?.description, ru?.label, ru?.description]''',
        "settings search: include zh-TW labels",
    )

    # ---- 4. Electron native menus / tray --------------------------------
    main_i18n = root / "src/main/i18n.ts"
    replace_once(
        main_i18n,
        'import { RU_MAIN_TEXT } from "./native-ru";',
        'import { RU_MAIN_TEXT } from "./native-ru";\nimport { ZH_TW_MAIN_TEXT } from "./native-zh-TW";',
        "native menus: import",
    )
    replace_once(
        main_i18n,
        'const TEXT: Record<MainTextKey, Record<Exclude<MainLanguage, "ru">, string>> = {',
        'const TEXT: Record<MainTextKey, Record<Exclude<MainLanguage, "ru" | "zh-TW">, string>> = {',
        "native menus: type",
    )
    replace_once(
        main_i18n,
        '\tconst text = language === "ru" ? RU_MAIN_TEXT[key] : TEXT[key][language];',
        '\tconst text =\n\t\tlanguage === "ru"\n\t\t\t? RU_MAIN_TEXT[key]\n\t\t\t: language === "zh-TW"\n\t\t\t\t? ZH_TW_MAIN_TEXT[key]\n\t\t\t\t: TEXT[key][language];',
        "native menus: lookup",
    )
    tray = root / "src/main/tray-labels.ts"
    replace_once(
        tray,
        'import { RU_TRAY_TEXT } from "./native-ru";',
        'import { RU_TRAY_TEXT } from "./native-ru";\nimport { ZH_TW_TRAY_TEXT } from "./native-tray-zh-TW";',
        "tray: import",
    )
    replace_once(
        tray,
        '\treturn lang === "ru" ? RU_TRAY_TEXT[key] : TRAY_LABELS[key][lang];',
        '''\tif (lang === "ru") return RU_TRAY_TEXT[key];
\tif (lang === "zh-TW") return ZH_TW_TRAY_TEXT[key];
\treturn TRAY_LABELS[key][lang as "en" | "zh"];''',
        "tray: lookup",
    )

    # ---- 5. freeze fix: no blocking forced discovery on mutations -------
    dialog = root / "src/renderer/components/settings/ProviderConfigDialog.tsx"
    replace_once(
        dialog,
        '''\t\t\tawait window.omp.models.deleteProvider(pendingDelete.id);
\t\t\ttry {
\t\t\t\tawait refreshProviders(true);
\t\t\t} catch (cause) {
\t\t\t\ttoast({
\t\t\t\t\tvariant: "warning",
\t\t\t\t\ttitle: t("providerCfg.toast.refreshFailed"),
\t\t\t\t\tmessage: describeError(cause),
\t\t\t\t});
\t\t\t}''',
        '''\t\t\tawait window.omp.models.deleteProvider(pendingDelete.id);
\t\t\t// A forced catalog discovery sweeps every configured provider over the
\t\t\t// network. The sidecar's RPC queue is serial, so awaiting it here froze
\t\t\t// the dialog, the rest of the GUI and the embedded CLI for minutes.
\t\t\t// Read from the cache in the background; model_catalog_update pushes
\t\t\t// (and ProvidersWindow's refreshPending poll) converge the list later.
\t\t\tvoid refreshProviders().catch(() => {});''',
        "freeze fix: delete provider",
    )
    replace_once(
        dialog,
        '''\t\t\ttry {
\t\t\t\tconst catalog = await refreshProviders(true);
\t\t\t\tconst discoveryError = catalog.discoveryStates.find(
\t\t\t\t\tstate => state.provider === input.id && state.status === "unavailable",
\t\t\t\t);
\t\t\t\tif (discoveryError) {
\t\t\t\t\ttoast({
\t\t\t\t\t\tvariant: "warning",
\t\t\t\t\t\ttitle: t("providerCfg.toast.refreshFailed"),
\t\t\t\t\t\tmessage: discoveryError.error ?? t("providers.discoveryUnavailable"),
\t\t\t\t\t});
\t\t\t\t}
\t\t\t} catch (cause) {
\t\t\t\ttoast({
\t\t\t\t\tvariant: "warning",
\t\t\t\t\ttitle: t("providerCfg.toast.refreshFailed"),
\t\t\t\t\tmessage: describeError(cause),
\t\t\t\t});
\t\t\t}''',
        '''\t\t\t// Keep the save dialog responsive: never await a forced discovery here.
\t\t\tvoid refreshProviders()
\t\t\t\t.then(catalog => {
\t\t\t\t\tconst discoveryError = catalog.discoveryStates.find(
\t\t\t\t\t\tstate => state.provider === input.id && state.status === "unavailable",
\t\t\t\t\t);
\t\t\t\t\tif (discoveryError) {
\t\t\t\t\t\ttoast({
\t\t\t\t\t\t\tvariant: "warning",
\t\t\t\t\t\t\ttitle: t("providerCfg.toast.refreshFailed"),
\t\t\t\t\t\t\tmessage: discoveryError.error ?? t("providers.discoveryUnavailable"),
\t\t\t\t\t\t});
\t\t\t\t\t}
\t\t\t\t})
\t\t\t\t.catch(cause => {
\t\t\t\t\ttoast({
\t\t\t\t\t\tvariant: "warning",
\t\t\t\t\t\ttitle: t("providerCfg.toast.refreshFailed"),
\t\t\t\t\t\tmessage: describeError(cause),
\t\t\t\t\t});
\t\t\t\t});''',
        "freeze fix: save provider",
    )

    # ---- 6. ship generated catalogs -------------------------------------
    copies = {
        "zh-TW.ts": "src/renderer/locales/zh-TW.ts",
        "schema-zh-TW.ts": "src/renderer/components/settings/schema-zh-TW.ts",
        "schema-option-zh-TW.ts": "src/renderer/components/settings/schema-option-zh-TW.ts",
        "native-zh-TW.ts": "src/main/native-zh-TW.ts",
        "native-tray-zh-TW.ts": "src/main/native-tray-zh-TW.ts",
    }
    for name, dest in copies.items():
        src = assets / name
        if not src.is_file():
            raise SystemExit(f"FATAL: missing asset {src}")
        target = root / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        print(f"  ok  installed {dest}")

    # ---- 7. self-check ---------------------------------------------------
    checks = {
        "zh-TW registered": ('"zh-TW", name: "繁體中文"' in lang.read_text(encoding="utf-8")),
        "no forced refresh in dialog": ("refreshProviders(true)" not in dialog.read_text(encoding="utf-8")),
        "renderer locale wired": ('"zh-TW": zhTW' in i18n.read_text(encoding="utf-8")),
        "native menu wired": ("ZH_TW_MAIN_TEXT[key]" in main_i18n.read_text(encoding="utf-8")),
        "tray wired": ("ZH_TW_TRAY_TEXT[key]" in tray.read_text(encoding="utf-8")),
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise SystemExit("FATAL: self-check failed: " + ", ".join(failed))
    for k in checks:
        print(f"  ok  check: {k}")
    print("omp-gui-fixes: all patches applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

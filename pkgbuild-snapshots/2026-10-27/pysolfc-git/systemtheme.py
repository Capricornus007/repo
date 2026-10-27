#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Follow the desktop palette (KDE/Qt/Kvantum kdeglobals, or GTK css) for the
Tk widgets, instead of PySol's hard-coded light-grey Motif look.

Why this exists: pysollib/winsystems/x11.py used to do

    root.tk_setPalette(<clam's own grey>)
    root.option_add('*Listbox.background', 'white')
    root.option_add('*selectBackground', '#0a5f89')

i.e. every Tk app on a dark desktop still looked like Windows 95. Nothing here
needs a third-party theme pack (``ttkthemes`` is not packaged in Arch/Artix),
it only recolors the ttk themes that ship with Tk itself.

Precedence for the palette:
  1. ~/.config/kdeglobals  [Colors:*]      (KDE/Qt, incl. Kvantum colour schemes)
  2. ~/.config/gtk-3.0/colors.css          (user-level GTK overrides)
  3. <theme dir>/gtk-3.0/gtk-3.0/gtk.css or colors.css, plus
     gtk-2.0/gtkrc of the same theme       (Adwaita-dark, Layan-Dark, ...)
  4. fall back to whatever Tk already had (we do nothing).
"""
import configparser
import os
import re

__all__ = ('read_palette', 'apply', 'reset', 'is_dark')

KEYS = (
    'background',        # windows / dialogs
    'foreground',
    'base',              # text entries, lists, trees
    'text',
    'button',
    'button_text',
    'selection',         # selected item background
    'selection_text',
    'tooltip',
    'tooltip_text',
    'inactive',
    'focus',
)

_RGB = re.compile(r'^\s*(\d{1,3})[,\s]+(\d{1,3})[,\s]+(\d{1,3})\s*$')
_HEX = re.compile(r'#([0-9a-fA-F]{6})\b')
# Kvantum 的 kvconfig 會寫 `highlight.text.color=white` 這種 X11 色名，
# 只認 #rrggbb 的話會回 None，而 None 進 tk_setPalette 的鍵值對清單
# 會炸成 "list must have an even number of elements"（實測過）。
_NAMED = re.compile(r'^[A-Za-z]+$')


def _rgb(value):
    if not value:
        return None
    m = _RGB.match(str(value))
    if m:
        try:
            r, g, b = (int(x) for x in m.groups())
        except ValueError:
            return None
        if max(r, g, b) > 255:
            return None
        return '#%02x%02x%02x' % (r, g, b)
    m = _HEX.search(str(value))
    if m:
        return '#' + m.group(1).lower()
    text = str(value).strip()
    if _NAMED.match(text):
        # 交給 Tk 自己解 X11 色名，但一定要回字串、不能回 None
        return text.lower()
    return None


def _home(*p):
    return os.path.join(os.path.expanduser('~'), *p)


# --------------------------------------------------------------------------
# Kvantum theme config (the colours Qt/Kvantum actually paint with)
# --------------------------------------------------------------------------
def _kvantum_theme_files():
    """Yield candidate kvconfig paths for the *active* Kvantum theme."""
    import glob
    active = None
    cfg = _home('.config', 'Kvantum', 'kvantum.kvconfig')
    if os.path.isfile(cfg):
        cp = configparser.ConfigParser(interpolation=None)
        cp.optionxform = str
        try:
            cp.read(cfg, encoding='utf-8')
            active = cp.get('General', 'theme', fallback=None) or \
                cp.get('General', 'Theme', fallback=None)
        except Exception:
            active = None
    names = [active] if active else []
    if active and '/' in active:
        names.append(active.split('/')[-1])
    names.append('LayanDark')  # harmless: only used if nothing else resolves
    out = []
    for name in names:
        for pattern in (
                _home('.config', 'Kvantum', '*', name + '.kvconfig'),
                '/usr/share/Kvantum/' + name + '/' + name + '.kvconfig',
                '/usr/share/Kvantum/' + name + '.kvconfig'):
            out.extend(sorted(glob.glob(pattern)))
    seen, uniq = set(), []
    for path in out:
        if path not in seen and os.path.isfile(path):
            seen.add(path)
            uniq.append(path)
    return uniq


def _from_kvantum_file(path):
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str
    try:
        cp.read(path, encoding='utf-8')
    except Exception:
        return None
    sec = 'GeneralColors'
    if not cp.has_section(sec):
        return None
    get = lambda key: _rgb(cp.get(sec, key, fallback=None))
    pal = {
        'background': get('window.color'),
        'foreground': get('window.text.color'),
        'base': get('base.color'),
        'text': get('text.color'),
        'button': get('button.color'),
        'button_text': get('button.text.color'),
        'selection': get('highlight.color'),
        'selection_text': get('highlight.text.color'),
        'tooltip': get('window.color'),
        'tooltip_text': get('tooltip.text.color'),
        'inactive': get('disabled.text.color'),
        # Kvantum 的 focus/選取強調色就是 highlight，不是 kdeglobals 的 DecorationFocus
        'focus': get('highlight.color'),
    }
    alt = get('alt.base.color')
    if alt:
        pal['alternate'] = alt
    shade = get('dark.color')
    if shade:
        pal['shade'] = shade
    if not pal.get('background'):
        return None
    return pal


def _from_kvantum():
    for path in _kvantum_theme_files():
        pal = _from_kvantum_file(path)
        if pal:
            return pal
    return None


# --------------------------------------------------------------------------
# kdeglobals (KDE / Qt / Kvantum)
# --------------------------------------------------------------------------
def _from_kdeglobals(path):
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str
    try:
        cp.read(path, encoding='utf-8')
    except Exception:
        return None
    if not cp.has_section('Colors:Window'):
        return None

    def get(section, key, default=None):
        for sec in (section, 'Colors:Window'):
            if cp.has_option(sec, key):
                return _rgb(cp.get(sec, key))
        return default

    pal = {
        'background': get('Colors:Window', 'BackgroundNormal'),
        'foreground': get('Colors:Window', 'ForegroundNormal'),
        'base': get('Colors:View', 'BackgroundNormal'),
        'text': get('Colors:View', 'ForegroundNormal'),
        'button': get('Colors:Button', 'BackgroundNormal'),
        'button_text': get('Colors:Button', 'ForegroundNormal'),
        'selection': get('Colors:Selection', 'BackgroundNormal'),
        'selection_text': get('Colors:Selection', 'ForegroundNormal'),
        'tooltip': get('Colors:Tooltip', 'BackgroundNormal'),
        'tooltip_text': get('Colors:Tooltip', 'ForegroundNormal'),
        'inactive': get('Colors:Window', 'ForegroundInactive'),
        'focus': get('Colors:Window', 'DecorationFocus'),
    }
    alt = get('Colors:View', 'BackgroundAlternate')
    if alt:
        pal['alternate'] = alt
    return pal


# --------------------------------------------------------------------------
# GTK css
# --------------------------------------------------------------------------
_CSS_VAR = re.compile(r'^\s*(@?[a-z_]+)\s*:\s*([^;]+);', re.M)


def _from_css(text):
    found = {}
    for name, value in _CSS_VAR.findall(text):
        color = _rgb(value.strip())
        if not color:
            continue
        found[name.lstrip('@')] = color
    pick = {
        'background': ('background_color', 'bg_color', 'theme_bg_color'),
        'foreground': ('foreground_color', 'fg_color', 'theme_fg_color'),
        'base': ('base_color', 'theme_base_color'),
        'text': ('text_color', 'theme_text_color'),
        'button': ('button', 'theme_button_background_color'),
        'button_text': ('button_content', 'theme_button_foreground_color'),
        'selection': ('selection_background_color', 'theme_selected_bg_color'),
        'selection_text': ('selection_foreground_color', 'theme_selected_fg_color'),
        'tooltip': ('tooltip_background_color', 'theme_tooltip_bg_color'),
        'tooltip_text': ('tooltip_foreground_color', 'theme_tooltip_fg_color'),
        'focus': ('focus_color', 'theme_selected_bg_color'),
    }
    pal = {}
    for key, names in pick.items():
        for name in names:
            if name in found:
                pal[key] = found[name]
                break
    return pal or None


def _gtk_theme_dirs():
    name = None
    dark = False
    for path in (_home('.config', 'gtk-3.0', 'settings.ini'), _home('.gtkrc-2.0')):
        if not os.path.isfile(path):
            continue
        try:
            text = open(path, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        m = re.search(r'gtk-theme-name\s*=\s*"?([^"\n\]]+)"?', text)
        if m and not name:
            name = m.group(1).strip()
        if re.search(r'gtk-application-prefer-dark-theme\s*=\s*1', text):
            dark = True
    return name, dark


def _from_gtk(theme_name, prefer_dark):
    roots = (
        _home('.themes'), '/usr/share/themes', '/usr/lib/gtk-3.0/themes',
        _home('.local', 'share', 'themes'),
    )
    candidates = []
    if theme_name:
        candidates.append(theme_name)
    if prefer_dark and theme_name and not theme_name.lower().endswith('-dark'):
        candidates.append(theme_name + '-dark')
    if not candidates:
        candidates.append('Default')
    for name in candidates:
        for root in roots:
            base = os.path.join(root, name)
            for rel in (
                ('gtk-3.0', 'colors.css'),
                ('gtk-3.0', 'gtk.css'),
                ('gtk-3.0', 'gtk-3.0', 'gtk.css'),
                ('gtk-2.0', 'gtkrc'),
            ):
                path = os.path.join(base, *rel)
                if not os.path.isfile(path):
                    continue
                try:
                    text = open(path, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                pal = _from_css(text)
                if pal:
                    return pal
    return None


# --------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------
def read_palette():
    """Return a palette dict, or None when nothing usable was found.

    Source order matters and was measured on a real Layan-Dark + Kvantum
    desktop: kdeglobals said window=#3d3d3e / selection=#737373 while
    Kvantum's own theme file (and the qt5ct palette) paint window=#31313a
    / highlight=#5657f5.  So the theme engine that actually draws the
    widgets wins.
    """
    pal = _from_kvantum()
    if pal:
        return pal
    for path in (
            os.environ.get('KDE_CONFIG_HOME') and
            os.path.join(os.environ['KDE_CONFIG_HOME'], 'kdeglobals'),
            _home('.config', 'kdeglobals'),
            '/etc/kde/share/config/kdeglobals',
    ):
        if path and os.path.isfile(path):
            pal = _from_kdeglobals(path)
            if pal and pal.get('background'):
                return pal
    theme, dark = _gtk_theme_dirs()
    css = _home('.config', 'gtk-3.0', 'colors.css')
    if os.path.isfile(css):
        try:
            pal = _from_css(open(css, encoding='utf-8', errors='replace').read())
        except OSError:
            pal = None
        if pal:
            base = _from_gtk(theme, dark) or {}
            merged = dict(base)
            merged.update(pal)
            if merged.get('background'):
                return merged
    pal = _from_gtk(theme, dark)
    if pal and pal.get('background'):
        if not dark and theme and not theme.lower().endswith('-dark'):
            pass
        return pal
    return None


def is_dark(pal):
    """Luma test so we can pick matching fallbacks for the missing roles."""
    hexv = (pal or {}).get('background') or ''
    try:
        r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
    except (ValueError, IndexError):
        return False
    return (0.299 * r + 0.587 * g + 0.114 * b) < 128


def _fill_gaps(pal):
    dark = is_dark(pal)
    defaults = {
        'background': '#3d3d3e' if dark else '#f0f0f0',
        'foreground': '#ffffff' if dark else '#1a1a1a',
        'base': '#2b2b2b' if dark else '#ffffff',
        'text': '#ffffff' if dark else '#000000',
        'button': '#4a4a4b' if dark else '#e8e8e8',
        'inactive': '#a0a0a0',
        'focus': '#aaaaaa',
    }
    for key, value in defaults.items():
        pal.setdefault(key, value)
    pal.setdefault('selection', pal.get('focus') or '#2a76c6')
    pal.setdefault('selection_text', '#ffffff' if dark else '#ffffff')
    pal.setdefault('button_text', pal.get('foreground'))
    pal.setdefault('tooltip', '#4d4d4d' if dark else '#ffffa0')
    pal.setdefault('tooltip_text', pal.get('foreground'))
    pal.setdefault('alternate', _mix(pal['base'], pal['background'], 0.5))
    return pal


def _mix(a, b, ratio):
    try:
        ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
        cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    except (ValueError, IndexError):
        return a
    return '#%02x%02x%02x' % tuple(
        int(x * ratio + y * (1.0 - ratio)) for x, y in zip(ca, cb))


def reset(root, style=None):
    """Undo apply(): go back to whatever the selected ttk theme provides.

    Mirrors what upstream pysollib/winsystems/x11.py does at startup, so
    turning the option off really does restore the old look.
    """
    if style is None:
        try:
            import tkinter.ttk as ttk
            style = ttk.Style(root)
        except Exception:
            return
    color = style.lookup('.', 'background')
    if color:
        root.tk_setPalette(color)
    add = root.option_add
    add('*Menu.activeBorderWidth', 1, 60)
    if color:
        active = style.lookup('.', 'background', ['active'])
        if active:
            add('*Menu.activeBackground', active, 60)
    add('*Listbox.background', 'white', 60)
    add('*Listbox.foreground', 'black', 60)
    add('*Text.background', 'white', 60)
    add('*Text.foreground', 'black', 60)
    add('*selectForeground', 'white', 60)
    add('*selectBackground', '#0a5f89', 60)
    return None


def apply(root, style=None):
    """Recolor a Tk root window (and its ttk style) from the desktop theme.

    Returns the palette used, or None if nothing was applied.
    """
    pal = read_palette()
    if not pal:
        return None
    pal = _fill_gaps(pal)
    dark = is_dark(pal)

    palette_args = {
        'background': pal['background'],
        'foreground': pal['foreground'],
        'selectBackground': pal['selection'],
        'selectForeground': pal['selection_text'],
        'activeBackground': pal['button'],
        'activeForeground': pal['button_text'],
        'disabledForeground': pal['inactive'],
        'highlightColor': pal['focus'],
        'highlightBackground': pal['selection'],
        'troughColor': pal['alternate'],
    }
    # 少一個顏色就少傳一個鍵，不要讓 None 混進鍵值對
    root.tk_setPalette(**{k: v for k, v in palette_args.items() if v})
    add = root.option_add
    add('*Menu.background', pal['background'], 60)
    add('*Menu.foreground', pal['foreground'], 60)
    add('*Menu.activeBackground', pal['selection'], 60)
    add('*Menu.activeForeground', pal['selection_text'], 60)
    add('*Menu.disabledForeground', pal['inactive'], 60)
    add('*Menu.selectColor', pal['background'], 60)
    add('*Listbox.background', pal['base'], 60)
    add('*Listbox.foreground', pal['text'], 60)
    add('*Listbox.selectBackground', pal['selection'], 60)
    add('*Listbox.selectForeground', pal['selection_text'], 60)
    add('*Listbox.disabledForeground', pal['inactive'], 60)
    add('*Text.background', pal['base'], 60)
    add('*Text.foreground', pal['text'], 60)
    add('*Entry.background', pal['base'], 60)
    add('*Entry.foreground', pal['text'], 60)
    add('*Canvas.background', pal['background'], 60)
    add('*Scale.background', pal['background'], 60)
    add('*SelectBackground', pal['selection'], 60)
    add('*SelectForeground', pal['selection_text'], 60)

    if style is None:
        try:
            import tkinter.ttk as ttk
            style = ttk.Style(root)
        except Exception:
            return pal
    try:
        style.theme_use('clam')
    except Exception:
        return pal

    border = pal.get('shade') or _mix(pal['background'], pal['foreground'], 0.35)
    edge = _mix(pal['background'], pal['foreground'], 0.2)
    style.configure(
        '.',
        background=pal['background'],
        foreground=pal['foreground'],
        fieldbackground=pal['base'],
        bordercolor=border,
        lightcolor=pal['background'],
        darkcolor=pal['background'],
        troughcolor=pal['alternate'],
        focuscolor=pal['focus'],
        arrowcolor=pal['foreground'],
        selectbackground=pal['selection'],
        selectforeground=pal['selection_text'],
    )
    style.map(
        '.',
        background=[('disabled', pal['background']),
                    ('selected', pal['selection'])],
        foreground=[('disabled', pal['inactive']),
                    ('selected', pal['selection_text'])],
        bordercolor=[('focus', pal['focus'])],
        lightcolor=[('active', pal['button']), ('pressed', edge)],
        darkcolor=[('active', pal['button']), ('pressed', edge)],
        arrowcolor=[('disabled', pal['inactive'])],
    )
    for name in ('TFrame', 'TLabel', 'TLabelframe', 'TLabelframe.Label',
                 'Header', 'Menu', 'Vertical.TScrollbar', 'Horizontal.TScrollbar'):
        try:
            style.configure(name, background=pal['background'],
                            foreground=pal['foreground'])
        except Exception:
            pass
    try:
        style.configure('TLabelframe', bordercolor=border, relief='solid')
    except Exception:
        pass
    for name in ('TButton', 'Toolbutton', 'TMenubutton', 'TCheckbutton',
                 'TRadiobutton'):
        try:
            style.configure(
                name, background=pal['button'], foreground=pal['button_text'],
                bordercolor=border, lightcolor=pal['button'],
                darkcolor=pal['button'])
            style.map(
                name,
                background=[('disabled', pal['background']),
                            ('pressed', pal['selection']),
                            ('active', _mix(pal['button'], pal['selection'], 0.3))],
                foreground=[('disabled', pal['inactive']),
                            ('pressed', pal['selection_text']),
                            ('selected', pal['selection_text'])])
        except Exception:
            pass
    for name in ('TEntry', 'TCombobox', 'TSpinbox'):
        try:
            style.configure(
                name, fieldbackground=pal['base'], background=pal['base'],
                foreground=pal['text'], arrowcolor=pal['foreground'],
                bordercolor=border, lightcolor=pal['base'],
                darkcolor=pal['base'], insertcolor=pal['text'])
            style.map(
                name,
                bordercolor=[('focus', pal['focus']), ('disabled', pal['background'])],
                fieldbackground=[('disabled', pal['background']),
                                 ('readonly', pal['background'])],
                foreground=[('disabled', pal['inactive'])],
                arrowcolor=[('disabled', pal['inactive']),
                            ('pressed', pal['selection_text'])])
        except Exception:
            pass
    try:
        style.configure(
            'Treeview',
            background=pal['base'], fieldbackground=pal['base'],
            foreground=pal['text'], rowheight=None, bordercolor=border,
            lightcolor=pal['base'], darkcolor=pal['base'])
        style.configure('Treeview.Heading', background=pal['button'],
                        foreground=pal['button_text'], bordercolor=border,
                        lightcolor=pal['button'], darkcolor=pal['button'])
        style.map(
            'Treeview',
            background=[('selected', pal['selection'])],
            foreground=[('selected', pal['selection_text'])])
        style.map('Treeview.Heading',
                  background=[('active', _mix(pal['button'], pal['selection'], 0.3))])
    except Exception:
        pass
    try:
        style.configure('TNotebook', background=pal['background'], bordercolor=border)
        style.configure('TNotebook.Tab', background=pal['button'],
                        foreground=pal['button_text'], bordercolor=border,
                        lightcolor=pal['button'], darkcolor=pal['button'])
        style.map(
            'TNotebook.Tab',
            background=[('selected', pal['base']), ('active', pal['alternate'])],
            foreground=[('selected', pal['text']), ('disabled', pal['inactive'])],
            lightcolor=[('selected', pal['base'])],
            darkcolor=[('selected', pal['base'])])
    except Exception:
        pass
    for name in ('Vertical.TScrollbar', 'Horizontal.TScrollbar'):
        try:
            style.configure(
                name, background=pal['button'], troughcolor=pal['alternate'],
                arrowcolor=pal['foreground'], bordercolor=border,
                lightcolor=pal['button'], darkcolor=pal['button'])
            style.map(name, background=[('active', pal['selection']),
                                        ('pressed', pal['selection'])],
                      arrowcolor=[('pressed', pal['selection_text']),
                                  ('active', pal['selection_text'])])
        except Exception:
            pass
    try:
        style.configure('TProgressbar', background=pal['selection'],
                        troughcolor=pal['alternate'], bordercolor=border,
                        lightcolor=pal['selection'], darkcolor=pal['selection'])
    except Exception:
        pass
    try:
        style.configure('TSeparator', background=border)
    except Exception:
        pass
    return pal

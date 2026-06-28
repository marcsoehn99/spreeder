"""spreeder v2 — config.json persistence for ~/Library/Application Support/spreeder/."""
import json
import subprocess
import sys
from pathlib import Path

_APP_SUPPORT = Path.home() / 'Library' / 'Application Support' / 'spreeder'
_CONFIG_FILE = _APP_SUPPORT / 'config.json'
_LAUNCH_AGENTS_DIR = Path.home() / 'Library' / 'LaunchAgents'
_PLIST_LABEL = 'com.spreeder.app'
_PLIST_PATH = _LAUNCH_AGENTS_DIR / f'{_PLIST_LABEL}.plist'

# macOS virtual key codes for keys usable as hotkey triggers
KEY_CODES: dict[str, int] = {
    'a': 0, 's': 1, 'd': 2, 'f': 3, 'h': 4, 'g': 5, 'z': 6, 'x': 7,
    'c': 8, 'v': 9, 'b': 11, 'q': 12, 'w': 13, 'e': 14, 'r': 15,
    'y': 16, 't': 17, '1': 18, '2': 19, '3': 20, '4': 21, '6': 22,
    '5': 23, '9': 25, '7': 26, '8': 28, '0': 29,
    'o': 31, 'u': 32, 'i': 34, 'p': 35, 'l': 37, 'j': 38,
    'k': 40, 'n': 45, 'm': 46,
}

DEFAULTS: dict = {
    'wpm': 300,
    'chunk_size': 1,
    'adaptive': False,
    'hotkey_key': 'r',
    'hotkey_keycode': 15,
    'hotkey_ctrl': True,
    'hotkey_cmd': True,
    'hotkey_shift': False,
    'hotkey_option': False,
    'panel_offset_x': 0,
    'panel_offset_y': 0,
    'autostart': False,
    'autostart_prompted': False,
}


def load_config() -> dict:
    """Return config from disk merged with DEFAULTS; falls back to DEFAULTS on any error."""
    try:
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
        return {**DEFAULTS, **data}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULTS)


def save_config(cfg: dict) -> None:
    """Write cfg to config.json atomically, creating the directory if needed."""
    _APP_SUPPORT.mkdir(parents=True, exist_ok=True)
    tmp = _CONFIG_FILE.with_suffix('.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(cfg, f, indent=2)
    tmp.replace(_CONFIG_FILE)


def hotkey_display(cfg: dict) -> str:
    """Return a symbol string like ⌃⌘R for the configured hotkey."""
    mods = ''
    if cfg.get('hotkey_ctrl'):
        mods += '⌃'
    if cfg.get('hotkey_option'):
        mods += '⌥'
    if cfg.get('hotkey_cmd'):
        mods += '⌘'
    if cfg.get('hotkey_shift'):
        mods += '⇧'
    return mods + cfg.get('hotkey_key', 'r').upper()


def set_autostart(enabled: bool) -> None:
    """Install or remove the LaunchAgent plist for login autostart."""
    if enabled:
        py = sys.executable
        script = str(Path(__file__).parent / 'menubar.py')
        plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{_PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{py}</string>
        <string>{script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>'''
        _LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        _PLIST_PATH.write_text(plist)
        subprocess.run(['launchctl', 'load', str(_PLIST_PATH)], check=False, capture_output=True)
    else:
        if _PLIST_PATH.exists():
            subprocess.run(
                ['launchctl', 'unload', str(_PLIST_PATH)], check=False, capture_output=True
            )
            _PLIST_PATH.unlink(missing_ok=True)

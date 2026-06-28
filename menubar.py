#!/usr/bin/env python3
"""spreeder v2 — menu-bar resident entry point.

Runs as a quiet status-bar app (no dock icon) that listens for the global
hotkey (default ⌃⌘R, configurable) and provides access to the Full window
via the menu-bar icon.
"""
import ctypes
import os
import subprocess
import sys

import rumps
from AppKit import (
    NSDeviceIndependentModifierFlagsMask,
    NSEvent,
    NSEventModifierFlagCommand,
    NSEventModifierFlagControl,
    NSEventModifierFlagOption,
    NSEventModifierFlagShift,
    NSKeyDownMask,
)

import config as cfg_mod

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_PY = os.path.join(_HERE, 'app.py')
_HUD_PY = os.path.join(_HERE, 'hud.py')

_AX_FRAMEWORK = (
    '/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices'
)

_AX_SETTINGS_URL = (
    'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
)


def _ax_trusted() -> bool:
    ax = ctypes.cdll.LoadLibrary(_AX_FRAMEWORK)
    ax.AXIsProcessTrusted.restype = ctypes.c_bool
    return bool(ax.AXIsProcessTrusted())


def _build_mods(cfg: dict) -> int:
    mods = 0
    if cfg.get('hotkey_ctrl'):
        mods |= NSEventModifierFlagControl
    if cfg.get('hotkey_cmd'):
        mods |= NSEventModifierFlagCommand
    if cfg.get('hotkey_shift'):
        mods |= NSEventModifierFlagShift
    if cfg.get('hotkey_option'):
        mods |= NSEventModifierFlagOption
    return mods


class SpreederMenuBar(rumps.App):
    def __init__(self):
        super().__init__('📖', quit_button=None)
        self._win_proc: subprocess.Popen | None = None
        self._hotkey_monitor = None
        self._hotkey_active = False
        self._ax_notified = False

        # Track which hotkey is currently installed
        self._installed_key: str | None = None
        self._installed_keycode: int | None = None
        self._installed_mods: int | None = None

        cfg = cfg_mod.load_config()
        display = cfg_mod.hotkey_display(cfg)
        self._hotkey_item = rumps.MenuItem(
            f'Enable global hotkey {display}…',
            callback=self._open_ax_settings,
        )

        self.menu = [
            rumps.MenuItem('Read clipboard now', callback=self._read_clipboard),
            None,
            rumps.MenuItem('Open spreeder', callback=self._open_window),
            None,
            self._hotkey_item,
            None,
            rumps.MenuItem('Quit', callback=self._quit),
        ]

        # Schedule first-run autostart prompt
        self._first_run_timer = rumps.Timer(self._check_first_run, 1)
        self._first_run_timer.start()

    # ---- First-run prompt ------------------------------------------------

    def _check_first_run(self, timer) -> None:
        timer.stop()
        cfg = cfg_mod.load_config()
        if not cfg['autostart_prompted']:
            self._prompt_autostart()

    def _prompt_autostart(self) -> None:
        result = rumps.alert(
            title='spreeder',
            message=(
                'Start spreeder automatically when you log in?\n\n'
                'You can change this later in the Full window (Open spreeder).'
            ),
            ok='Yes, start at login',
            cancel='Not now',
        )
        enabled = bool(result)
        cfg = cfg_mod.load_config()
        cfg['autostart'] = enabled
        cfg['autostart_prompted'] = True
        cfg_mod.save_config(cfg)
        if enabled:
            cfg_mod.set_autostart(True)

    # ---- Accessibility polling ------------------------------------------------

    @rumps.timer(3)
    def _poll_ax(self, _) -> None:
        if not self._hotkey_active:
            if _ax_trusted():
                self._install_hotkey()
            elif not self._ax_notified:
                self._ax_notified = True
                rumps.notification(
                    title='spreeder',
                    subtitle='Accessibility permission needed',
                    message=(
                        'To use the global hotkey, grant Accessibility access. '
                        'Click "Enable global hotkey…" in the spreeder menu.'
                    ),
                    sound=False,
                )
        else:
            # Check if the hotkey was changed via the Full window
            self._maybe_update_hotkey()

    def _maybe_update_hotkey(self) -> None:
        cfg = cfg_mod.load_config()
        new_key = cfg.get('hotkey_key')
        new_keycode = cfg.get('hotkey_keycode')
        new_mods = _build_mods(cfg)
        if (new_key != self._installed_key or
                new_keycode != self._installed_keycode or
                new_mods != self._installed_mods):
            if self._hotkey_monitor is not None:
                NSEvent.removeMonitor_(self._hotkey_monitor)
                self._hotkey_monitor = None
            self._hotkey_active = False
            self._install_hotkey()

    def _install_hotkey(self) -> None:
        cfg = cfg_mod.load_config()
        keycode = cfg.get('hotkey_keycode', 15)
        mods = _build_mods(cfg)
        display = cfg_mod.hotkey_display(cfg)

        def _handler(event) -> None:
            device_flags = event.modifierFlags() & NSDeviceIndependentModifierFlagsMask
            if event.keyCode() == keycode and (device_flags & mods) == mods:
                self._read_clipboard(None)

        self._hotkey_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
            NSKeyDownMask, _handler
        )
        self._hotkey_active = True
        self._installed_key = cfg.get('hotkey_key')
        self._installed_keycode = keycode
        self._installed_mods = mods
        self._hotkey_item.title = f'Global hotkey {display}: active'
        self._hotkey_item.set_callback(None)

    def _open_ax_settings(self, _) -> None:
        subprocess.Popen(['open', _AX_SETTINGS_URL])
        cfg = cfg_mod.load_config()
        display = cfg_mod.hotkey_display(cfg)
        rumps.alert(
            title='Accessibility required',
            message=(
                'In System Settings → Privacy & Security → Accessibility, '
                f'enable spreeder.\n\n'
                f'Once granted, the hotkey {display} activates automatically — '
                'no restart required.'
            ),
        )

    # ---- Actions -------------------------------------------------------------

    def _read_clipboard(self, _) -> None:
        subprocess.Popen([sys.executable, _HUD_PY])

    def _open_window(self, _) -> None:
        if self._win_proc and self._win_proc.poll() is None:
            return
        self._win_proc = subprocess.Popen([sys.executable, _APP_PY])

    def _quit(self, _) -> None:
        if self._win_proc and self._win_proc.poll() is None:
            self._win_proc.terminate()
        if self._hotkey_monitor is not None:
            NSEvent.removeMonitor_(self._hotkey_monitor)
        rumps.quit_application()


def main():
    SpreederMenuBar().run()


if __name__ == '__main__':
    main()

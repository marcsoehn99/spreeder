#!/usr/bin/env python3
"""spreeder v2 — menu-bar resident entry point.

Runs as a quiet status-bar app (no dock icon) that listens for the global
hotkey ⌃⌘R and provides access to the Full window via the menu-bar icon.
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
    NSKeyDownMask,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_PY = os.path.join(_HERE, 'app.py')
_HUD_PY = os.path.join(_HERE, 'hud.py')

_AX_FRAMEWORK = (
    '/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices'
)
# macOS virtual key code for 'r'
_R_KEYCODE = 15
# Required modifiers for the default hotkey ⌃⌘R
_HOTKEY_MODS = NSEventModifierFlagControl | NSEventModifierFlagCommand

_AX_SETTINGS_URL = (
    'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
)


def _ax_trusted() -> bool:
    """Return True if this process has macOS Accessibility permission."""
    ax = ctypes.cdll.LoadLibrary(_AX_FRAMEWORK)
    ax.AXIsProcessTrusted.restype = ctypes.c_bool
    return bool(ax.AXIsProcessTrusted())


class SpreederMenuBar(rumps.App):
    def __init__(self):
        super().__init__('📖', quit_button=None)
        self._win_proc: subprocess.Popen | None = None
        self._hotkey_monitor = None
        self._hotkey_active = False
        self._ax_notified = False

        self._hotkey_item = rumps.MenuItem(
            'Enable global hotkey ⌃⌘R…',
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

    # ---- Accessibility polling ------------------------------------------------

    @rumps.timer(3)
    def _poll_ax(self, _) -> None:
        """Poll for Accessibility grant and install the hotkey once permitted."""
        if self._hotkey_active:
            return
        if _ax_trusted():
            self._install_hotkey()
        elif not self._ax_notified:
            self._ax_notified = True
            rumps.notification(
                title='spreeder',
                subtitle='Accessibility permission needed',
                message=(
                    'To use the global hotkey ⌃⌘R, grant Accessibility access. '
                    'Click "Enable global hotkey ⌃⌘R…" in the spreeder menu.'
                ),
                sound=False,
            )

    def _install_hotkey(self) -> None:
        """Register the global key monitor for ⌃⌘R (read hotkey from settings later)."""
        def _handler(event) -> None:
            device_flags = event.modifierFlags() & NSDeviceIndependentModifierFlagsMask
            if event.keyCode() == _R_KEYCODE and (device_flags & _HOTKEY_MODS) == _HOTKEY_MODS:
                self._read_clipboard(None)

        self._hotkey_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
            NSKeyDownMask, _handler
        )
        self._hotkey_active = True
        self._hotkey_item.title = 'Global hotkey ⌃⌘R: active'
        self._hotkey_item.set_callback(None)

    def _open_ax_settings(self, _) -> None:
        """Open the Accessibility pane and explain what to do."""
        subprocess.Popen(['open', _AX_SETTINGS_URL])
        rumps.alert(
            title='Accessibility required',
            message=(
                'In System Settings → Privacy & Security → Accessibility, '
                'enable spreeder.\n\n'
                'Once granted, the hotkey ⌃⌘R activates automatically — '
                'no restart required.'
            ),
        )

    # ---- Actions -------------------------------------------------------------

    def _read_clipboard(self, _) -> None:
        subprocess.Popen([sys.executable, _HUD_PY])

    def _open_window(self, _) -> None:
        if self._win_proc and self._win_proc.poll() is None:
            return  # Full window already open
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

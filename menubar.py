#!/usr/bin/env python3
"""spreeder v2 — menu-bar resident entry point.

Runs as a quiet status-bar app (no dock icon) that listens for the global
hotkey and provides access to the Full window via the menu-bar icon.
"""
import os
import subprocess
import sys

import rumps

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_PY = os.path.join(_HERE, 'app.py')


class SpreederMenuBar(rumps.App):
    def __init__(self):
        super().__init__('📖', quit_button=None)
        self.menu = [
            rumps.MenuItem('Open spreeder', callback=self._open_window),
            None,
            rumps.MenuItem('Quit', callback=self._quit),
        ]
        self._win_proc: subprocess.Popen | None = None

    def _open_window(self, _):
        if self._win_proc and self._win_proc.poll() is None:
            return  # Full window already open — don't open a second one
        self._win_proc = subprocess.Popen([sys.executable, _APP_PY])

    def _quit(self, _):
        if self._win_proc and self._win_proc.poll() is None:
            self._win_proc.terminate()
        rumps.quit_application()


def main():
    SpreederMenuBar().run()


if __name__ == '__main__':
    main()

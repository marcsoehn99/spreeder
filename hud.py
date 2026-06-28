#!/usr/bin/env python3
"""spreeder v2 — HUD playback window.

Launched by the menu bar's 'Read clipboard now' action.
Reads the clipboard, normalises it via engine.py, and plays RSVP in a
small borderless always-on-top HUD.
"""
import sys
import os
import tkinter as tk
from tkinter import font as tkfont

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from engine import build_session
import config as cfg_mod

FONT_FAMILY = 'Menlo'
FONT_SIZE = 36
CANVAS_W = 700
CANVAS_H = 100
PROGRESS_H = 4
BG = '#1a1a1a'
FG = '#e0e0e0'
ORP_COLOR = '#ff3b30'
PROGRESS_BG = '#333'
PROGRESS_FG = '#0a84ff'
ORP_X = 320  # left edge of the ORP character — fixed

AUTO_CLOSE_MS = 1000       # hold after last chunk before auto-close
NOTHING_TO_READ_MS = 1800  # how long the "nothing to read" cue is shown


def _read_clipboard(root: tk.Tk) -> str | None:
    try:
        text = root.clipboard_get()
    except tk.TclError:
        return None
    if not text or not text.strip():
        return None
    return text


class HUD:
    def __init__(self, root: tk.Tk, text: str, active_window: tuple | None = None):
        self.root = root
        self._timer_id: str | None = None
        self._chunks: list = []
        self._index: int = 0
        self._paused: bool = False
        self._chunk_duration_ms = None
        self._char_width: int = 0
        self._ref_cx: int = 0
        self._ref_cy: int = 0
        # drag state
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._win_start_x: int = 0
        self._win_start_y: int = 0

        self._setup_window(active_window)
        self._build_ui()
        self.root.after(10, self._init_then_play, text)

    def _setup_window(self, active_window: tuple | None = None) -> None:
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        total_h = CANVAS_H + PROGRESS_H
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        if active_window:
            ax, ay, aw, ah = active_window
            self._ref_cx = ax + aw // 2
            self._ref_cy = ay + ah // 2
        else:
            self._ref_cx = sw // 2
            self._ref_cy = sh // 2

        cfg = cfg_mod.load_config()
        offset_x = int(cfg.get('panel_offset_x', 0))
        offset_y = int(cfg.get('panel_offset_y', 0))

        x = self._ref_cx - CANVAS_W // 2 + offset_x
        y = self._ref_cy - total_h // 2 + offset_y
        self.root.geometry(f'{CANVAS_W}x{total_h}+{x}+{y}')
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

    def _build_ui(self) -> None:
        self._canvas = tk.Canvas(
            self.root, width=CANVAS_W, height=CANVAS_H,
            bg=BG, highlightthickness=0,
        )
        self._canvas.pack(side='top', fill='x')

        self._progress_canvas = tk.Canvas(
            self.root, width=CANVAS_W, height=PROGRESS_H,
            bg=PROGRESS_BG, highlightthickness=0,
        )
        self._progress_canvas.pack(side='top', fill='x')

        self.root.bind('<space>', self._on_space)
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<r>', self._on_restart)
        self.root.bind('<R>', self._on_restart)
        self.root.bind('<ButtonPress-1>', self._on_drag_start)
        self.root.bind('<B1-Motion>', self._on_drag_motion)
        self.root.bind('<ButtonRelease-1>', self._on_drag_end)
        self.root.focus_force()

    def _init_then_play(self, text: str) -> None:
        f = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        self._char_width = f.measure('M')
        loaded = cfg_mod.load_config()
        settings = {
            'wpm': loaded['wpm'],
            'chunk_size': loaded['chunk_size'],
            'adaptive': loaded['adaptive'],
        }
        result = build_session(text, settings)
        self._chunks = result['chunks']
        self._chunk_duration_ms = result['chunk_duration_ms']
        self._index = 0
        self._paused = False
        self._advance()

    # --- Controls ---

    def _on_space(self, _event=None) -> None:
        if not self._chunks:
            return
        if self._paused:
            self._paused = False
            self._advance()
        else:
            self._paused = True
            self._stop_timer()

    def _on_escape(self, _event=None) -> None:
        self._stop_timer()
        self.root.destroy()

    def _on_restart(self, _event=None) -> None:
        if not self._chunks:
            return
        self._stop_timer()
        self._index = 0
        self._paused = False
        self._advance()

    # --- Drag to reposition ---

    def _on_drag_start(self, event) -> None:
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.root.winfo_x()
        self._win_start_y = self.root.winfo_y()

    def _on_drag_motion(self, event) -> None:
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        self.root.geometry(f'+{self._win_start_x + dx}+{self._win_start_y + dy}')

    def _on_drag_end(self, event) -> None:
        total_h = CANVAS_H + PROGRESS_H
        hud_cx = self.root.winfo_x() + CANVAS_W // 2
        hud_cy = self.root.winfo_y() + total_h // 2
        offset_x = hud_cx - self._ref_cx
        offset_y = hud_cy - self._ref_cy
        cfg = cfg_mod.load_config()
        cfg['panel_offset_x'] = offset_x
        cfg['panel_offset_y'] = offset_y
        cfg_mod.save_config(cfg)

    # --- Timer loop ---

    def _advance(self) -> None:
        if self._index >= len(self._chunks):
            # Hold the last chunk briefly then auto-close
            self._timer_id = self.root.after(AUTO_CLOSE_MS, self.root.destroy)
            return
        chunk = self._chunks[self._index]
        self._render_chunk(chunk)
        self._render_progress()
        duration = max(1, int(self._chunk_duration_ms(chunk)))
        self._index += 1
        self._timer_id = self.root.after(duration, self._advance)

    def _stop_timer(self) -> None:
        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

    # --- Rendering ---

    def _render_chunk(self, chunk: dict) -> None:
        self._canvas.delete('all')
        text = chunk['text']
        orp_index = chunk['orp_index']
        cy = CANVAS_H // 2
        cw = self._char_width or 22

        font = (FONT_FAMILY, FONT_SIZE)
        pre = text[:orp_index]
        orp_char = text[orp_index]
        post = text[orp_index + 1:]

        if pre:
            self._canvas.create_text(ORP_X, cy, text=pre, font=font, anchor='e', fill=FG)
        self._canvas.create_text(ORP_X, cy, text=orp_char, font=font, anchor='w', fill=ORP_COLOR)
        if post:
            self._canvas.create_text(ORP_X + cw, cy, text=post, font=font, anchor='w', fill=FG)

    def _render_progress(self) -> None:
        self._progress_canvas.delete('all')
        if not self._chunks:
            return
        # Show progress including the chunk currently being displayed
        frac = (self._index + 1) / len(self._chunks)
        bar_w = int(CANVAS_W * frac)
        if bar_w > 0:
            self._progress_canvas.create_rectangle(
                0, 0, bar_w, PROGRESS_H,
                fill=PROGRESS_FG, outline='',
            )


def _setup_nothing_cue(root: tk.Tk) -> None:
    """Configure root as a brief 'nothing to read' toast near the bottom."""
    root.overrideredirect(True)
    root.attributes('-topmost', True)
    w, h = 280, 44
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = sh - h - 80
    root.geometry(f'{w}x{h}+{x}+{y}')
    root.configure(bg='#2a2a2a')
    tk.Label(
        root, text='nothing to read',
        font=('Menlo', 15), bg='#2a2a2a', fg='#666',
    ).pack(expand=True)
    root.after(NOTHING_TO_READ_MS, root.destroy)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--active-window', nargs=4, type=int, metavar=('X', 'Y', 'W', 'H'))
    args, _ = parser.parse_known_args()
    active_window = tuple(args.active_window) if args.active_window else None

    root = tk.Tk()
    root.withdraw()

    text = _read_clipboard(root)
    if text is None:
        _setup_nothing_cue(root)
        root.deiconify()
    else:
        HUD(root, text, active_window=active_window)
        root.deiconify()

    root.mainloop()


if __name__ == '__main__':
    main()

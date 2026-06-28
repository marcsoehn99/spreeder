#!/usr/bin/env python3
"""spreeder v2 — Full window: paste field + RSVP playback on a Tkinter Canvas."""
import tkinter as tk
from tkinter import font as tkfont
from engine import build_session

# --- Display constants ---
FONT_FAMILY = 'Menlo'
FONT_SIZE = 48
CANVAS_W = 900
CANVAS_H = 130
BG = '#1a1a1a'
FG = '#e0e0e0'
ORP_COLOR = '#ff3b30'

# ORP_X is the x-coordinate of the LEFT EDGE of the ORP character — fixed across all chunks.
ORP_X = 420

DEFAULTS = {'wpm': 300, 'chunk_size': 1, 'adaptive': False}


class FullWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('spreeder')
        self.root.configure(bg='#2a2a2a')
        self.root.resizable(False, False)

        self._timer_id: str | None = None
        self._chunks: list = []
        self._index: int = 0
        self._chunk_duration_ms = None
        self._char_width: int = 0

        self._build_ui()
        # Measure character width after window exists
        self.root.after(10, self._init_font_metrics)

    def _build_ui(self) -> None:
        pad = {'padx': 12, 'pady': 8}

        # Paste area
        lbl = tk.Label(self.root, text='Paste text to read:', bg='#2a2a2a', fg='#aaa',
                       font=('Menlo', 13), anchor='w')
        lbl.pack(fill='x', **pad)

        self._text_area = tk.Text(
            self.root, height=8, wrap='word',
            font=('Menlo', 13), bg='#111', fg='#ddd',
            insertbackground='#ddd', relief='flat', padx=8, pady=6,
        )
        self._text_area.pack(fill='x', padx=12)

        # Play button
        self._play_btn = tk.Button(
            self.root, text='▶  Play', command=self._on_play,
            font=('Menlo', 14, 'bold'), bg='#0a84ff', fg='white',
            activebackground='#409cff', activeforeground='white',
            relief='flat', padx=16, pady=6, cursor='hand2',
        )
        self._play_btn.pack(pady=10)

        # RSVP canvas
        self._canvas = tk.Canvas(
            self.root, width=CANVAS_W, height=CANVAS_H,
            bg=BG, highlightthickness=0,
        )
        self._canvas.pack(padx=12, pady=(0, 12))

        # Keyboard bindings on the root window
        self.root.bind('<space>', self._on_space)
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<r>', self._on_restart)
        self.root.bind('<R>', self._on_restart)

    def _init_font_metrics(self) -> None:
        f = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        # Use measure of a single wide char; monospace so all chars equal
        self._char_width = f.measure('M')

    # --- Playback control ---

    def _on_play(self) -> None:
        raw = self._text_area.get('1.0', 'end')
        result = build_session(raw, DEFAULTS)
        chunks = result['chunks']
        if not chunks:
            self._show_message('nothing to read')
            return
        self._stop_timer()
        self._chunks = chunks
        self._chunk_duration_ms = result['chunk_duration_ms']
        self._index = 0
        self._paused = False
        self._advance()

    def _on_space(self, _event=None) -> None:
        if not self._chunks:
            return
        if getattr(self, '_paused', False):
            self._paused = False
            self._advance()
        else:
            self._paused = True
            self._stop_timer()

    def _on_escape(self, _event=None) -> None:
        self._stop_timer()
        self._chunks = []
        self._canvas.delete('all')

    def _on_restart(self, _event=None) -> None:
        if not self._chunks:
            return
        self._stop_timer()
        self._index = 0
        self._paused = False
        self._advance()

    # --- Timer loop ---

    def _advance(self) -> None:
        if self._index >= len(self._chunks):
            return  # done — leave last chunk visible, stop cleanly
        chunk = self._chunks[self._index]
        self._render_chunk(chunk)
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
        cw = self._char_width or 28  # fallback before font metrics load

        font = (FONT_FAMILY, FONT_SIZE)

        pre = text[:orp_index]
        orp_char = text[orp_index]
        post = text[orp_index + 1:]

        # Pre-ORP: right-aligned so it ends exactly at ORP_X
        if pre:
            self._canvas.create_text(ORP_X, cy, text=pre, font=font, anchor='e', fill=FG)

        # ORP character: left edge pinned at ORP_X, always red
        self._canvas.create_text(ORP_X, cy, text=orp_char, font=font, anchor='w', fill=ORP_COLOR)

        # Post-ORP: left edge starts right after the ORP character
        if post:
            self._canvas.create_text(ORP_X + cw, cy, text=post, font=font, anchor='w', fill=FG)

    def _show_message(self, msg: str) -> None:
        self._canvas.delete('all')
        self._canvas.create_text(
            CANVAS_W // 2, CANVAS_H // 2,
            text=msg, font=(FONT_FAMILY, 22), fill='#555', anchor='center',
        )


def main() -> None:
    root = tk.Tk()
    FullWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()

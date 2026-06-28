#!/usr/bin/env python3
"""spreeder v2 — Full window: paste field + RSVP playback + settings."""
import tkinter as tk
from tkinter import font as tkfont

import config as cfg_mod
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


class _HotkeyDialog:
    """Small dialog to capture a new hotkey combination."""

    def __init__(self, parent: tk.Tk, current_cfg: dict, on_apply):
        self._on_apply = on_apply
        self._dlg = tk.Toplevel(parent)
        self._dlg.title('Change Hotkey')
        self._dlg.resizable(False, False)
        self._dlg.transient(parent)
        self._dlg.grab_set()
        self._dlg.configure(bg='#2a2a2a')

        pad = {'padx': 10, 'pady': 6}

        tk.Label(
            self._dlg, text='Key (single letter or digit):',
            bg='#2a2a2a', fg='#aaa', font=('Menlo', 12),
        ).grid(row=0, column=0, columnspan=2, sticky='w', **pad)

        self._key_var = tk.StringVar(value=current_cfg.get('hotkey_key', 'r'))
        key_entry = tk.Entry(
            self._dlg, textvariable=self._key_var,
            width=4, font=('Menlo', 14), bg='#111', fg='#ddd',
            insertbackground='#ddd', relief='flat',
        )
        key_entry.grid(row=1, column=0, columnspan=2, sticky='w', **pad)

        tk.Label(
            self._dlg, text='Modifiers:', bg='#2a2a2a', fg='#aaa', font=('Menlo', 12),
        ).grid(row=2, column=0, columnspan=2, sticky='w', **pad)

        self._ctrl_var = tk.BooleanVar(value=current_cfg.get('hotkey_ctrl', True))
        self._cmd_var = tk.BooleanVar(value=current_cfg.get('hotkey_cmd', True))
        self._shift_var = tk.BooleanVar(value=current_cfg.get('hotkey_shift', False))
        self._option_var = tk.BooleanVar(value=current_cfg.get('hotkey_option', False))

        ck_style = {'bg': '#2a2a2a', 'fg': '#ddd', 'selectcolor': '#444',
                    'activebackground': '#2a2a2a', 'font': ('Menlo', 12)}

        tk.Checkbutton(self._dlg, text='⌃ Control', variable=self._ctrl_var,
                       command=self._update_preview, **ck_style).grid(
            row=3, column=0, sticky='w', padx=10, pady=2)
        tk.Checkbutton(self._dlg, text='⌘ Command', variable=self._cmd_var,
                       command=self._update_preview, **ck_style).grid(
            row=4, column=0, sticky='w', padx=10, pady=2)
        tk.Checkbutton(self._dlg, text='⌥ Option', variable=self._option_var,
                       command=self._update_preview, **ck_style).grid(
            row=5, column=0, sticky='w', padx=10, pady=2)
        tk.Checkbutton(self._dlg, text='⇧ Shift', variable=self._shift_var,
                       command=self._update_preview, **ck_style).grid(
            row=6, column=0, sticky='w', padx=10, pady=2)

        self._preview_var = tk.StringVar()
        tk.Label(
            self._dlg, textvariable=self._preview_var,
            bg='#2a2a2a', fg='#0a84ff', font=('Menlo', 20, 'bold'),
        ).grid(row=3, column=1, rowspan=4, padx=16)

        btn_frame = tk.Frame(self._dlg, bg='#2a2a2a')
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)

        tk.Button(
            btn_frame, text='Apply', command=self._apply,
            font=('Menlo', 13, 'bold'), bg='#0a84ff', fg='white',
            activebackground='#409cff', relief='flat', padx=12, pady=4,
        ).pack(side='left', padx=6)
        tk.Button(
            btn_frame, text='Cancel', command=self._dlg.destroy,
            font=('Menlo', 13), bg='#444', fg='#ddd',
            activebackground='#555', relief='flat', padx=12, pady=4,
        ).pack(side='left', padx=6)

        self._key_var.trace_add('write', lambda *_: self._update_preview())
        self._update_preview()
        key_entry.focus_set()

    def _update_preview(self) -> None:
        tmp = {
            'hotkey_key': self._key_var.get() or '?',
            'hotkey_ctrl': self._ctrl_var.get(),
            'hotkey_cmd': self._cmd_var.get(),
            'hotkey_shift': self._shift_var.get(),
            'hotkey_option': self._option_var.get(),
        }
        self._preview_var.set(cfg_mod.hotkey_display(tmp))

    def _apply(self) -> None:
        key = self._key_var.get().lower().strip()
        if not key or key not in cfg_mod.KEY_CODES:
            self._preview_var.set('Invalid key')
            return
        if not (self._ctrl_var.get() or self._cmd_var.get()
                or self._shift_var.get() or self._option_var.get()):
            self._preview_var.set('Pick ≥1 modifier')
            return
        new_cfg = {
            'hotkey_key': key,
            'hotkey_keycode': cfg_mod.KEY_CODES[key],
            'hotkey_ctrl': self._ctrl_var.get(),
            'hotkey_cmd': self._cmd_var.get(),
            'hotkey_shift': self._shift_var.get(),
            'hotkey_option': self._option_var.get(),
        }
        self._dlg.destroy()
        self._on_apply(new_cfg)


class FullWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('spreeder')
        self.root.configure(bg='#2a2a2a')
        self.root.resizable(False, False)

        self._cfg = cfg_mod.load_config()

        self._timer_id: str | None = None
        self._chunks: list = []
        self._index: int = 0
        self._chunk_duration_ms = None
        self._char_width: int = 0
        self._paused: bool = False

        self._build_ui()
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
        self._canvas.pack(padx=12, pady=(0, 8))

        # Settings row
        self._build_settings_ui()

        # Keyboard bindings
        self.root.bind('<space>', self._on_space)
        self.root.bind('<Escape>', self._on_escape)
        self.root.bind('<r>', self._on_restart)
        self.root.bind('<R>', self._on_restart)

    def _build_settings_ui(self) -> None:
        sep = tk.Frame(self.root, bg='#444', height=1)
        sep.pack(fill='x', padx=12)

        frame = tk.Frame(self.root, bg='#2a2a2a')
        frame.pack(fill='x', padx=12, pady=8)

        lbl_style = {'bg': '#2a2a2a', 'fg': '#888', 'font': ('Menlo', 11)}
        entry_style = {'font': ('Menlo', 12), 'bg': '#111', 'fg': '#ddd',
                       'insertbackground': '#ddd', 'relief': 'flat'}
        spin_style = {'font': ('Menlo', 12), 'bg': '#111', 'fg': '#ddd',
                      'buttonbackground': '#333', 'relief': 'flat', 'width': 5}
        ck_style = {'bg': '#2a2a2a', 'fg': '#ccc', 'selectcolor': '#444',
                    'activebackground': '#2a2a2a', 'font': ('Menlo', 12)}

        # WPM
        tk.Label(frame, text='WPM:', **lbl_style).pack(side='left')
        self._wpm_var = tk.StringVar(value=str(self._cfg['wpm']))
        wpm_spin = tk.Spinbox(
            frame, from_=50, to=1500, increment=25,
            textvariable=self._wpm_var, **spin_style,
        )
        wpm_spin.pack(side='left', padx=(2, 12))

        # Chunk size
        tk.Label(frame, text='Chunk:', **lbl_style).pack(side='left')
        self._chunk_var = tk.StringVar(value=str(self._cfg['chunk_size']))
        chunk_spin = tk.Spinbox(
            frame, from_=1, to=10, increment=1,
            textvariable=self._chunk_var, width=3, **{k: v for k, v in spin_style.items() if k != 'width'},
        )
        chunk_spin.config(width=3)
        chunk_spin.pack(side='left', padx=(2, 12))

        # Adaptive
        self._adaptive_var = tk.BooleanVar(value=bool(self._cfg['adaptive']))
        tk.Checkbutton(
            frame, text='Adaptive', variable=self._adaptive_var,
            command=self._on_setting_change, **ck_style,
        ).pack(side='left', padx=(0, 12))

        # Hotkey
        tk.Label(frame, text='Hotkey:', **lbl_style).pack(side='left')
        self._hotkey_label_var = tk.StringVar(value=cfg_mod.hotkey_display(self._cfg))
        tk.Label(
            frame, textvariable=self._hotkey_label_var,
            bg='#2a2a2a', fg='#0a84ff', font=('Menlo', 13, 'bold'),
        ).pack(side='left', padx=(2, 4))
        tk.Button(
            frame, text='Change', command=self._on_change_hotkey,
            font=('Menlo', 11), bg='#444', fg='#ddd',
            activebackground='#555', relief='flat', padx=6, pady=2,
        ).pack(side='left', padx=(0, 12))

        # Autostart
        self._autostart_var = tk.BooleanVar(value=bool(self._cfg['autostart']))
        tk.Checkbutton(
            frame, text='Launch at login', variable=self._autostart_var,
            command=self._on_autostart_change, **ck_style,
        ).pack(side='left')

        # Trace WPM and chunk changes
        self._wpm_var.trace_add('write', self._on_setting_change)
        self._chunk_var.trace_add('write', self._on_setting_change)

    def _on_setting_change(self, *_) -> None:
        try:
            wpm = int(self._wpm_var.get())
            chunk_size = int(self._chunk_var.get())
        except ValueError:
            return
        wpm = max(50, min(1500, wpm))
        chunk_size = max(1, min(10, chunk_size))
        self._cfg = cfg_mod.load_config()
        self._cfg['wpm'] = wpm
        self._cfg['chunk_size'] = chunk_size
        self._cfg['adaptive'] = bool(self._adaptive_var.get())
        cfg_mod.save_config(self._cfg)

    def _on_autostart_change(self) -> None:
        enabled = bool(self._autostart_var.get())
        self._cfg = cfg_mod.load_config()
        self._cfg['autostart'] = enabled
        self._cfg['autostart_prompted'] = True
        cfg_mod.save_config(self._cfg)
        cfg_mod.set_autostart(enabled)

    def _on_change_hotkey(self) -> None:
        _HotkeyDialog(self.root, self._cfg, self._apply_hotkey)

    def _apply_hotkey(self, hotkey_cfg: dict) -> None:
        self._cfg = cfg_mod.load_config()
        self._cfg.update(hotkey_cfg)
        cfg_mod.save_config(self._cfg)
        self._hotkey_label_var.set(cfg_mod.hotkey_display(self._cfg))

    def _init_font_metrics(self) -> None:
        f = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        self._char_width = f.measure('M')

    # --- Playback control ---

    def _on_play(self) -> None:
        raw = self._text_area.get('1.0', 'end')
        self._cfg = cfg_mod.load_config()
        settings = {
            'wpm': self._cfg['wpm'],
            'chunk_size': self._cfg['chunk_size'],
            'adaptive': self._cfg['adaptive'],
        }
        result = build_session(raw, settings)
        chunks = result['chunks']
        self._stop_timer()
        if not chunks:
            self._chunks = []
            self._show_message('nothing to read')
            return
        self._chunks = chunks
        self._chunk_duration_ms = result['chunk_duration_ms']
        self._index = 0
        self._paused = False
        self._advance()

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
            return
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
        cw = self._char_width or 28

        font = (FONT_FAMILY, FONT_SIZE)
        pre = text[:orp_index]
        orp_char = text[orp_index]
        post = text[orp_index + 1:]

        if pre:
            self._canvas.create_text(ORP_X, cy, text=pre, font=font, anchor='e', fill=FG)
        self._canvas.create_text(ORP_X, cy, text=orp_char, font=font, anchor='w', fill=ORP_COLOR)
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

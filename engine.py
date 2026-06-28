"""Pure RSVP engine — no GUI, no timers, no clipboard, no file I/O."""
import re


def _normalize_text(raw: str) -> str:
    text = raw
    # Remove fenced code blocks entirely (```lang\n...\n```)
    text = re.sub(r'```[^\n]*\n[\s\S]*?```', '', text)
    # Strip markdown links: [text](url) → text, strip URL entirely
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # Strip heading markers at line start
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Strip leading list item markers (-, *, + at line start)
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
    # Strip bold/italic markers (**text** or *text*)
    text = re.sub(r'\*{1,2}([^*\n]+)\*{1,2}', r'\1', text)
    # Strip inline backticks
    text = re.sub(r'`([^`\n]*)`', r'\1', text)
    return text


def _compute_orp_index(text: str) -> int:
    """Spritz-style ORP: slightly left of centre, stepped by word length."""
    n = len(text)
    if n <= 1:
        return 0
    if n <= 5:
        return 1
    if n <= 9:
        return 2
    if n <= 13:
        return 3
    return min(int(n * 0.3), n - 1)


def build_session(raw_text: str, settings: dict | None = None) -> dict:
    """
    build_session(raw_text, settings) → { 'chunks': [...], 'chunk_duration_ms': fn }

    chunks: list of { 'text': str, 'orp_index': int }
    chunk_duration_ms(chunk) → float  milliseconds to display chunk
    """
    s = settings or {}
    wpm = s.get('wpm', 300)
    chunk_size = s.get('chunk_size', 1)
    adaptive = s.get('adaptive', False)

    words = _normalize_text(raw_text or '').split()
    # split() already filters empty strings

    chunks = []
    for i in range(0, len(words), chunk_size):
        text = ' '.join(words[i:i + chunk_size])
        chunks.append({'text': text, 'orp_index': _compute_orp_index(text)})

    def chunk_duration_ms(chunk: dict) -> float:
        chunk_words = chunk['text'].split()
        word_count = len(chunk_words)
        base = (word_count / wpm) * 60_000

        if not adaptive:
            return base

        avg_char_len = sum(len(w) for w in chunk_words) / word_count
        has_sentence_end = bool(re.search(r'[.!?]\s*$', chunk['text']))

        scale = 1.0
        if avg_char_len > 5:
            scale += (avg_char_len - 5) * 0.05
        if has_sentence_end:
            scale += 0.2

        return base * min(scale, 2.0)

    return {'chunks': chunks, 'chunk_duration_ms': chunk_duration_ms}


def compute_column_widths(chunks: list) -> dict:
    """Return max pre-ORP and post-ORP lengths for fixed-column layout."""
    max_pre = 0
    max_post = 0
    for chunk in chunks:
        orp = chunk['orp_index']
        max_pre = max(max_pre, orp)
        max_post = max(max_post, len(chunk['text']) - orp - 1)
    return {'max_pre_len': max(max_pre, 1), 'max_post_len': max(max_post, 1)}

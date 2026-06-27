// Spritz-style ORP: slightly left of centre, stepped by word length
function computeOrpIndex(text) {
  const len = text.length;
  if (len <= 1) return 0;
  if (len <= 5) return 1;
  if (len <= 9) return 2;
  if (len <= 13) return 3;
  return Math.min(Math.floor(len * 0.3), len - 1);
}

/**
 * buildSession(rawText, settings) → { chunks, chunkDurationMs }
 *
 * Pure function — no DOM, no timers, no storage.
 *
 * chunks: Array<{ text: string, orpIndex: number }>
 *   Ordered sequence of display units. orpIndex is the character within text
 *   that should be pinned at the horizontal focal point (marked red).
 *
 * chunkDurationMs(chunk) → number
 *   Milliseconds to display chunk. Tracks wpm and word count; scales up for
 *   heavier chunks when adaptive is on.
 */
export function buildSession(rawText, settings) {
  const { wpm = 300, chunkSize = 1, adaptive = false } = settings || {};

  const words = (rawText || '').trim().split(/\s+/).filter(w => w.length > 0);

  const chunks = [];
  for (let i = 0; i < words.length; i += chunkSize) {
    const text = words.slice(i, i + chunkSize).join(' ');
    chunks.push({ text, orpIndex: computeOrpIndex(text) });
  }

  function chunkDurationMs(chunk) {
    const chunkWords = chunk.text.split(/\s+/).filter(w => w.length > 0);
    const wordCount = chunkWords.length;
    const base = (wordCount / wpm) * 60_000;

    if (!adaptive) return base;

    const avgCharLen = chunkWords.reduce((sum, w) => sum + w.length, 0) / wordCount;
    const hasSentenceEnd = /[.!?]\s*$/.test(chunk.text);

    let scale = 1;
    if (avgCharLen > 5) scale += (avgCharLen - 5) * 0.05;
    if (hasSentenceEnd) scale += 0.2;

    return base * Math.min(scale, 2);
  }

  return { chunks, chunkDurationMs };
}

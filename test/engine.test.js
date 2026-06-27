import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildSession } from '../engine.js';

test('buildSession splits a sample string into one-word chunks', () => {
  const { chunks } = buildSession('hello world foo', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.deepEqual(
    chunks.map(c => c.text),
    ['hello', 'world', 'foo']
  );
});

test('buildSession respects chunkSize=2', () => {
  const { chunks } = buildSession('one two three four five', { wpm: 300, chunkSize: 2, adaptive: false });
  assert.deepEqual(
    chunks.map(c => c.text),
    ['one two', 'three four', 'five']
  );
});

test('buildSession returns no chunks for empty input', () => {
  const { chunks } = buildSession('', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks.length, 0);
});

test('buildSession returns no chunks for whitespace-only input', () => {
  const { chunks } = buildSession('   \n\t  ', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks.length, 0);
});

test('each chunk has an in-range orpIndex', () => {
  const { chunks } = buildSession('hello world extraordinary', { wpm: 300, chunkSize: 1, adaptive: false });
  for (const chunk of chunks) {
    assert.ok(typeof chunk.orpIndex === 'number', 'orpIndex must be a number');
    assert.ok(chunk.orpIndex >= 0, `orpIndex must be >= 0 (got ${chunk.orpIndex} for "${chunk.text}")`);
    assert.ok(chunk.orpIndex < chunk.text.length, `orpIndex must be < text.length (got ${chunk.orpIndex} for "${chunk.text}")`);
  }
});

test('chunkDurationMs is proportional to word count at fixed WPM', () => {
  const { chunks: c1, chunkDurationMs: d1 } = buildSession('hello', { wpm: 300, chunkSize: 1, adaptive: false });
  const { chunks: c2, chunkDurationMs: d2 } = buildSession('hello world', { wpm: 300, chunkSize: 2, adaptive: false });
  // At 300 WPM: 1 word = 200 ms, 2 words = 400 ms
  assert.strictEqual(d1(c1[0]), 200);
  assert.strictEqual(d2(c2[0]), 400);
});

test('chunkDurationMs with adaptive off is independent of word shape', () => {
  const { chunks: short, chunkDurationMs: ds } = buildSession('a', { wpm: 300, chunkSize: 1, adaptive: false });
  const { chunks: long, chunkDurationMs: dl } = buildSession('extraordinary', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(ds(short[0]), dl(long[0]), 'same WPM, same word count → same duration');
});

test('chunkDurationMs scales inversely with WPM', () => {
  const { chunks: c1, chunkDurationMs: d1 } = buildSession('hello', { wpm: 300, chunkSize: 1, adaptive: false });
  const { chunks: c2, chunkDurationMs: d2 } = buildSession('hello', { wpm: 600, chunkSize: 1, adaptive: false });
  // 600 WPM is twice as fast → half the duration
  assert.strictEqual(d1(c1[0]), 200);
  assert.strictEqual(d2(c2[0]), 100);
});

test('buildSession with chunkSize=3 preserves order and short final chunk', () => {
  const { chunks } = buildSession('one two three four five six seven', { wpm: 300, chunkSize: 3, adaptive: false });
  assert.deepEqual(chunks.map(c => c.text), ['one two three', 'four five six', 'seven']);
});

// ORP focal-point tests (issue 03)
test('orpIndex for single-character chunk is 0', () => {
  const { chunks } = buildSession('a', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 0);
});

test('orpIndex for 2-char chunk is 1', () => {
  const { chunks } = buildSession('hi', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 1);
});

test('orpIndex for 3-char chunk is 1', () => {
  const { chunks } = buildSession('the', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 1);
});

test('orpIndex for 5-char chunk is 1', () => {
  const { chunks } = buildSession('hello', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 1);
});

test('orpIndex for 6-char chunk is 2', () => {
  const { chunks } = buildSession('speaks', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 2);
});

test('orpIndex for 9-char chunk is 2', () => {
  const { chunks } = buildSession('something', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 2);
});

test('orpIndex for 13-char chunk is 3', () => {
  const { chunks } = buildSession('extraordinary', { wpm: 300, chunkSize: 1, adaptive: false });
  assert.strictEqual(chunks[0].orpIndex, 3);
});

test('orpIndex is always within chunk bounds for varied lengths', () => {
  const words = ['a', 'hi', 'the', 'hello', 'speaks', 'something', 'persistence', 'extraordinary'];
  for (const word of words) {
    const { chunks } = buildSession(word, { wpm: 300, chunkSize: 1, adaptive: false });
    const { orpIndex, text } = chunks[0];
    assert.ok(orpIndex >= 0, `orpIndex must be >= 0 for "${word}"`);
    assert.ok(orpIndex < text.length, `orpIndex must be < length for "${word}" (got ${orpIndex})`);
  }
});

"""Pytest port of test/engine.test.js — tests the pure engine.py seam."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import build_session


def test_build_session_splits_into_one_word_chunks():
    result = build_session('hello world foo', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert [c['text'] for c in result['chunks']] == ['hello', 'world', 'foo']


def test_build_session_respects_chunk_size_2():
    result = build_session('one two three four five', {'wpm': 300, 'chunk_size': 2, 'adaptive': False})
    assert [c['text'] for c in result['chunks']] == ['one two', 'three four', 'five']


def test_build_session_empty_input():
    result = build_session('', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert len(result['chunks']) == 0


def test_build_session_whitespace_only():
    result = build_session('   \n\t  ', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert len(result['chunks']) == 0


def test_each_chunk_has_in_range_orp_index():
    result = build_session('hello world extraordinary', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    for chunk in result['chunks']:
        assert isinstance(chunk['orp_index'], int), 'orp_index must be an int'
        assert chunk['orp_index'] >= 0, f"orp_index must be >= 0 for '{chunk['text']}'"
        assert chunk['orp_index'] < len(chunk['text']), f"orp_index must be < text length for '{chunk['text']}'"


def test_chunk_duration_ms_proportional_to_word_count():
    r1 = build_session('hello', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    r2 = build_session('hello world', {'wpm': 300, 'chunk_size': 2, 'adaptive': False})
    assert r1['chunk_duration_ms'](r1['chunks'][0]) == 200
    assert r2['chunk_duration_ms'](r2['chunks'][0]) == 400


def test_chunk_duration_ms_adaptive_off_word_shape_independent():
    r_short = build_session('a', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    r_long = build_session('extraordinary', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert r_short['chunk_duration_ms'](r_short['chunks'][0]) == r_long['chunk_duration_ms'](r_long['chunks'][0])


def test_chunk_duration_ms_scales_inversely_with_wpm():
    r1 = build_session('hello', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    r2 = build_session('hello', {'wpm': 600, 'chunk_size': 1, 'adaptive': False})
    assert r1['chunk_duration_ms'](r1['chunks'][0]) == 200
    assert r2['chunk_duration_ms'](r2['chunks'][0]) == 100


def test_build_session_chunk_size_3_order_and_short_final():
    result = build_session('one two three four five six seven', {'wpm': 300, 'chunk_size': 3, 'adaptive': False})
    assert [c['text'] for c in result['chunks']] == ['one two three', 'four five six', 'seven']


# ORP focal-point tests
def test_orp_index_single_char():
    result = build_session('a', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 0


def test_orp_index_2_char():
    result = build_session('hi', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 1


def test_orp_index_3_char():
    result = build_session('the', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 1


def test_orp_index_5_char():
    result = build_session('hello', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 1


def test_orp_index_6_char():
    result = build_session('speaks', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 2


def test_orp_index_9_char():
    result = build_session('something', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 2


def test_orp_index_13_char():
    result = build_session('extraordinary', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert result['chunks'][0]['orp_index'] == 3


def test_orp_index_within_bounds_varied_lengths():
    words = ['a', 'hi', 'the', 'hello', 'speaks', 'something', 'persistence', 'extraordinary']
    for word in words:
        result = build_session(word, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
        chunk = result['chunks'][0]
        assert chunk['orp_index'] >= 0, f"orp_index >= 0 for '{word}'"
        assert chunk['orp_index'] < len(chunk['text']), f"orp_index < length for '{word}'"


# Input normalization tests
def test_normalization_removes_fenced_code_blocks():
    text = 'before\n```js\nconsole.log("hello");\n```\nafter'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert not any('console' in t for t in texts), 'code block content must be removed'
    assert not any('```' in t for t in texts), 'fences must be removed'
    assert texts == ['before', 'after']


def test_normalization_fenced_block_no_language_tag():
    text = 'text before\n```\nsome code here\n```\ntext after'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert not any('some' in t for t in texts), 'code block content must be removed'
    assert texts == ['text', 'before', 'text', 'after']


def test_normalization_strips_heading_markers():
    text = '# Title\n## Subtitle\nParagraph text'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert not any(t.startswith('#') for t in texts), 'hash markers must be stripped'
    assert 'Title' in texts
    assert 'Subtitle' in texts


def test_normalization_strips_bold_italic():
    text = 'This is **bold** and *italic* text'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert 'bold' in texts
    assert 'italic' in texts
    assert not any('**' in t or '*' in t for t in texts), 'asterisks must be stripped'


def test_normalization_strips_inline_backticks():
    text = 'Call the `foo` function'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert 'foo' in texts
    assert not any('`' in t for t in texts)


def test_normalization_strips_markdown_links():
    text = 'See [the docs](https://example.com) for details'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert 'the' in texts
    assert not any('[' in t for t in texts)
    assert not any('https' in t for t in texts)


def test_normalization_strips_list_markers():
    text = '- item one\n- item two\n* item three'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    texts = [c['text'] for c in result['chunks']]
    assert 'one' in texts
    assert not any(t == '-' or t == '*' for t in texts)


def test_normalization_collapses_whitespace():
    text = 'word1\n\n\n\nword2   word3\n\nword4'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert [c['text'] for c in result['chunks']] == ['word1', 'word2', 'word3', 'word4']


def test_empty_after_normalization():
    text = '```js\nconsole.log("hi");\n```'
    result = build_session(text, {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert len(result['chunks']) == 0


# Adaptive pacing tests
def test_adaptive_long_word_displays_longer():
    r_short = build_session('a', {'wpm': 300, 'chunk_size': 1, 'adaptive': True})
    r_long = build_session('extraordinary', {'wpm': 300, 'chunk_size': 1, 'adaptive': True})
    assert r_long['chunk_duration_ms'](r_long['chunks'][0]) > r_short['chunk_duration_ms'](r_short['chunks'][0])


def test_adaptive_sentence_end_adds_time():
    r_plain = build_session('hello', {'wpm': 300, 'chunk_size': 1, 'adaptive': True})
    r_sentence = build_session('hello.', {'wpm': 300, 'chunk_size': 1, 'adaptive': True})
    assert r_sentence['chunk_duration_ms'](r_sentence['chunks'][0]) > r_plain['chunk_duration_ms'](r_plain['chunks'][0])


def test_adaptive_off_same_duration():
    r_short = build_session('a', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    r_long = build_session('extraordinary', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert r_long['chunk_duration_ms'](r_long['chunks'][0]) == r_short['chunk_duration_ms'](r_short['chunks'][0])


def test_adaptive_off_sentence_end_no_extra_time():
    r_plain = build_session('hello', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    r_sentence = build_session('hello.', {'wpm': 300, 'chunk_size': 1, 'adaptive': False})
    assert r_sentence['chunk_duration_ms'](r_sentence['chunks'][0]) == r_plain['chunk_duration_ms'](r_plain['chunks'][0])

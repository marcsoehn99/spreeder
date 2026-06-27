# Strip markdown markers and remove code blocks from pasted input

Pasted text (typically agent output) is normalized before reading: markdown syntax markers (`#`, `*`, `-`, backticks, link brackets) are stripped, and fenced code blocks are removed entirely from the reading stream. The use case is internalizing prose/explanation quickly; code examples need to be read whole, not flashed word-by-word via RSVP, so they are excluded rather than mangled. If reading code ever becomes desirable, an "include code blocks" toggle can be added without reworking the normalization.

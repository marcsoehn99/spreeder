# 03 — ORP focal point

Status: done

## Parent

`.scratch/spreeder-v1/PRD.md`

## What to build

Give each chunk a stable focal point: the **ORP** (Optimal Recognition Point) character is pinned at a fixed horizontal position and marked red, so the reader's eye never moves.

- Engine: a deterministic, pure function computes `orpIndex` for a chunk from its text (a standard RSVP "slightly left of centre" rule based on length). In range for all chunk lengths, including single-character and single-word chunks.
- Shell: render each chunk as a three-part layout (pre-ORP / ORP / post-ORP) with the ORP column fixed so the red character sits at the same x-position for every chunk regardless of chunk length.

## Acceptance criteria

- [x] Each chunk shows exactly one red ORP character
- [x] The ORP character stays at the same horizontal position across chunks of differing length
- [x] `orpIndex` is deterministic and always within the chunk's bounds
- [x] Unit tests cover `orpIndex` for varying lengths including 1-character and single-word chunks
- [x] No eye movement required to track the focal point during playback (verified by opening the file)

## Blocked by

- `.scratch/spreeder-v1/issues/01-tracer-rsvp-playback.md`

# NFL Lab verification report

Capture date: 2026-11-13 UTC  ·  verifier: `scripts/verify_nfl_lab.py`

## What this gate proves

- Every factual row on the 11 lab pages carries an official-host (league/club) or repository source link.
- No official row points at a non-official host; repository rows are marked as such.
- Rows with no source are explicitly labelled `NO SOURCE — DESIGN` in the page itself.
- No numeric correlation value is published while every strategy fails a gate.
- The leaderboard is empty exactly when no strategy passes all ten gates.
- Each strategy's gate tally in the matrix matches the matrix data.
- Internal links on the lab pages resolve to real files.

## What it does NOT prove

- It does not re-fetch the sources; content accuracy of a transcribed row rests on the
  line-by-line read performed on 2026-11-13 and recorded in `research/nfl-lab-audit-2026-11-13.md`.
- It does not cover the 15 pages of the main dashboard (those are gated by `scripts/verify.py`).
- A passing gate means the page is structurally honest, not that the strategy is profitable.

## Counts

- Pages checked: 11
- Rows checked: 252 (official 104, repository 37, design 89, prose-with-context 22)
- Internal links: 299 (broken 0)
- Registered sources: 18
- Errors: 0
- Warnings: 0

## Result

PASS

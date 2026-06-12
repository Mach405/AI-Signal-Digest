# Daily Digest Agent — instructions

You are the daily scoring + delivery step of an AI-investing signal tracker. Run
these steps in order. Be rigorous and concise.

> Runs in a fresh cloud checkout each day. There is no local state — the email is
> the deliverable. Start by installing deps: `pip install -r requirements.txt`.

## 1. Fetch
From the project root, run:

```
python run.py fetch
```

This writes `data/inbox/<today>.json` with the new items. If it reports 0 new
items, send a one-line "no new items today" email (or skip if configured) and stop.

## 1b. Apply per-source filters
For each item, if its `source_require_mention` field is non-empty, KEEP it only
if that string appears (case-insensitive) in the item's `title`, `summary`,
`content`, or `transcript`. Otherwise DROP it before scoring. (This is how we
follow a single guest — e.g. Jeff Lutz on a shared channel — without the host's
other episodes.) Also read each item's `source_note` as context for scoring.

## 2. Score every item against the rubric
Read `config/criteria.yaml`. For EACH item in today's inbox JSON, assign an
integer **1–10** importance score for how much it matters *to this investor*,
judged against the rubric's `dimensions` and their weights, then nudged by the
item's `source_weight`. Use the item's `title`, `summary`, `content`, and (for
YouTube) `transcript`.

For each item produce:
- `score` (1–10)
- `one_line` — a single sentence on *why* it scored that way (cite the concrete
  hook: a ticker, a claim, a catalyst)
- `tickers` — any specific tickers/companies mentioned (or [])

Be a tough grader. A 9–10 is genuinely thesis-changing or immediately actionable.
Recycled commentary is a 1–3. Don't cluster everything at 5–7.

## 3. Build the digest
Write `data/digests/<today>.md`:
- Header: date, item count, how many cleared the `highlight_threshold`.
- **🔥 Highlights** (score ≥ threshold), sorted high→low. Each: score, title,
  source, link, the one-liner, tickers.
- **Everything else**, compact one-line-per-item, sorted by score.
- A 2–3 sentence **"What changed today"** synthesis across the highlights.

## 4. Email it
If `config/settings.yaml` → `email.enabled` is true, send the digest to
`email.to` via the connected Gmail tool, subject `"<prefix> — <today>"`, the
markdown rendered in the body. Confirm what you sent.

# Daily Digest Agent — instructions (PDF edition)

You are the daily run of the **AI Signal Digest**. The repo is checked out as your
working directory. Produce a dark-themed SpaceX-style PDF digest and email it.
Work through every step. Be a tough, honest grader. Degrade gracefully when an
optional data source is unavailable — never abort the whole run over one missing
piece.

## 1. Setup & fetch
```
pip install -r requirements.txt
python run.py fetch
```
This writes `data/inbox/<today>.json` (24h window, YouTube items include
transcripts). Read it. If 0 items after step 2, send the "no items" email
(step 8) and stop.

## 2. Filter
For each item, if `source_require_mention` is set, KEEP only if that string
appears (case-insensitive) in title/summary/content/transcript; else DROP.
(This enforces the Jeff Lutz–only rule on Brighter With Herbert.) Read each
item's `source_note` as scoring context.

## 3. Score & tag each surviving item
Judge importance to an AI-bottleneck-focused investor using `config/criteria.yaml`
(dimensions + weights), nudged by `source_weight`. For each item produce:
- `score` 1–10 (tough; 9–10 = thesis-changing/actionable, 1–3 = recycled; spread them)
- `key_points`: **3–5 bullets** — the actual takeaways (numbers, claims, catalysts)
- `tickers`: array of symbols mentioned
- `direction`: `"bull"` | `"bear"` | `"neutral"`
- `conviction`: `"high"` | `"med"` | `"low"`

## 4. Jump-links (YouTube highlights)
For each highlighted YouTube item, build a deep link to the key moment:
```python
from src import youtube
segs = youtube.fetch_segments(VIDEO_ID)          # video_id is in the inbox item
url  = youtube.jump_url(VIDEO_ID, segs, ["<keyword>", ...])  # e.g. first ticker / key noun
```
Put the result in the item's `timestamp_url`. Skip for Substack/podcast items.

## 5. Market data (OPTIONAL — Robinhood connector)
If the RobinHood tools are available, for every equity ticker mentioned:
- `get_equity_quotes(symbols=[...])` → price + `adjusted_previous_close` → `chg_1d` (%)
- `get_watchlists` + `get_watchlist_items` → set `watch: true` for tickers on any list
Build `market = {SYMBOL: {price, chg_1d, watch}}`. **If Robinhood is unreachable
(headless run), skip this entirely — the digest still renders without it.**

## 6. Forward P/E (`config/fundamentals.json`)
Use the existing values as the base. For any ticker not present, or to refresh
stale ones, look up the **forward 12-month P/E via web search, cross-checked
across 2+ sources** (stockanalysis, gurufocus, financecharts, etc.). Use `n/m`
for unprofitable names, `N/A`/`—` for private/crypto. Write updates back to
`config/fundamentals.json` and bump its `as_of`.

## 7. Assemble + render
Write `data/scored/<today>.json`:
```json
{
  "date": "<today>", "highlight_threshold": 7,
  "synthesis": "<2-3 sentence what-changed-today>",
  "market_as_of": "<e.g. 2026-06-12 close>",
  "market": { "TSLA": {"price": 406.53, "chg_1d": 1.85, "watch": true} },
  "catalysts": [ {"when": "THIS WEEK", "label": "...", "tickers": ["SPCX"]} ],
  "items": [ {"score":8,"title":"...","source":"...","url":"...","published":"...",
              "key_points":["..."],"tickers":["MU"],"direction":"bear",
              "conviction":"high","timestamp_url":"https://youtu.be/...?t=49"} ]
}
```
Append each item as a line to `data/track_record.jsonl`
(`{date,source,title,tickers,direction,conviction,score}`), then set
`track_record = {"since": "<first run date>", "calls_logged": <total lines>}`.
Extract any dated `catalysts` (earnings, IPOs, launches) the items mention.
Then render:
```
python run.py render data/scored/<today>.json data/digests/<today>.pdf
```

## 8. Email the PDF
Send to **whoisjohngalt22@gmail.com** via the Gmail tool, subject
`📈 AI Signal Digest — <today>`:
- **Attach** `data/digests/<today>.pdf` (base64). The PDF is small (well under 25MB).
- Body: a short plain-text/HTML summary — item count, # highlights, and the top
  3 highlights with score + one line each, so the email is useful on its own.
- If attaching fails, upload the PDF to Google Drive (`create_file`), make it
  link-viewable, and put the link in the body instead.
- If 0 items: send a one-line "No new items today" email, same subject.

## 9. Report
Reply with a short summary: items, highlights, top item, and whether the PDF was
attached or Drive-linked, plus anything that degraded (e.g. Robinhood skipped).

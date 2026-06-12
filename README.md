# AI Signal Digest

A daily digest of the highest-signal updates from the independent investors you
follow — across **YouTube, Substack, and podcasts** — each item scored **1–10**
against *your* rubric, with the best surfaced first and emailed to you.

No paid APIs, no scraping of walled platforms. Every source is an RSS feed;
YouTube transcripts come from the free `youtube-transcript-api`. (X/Twitter was
deliberately excluded — there's no free, fresh, ToS-clean way to read it.)

## How it works

```
  ┌─ run.py fetch (pure Python, no LLM, no keys) ──────────────────────────┐
  │  RSS: YouTube + Substack + podcasts → recent → dedupe (SQLite) →        │
  │  enrich YouTube w/ transcripts → data/inbox/<date>.json                 │
  └────────────────────────────────────────────────────────────────────────┘
  ┌─ scheduled Claude agent (digest_agent.md) ─────────────────────────────┐
  │  score each item vs config/criteria.yaml → data/digests/<date>.md →     │
  │  email via your connected Gmail                                         │
  └────────────────────────────────────────────────────────────────────────┘
```

Fetching is deterministic code. Scoring/email is a Claude agent so it uses your
rubric and Gmail with no extra API key or per-call cost.

## Setup

```bash
pip install -r requirements.txt
```

1. **Add your sources** in `config/sources.yaml`.
   - YouTube: get a channel's feed URL with
     `python run.py resolve "https://www.youtube.com/@Handle"`
   - Substack: `https://<name>.substack.com/feed`
   - Podcast: the show's RSS URL
2. **Tune your rubric** in `config/criteria.yaml` (seeded with your AI-bottleneck focus).
3. **Test the fetch:** `python run.py fetch` → check `data/inbox/<date>.json`.
4. **Schedule the daily run** (fetch + score + email) — see below.

## Scheduling the "chrono loop"

The daily agent follows `digest_agent.md`. Schedule it with Claude Code's
`/schedule` (a cloud cron agent) to run every morning. It will run the fetch,
score the inbox, build the digest, and email it.

## Files

| Path | What |
|---|---|
| `config/sources.yaml` | your channels / substacks / podcasts |
| `config/criteria.yaml` | the 1–10 ranking rubric |
| `config/settings.yaml` | lookback window, email, paths |
| `run.py` | `fetch`, `resolve`, `resolve-all` |
| `digest_agent.md` | instructions for the daily scoring/email agent |
| `data/inbox/` | raw fetched items per run |
| `data/digests/` | finished daily digests |

## Roadmap
- v2: Whisper transcription for podcasts that ship audio-only (no show notes).
- v2: per-source reliability stats + a weekly "who was right" scorecard.

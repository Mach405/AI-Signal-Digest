"""Orchestrates a fetch run:

  load sources -> fetch every feed -> keep recent -> drop already-seen ->
  enrich YouTube items with transcripts -> write data/inbox/<date>.json

The output JSON is what the daily scoring agent reads. Scoring/ranking and email
are intentionally NOT here — those are done by the scheduled Claude agent so they
use your rubric + your Gmail connection with no extra API keys.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from . import config, feeds, state, youtube

ROOT = Path(__file__).resolve().parent.parent


def run():
    cfg = config.settings()
    srcs = config.sources()
    now = datetime.now(timezone.utc)
    lookback = cfg.get("lookback_hours", 30)

    all_items = []
    for stype in ("youtube", "substack", "podcast"):
        for source in (srcs.get(stype) or []):
            if "EXAMPLE" in source.get("name", "") or "XXXX" in source.get("url", ""):
                continue  # skip placeholder rows
            if not source.get("enabled", True):
                print(f"  {stype:8} {source.get('name'):30} (disabled, skipped)")
                continue
            try:
                got = feeds.fetch_feed(stype, source)
            except Exception as e:
                print(f"  ! {stype}:{source.get('name')} failed: {e}")
                continue
            kept = feeds.recent(got, lookback)
            print(f"  {stype:8} {source.get('name'):30} {len(kept):>3} recent / {len(got)} total")
            all_items.extend(kept)

    new = state.filter_new(all_items)
    print(f"\n  {len(new)} new items (of {len(all_items)} recent)")

    # Enrich YouTube items with transcripts.
    max_chars = cfg.get("max_transcript_chars", 18000)
    for it in new:
        if it["source_type"] == "youtube" and it.get("video_id"):
            it["transcript"] = youtube.fetch_transcript(it["video_id"], max_chars)
            if it["transcript"]:
                print(f"    transcript ✓  {it['title'][:60]}")

    # Write the inbox file.
    inbox_dir = ROOT / cfg.get("inbox_dir", "data/inbox")
    inbox_dir.mkdir(parents=True, exist_ok=True)
    out = inbox_dir / f"{now.date()}.json"
    payload = {"generated_at": now.isoformat(), "count": len(new), "items": new}
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  wrote {out}  ({len(new)} items)")

    state.mark_seen(new, now.isoformat())
    return out

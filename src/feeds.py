"""Unified RSS fetching for YouTube / Substack / podcast feeds via feedparser.

Every source becomes a normalized item dict:
    id, source_type, source_name, source_weight, author, title, url,
    published (ISO8601 or ''), published_ts (epoch or 0), summary, content,
    video_id (YouTube only)
"""
import re
import time
import calendar
from datetime import datetime, timezone

import feedparser


def _clean(html):
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)        # strip tags
    text = re.sub(r"&[a-z]+;", " ", text)        # crude entity strip
    return re.sub(r"\s+", " ", text).strip()


def _published(entry):
    st = entry.get("published_parsed") or entry.get("updated_parsed")
    if not st:
        return "", 0
    ts = calendar.timegm(st)
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(), ts


def _video_id(entry):
    if entry.get("yt_videoid"):
        return entry["yt_videoid"]
    m = re.search(r"yt:video:([\w-]{11})", entry.get("id", ""))
    return m.group(1) if m else None


def fetch_feed(source_type, source):
    """Fetch one configured source -> list of normalized items."""
    parsed = feedparser.parse(source["url"])
    weight = float(source.get("weight", 1.0))
    name = source.get("name", parsed.feed.get("title", source["url"]))
    items = []

    for e in parsed.entries:
        published, ts = _published(e)
        vid = _video_id(e) if source_type == "youtube" else None
        # richest body the feed offers
        body = ""
        if e.get("content"):
            body = e["content"][0].get("value", "")
        body = body or e.get("summary", "") or e.get("description", "")

        items.append({
            "id": e.get("id") or e.get("link"),
            "source_type": source_type,
            "source_name": name,
            "source_weight": weight,
            "source_note": source.get("note", ""),
            "source_require_mention": source.get("require_mention", ""),
            "author": e.get("author", name),
            "title": _clean(e.get("title", "(untitled)")),
            "url": e.get("link", ""),
            "published": published,
            "published_ts": ts,
            "summary": _clean(e.get("summary", ""))[:1000],
            "content": _clean(body),
            "video_id": vid,
        })
    return items


def recent(items, lookback_hours):
    """Keep items published within the lookback window (undated items kept)."""
    cutoff = time.time() - lookback_hours * 3600
    return [it for it in items if it["published_ts"] == 0 or it["published_ts"] >= cutoff]

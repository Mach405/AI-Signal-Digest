"""YouTube helpers: resolve a channel URL/handle to its RSS feed, and fetch
transcripts. No API key — uses the public channel page and the free
youtube-transcript-api."""
import re
import requests

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def resolve_feed(url_or_handle):
    """Given a channel URL or @handle, return its RSS feed URL (or None)."""
    u = url_or_handle.strip()
    if u.startswith("@"):
        u = "https://www.youtube.com/" + u
    elif not u.startswith("http"):
        u = "https://www.youtube.com/@" + u

    # Already a channel_id URL?
    m = re.search(r"/channel/(UC[\w-]{22})", u)
    if m:
        return _feed(m.group(1))

    # Otherwise scrape the channel page for its channelId.
    try:
        html = requests.get(u, headers=UA, timeout=20).text
    except requests.RequestException as e:
        print(f"  ! could not fetch {u}: {e}")
        return None
    m = re.search(r'"channelId":"(UC[\w-]{22})"', html) or \
        re.search(r"/channel/(UC[\w-]{22})", html)
    return _feed(m.group(1)) if m else None


def _feed(channel_id):
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def fetch_transcript(video_id, max_chars):
    """Best-effort transcript text. Returns '' if unavailable (gracefully)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return ""

    chunks = None
    # The library's API has shifted across versions — try both shapes.
    try:  # newer instance-based API
        chunks = YouTubeTranscriptApi().fetch(video_id)
        chunks = [{"text": c.text} for c in chunks]
    except Exception:
        try:  # older classmethod API
            chunks = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception:
            return ""

    text = " ".join(c["text"] for c in chunks if c.get("text"))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def fetch_segments(video_id):
    """Return [(start_seconds, text), ...] for building &t= deep links. [] if none."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return []
    try:
        raw = YouTubeTranscriptApi().fetch(video_id)
        return [(float(c.start), c.text) for c in raw]
    except Exception:
        try:
            raw = YouTubeTranscriptApi.get_transcript(video_id)
            return [(float(c["start"]), c["text"]) for c in raw]
        except Exception:
            return []


def jump_url(video_id, segments, keywords, skip_intro=12.0):
    """Deep link to the first post-intro segment mentioning any keyword."""
    secs = 0.0
    for start, text in segments:
        if start < skip_intro:
            continue
        low = text.lower()
        if any(k.lower() in low for k in keywords):
            secs = start
            break
    return f"https://youtu.be/{video_id}?t={int(secs)}"

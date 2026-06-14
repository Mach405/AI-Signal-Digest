"""Score the day's inbox via headless `claude -p` (uses the Claude Code
subscription — no API key), then enrich with forward P/E, watchlist flags, and
YouTube jump-link timestamps. Writes data/scored/<date>.json for the renderer.
"""
import json
import os
import re
import subprocess
from pathlib import Path

from . import config, youtube

ROOT = Path(__file__).resolve().parent.parent
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")


def _filtered_rows(items):
    """Apply require_mention filters and build compact rows for scoring."""
    rows = []
    for it in items:
        rm = it.get("source_require_mention", "")
        if rm:
            hay = " ".join([it.get("title", ""), it.get("summary", ""),
                            it.get("content", ""), it.get("transcript", "")]).lower()
            if rm.lower() not in hay:
                continue
        body = it.get("transcript") or it.get("content") or it.get("summary") or ""
        rows.append({
            "id": it["id"],
            "title": it["title"],
            "source": it["source_name"],
            "source_note": it.get("source_note", ""),
            "text": re.sub(r"\s+", " ", body)[:3000],
        })
    return rows


def _prompt(rows, crit):
    return (
        "You are scoring items for an AI-bottleneck-focused investor's daily "
        "digest. Use this rubric:\n\n" + json.dumps(crit, ensure_ascii=False, indent=2) +
        "\n\nFor EACH item below produce an object with:\n"
        "- id (echo back exactly)\n"
        "- score: integer 1-10. Tough grader: 9-10 = thesis-changing/immediately "
        "actionable, 5-6 = middling, 1-3 = recycled/noise. SPREAD the scores.\n"
        "- key_points: array of 3-5 short bullet strings — the real takeaways "
        "(specific numbers, claims, tickers, catalysts)\n"
        "- tickers: array of uppercase stock symbols mentioned ([] if none)\n"
        "- direction: \"bull\" | \"bear\" | \"neutral\"\n"
        "- conviction: \"high\" | \"med\" | \"low\"\n\n"
        "Also produce top-level:\n"
        "- synthesis: 2-3 sentence 'what changed today' across the strongest items\n"
        "- catalysts: array of {when, label, tickers} for DATED events mentioned "
        "(earnings, IPOs, launches); [] if none\n\n"
        "Output ONLY valid JSON (no markdown fences), exactly this shape:\n"
        '{"items":[{"id":"...","score":8,"key_points":["..."],"tickers":["MU"],'
        '"direction":"bear","conviction":"high"}],"synthesis":"...","catalysts":[]}\n\n'
        "ITEMS:\n" + json.dumps(rows, ensure_ascii=False)
    )


def _invoke_claude(prompt, model):
    res = subprocess.run([CLAUDE, "-p", prompt, "--model", model],
                         capture_output=True, text=True, timeout=900)
    out = (res.stdout or "").strip()
    if not out:
        raise RuntimeError(f"claude -p returned nothing. stderr: {res.stderr[:400]}")
    out = re.sub(r"^```[a-z]*\n?", "", out)
    out = re.sub(r"\n?```$", "", out)
    m = re.search(r"\{.*\}", out, re.S)
    return json.loads(m.group(0) if m else out)


def run(inbox_path=None):
    cfg = config.settings()
    crit = config.criteria()
    thr = int(crit.get("highlight_threshold", 7))
    inbox_dir = ROOT / cfg.get("inbox_dir", "data/inbox")
    if inbox_path is None:
        inbox_path = sorted(inbox_dir.glob("*.json"))[-1]
    inbox = json.loads(Path(inbox_path).read_text(encoding="utf-8"))
    items = inbox["items"]
    date = inbox["generated_at"][:10]

    rows = _filtered_rows(items)
    if not rows:
        scored = {"date": date, "highlight_threshold": thr,
                  "synthesis": "No new items in this window.", "items": []}
        return _write(scored, date)

    result = _invoke_claude(_prompt(rows, crit), cfg.get("score_model", "sonnet"))
    by_id = {it["id"]: it for it in items}
    by_url = {it.get("url"): it for it in items}
    watch = set(cfg.get("watchlist") or [])

    out_items = []
    for s in result.get("items", []):
        src = by_id.get(s.get("id"))
        if not src:
            continue
        out_items.append({
            "score": int(s.get("score", 0)),
            "title": src["title"],
            "source": src["source_name"],
            "url": src.get("url", ""),
            "published": src.get("published", ""),
            "key_points": s.get("key_points", []),
            "tickers": [t.upper() for t in (s.get("tickers") or [])],
            "direction": s.get("direction", "neutral"),
            "conviction": s.get("conviction", "med"),
        })

    # jump-link timestamps for YouTube highlights
    for it in out_items:
        src = by_url.get(it["url"])
        if it["score"] >= thr and src and src.get("video_id"):
            segs = youtube.fetch_segments(src["video_id"])
            if segs:
                kw = it["tickers"][:2] or [it["title"].split()[0]]
                it["timestamp_url"] = youtube.jump_url(src["video_id"], segs, kw)

    market = {}
    for it in out_items:
        for t in it["tickers"]:
            if t in watch:
                market.setdefault(t, {})["watch"] = True

    # track record (accrues locally over time)
    tr = ROOT / "data" / "track_record.jsonl"
    tr.parent.mkdir(parents=True, exist_ok=True)
    with open(tr, "a", encoding="utf-8") as f:
        for it in out_items:
            f.write(json.dumps({"date": date, "source": it["source"], "title": it["title"],
                                "tickers": it["tickers"], "direction": it["direction"],
                                "conviction": it["conviction"], "score": it["score"]}) + "\n")
    calls = sum(1 for _ in open(tr, encoding="utf-8"))

    scored = {"date": date, "highlight_threshold": thr,
              "synthesis": result.get("synthesis", ""),
              "catalysts": result.get("catalysts", []),
              "market": market, "market_as_of": "watchlist flags (local)",
              "track_record": {"since": date, "calls_logged": calls},
              "items": out_items}
    return _write(scored, date)


def _write(scored, date):
    out_dir = ROOT / "data" / "scored"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{date}.json"
    p.write_text(json.dumps(scored, indent=2, ensure_ascii=False), encoding="utf-8")
    return p

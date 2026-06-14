"""Render a scored digest JSON into a dark-themed PDF.

Theme: SpaceX-inspired — deep space-black background with a faint starfield,
royal-blue accents, Robinhood-green tickers each followed by their forward P/E
(pulled from config/fundamentals.json), per-item key points, and native
infographics (by-source bar chart, most-mentioned tickers, per-item magnitude
bar + color spine).

Usage: python run.py render data/scored/<date>.json [out.pdf]
"""
import json
import random
from collections import Counter
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent

# ── Royal-blue / space theme (RGB) ────────────────────────────────────────────
# SpaceX monochrome: true-black background, white type, gray hairlines.
BG       = (4, 4, 6)         # space black
BAND     = (10, 10, 12)      # near-black
PANEL    = (15, 15, 18)      # dark-gray panel
CARD_HI  = (20, 20, 24)      # highlight wash
RULE     = (52, 52, 57)      # hairlines
TEXT     = (240, 240, 244)   # white text
MUTED    = (150, 150, 156)   # gray
ROYAL    = (236, 236, 240)   # white accent (heads, bars, spine, links) — mono
ROYAL_DK = (40, 40, 45)      # dark gray (bar tracks)
RH_GREEN = (0, 200, 5)       # Robinhood green for tickers (kept as accent)

_REPL = {"—": "-", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"',
         "…": "...", "•": "-", " ": " ", "→": "->"}

# deterministic starfield (fixed seed → reproducible across runs)
_RNG = random.Random(7)
_STARS = [(_RNG.uniform(0, 210), _RNG.uniform(0, 297),
           _RNG.uniform(0.12, 0.5), _RNG.uniform(0.3, 1.0)) for _ in range(110)]


def _san(s):
    if not s:
        return ""
    for k, v in _REPL.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "ignore").decode("latin-1")


def _band(score):
    s = int(score)
    if s >= 9:
        return (240, 240, 244)   # bright white — top signal
    if s >= 7:
        return (200, 200, 205)   # light gray — highlight
    if s >= 5:
        return (140, 140, 146)   # mid gray — middling
    return (90, 90, 96)          # dark gray — noise


def _space(s, gap=" "):
    """Letter-space a string for the tracked SpaceX masthead look."""
    return gap.join(list(_san(s)))


_FUND = None


def _fund():
    global _FUND
    if _FUND is None:
        try:
            _FUND = json.loads((ROOT / "config" / "fundamentals.json")
                               .read_text(encoding="utf-8")).get("forward_pe", {})
        except Exception:
            _FUND = {}
    return _FUND


_MARKET = {}


def _mkt(sym):
    return _MARKET.get(sym, {})


class _Digest(FPDF):
    def header(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, self.w, self.h, style="F")
        # starfield — brighter inside the top band, faint over the body
        for x, y, s, b in _STARS:
            v = int(150 + 105 * b)
            if y > 32:
                v = int(v * 0.4)        # dim body stars to protect readability
            self.set_fill_color(min(255, v), min(255, v), min(255, v + 6))
            self.ellipse(x, y, s, s, style="F")


def _hbar(pdf, x, y, maxw, frac, color, h=3.0):
    frac = max(0.0, min(1.0, frac))
    pdf.set_fill_color(*ROYAL_DK)
    pdf.rect(x, y, maxw, h, style="F")
    pdf.set_fill_color(*color)
    pdf.rect(x, y, max(0.6, maxw * frac), h, style="F")


def _overview(pdf, W, items):
    x0 = 15
    src = Counter(it["source"] for it in items)
    ticks = Counter(t for it in items for t in (it.get("tickers") or []))
    rows = src.most_common()
    top_ticks = ticks.most_common(8)

    n = max(len(rows), len(top_ticks), 1)
    ph = 13 + n * 5.4 + 5
    y = pdf.get_y()

    pdf.set_fill_color(*PANEL)
    pdf.rect(x0, y, W, ph, style="F")
    pdf.set_fill_color(*ROYAL)
    pdf.rect(x0, y, 1.5, ph, style="F")

    pdf.set_xy(x0 + 5, y + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ROYAL)
    pdf.cell(0, 5, "AT A GLANCE", ln=1)

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(x0 + 5, y + 9)
    pdf.cell(0, 4, "BY SOURCE", ln=0)
    maxc = max((c for _, c in rows), default=1)
    lbl_x, bar_x, bar_w, cnt_x = x0 + 5, x0 + 48, 52, x0 + 103
    for i, (name, cnt) in enumerate(rows):
        ry = y + 14 + i * 5.4
        pdf.set_xy(lbl_x, ry - 0.5)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*TEXT)
        pdf.cell(bar_x - lbl_x - 2, 4, _san(name[:22]), ln=0)
        _hbar(pdf, bar_x, ry, bar_w, cnt / maxc, ROYAL)
        pdf.set_xy(cnt_x, ry - 0.5)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*MUTED)
        pdf.cell(8, 4, str(cnt), ln=0)

    rx = x0 + 120
    pdf.set_xy(rx, y + 9)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 4, "MOST MENTIONED", ln=0)
    fund = _fund()
    for j, (tk, c) in enumerate(top_ticks):
        ry = y + 14 + j * 5.4
        pdf.set_xy(rx, ry - 0.5)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*RH_GREEN)
        pdf.cell(18, 4, _san(tk), ln=0)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*MUTED)
        pe = fund.get(tk, {}).get("pe")
        pdf.cell(20, 4, _san(f"x{c}   fP/E {pe}" if pe else f"x{c}"), ln=0)

    pdf.set_y(y + ph + 4)


def _section(pdf, W, label):
    pdf.ln(2)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*ROYAL)
    pdf.cell(0, 7, _san(label.upper()), ln=1)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.3)
    yy = pdf.get_y()
    pdf.line(15, yy, 15 + W, yy)
    pdf.ln(3)


def _tickers(pdf, tx, tw, tk):
    """One ticker per line: green symbol, then forward P/E, live price, 1-day
    move (muted), and a * WATCH flag if it's on the user's watchlist."""
    fund = _fund()
    for sym in tk:
        pe = fund.get(sym, {}).get("pe")
        m = _mkt(sym)
        pdf.set_x(tx)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RH_GREEN)
        pdf.cell(pdf.get_string_width(_san(sym)) + 2.5, 4.9, _san(sym), ln=0)
        parts = []
        if pe:
            parts.append(f"fP/E {pe}")
        if m.get("price") is not None:
            parts.append(f"${m['price']}")
            chg = m.get("chg_1d")
            if chg is not None:
                parts.append(f"{'+' if chg >= 0 else ''}{chg}%")
        tail = "    ".join(parts)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*MUTED)
        pdf.cell(pdf.get_string_width(_san(tail)) + 4, 4.9, _san(tail), ln=0)
        if m.get("watch"):
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*TEXT)
            pdf.cell(16, 4.9, _san("  * WATCH"), ln=0)
        pdf.ln(4.9)


def _item(pdf, W, it):
    x0 = 15
    y0 = pdf.get_y()
    indent = 16
    tx, tw = x0 + indent, W - indent
    band = _band(it.get("score", 0))

    pdf.set_xy(tx, y0)
    pdf.set_font("Helvetica", "B", 11.5)
    pdf.set_text_color(*TEXT)
    pdf.multi_cell(tw, 5.6, _san(it.get("title", "")), align="L")

    # direction / conviction chip
    d = (it.get("direction") or "").upper()
    c = (it.get("conviction") or "").upper()
    if d or c:
        pdf.set_x(tx)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(*TEXT)
        pdf.cell(0, 4.2, _san("  /  ".join([x for x in (d, c) if x])), ln=1)

    pdf.set_x(tx)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    meta = f"{it.get('source', '')}   -   {str(it.get('published', ''))[:10]}"
    pdf.cell(tw * 0.55, 4.8, _san(meta), ln=0)
    by = pdf.get_y() + 1.4
    _hbar(pdf, tx + tw * 0.62, by, tw * 0.30, int(it.get("score", 0)) / 10.0, band, h=2.6)
    pdf.set_xy(tx + tw * 0.62 + tw * 0.30 + 2, pdf.get_y())
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*band)
    pdf.cell(10, 4.8, f"{int(it.get('score', 0))}/10", ln=1)

    pts = it.get("key_points") or ([it["one_line"]] if it.get("one_line") else [])
    pdf.ln(0.5)
    for p in pts:
        py = pdf.get_y()
        pdf.set_fill_color(*band)
        pdf.rect(tx + 1, py + 1.7, 1.4, 1.4, style="F")
        pdf.set_xy(tx + 5, py)
        pdf.set_font("Helvetica", "", 9.6)
        pdf.set_text_color(*TEXT)
        pdf.multi_cell(tw - 5, 4.8, _san(p))

    if it.get("tickers"):
        _tickers(pdf, tx, tw, it["tickers"])

    if it.get("timestamp_url"):
        import re as _re
        mt = _re.search(r"t=(\d+)", it["timestamp_url"])
        sec = int(mt.group(1)) if mt else 0
        mm, ss = divmod(sec, 60)
        pdf.set_x(tx)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*TEXT)
        pdf.cell(tw, 4.6, _san(f">> JUMP TO KEY MOMENT  {mm}:{ss:02d}"),
                 ln=1, link=it["timestamp_url"])

    if it.get("url"):
        pdf.set_x(tx)
        pdf.set_font("Helvetica", "", 7.8)
        pdf.set_text_color(*MUTED)
        pdf.cell(tw, 4.6, _san(it["url"][:95]), ln=1, link=it["url"])

    y1 = pdf.get_y()

    pdf.set_fill_color(*band)
    pdf.rect(x0, y0 + 1, 1.6, max(2.0, y1 - y0 - 1), style="F")
    pdf.rect(x0 + 3.5, y0, 10.5, 7.5, style="F")
    pdf.set_xy(x0 + 3.5, y0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*BG)
    pdf.cell(10.5, 7.5, str(it.get("score", "")), align="C")

    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.2)
    pdf.line(x0, y1 + 2.5, x0 + W, y1 + 2.5)
    pdf.set_y(y1 + 6)


def _consensus(pdf, W, items):
    """Per-ticker mention count + bull/neutral/bear split for names hit by 2+ items."""
    from collections import defaultdict
    agg = defaultdict(lambda: {"n": 0, "bull": 0, "bear": 0, "neu": 0})
    for it in items:
        d = it.get("direction", "neutral")
        for t in (it.get("tickers") or []):
            a = agg[t]
            a["n"] += 1
            a["bull"] += d == "bull"
            a["bear"] += d == "bear"
            a["neu"] += d not in ("bull", "bear")
    rows = sorted([(t, a) for t, a in agg.items() if a["n"] >= 2],
                  key=lambda x: -x[1]["n"])[:6]
    if not rows:
        return
    x0 = 15
    y = pdf.get_y()
    ph = 14 + len(rows) * 5.6 + 4
    pdf.set_fill_color(*PANEL)
    pdf.rect(x0, y, W, ph, style="F")
    pdf.set_fill_color(*ROYAL)
    pdf.rect(x0, y, 1.5, ph, style="F")
    pdf.set_xy(x0 + 5, y + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ROYAL)
    pdf.cell(0, 5, "WHERE YOUR SOURCES CONVERGE", ln=1)
    pdf.set_xy(x0 + 5, y + 8.6)
    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 4, "SPLIT BAR: BULL (LIGHT) / NEUTRAL (MID) / BEAR (DARK)", ln=0)
    fund = _fund()
    for i, (t, a) in enumerate(rows):
        ry = y + 14 + i * 5.6
        pdf.set_xy(x0 + 5, ry - 0.6)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*RH_GREEN)
        pdf.cell(18, 4.5, _san(t), ln=0)
        bx, bw, n = x0 + 32, 92, a["n"]
        cx = bx
        for key, col in (("bull", (232, 232, 236)), ("neu", (122, 122, 128)), ("bear", (58, 58, 64))):
            wseg = bw * (a[key] / n)
            if wseg > 0.2:
                pdf.set_fill_color(*col)
                pdf.rect(cx, ry, wseg, 3.2, style="F")
                cx += wseg
        pdf.set_xy(bx + bw + 3, ry - 0.6)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*MUTED)
        m = _mkt(t)
        extra = f"{n} mentions"
        if m.get("chg_1d") is not None:
            extra += f"    {'+' if m['chg_1d'] >= 0 else ''}{m['chg_1d']}%"
        pdf.cell(0, 4.5, _san(extra), ln=0)
    pdf.set_y(y + ph + 4)


def _catalysts(pdf, W, cats):
    if not cats:
        return
    x0 = 15
    y = pdf.get_y()
    ph = 11 + len(cats) * 5.2 + 3
    pdf.set_fill_color(*PANEL)
    pdf.rect(x0, y, W, ph, style="F")
    pdf.set_fill_color(*ROYAL)
    pdf.rect(x0, y, 1.5, ph, style="F")
    pdf.set_xy(x0 + 5, y + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*ROYAL)
    pdf.cell(0, 5, "CATALYSTS AHEAD", ln=1)
    for i, c in enumerate(cats):
        ry = y + 10.5 + i * 5.2
        pdf.set_xy(x0 + 5, ry)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*TEXT)
        pdf.cell(28, 4.6, _san(c.get("when", "")), ln=0)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 4.6, _san(c.get("label", "")), ln=1)
    pdf.set_y(y + ph + 4)


def render(scored_path, out_path=None):
    data = json.loads(Path(scored_path).read_text(encoding="utf-8"))
    items = data.get("items", [])
    global _MARKET
    _MARKET = data.get("market", {})
    thr = int(data.get("highlight_threshold", 7))
    highlights = sorted([i for i in items if int(i.get("score", 0)) >= thr],
                        key=lambda x: -int(x.get("score", 0)))
    others = sorted([i for i in items if int(i.get("score", 0)) < thr],
                    key=lambda x: -int(x.get("score", 0)))

    pdf = _Digest(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_title("AI Signal Digest")
    pdf.add_page()
    W = pdf.w - 30

    # masthead — black with starfield + thin white rule (SpaceX mono)
    for x, y, s, b in _STARS:
        if y < 33:
            v = int(165 + 90 * b)
            pdf.set_fill_color(v, v, v)
            pdf.ellipse(x, y, s, s, style="F")
    pdf.set_xy(15, 9)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 4, _space("DAILY MISSION BRIEF"), ln=1)
    pdf.set_xy(15, 13)
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_text_color(*TEXT)
    pdf.cell(0, 10, _space("AI SIGNAL DIGEST"), ln=1)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    sub = f"{data.get('date', '')}    /    {len(items)} ITEMS    /    {len(highlights)} HIGHLIGHTS"
    pdf.cell(0, 5, _san(sub.upper()), ln=1)
    pdf.set_draw_color(*TEXT)
    pdf.set_line_width(0.4)
    pdf.line(15, 31, pdf.w - 15, 31)
    pdf.set_y(37)

    if data.get("synthesis"):
        pdf.set_x(15)
        pdf.set_font("Helvetica", "I", 9.8)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(W, 5.2, _san(data["synthesis"]))
        pdf.ln(2)

    if items:
        _overview(pdf, W, items)
        _consensus(pdf, W, items)
    if data.get("catalysts"):
        _catalysts(pdf, W, data["catalysts"])

    if highlights:
        _section(pdf, W, "Highlights")
        for it in highlights:
            _item(pdf, W, it)
    if others:
        _section(pdf, W, "Everything else")
        for it in others:
            _item(pdf, W, it)
    if not items:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 8, "No new items in this window.", ln=1)

    # footer — track record + data provenance
    pdf.ln(3)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 15 + W, pdf.get_y())
    pdf.ln(2)
    tr = data.get("track_record")
    if tr:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.multi_cell(W, 3.8, _san(
            f"Track record: logging since {tr.get('since')} - {tr.get('calls_logged')} "
            "calls recorded. Per-source accuracy activates as calls mature."))
    pdf.set_x(15)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(W, 3.6, _san(
        f"Prices: {data.get('market_as_of', 'n/a')} via Robinhood. "
        "Forward P/E = consensus NTM, cross-checked 2+ sources. Not investment advice."))

    if out_path is None:
        out_path = str(Path(scored_path).with_suffix(".pdf"))
    pdf.output(out_path)
    return out_path

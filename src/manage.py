"""Source-management CLI: list / add / remove / enable / disable.

Uses ruamel.yaml so edits preserve the comments in config/sources.yaml.
"""
from pathlib import Path

from ruamel.yaml import YAML

from . import youtube

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "config" / "sources.yaml"
TYPES = ("youtube", "substack", "podcast")

_yaml = YAML()
_yaml.preserve_quotes = True
_yaml.indent(mapping=2, sequence=2, offset=0)


def _load():
    with open(SOURCES_PATH, encoding="utf-8") as f:
        data = _yaml.load(f)
    for t in TYPES:
        if data.get(t) is None:
            data[t] = []
    return data


def _save(data):
    with open(SOURCES_PATH, "w", encoding="utf-8") as f:
        _yaml.dump(data, f)


def list_sources():
    data = _load()
    for t in TYPES:
        rows = data.get(t) or []
        print(f"\n{t} ({len(rows)})")
        if not rows:
            print("  (none)")
        for s in rows:
            state = "" if s.get("enabled", True) else "  [DISABLED]"
            w = s.get("weight", 1.0)
            extra = "  ⟨require: %s⟩" % s["require_mention"] if s.get("require_mention") else ""
            print(f"  • {s.get('name','?'):34} w={w}{state}{extra}")
            print(f"      {s.get('url','')}")


def add_source(stype, name, url_or_handle, weight=1.0, note=None):
    if stype not in TYPES:
        print(f"  ! type must be one of {TYPES}")
        return
    url = url_or_handle
    if stype == "youtube" and "feeds/videos.xml" not in url_or_handle:
        resolved = youtube.resolve_feed(url_or_handle)
        if not resolved:
            print(f"  ! could not resolve YouTube source '{url_or_handle}'")
            return
        url = resolved
        print(f"  resolved -> {url}")

    data = _load()
    if any(s.get("name") == name for s in data[stype]):
        print(f"  ! a {stype} source named '{name}' already exists")
        return
    entry = {"name": name, "url": url, "weight": float(weight), "enabled": True}
    if note:
        entry["note"] = note
    data[stype].append(entry)
    _save(data)
    print(f"  added {stype}: {name}")


def remove_source(name):
    data = _load()
    removed = 0
    for t in TYPES:
        before = len(data[t])
        data[t] = [s for s in data[t] if s.get("name") != name]
        removed += before - len(data[t])
    if removed:
        _save(data)
        print(f"  removed {removed} source(s) named '{name}'")
    else:
        print(f"  ! no source named '{name}'")


def set_enabled(name, enabled):
    data = _load()
    hit = 0
    for t in TYPES:
        for s in data[t]:
            if s.get("name") == name:
                s["enabled"] = enabled
                hit += 1
    if hit:
        _save(data)
        print(f"  {'enabled' if enabled else 'disabled'} '{name}'")
    else:
        print(f"  ! no source named '{name}'")

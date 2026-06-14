#!/usr/bin/env python3
"""Entry point.

  python run.py fetch                  # run the daily fetch -> data/inbox/<date>.json
  python run.py render <scored.json>   # render a scored digest JSON -> dark-theme PDF
  python run.py list                   # list all configured sources
  python run.py add <type> "<name>" <url-or-@handle> [--weight W] [--note "..."]
  python run.py remove "<name>"        # remove source(s) by name
  python run.py enable "<name>"        # un-mute a source
  python run.py disable "<name>"       # mute a source without deleting it
  python run.py resolve <url|@handle>  # print a YouTube channel's RSS feed URL
  python run.py resolve-all            # resolve every youtube source in sources.yaml

  <type> is one of: youtube | substack | podcast
"""
import argparse
import sys

from src import pipeline, youtube, config, manage


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    rest = sys.argv[2:]

    if cmd == "fetch":
        pipeline.run()

    elif cmd == "render":
        if not rest:
            print("usage: python run.py render <scored.json> [out.pdf]"); return
        from src import render
        out = render.render(rest[0], rest[1] if len(rest) > 1 else None)
        print(f"  wrote {out}")

    elif cmd == "list":
        manage.list_sources()

    elif cmd == "add":
        p = argparse.ArgumentParser(prog="run.py add")
        p.add_argument("type")
        p.add_argument("name")
        p.add_argument("url")
        p.add_argument("--weight", type=float, default=1.0)
        p.add_argument("--note", default=None)
        a = p.parse_args(rest)
        manage.add_source(a.type, a.name, a.url, a.weight, a.note)

    elif cmd == "remove":
        if not rest:
            print('usage: python run.py remove "<name>"'); return
        manage.remove_source(rest[0])

    elif cmd in ("enable", "disable"):
        if not rest:
            print(f'usage: python run.py {cmd} "<name>"'); return
        manage.set_enabled(rest[0], cmd == "enable")

    elif cmd == "resolve":
        if not rest:
            print("usage: python run.py resolve <channel-url-or-@handle>"); return
        feed = youtube.resolve_feed(rest[0])
        print(feed or "  (could not resolve — check the URL/handle)")

    elif cmd == "resolve-all":
        for s in (config.sources().get("youtube") or []):
            feed = youtube.resolve_feed(s["url"]) if "feeds/videos.xml" not in s["url"] else s["url"]
            print(f"{s.get('name','?'):30} -> {feed or 'UNRESOLVED'}")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()

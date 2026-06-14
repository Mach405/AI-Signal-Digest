#!/bin/zsh
# launchd wrapper for the daily AI Signal Digest run. Sets a clean PATH (so the
# `claude` CLI is found) and logs to data/daily.log.
export PATH="/Users/jonathanreed/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd /Users/jonathanreed/my-first-project || exit 1
echo "===== $(date) : starting daily run =====" >> data/daily.log
/usr/bin/python3 run.py daily >> data/daily.log 2>&1
echo "===== $(date) : finished (exit $?) =====" >> data/daily.log

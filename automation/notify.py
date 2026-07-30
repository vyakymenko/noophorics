#!/usr/bin/env python3
"""Report experiment state to a Telegram chat, or to stdout.

WHAT THIS DELIBERATELY CANNOT DO
--------------------------------
It does not receive. There is no polling loop, no webhook, no command handling.
A bot that accepts instructions from a chat is remote code execution on the
machine running the experiments, and the value of the feature -- knowing that a
run voided at 3am -- needs none of it.

It also does not interpret. Everything it emits is a fact with its provenance:
a gate value against its threshold, a void reason quoted from the runner, a
count of probe-conditions. It never says whether a result is good. That is the
line in CONTRIBUTING's automation table and it is the whole reason a loop is
allowed to exist here at all.

CREDENTIALS
-----------
The token is read from ``NOOPHORICS_TG_TOKEN`` and the destination from
``NOOPHORICS_TG_CHAT``. Neither is ever written to disk, logged, or committed;
this module refuses to print them even in errors. With either absent it falls
back to stdout, which is a fully supported mode -- the loop is useful without a
bot and must never require one.

    export NOOPHORICS_TG_TOKEN='...'      # from @BotFather
    export NOOPHORICS_TG_CHAT='...'       # your numeric chat id
    python3 automation/notify.py --test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

TOKEN_ENV = "NOOPHORICS_TG_TOKEN"
CHAT_ENV = "NOOPHORICS_TG_CHAT"
TIMEOUT_S = 15
# Telegram hard-limits a message to 4096 characters. Truncate rather than let
# the send fail: a truncated alert is better than a silent one.
MAX_CHARS = 3900


def configured() -> bool:
    return bool(os.environ.get(TOKEN_ENV) and os.environ.get(CHAT_ENV))


def _redact(text: str) -> str:
    """Strip the token from any string before it can reach a log."""
    token = os.environ.get(TOKEN_ENV)
    return text.replace(token, "<token>") if token else text


def send(text: str, silent: bool = False) -> bool:
    """Deliver one message. Returns True if it reached Telegram.

    Never raises. A notifier that can take down the run it is reporting on is
    worse than no notifier -- this is a monitoring path, and monitoring must not
    be able to break the thing it monitors.
    """
    body = text if len(text) <= MAX_CHARS else text[:MAX_CHARS] + "\n[truncated]"
    if not configured():
        print(body, flush=True)
        return False
    payload = urllib.parse.urlencode({
        "chat_id": os.environ[CHAT_ENV],
        "text": body,
        "disable_notification": "true" if silent else "false",
        "disable_web_page_preview": "true",
    }).encode()
    url = "https://api.telegram.org/bot%s/sendMessage" % os.environ[TOKEN_ENV]
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, data=payload), timeout=TIMEOUT_S) as r:
            ok = bool(json.load(r).get("ok"))
        if not ok:
            print("[notify] telegram rejected the message", file=sys.stderr)
        return ok
    except urllib.error.HTTPError as exc:
        # 401/400 carry the token in the URL; never let that reach a log.
        print("[notify] HTTP %s -- %s" % (exc.code, _redact(str(exc.reason))),
              file=sys.stderr)
    except Exception as exc:                                  # noqa: BLE001
        print("[notify] %s" % _redact(str(exc)), file=sys.stderr)
    print(body, flush=True)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="send one notification")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("message", nargs="*")
    args = ap.parse_args()
    if args.test:
        print("token set: %s | chat set: %s"
              % (bool(os.environ.get(TOKEN_ENV)), bool(os.environ.get(CHAT_ENV))))
        ok = send("noophorics: notifier test. Reports only; accepts no commands.")
        print("delivered to telegram: %s" % ok)
        return 0
    if not args.message:
        ap.error("nothing to send")
    send(" ".join(args.message))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

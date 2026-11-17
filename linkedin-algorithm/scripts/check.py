#!/usr/bin/env python3
"""Check a LinkedIn post against the ten feed-ranking vectors.

    python3 check.py post.txt --reader "sales leaders" --headline "..." --posted-today no [--json]

Exit 0 = pass (warnings allowed), 1 = at least one block, 2 = error.
No network, no dependencies beyond the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_READERS = (
    r"leaders?|founders?|ceos?|cfos?|ctos?|cmos?|cros?\b|vps?\b|heads? of|directors?|managers?|owners?|"
    r"operators?|executives?|sellers?|reps?\b|aes?\b|sdrs?|bdrs?|recruiters?|hiring managers?|marketers?|"
    r"engineers?|developers?|designers?|analysts?|consultants?|nurses?|doctors?|teachers?|lawyers?|"
    r"accountants?|investors?|students?|job seekers?|teams?\b|anyone who|if you(?:'re| are| run| lead| manage| own)"
)
STOP = {"the", "and", "for", "with", "that", "this", "your", "you", "are", "who", "from", "into", "they",
        "their", "about", "build", "help", "helping", "i", "a", "an", "of", "to", "in", "on", "at", "|", "&"}
BAIT = [
    (r"\bcomment\s+[\"'“]?[A-Z]{2,}[\"'”]?(?=[\s.,!]|$)", 0, "comment-a-keyword ask"),
    (r"\b(comment|reply|type|drop)\b[^.\n]{0,40}\b(and|&)\s+i('| wi)ll\s+(send|dm|share)", re.I, "comment-to-get ask"),
    (r"(?im)^\s*(agree|thoughts|right|yes or no)\s*\?\s*$", 0, "one-word bait question"),
    (r"\bcomment\s+(yes|no|below if|\"?yes\"?)\b", re.I, "comment-yes bait"),
    (r"\b(like|repost|share)\s+(this\s+)?if\b", re.I, "like/repost-if bait"),
    (r"\btag\s+(someone|a friend|a colleague|3|three|your)\b", re.I, "tag-a-friend bait"),
]
AI_TELLS = [r"\bdelve\b", r"\blandscape\b", r"\bgame[- ]changer\b", r"\bin today's fast[- ]paced\b",
            r"\bunlock(ing)? the (power|potential)\b", r"\bit'?s not (just )?\w+[^.\n]{0,30}, it'?s\b",
            r"\btestament to\b", r"\bseamless(ly)?\b", r"\bleverag(e|ing)\b", r"\belevate\b", r"(?m)^\s*(→|->)\s"]
URL_RX = re.compile(r"(https?://|www\.)\S+|\b[a-z0-9-]+\.(ai|com|io|co|net|org|app|dev)(/\S*)?\b", re.I)
MENTION_RX = re.compile(r"(?<![\w.])@[A-Za-z][\w.-]{1,40}")
EMOJI_BULLET = re.compile("(?m)^\\s*[\U0001F300-\U0001FAFF☀-➿✅❌]")


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9$+%]+", s.lower()) if len(w) > 2 and w not in STOP}


def check(text: str, reader: str = "", headline: str = "", posted_today: str = "") -> list[dict]:
    F: list[dict] = []
    add = lambda sev, v, d: F.append({"severity": sev, "vector": v, "detail": d})
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return [{"severity": "block", "vector": "input", "detail": "empty post"}]
    head3 = " ".join(lines[:3])

    # 1 + 5: reader and topic up front
    reader_rx = DEFAULT_READERS + ("|" + "|".join(re.escape(w) for w in reader.lower().split() if len(w) > 3) if reader else "")
    if not re.search(reader_rx, head3, re.I):
        add("block", "1+5", "the first 3 lines never say who this is for. Name the reader up front"
            + (f" ({reader})." if reader else "."))
    if headline and not (words(head3) & words(headline)) and not (reader and words(head3) & words(reader)):
        add("warn", "1", "the first 3 lines don't name the topic in the words your headline uses.")

    # 2: hook and skip model
    n1 = len(lines[0].split())
    if n1 > 18:
        add("warn", "2", f"line 1 is {n1} words. The scroller decides on it; aim for 18 or fewer.")
    if len(text) > 1800:
        add("warn", "2", f"{len(text)} characters. Past ~1,800, cut it or make it a document carousel.")

    # 3: bait
    for pat, flags, name in BAIT:
        m = re.search(pat, text, flags)
        if m:
            add("block", "3", f"engagement bait ({name}): \"{m.group(0)[:60]}\". Put a giveaway ask on the image, "
                "write \"free access below\", and end on a real question.")

    # 4: obvious AI phrasing
    hits = [re.search(p, text, re.I).group(0) for p in AI_TELLS if re.search(p, text, re.I)]
    if EMOJI_BULLET.search(text):
        hits.append("emoji bullets")
    if len(hits) >= 2:
        add("block", "4", "reads machine-written (" + ", ".join(h.strip() for h in hits[:5]) + "). Rewrite in your own words.")
    elif hits:
        add("warn", "4", f"AI tell: {hits[0].strip()}.")

    # 6: tags
    tags = MENTION_RX.findall(text)
    if len(tags) >= 4:
        add("block", "6", f"{len(tags)} tags. Tag only people who are part of the post.")
    elif len(tags) >= 2:
        add("warn", "6", f"{len(tags)} tags. Keep only people who are in the post.")

    # 7: closing question
    tail = " ".join(lines[-2:])
    if "?" not in tail:
        add("warn", "7", "no closing question. End on one people can take a side on (\"X or Y?\").")
    elif re.search(r"\b(what do you think|thoughts|agree|any thoughts|what about you)\s*\?", tail, re.I):
        add("warn", "7", "the closing question is generic. Ask one with two sides.")

    # 9: profile match
    if headline and not (words(text) & words(headline)):
        add("warn", "9", "the post shares no topic words with your headline. LinkedIn reads the profile to pick readers.")

    # link
    u = URL_RX.search(text)
    if u:
        add("block", "link", f"link in the body (\"{u.group(0)[:50]}\"). Put it in the comments, your profile or a DM.")

    # 10: frequency
    if posted_today.lower().startswith("y"):
        add("block", "10", "you already posted today. One a day; schedule this for tomorrow at your usual time.")
    elif not posted_today:
        add("warn", "10", "unknown whether you posted today. One a day, same time, reply for the first hour.")
    return F


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="post text file, or - for stdin")
    ap.add_argument("--reader", default="", help="who the post is for, e.g. 'sales leaders'")
    ap.add_argument("--headline", default="", help="your LinkedIn headline")
    ap.add_argument("--posted-today", default="", help="yes or no")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        text = sys.stdin.read() if a.file == "-" else Path(a.file).read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    F = check(text, a.reader, a.headline, a.posted_today)
    blocks = sum(f["severity"] == "block" for f in F)
    if a.json:
        print(json.dumps({"pass": blocks == 0, "findings": F}, indent=2))
    else:
        for f in F:
            print(f"[{'BLOCK' if f['severity'] == 'block' else 'warn '}] vector {f['vector']}: {f['detail']}")
        print(f"{'PASS' if not blocks else 'FAIL'}: {blocks} block, {len(F) - blocks} warn")
    sys.exit(1 if blocks else 0)


if __name__ == "__main__":
    main()

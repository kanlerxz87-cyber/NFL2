#!/usr/bin/env python3
"""Reserve-vs-injury-hub availability join (BL-65, session 6eeab460, R7).

Rule (BL-65): "not listed" on the weekly injury report never means "available". Each November 2026
Reserve/Injured placement is joined against the Week 10 injury-hub read. The output is a DELTA per
placement, never a level (BL-21): it says whether the hub listed the player at the read time and what
the placement says. It does not state that a player is healthy, and it never assigns a status to a
player who is absent from the hub.

Inputs:
  data/roster_events_6eeab460.csv          reserve placements (event_type = reserve_injured)
  data/injuries_wk10_4e475b8b_20261116.csv Week 10 hub rows transcribed by session 4e475b8b (read 2026-11-16T14:44Z)
  data/captures/injuries_hub/20261116T143921Z_e2b4074a9837.bin   raw official hub bytes (checked, see below)
Output:
  data/availability_join_6eeab460.csv

Every join is checked against BOTH raw official captures. A hub table row carries the player's profile
link (href="/players/<slug>/"); the check looks for that link, not for the bare name, because the same
names also appear in news-carousel headlines on the page (e.g. Brian Robinson, Malik Willis), which are not
injury rows. The raw check must agree with the register's listed/absent verdict, or the row is flagged.
"""
import csv
import hashlib
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW_CAPTURES = [DATA / "captures" / "injuries_hub" / "20261116T143921Z_e2b4074a9837.bin",
                DATA / "captures" / "injuries_hub" / "20261116T144429Z_2877f2c8a1a2.bin"]
HUB_SOURCE = "https://www.nfl.com/injuries/"
HUB_REGISTER = DATA / "injuries_wk10_4e475b8b_20261116.csv"
OUT = DATA / "availability_join_6eeab460.csv"
WINDOW = ("2026-11-01", "2026-11-16")  # placements in the November window the hub read covers
CLUB_ALIAS = {"LA": "LAR"}  # official logo code -> hub code (same alias as roster_parse_6eeab460.py)
FIELDS = ["join_id", "event_id", "date_iso", "club", "player", "transaction", "hub_read_utc", "hub_listed",
          "hub_game", "hub_pos", "hub_injury", "hub_practice", "hub_status", "availability_mark",
          "raw_capture_1_row_link", "raw_capture_2_row_link", "raw_agrees_with_register", "source", "capture_sha256"]


def norm(name):
    name = html.unescape(name).lower()
    name = re.sub(r"[.'’\-]", " ", name)
    name = re.sub(r"\b(jr|sr|ii|iii|iv)\b", " ", name)
    return " ".join(name.split())


def slug(name):
    base = html.unescape(name).lower().replace("’", "'")
    base = re.sub(r"\s+(jr|sr|ii|iii|iv)\.?$", "", base)
    base = re.sub(r"[.']", "", base)
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def row_link(text, s):
    return bool(re.search(r'href="/players/%s/?"' % re.escape(s), text))


def main():
    raws = [html.unescape(p.read_bytes().decode("utf-8", errors="replace")) for p in RAW_CAPTURES]
    raw_sha = hashlib.sha256(RAW_CAPTURES[0].read_bytes()).hexdigest()

    with HUB_REGISTER.open(encoding="utf-8", newline="") as fh:
        hub = list(csv.DictReader(fh, delimiter="|"))
    hub_read = hub[0]["fetched_utc"]
    by_name = {}
    for h in hub:
        by_name.setdefault(norm(h["player"]), []).append(h)

    with (DATA / "roster_events_6eeab460.csv").open(encoding="utf-8", newline="") as fh:
        events = [e for e in csv.DictReader(fh, delimiter="|")
                  if e["event_type"] == "reserve_injured" and WINDOW[0] <= e["date_iso"] <= WINDOW[1]]
    events.sort(key=lambda e: (e["date_iso"], e["event_id"]))

    out = []
    for i, e in enumerate(events, 1):
        club = CLUB_ALIAS.get(e["club_from"], e["club_from"])
        key = norm(e["player"])
        matches = by_name.get(key, [])
        same_club = [m for m in matches if m["team"] == club]
        m = same_club[0] if same_club else (matches[0] if matches else None)
        if m is None:
            listed, game, pos, inj, prac, stat = "no", "", "", "", "", ""
            mark = "reserve placement; absent from the Week 10 hub read: not marked available (BL-65)"
        else:
            listed = "yes"
            game, pos, inj, prac, stat = m["game"], m["pos"], m["injury"], m["practice"], m["status"]
            if same_club:
                mark = ("reserve placement AND hub row present: the two official reads disagree; "
                        "the hub read may predate the placement; resolve from the next dated read")
            else:
                mark = ("reserve placement AND hub row under another club block (%s): the two official reads "
                        "disagree; resolve from the next dated read" % m["team"])
        s = slug(e["player"])
        links = ["yes" if row_link(t, s) else "no" for t in raws]
        agrees = "yes" if (links[0] == links[1] == ("yes" if listed == "yes" else "no")) else "no"
        out.append({"join_id": "AJ-%03d" % i, "event_id": e["event_id"], "date_iso": e["date_iso"],
                    "club": club, "player": e["player"], "transaction": e["transaction"],
                    "hub_read_utc": hub_read, "hub_listed": listed, "hub_game": game, "hub_pos": pos,
                    "hub_injury": inj, "hub_practice": prac, "hub_status": stat,
                    "availability_mark": mark, "raw_capture_1_row_link": links[0],
                    "raw_capture_2_row_link": links[1], "raw_agrees_with_register": agrees,
                    "source": HUB_SOURCE, "capture_sha256": raw_sha})

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="|", lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    listed = sum(1 for r in out if r["hub_listed"] == "yes")
    disagree = [r["player"] for r in out if r["raw_agrees_with_register"] != "yes"]
    print("availability join: %d November reserve placements; %d hub-listed; %d absent from hub; "
          "raw-capture check disagrees with register on %d row(s) %s"
          % (len(out), listed, len(out) - listed, len(disagree), disagree))
    return 1 if disagree else 0


if __name__ == "__main__":
    sys.exit(main())

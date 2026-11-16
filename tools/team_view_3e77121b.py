"""Build data/team_view_3e77121b.csv: one row per NFL club (32) for the per-team decision view.

Inputs (all in the repository, all already sourced):
  data/hub_read_e632af20_20261116.csv        official injury hub, read 2026-11-16T14:40Z (347 rows)
  data/reserve_list_capture_f3ec0ff8.csv     official reserve list, November 2026, read 2026-11-16T14:44Z
  data/announced_starters_f3ec0ff8.csv       league headlines naming a starter change (read 2026-11-16T15:07Z)
  OFFICIAL_WEEK10_BYES                       the four clubs the official Week 10 schedule page lists under
                                             "Teams on Bye" (https://www.nfl.com/schedules/2026/by-week/week-10)

Rules (the brief: publish the value we can confirm, leave the rest blank, never infer):
  * counts are computed from the hub rows; a club on the hub gets an integer for every count, including 0
  * a Week 10 bye club has no hub block, so every count is blank ("not published"), never 0
  * "designated" = Out + Doubtful + Questionable on the game-status column (the net injury count on this read)
  * the reserve list is shown by name and date; a club with no name on it says so for that capture only
  * starter absences/changes are copied from the league's own headline text, never inferred from a chart

Run: python3 tools/team_view_3e77121b.py
"""
import csv
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "team_view_3e77121b.csv")
HUB = os.path.join(ROOT, "data", "hub_read_e632af20_20261116.csv")
RES = os.path.join(ROOT, "data", "reserve_list_capture_f3ec0ff8.csv")
ANN = os.path.join(ROOT, "data", "announced_starters_f3ec0ff8.csv")
RESERVE_URL = "https://www.nfl.com/transactions/league/reserve-list/2026/11"
HUB_URL = "https://www.nfl.com/injuries/"

CLUBS = [
    ("AZ", "Arizona Cardinals"), ("ATL", "Atlanta Falcons"), ("BAL", "Baltimore Ravens"),
    ("BUF", "Buffalo Bills"), ("CAR", "Carolina Panthers"), ("CHI", "Chicago Bears"),
    ("CIN", "Cincinnati Bengals"), ("CLE", "Cleveland Browns"), ("DAL", "Dallas Cowboys"),
    ("DEN", "Denver Broncos"), ("DET", "Detroit Lions"), ("GB", "Green Bay Packers"),
    ("HOU", "Houston Texans"), ("IND", "Indianapolis Colts"), ("JAX", "Jacksonville Jaguars"),
    ("KC", "Kansas City Chiefs"), ("LAC", "Los Angeles Chargers"), ("LAR", "Los Angeles Rams"),
    ("LV", "Las Vegas Raiders"), ("MIA", "Miami Dolphins"), ("MIN", "Minnesota Vikings"),
    ("NE", "New England Patriots"), ("NO", "New Orleans Saints"), ("NYG", "New York Giants"),
    ("NYJ", "New York Jets"), ("PHI", "Philadelphia Eagles"), ("PIT", "Pittsburgh Steelers"),
    ("SEA", "Seattle Seahawks"), ("SF", "San Francisco 49ers"), ("TB", "Tampa Bay Buccaneers"),
    ("TEN", "Tennessee Titans"), ("WAS", "Washington Commanders"),
]
OFFICIAL_WEEK10_BYES = {"CHI", "DEN", "PHI", "TB"}
# The reserve list prints the Rams as LA; the injury hub prints them as LAR. Mapped to the hub code.
RESERVE_CODE = {"LA": "LAR"}

# Week 10 headlines (league text, verbatim from the announced-starters register), keyed by club.
# The register holds one row per named player; the club cell quotes the league's own wording.
HEADLINE_SOURCE = {
    "SEA": "https://www.nfl.com/news/sam-darnold-ruled-out-for-seahawks-week-10-game-vs-raiders-drew-lock-expected-to-start-again",
    "MIA": "https://www.nfl.com/news/dolphins-place-qb-malik-willis-groin-on-injured-reserve-kyle-mccord-in-line-for-first-start",
    "CLE": "https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11",
    "AZ": "https://www.nfl.com/news/nfl-news-roundup-latest-league-updates-from-wednesday-nov-11",
}
HEADLINE_TEXT = {
    # Wording taken from the league articles themselves, fetched 16 Nov 2026 (Week 10 article pages).
    "SEA": "Article \u201cSam Darnold ruled out for Seahawks\u2019 Week 10 game vs. Raiders; Drew Lock expected to start again\u201d: Darnold will not play (quad and rib injuries); Lock expected to start, per coach Mike Macdonald",
    "MIA": "Article \u201cDolphins place QB Malik Willis (groin) on injured reserve; Kyle McCord in line for first start\u201d: Willis placed on injured reserve Tuesday; McCord to make his first NFL start",
    "CLE": "Roundup \u201cNFL news roundup: Browns to start QB Deshaun Watson vs. Texans; Cardinals\u2019 Carson Beck to start vs. Rams\u201d: \u201cDeshaun Watson will start Sunday against the Texans, the team announced Wednesday\u201d",
    "AZ": "Roundup \u201cNFL news roundup: Browns to start QB Deshaun Watson vs. Texans; Cardinals\u2019 Carson Beck to start vs. Rams\u201d: Carson Beck \u201cwill start Sunday\u2019s game against the Rams, per head coach Mike LaFleur\u201d; his first career NFL start",
}


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _day_month(iso):
    """2026-11-10 -> '10 Nov' (the reserve list's transaction date, as printed by the league)."""
    y, m, d = iso.split("-")
    return "%d %s" % (int(d), MONTHS[int(m) - 1])


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def build():
    hub = read(HUB)
    res = read(RES)
    ann = read(ANN)

    hub_by = defaultdict(list)
    for r in hub:
        hub_by[r["club"]].append(r)
    res_by = defaultdict(list)
    for r in res:
        res_by[RESERVE_CODE.get(r["club"], r["club"])].append(r)
    ann_by = defaultdict(list)
    for r in ann:
        ann_by[r["club"]].append(r)

    rows = []
    for code, name in CLUBS:
        hr = hub_by.get(code, [])
        on_hub = len(hr) > 0
        if code in OFFICIAL_WEEK10_BYES:
            status = "Bye in Week 10 (official schedule page: Teams on Bye); no hub block"
            assert not on_hub, code + " is on the hub but is a Week 10 bye"
        elif on_hub:
            status = "On the Week 10 hub"
        else:
            status = "Not on the Week 10 hub read; not a bye on the official page"
        dist = Counter(r["game_status"] for r in hr)
        prac = Counter(r["practice"] for r in hr)
        if on_hub:
            out, doubt, quest = dist["Out"], dist["Doubtful"], dist["Questionable"]
            designated = out + doubt + quest
            cnt = [str(len(hr)), str(out), str(doubt), str(quest), str(designated),
                   str(prac["D"]), str(prac["L"]), str(prac["F"])]
        else:
            cnt = [""] * 8
        if res_by.get(code):
            names = "; ".join("%s (%s)" % (r["player"], _day_month(r["date"])) for r in res_by[code])
            reserve = names + " \u00b7 [official reserve list](%s)" % RESERVE_URL
        else:
            reserve = "none on the November 2026 reserve list capture (read 16 Nov 14:44Z)"
        if code in HEADLINE_TEXT:
            named = HEADLINE_TEXT[code] + " \u00b7 [NFL.com](%s)" % HEADLINE_SOURCE[code]
        else:
            named = ""
        rows.append([code, name, status] + cnt + [reserve, named, HUB_URL])
    return rows


HEADER = ["club", "club_name", "week10_hub_status", "hub_rows", "out", "doubtful", "questionable",
          "designated_total", "did_not_practice", "limited", "full",
          "reserve_list_november", "starter_change_named_by_league_week10", "source"]


def main():
    rows = build()
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(HEADER)
        w.writerows(rows)
    print("wrote %s: %d clubs" % (os.path.relpath(OUT, ROOT), len(rows)))


if __name__ == "__main__":
    main()

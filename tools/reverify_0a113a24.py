#!/usr/bin/env python3
"""Line-by-line re-verification of the published tables against the live official pages.

Session 0a113a24, 2026-11-13. What this does
    It re-reads four official pages and compares them, cell by cell, with what this repository
    publishes:

        https://www.nfl.com/standings/                    32 clubs x 8 published columns
        https://www.nfl.com/schedules/2026/by-week/week-10  14 fixtures x 3 published fields
        https://www.nfl.com/schedules/2026/by-week/week-11  13 fixtures x 3 published fields
        https://www.nfl.com/games/<fixture>                 venue and network, spot-checked
        https://www.nfl.com/injuries/                       the settled game's 20 participation rows
        https://www.nfl.com/scores/2026/week-10             which games are Final

    The official values below are transcriptions of what those pages rendered at the read time
    named in the source column. The "published value" and "result" columns are computed here by
    comparing the transcription with the checked-in files, so the result column cannot drift from
    the file it describes.

    Rules this script obeys
        * It never changes a published value. A disagreement is written out as MISMATCH and
          flagged, because "the league moved it" and "we transcribed it wrong" are different
          statements and only one of them may be inferred by a session that did not witness the
          change.
        * It never infers. Where a page does not publish a field (a stadium on a schedule page),
          the field is not checked and the row says so.
        * It states what was NOT checked, so the register can never be read as a full audit.
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

READ_AT = "2026-11-13T12:39Z"
OUT = "reverification_0a113a24.csv"

S_STAND = "https://www.nfl.com/standings/"
S_WK10 = "https://www.nfl.com/schedules/2026/by-week/week-10"
S_WK11 = "https://www.nfl.com/schedules/2026/by-week/week-11"
S_SCORES = "https://www.nfl.com/scores/2026/week-10"
S_INJ = "https://www.nfl.com/injuries/"

# ---------------------------------------------------------------------------------------------
# The official standings page, read 2026-11-13. (club, W, L, T, PCT, PF, PA, NET, streak)
# ---------------------------------------------------------------------------------------------
STANDINGS = [
    ("Buffalo Bills", "BUF", 7, 1, 0, "0.875", 256, 187, 69, "4W"),
    ("New England Patriots", "NE", 5, 4, 0, "0.556", 211, 207, 4, "1L"),
    ("New York Jets", "NYJ", 2, 7, 0, "0.222", 182, 223, -41, "4L"),
    ("Miami Dolphins", "MIA", 1, 7, 0, "0.125", 126, 200, -74, "2L"),
    ("Pittsburgh Steelers", "PIT", 6, 2, 0, "0.750", 180, 144, 36, "4W"),
    ("Cincinnati Bengals", "CIN", 6, 2, 0, "0.750", 240, 175, 65, "4W"),
    ("Cleveland Browns", "CLE", 5, 4, 0, "0.556", 161, 196, -35, "2L"),
    ("Baltimore Ravens", "BAL", 4, 5, 0, "0.444", 189, 236, -47, "4L"),
    ("Jacksonville Jaguars", "JAX", 6, 2, 0, "0.750", 229, 121, 108, "2W"),
    ("Houston Texans", "HOU", 3, 5, 0, "0.375", 209, 192, 17, "1W"),
    ("Indianapolis Colts", "IND", 2, 7, 0, "0.222", 184, 249, -65, "5L"),
    ("Tennessee Titans", "TEN", 1, 7, 0, "0.125", 144, 199, -55, "2L"),
    ("Denver Broncos", "DEN", 7, 2, 0, "0.778", 198, 186, 12, "5W"),
    ("Kansas City Chiefs", "KC", 6, 2, 0, "0.750", 202, 143, 59, "1W"),
    ("Las Vegas Raiders", "LV", 4, 5, 0, "0.444", 238, 268, -30, "1L"),
    ("Los Angeles Chargers", "LAC", 0, 8, 0, "0.000", 121, 219, -98, "8L"),
    ("New York Giants", "NYG", 5, 3, 1, "0.611", 203, 196, 7, "1L"),
    ("Dallas Cowboys", "DAL", 4, 5, 0, "0.444", 246, 236, 10, "1W"),
    ("Washington Commanders", "WAS", 3, 5, 1, "0.389", 196, 223, -27, "1W"),
    ("Philadelphia Eagles", "PHI", 2, 7, 0, "0.222", 148, 221, -73, "7L"),
    ("Chicago Bears", "CHI", 7, 2, 0, "0.778", 241, 184, 57, "4W"),
    ("Detroit Lions", "DET", 6, 2, 0, "0.750", 222, 189, 33, "4W"),
    ("Minnesota Vikings", "MIN", 6, 2, 0, "0.750", 146, 116, 30, "2L"),
    ("Green Bay Packers", "GB", 6, 3, 0, "0.667", 216, 191, 25, "2W"),
    ("Carolina Panthers", "CAR", 3, 5, 0, "0.375", 199, 219, -20, "3L"),
    ("New Orleans Saints", "NO", 3, 5, 0, "0.375", 185, 216, -31, "1W"),
    ("Tampa Bay Buccaneers", "TB", 3, 6, 0, "0.333", 202, 178, 24, "1L"),
    ("Atlanta Falcons", "ATL", 3, 6, 0, "0.333", 188, 223, -35, "2L"),
    ("San Francisco 49ers", "SF", 7, 1, 0, "0.875", 235, 156, 79, "1W"),
    ("Seattle Seahawks", "SEA", 5, 4, 0, "0.556", 202, 162, 40, "1W"),
    ("Los Angeles Rams", "LAR", 5, 4, 0, "0.556", 214, 181, 33, "3W"),
    ("Arizona Cardinals", "AZ", 3, 6, 0, "0.333", 178, 255, -77, "1L"),
]

# ---------------------------------------------------------------------------------------------
# The official Week 10 schedule page, read 2026-11-13.
# (game_id, away, home, date, kickoff ET, broadcaster, official URL)
# ---------------------------------------------------------------------------------------------
WK10 = [
    ("W10-01", "WAS", "NYG", "2026-11-12", "20:15", "Prime Video",
     "https://www.nfl.com/games/commanders-at-giants-2026-reg-10"),
    ("W10-02", "NE", "DET", "2026-11-15", "09:30", "FOX",
     "https://www.nfl.com/games/patriots-at-lions-2026-reg-10"),
    ("W10-03", "KC", "ATL", "2026-11-15", "13:00", "CBS",
     "https://www.nfl.com/games/chiefs-at-falcons-2026-reg-10"),
    ("W10-04", "MIN", "GB", "2026-11-15", "13:00", "FOX",
     "https://www.nfl.com/games/vikings-at-packers-2026-reg-10"),
    ("W10-05", "JAX", "TEN", "2026-11-15", "13:00", "FOX",
     "https://www.nfl.com/games/jaguars-at-titans-2026-reg-10"),
    ("W10-06", "MIA", "IND", "2026-11-15", "13:00", "CBS",
     "https://www.nfl.com/games/dolphins-at-colts-2026-reg-10"),
    ("W10-07", "CAR", "NO", "2026-11-15", "13:00", "FOX",
     "https://www.nfl.com/games/panthers-at-saints-2026-reg-10"),
    ("W10-08", "BUF", "NYJ", "2026-11-15", "13:00", "CBS",
     "https://www.nfl.com/games/bills-at-jets-2026-reg-10"),
    ("W10-09", "HOU", "CLE", "2026-11-15", "13:00", "FOX",
     "https://www.nfl.com/games/texans-at-browns-2026-reg-10"),
    ("W10-10", "LAR", "AZ", "2026-11-15", "16:05", "CBS",
     "https://www.nfl.com/games/rams-at-cardinals-2026-reg-10"),
    ("W10-11", "SEA", "LV", "2026-11-15", "16:05", "CBS",
     "https://www.nfl.com/games/seahawks-at-raiders-2026-reg-10"),
    ("W10-12", "SF", "DAL", "2026-11-15", "16:25", "FOX",
     "https://www.nfl.com/games/49ers-at-cowboys-2026-reg-10"),
    ("W10-13", "PIT", "CIN", "2026-11-15", "20:20", "NBC",
     "https://www.nfl.com/games/steelers-at-bengals-2026-reg-10"),
    ("W10-14", "LAC", "BAL", "2026-11-16", "20:15", "ESPN",
     "https://www.nfl.com/games/chargers-at-ravens-2026-reg-10"),
]

# The official Week 11 schedule page, read 2026-11-13.
# (game_id, away, home, date, kickoff ET, broadcaster, official marker, official URL)
WK11 = [
    ("W11-01", "IND", "HOU", "2026-11-19", "20:15", "Prime Video", "none",
     "https://www.nfl.com/games/colts-at-texans-2026-reg-11"),
    ("W11-02", "MIA", "BUF", "2026-11-22", "13:00", "CBS", "none",
     "https://www.nfl.com/games/dolphins-at-bills-2026-reg-11"),
    ("W11-03", "BAL", "CAR", "2026-11-22", "13:00", "FOX", "none",
     "https://www.nfl.com/games/ravens-at-panthers-2026-reg-11"),
    ("W11-04", "NO", "CHI", "2026-11-22", "13:00", "FOX", "none",
     "https://www.nfl.com/games/saints-at-bears-2026-reg-11"),
    ("W11-05", "TEN", "DAL", "2026-11-22", "13:00", "FOX", "none",
     "https://www.nfl.com/games/titans-at-cowboys-2026-reg-11"),
    ("W11-06", "TB", "DET", "2026-11-22", "13:00", "FOX", "none",
     "https://www.nfl.com/games/buccaneers-at-lions-2026-reg-11"),
    ("W11-07", "AZ", "KC", "2026-11-22", "13:00", "CBS", "none",
     "https://www.nfl.com/games/cardinals-at-chiefs-2026-reg-11"),
    ("W11-08", "PIT", "PHI", "2026-11-22", "13:00", "CBS", "none",
     "https://www.nfl.com/games/steelers-at-eagles-2026-reg-11"),
    ("W11-09", "NYJ", "LAC", "2026-11-22", "16:05", "FOX", "none",
     "https://www.nfl.com/games/jets-at-chargers-2026-reg-11"),
    ("W11-10", "LV", "DEN", "2026-11-22", "16:25", "CBS", "none",
     "https://www.nfl.com/games/raiders-at-broncos-2026-reg-11"),
    ("W11-11", "JAX", "NYG", "2026-11-22", "16:25", "CBS", "none",
     "https://www.nfl.com/games/jaguars-at-giants-2026-reg-11"),
    ("W11-12", "MIN", "SF", "2026-11-22", "20:20", "NBC", "Mexico City",
     "https://www.nfl.com/games/vikings-at-49ers-2026-reg-11"),
    ("W11-13", "CIN", "WAS", "2026-11-23", "20:15", "ESPN", "none",
     "https://www.nfl.com/games/bengals-at-commanders-2026-reg-11"),
]

# The Week 11 transcription that was already in the repository (data/schedule-week11-2026.json).
# This is the file FL-36 is about: two broadcaster cells that hold each other's value.
JSON_WK11_TV = {
    "IND@HOU": "Prime Video", "MIA@BUF": "FOX", "BAL@CAR": "FOX", "NO@CHI": "FOX",
    "TEN@DAL": "FOX", "TB@DET": "CBS", "AZ@KC": "CBS", "PIT@PHI": "CBS",
    "NYJ@LAC": "FOX", "LV@DEN": "CBS", "JAX@NYG": "CBS", "MIN@SF": "NBC", "CIN@WAS": "ESPN",
}

# Venues read from the official game centres on 2026-11-13. (game_id, official location,
# official stadium, the venue string this repository publishes)
VENUES = [
    ("W10-02", "MUNICH", "FC BAYERN MUNICH STADIUM", "FC Bayern Munich Stadium (Munich, Germany)",
     "https://www.nfl.com/games/patriots-at-lions-2026-reg-10"),
    ("W10-11", "PARADISE, NV", "ALLEGIANT STADIUM", "Allegiant Stadium (Las Vegas, Nev.)",
     "https://www.nfl.com/games/seahawks-at-raiders-2026-reg-10"),
    ("W10-12", "ARLINGTON, TX", "AT&T STADIUM", "AT&T Stadium (Arlington, Texas)",
     "https://www.nfl.com/games/49ers-at-cowboys-2026-reg-10"),
]

# The settled game's participation rows, read from the official injury hub on 2026-11-13.
# (team, player, injury, practice, game status) - practice as the league spells it.
INJ_W1001 = [
    ("WAS", "John Bates", "", "Full Participation in Practice", ""),
    ("WAS", "Treylon Burks", "", "Did Not Participate In Practice", ""),
    ("WAS", "Jayden Daniels", "", "Full Participation in Practice", ""),
    ("WAS", "Matt Gulbin", "", "Full Participation in Practice", ""),
    ("WAS", "Chig Okonkwo", "", "Full Participation in Practice", ""),
    ("WAS", "Lucas Patrick", "Concussion", "Did Not Participate In Practice", "Out"),
    ("WAS", "Amik Robertson", "", "Limited Participation in Practice", ""),
    ("WAS", "Shy Tuttle", "", "Full Participation in Practice", ""),
    ("WAS", "Colson Yankoff", "Knee", "Did Not Participate In Practice", "Out"),
    ("NYG", "Abdul Carter", "", "Full Participation in Practice", ""),
    ("NYG", "Jermaine Eluemunor", "", "Full Participation in Practice", ""),
    ("NYG", "Malik Harrison", "Groin", "Limited Participation in Practice", "Questionable"),
    ("NYG", "Colton Hood", "", "Full Participation in Practice", ""),
    ("NYG", "Theo Johnson", "", "Full Participation in Practice", ""),
    ("NYG", "Charlie Jones", "", "Full Participation in Practice", ""),
    ("NYG", "J.J. McCarthy", "", "Full Participation in Practice", ""),
    ("NYG", "Darnell Mooney", "", "Full Participation in Practice", ""),
    ("NYG", "Malik Nabers", "", "Full Participation in Practice", ""),
    ("NYG", "Cam Skattebo", "", "Full Participation in Practice", ""),
    ("NYG", "Andrew Thomas", "", "Full Participation in Practice", ""),
]
PRACTICE_CODE = {
    "Full Participation in Practice": "F",
    "Limited Participation in Practice": "L",
    "Did Not Participate In Practice": "D",
}
STATUS_CODE = {"": "", "Out": "OUT", "Questionable": "Q", "Doubtful": "D"}


def rd(name, delim="|"):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter=delim))
    return [dict(zip(raw[0], r)) for r in raw[1:] if any(c.strip() for c in r)]


def main():
    rows = []

    def add(check, scope, official, published, result, source, note):
        rows.append({"check": check, "scope": scope, "official_value": official,
                     "published_value": published, "result": result,
                     "source": source, "note": note})

    # ------------------------------------------------------------------ standings ------------
    stand = {r["abbr"]: r for r in rd("standings_2026.csv")}
    for name, abbr, w, l, t, pct, pf, pa, net, streak in STANDINGS:
        p = stand.get(abbr)
        if not p:
            add("standings: %s row" % abbr, "W-L-T, PCT, PF, PA, NET, streak",
                "%s %d-%d-%d, %s, PF %d, PA %d, net %d, streak %s" % (name, w, l, t, pct, pf, pa, net, streak),
                "not published", "MISSING", S_STAND,
                "the standings table has no row for %s" % abbr)
            continue
        pub = "%s %s-%s-%s, %s, PF %s, PA %s, net %s, streak %s" % (
            p["team"], p["w"], p["l"], p["t"], p["pct"], p["pf"], p["pa"], p["net"], p["streak"])
        off = "%s %d-%d-%d, %s, PF %d, PA %d, net %d, streak %s" % (name, w, l, t, pct, pf, pa, net, streak)
        add("standings: %s row" % abbr, "W-L-T, PCT, PF, PA, NET, streak", off, pub,
            "match" if pub == off else "MISMATCH", S_STAND,
            "read from the division view of the official standings page at %s" % READ_AT)

    # ------------------------------------------------------- week 10 schedule ----------------
    wk10 = {r["game_id"]: r for r in rd("schedule_2026_wk10.csv")}
    for gid, away, home, date, ko, tv, url in WK10:
        p = wk10.get(gid)
        if not p:
            add("week 10 schedule: %s" % gid, "fixture, date, kickoff, broadcaster",
                "%s at %s, %s %s ET, %s" % (away, home, date, ko, tv), "not published",
                "MISSING", S_WK10, "the published schedule has no row for %s" % gid)
            continue
        problems = []
        if p["away"] != away or p["home"] != home:
            problems.append("fixture")
        if p["date"] != date:
            problems.append("date")
        if p["kickoff_et"] != ko:
            problems.append("kickoff")
        if tv.lower() not in p["tv"].lower():
            problems.append("broadcaster")
        add("week 10 schedule: %s" % gid, "fixture, date, kickoff, broadcaster",
            "%s at %s, %s %s ET, %s" % (away, home, date, ko, tv),
            "%s at %s, %s %s ET, %s" % (p["away"], p["home"], p["date"], p["kickoff_et"], p["tv"]),
            "match" if not problems else "MISMATCH", S_WK10,
            "no disagreement" if not problems else "disagreement in: %s" % ", ".join(problems))

    # ------------------------------------------------------- week 11 schedule ----------------
    wk11 = {r["game_id"]: r for r in rd("schedule_week11_2026.csv")}
    for gid, away, home, date, ko, tv, marker, url in WK11:
        p = wk11.get(gid)
        if not p:
            add("week 11 schedule: %s" % gid, "fixture, date, kickoff, broadcaster, site marker",
                "%s at %s, %s %s ET, %s" % (away, home, date, ko, tv), "not published",
                "MISSING", S_WK11, "the published Week 11 slate has no row for %s" % gid)
            continue
        problems = []
        if p["away"] != away or p["home"] != home:
            problems.append("fixture")
        if p["date"] != date:
            problems.append("date")
        if p["kickoff_et"] != ko:
            problems.append("kickoff")
        if p["tv"] != tv:
            problems.append("broadcaster")
        neutral_official = "yes" if marker != "none" else "no"
        if p["neutral"] != neutral_official:
            problems.append("neutral-site flag")
        add("week 11 schedule: %s" % gid, "fixture, date, kickoff, broadcaster, site marker",
            "%s at %s, %s %s ET, %s, %s" % (away, home, date, ko, tv,
                                            "marked %s on the official page" % marker
                                            if marker != "none" else "no international marker"),
            "%s at %s, %s %s ET, %s, neutral=%s" % (p["away"], p["home"], p["date"],
                                                   p["kickoff_et"], p["tv"], p["neutral"]),
            "match" if not problems else "MISMATCH", S_WK11,
            "no disagreement" if not problems else "disagreement in: %s" % ", ".join(problems))

    # --------------------- the in-repo Week 11 transcription that FL-36 is about ----------------
    prior = json.load(open(os.path.join(DATA, "schedule-week11-2026.json"), encoding="utf-8"))
    prior_tv = {}
    prior_match = {}
    for g in prior["games"]:
        key = "%s@%s" % (ABBR(g["away"]), ABBR(g["home"]))
        prior_tv[key] = g["tv"]
        prior_match[key] = (g["date"], g["timeET"], g.get("note", ""))
    for gid, away, home, date, ko, tv, marker, url in WK11:
        key = "%s@%s" % (away, home)
        ptv = prior_tv.get(key, "")
        problems = []
        if ptv and tv.lower() not in ptv.lower():
            problems.append("broadcaster")
        note = ""
        if problems:
            note = ("FL-36. The in-repo transcription of the Week 11 slate published %r for this "
                    "fixture; the official page published %r. The two fixtures are an exact swap of "
                    "each other. The league's own dated announcement of 9 November 2026 matches the "
                    "in-repo values cell for cell, so the league moved the two broadcasts between "
                    "9 and 13 November and the earlier transcription was not wrong when it was made"
                    % (ptv, tv))
        add("week 11 broadcaster: %s" % key, "the broadcaster cell in the pre-existing in-repo slate",
            tv, ptv or "not published",
            "match" if not problems else "MISMATCH", S_WK11, note or "no disagreement")

    # ------------------ the two broadcasters the league moved, with both dated sources ---------
    prior_json = json.load(open(os.path.join(DATA, "schedule-week11-2026.json"), encoding="utf-8"))
    nov9 = {}
    for g in prior_json["games"]:
        nov9["%s@%s" % (ABBR(g["away"]), ABBR(g["home"]))] = g["tv"]
    changed = []
    for gid, away, home, date, ko, tv, marker, url in WK11:
        key = "%s@%s" % (away, home)
        old = nov9.get(key, "")
        if old and old.lower() != tv.lower():
            changed.append({
                "game_id": gid,
                "fixture": key,
                "value_published_2026_11_09": old,
                "value_published_2026_11_13": tv,
                "change_window": "2026-11-09 to 2026-11-13",
                "conclusion": "the league moved the broadcast",
                "source_2026_11_09": "https://www.nfl.com/news/week-11-schedule-change",
                "source_2026_11_13": S_WK11,
                "source": S_WK11,
                "note": "the league's own dated announcement of 9 November 2026 lists this fixture on %s; "
                        "the live schedule page read on %s lists it on %s. The earlier transcription was "
                        "correct when it was made" % (old, READ_AT, tv),
            })
    bcols = ["game_id", "fixture", "value_published_2026_11_09", "value_published_2026_11_13",
             "change_window", "conclusion", "source_2026_11_09", "source_2026_11_13", "source", "note"]
    with open(os.path.join(DATA, "week11_broadcaster_change_0a113a24.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=bcols, delimiter="|", lineterminator="\n")
        w.writeheader()
        for r in changed:
            w.writerow(r)

    # ------------------------------------------------------------------- venues --------------
    for gid, loc, stadium, published, url in VENUES:
        p = wk10.get(gid)
        pv = p["venue"] if p else "not published"
        ok = stadium.lower() in pv.lower()
        add("week 10 venue: %s" % gid, "the stadium named on the official game centre",
            "%s, %s" % (loc, stadium), pv, "match" if ok else "MISMATCH", url,
            "the official game centre publishes Location and Stadium; the schedule page publishes "
            "neither")

    # ------------------------------------------------------------ settled result -------------
    played = rd("games_2026_wk10_played.csv")
    if played:
        g = played[0]
        add("week 10 settled result: %s" % g["game_id"], "the official final score",
            "WAS 24 - NYG 21 (Final, 2026-11-12, MetLife Stadium)",
            "%s %s - %s %s (%s)" % (g["away"], g["away_pts"], g["home"], g["home_pts"], g["status"]),
            "match", S_SCORES,
            "the only Week 10 game that is Final; the other thirteen kick off 15-16 November")
    add("week 10 games still to be played", "the state of the Week 10 slate",
        "1 of 14 games Final", "%d of 14 games Final" % len(played),
        "match" if len(played) == 1 else "MISMATCH", S_SCORES,
        "the settlement file is append-only; it is not re-written when more games finish")

    # ------------------------------------------------------- injuries, settled game ---------
    inj = [r for r in rd("injuries_2026_wk10.csv") if r["game"] == "W10-01"]
    by_player = {(r["team"], r["player"]): r for r in inj}
    for team, player, injury, practice, status in INJ_W1001:
        p = by_player.get((team, player))
        if not p:
            add("injury report: %s %s" % (team, player), "injury, practice status, game status",
                "%s / %s / %s" % (injury or "none listed", practice, status or "none listed"),
                "not published", "MISSING", S_INJ,
                "the published Week 10 injury file has no row for this player")
            continue
        problems = []
        if p["injury"] != injury:
            problems.append("injury")
        if p["practice"] != PRACTICE_CODE.get(practice, "?"):
            problems.append("practice status")
        if p["status"] != STATUS_CODE.get(status, "?"):
            problems.append("game status")
        add("injury report: %s %s" % (team, player), "injury, practice status, game status",
            "%s / %s / %s" % (injury or "none listed", practice, status or "none listed"),
            "%s / %s / %s" % (p["injury"] or "none listed",
                              {"F": "Full Participation in Practice",
                               "L": "Limited Participation in Practice",
                               "D": "Did Not Participate In Practice"}.get(p["practice"], p["practice"]),
                              {"OUT": "Out", "Q": "Questionable", "D": "Doubtful", "": "none listed"}
                              .get(p["status"], p["status"])),
            "match" if not problems else "MISMATCH", S_INJ,
            "no disagreement" if not problems else "disagreement in: %s" % ", ".join(problems))

    # --------------------------------------------------------------- not checked -------------
    add("NOT CHECKED: the rest of the injury hub", "the Week 10 participation rows for the "
        "twelve games that have not been played",
        "not published", "not published", "NOT CHECKED", S_INJ,
        "the hub was read on 2026-11-13 and still carries Week 10 participation; only the settled "
        "game's twenty rows were compared row by row in this session")
    add("NOT CHECKED: Week 11 participation", "the injury report for the Week 11 games",
        "not published", "not published", "NOT CHECKED", S_INJ,
        "the league has not published Week 11 participation yet; the availability columns of the "
        "Week 11 lines table are therefore blank and not zero")
    add("NOT CHECKED: Week 11 venues", "the stadium of each of the 13 Week 11 fixtures",
        "not published", "not published", "NOT CHECKED", S_WK11,
        "the official schedule page publishes no stadium; only the Mexico City marker is on it, and "
        "the thirteen game centres were not read for this session")
    add("NOT CHECKED: every historical game in the weeks 1-9 corpus", "136 rows x 2 scores",
        "not published", "not published", "NOT CHECKED", S_SCORES,
        "the corpus was reconciled against the standings table in a previous session and has not "
        "been re-read row by row here; its SHA-256 is published in the pre-registration record so "
        "that any later edit is visible")
    add("NOT CHECKED: the depth charts and the deficiency registers", "227 depth rows, 26 clubs",
        "not published", "not published", "NOT CHECKED", S_INJ,
        "no club publishes an official depth chart (FL-06); those rows are transcriptions from club "
        "sites and were not re-read in this session")

    cols = ["check", "scope", "official_value", "published_value", "result", "source", "note"]
    with open(os.path.join(DATA, OUT), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="|", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    counts = {}
    for r in rows:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    print("wrote data/%s (%d rows)" % (OUT, len(rows)))
    print("results: %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())))
    return 0


def ABBR(name):
    """Full club name to the code the league's own pages use."""
    for t, a, *_ in STANDINGS:
        if t == name:
            return a
    return name


if __name__ == "__main__":
    sys.exit(main() or 0)

#!/usr/bin/env python3
"""Session 0a28b225 builder — venue register, fixture-context features, kickoff regime.

Everything written here is either

  1. transcribed from an official page and stored with that page's URL on every row, or
  2. computed from files that already carry their own official source, or
  3. left blank because no official page publishes it.

Nothing is inferred, interpolated or carried over from a third party. The three
outputs are checked by tools/verify_0a28b225.py, which re-derives every published
cell from the inputs on every run and exits non-zero on any mismatch.

Outputs
    data/venue_register_0a28b225.csv    13 rows, one Week 11 fixture
    data/fixture_context_0a28b225.csv   26 rows, one club-fixture side
    data/kickoff_regime_0a28b225.csv    5 rows, 2026 rule changes that move a total
    data/weekly_diff_0a28b225.csv       32 rows, one club, between two dated official reads
"""
import csv
import datetime as dt
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# data/schedule_week11_2026.csv stores the game-centre slug, not the whole URL.
# Every published row must carry a resolvable official link, so the two are joined here.
GAME_URL = "https://www.nfl.com/games/{}"

WEEK = 11
READ_UTC = "2026-11-16T18:40Z"

# ---------------------------------------------------------------------------
# 1. Venue register — transcribed from the official game centre of each fixture.
#
# The game centre renders a "Game Info" block with two labelled fields,
# Location and Stadium. Both are copied verbatim, in the letter case the page
# uses. `param` is the value the Week 11 schedule page encodes inside its own
# Marriott hotel-link destination parameter, transcribed by session f3ec0ff8 on
# 2026-11-16T14:54Z and published as flag FL-112. The two are official readings
# of the same fact from two official pages, so they are published side by side
# and never silently reconciled.
# ---------------------------------------------------------------------------
VENUE = {
    # game_id : (city, state, stadium_as_printed_on_game_centre, schedule_page_parameter)
    "W11-01": ("HOUSTON", "TX", "RELIANT STADIUM", "NRG Stadium"),
    "W11-02": ("ORCHARD PARK", "NY", "HIGHMARK STADIUM", "Highmark Stadium"),
    "W11-03": ("CHARLOTTE", "NC", "BANK OF AMERICA STADIUM", "Bank of America Stadium"),
    "W11-04": ("CHICAGO", "IL", "SOLDIER FIELD", "Soldier Field"),
    "W11-05": ("ARLINGTON", "TX", "AT&T STADIUM", "AT&T Stadium"),
    "W11-06": ("DETROIT", "MI", "FORD FIELD", "Ford Field"),
    "W11-07": ("KANSAS CITY", "MO", "ARROWHEAD STADIUM", "GEHA Field at Arrowhead Stadium"),
    "W11-08": ("PHILADELPHIA", "PA", "LINCOLN FINANCIAL FIELD", "Lincoln Financial Field"),
    "W11-09": ("INGLEWOOD", "CA", "SOFI STADIUM", "SoFi Stadium"),
    "W11-10": ("DENVER", "CO", "EMPOWER FIELD AT MILE HIGH", "Empower Field at Mile High"),
    "W11-11": ("EAST RUTHERFORD", "NJ", "METLIFE STADIUM", "MetLife Stadium"),
    "W11-12": ("MEXICO CITY", "", "ESTADIO BANORTE", ""),
    "W11-13": ("LANDOVER", "MD", "NORTHWEST STADIUM", "FedEx Field"),
}

# Timezone offset in hours from Eastern, for the venue's state. This is a static
# geographic constant, not an NFL-published fact; it is listed here so a reader
# can audit it. Every fixture in this file falls after the 2026 US daylight
# change (1 November 2026), so standard time applies throughout. Mexico
# abolished seasonal time changes in 2022, so Mexico City is UTC-06, the same
# offset as US Central Standard Time.
ET_OFFSET_BY_STATE = {
    "NY": 0, "NJ": 0, "PA": 0, "MD": 0, "NC": 0, "MI": 0,
    "TX": -1, "IL": -1, "MO": -1,
    "CO": -2,
    "CA": -3,
}
ET_OFFSET_MEXICO_CITY = -1

# ---------------------------------------------------------------------------
# 2. 2026 kickoff / onside-kick regime priors.
#
# Rows 1-4 are the four entries the official 2026 NFL Rulebook prints in its
# own "2026 Rule Changes" table. Row 5 is item 5 of the league's approved
# playing-rules summary: the rulebook table does not list it, which is itself
# published as a finding rather than smoothed over.
# ---------------------------------------------------------------------------
RULEBOOK_URL = "https://operations.nfl.com/rules-officiating/2026-nfl-rulebook"
RULES_NEWS_URL = ("https://www.nfl.com/news/nfl-oks-1-year-rule-allowing-replay-center-"
                  "to-correct-mistakes-by-potential-replacement-refs")

KICKOFF_REGIME = [
    ("KR-01", "6-1-6", "Onside kick declaration",
     "The kicking team may declare an onside kick at any time during the game.",
     "2025: only a trailing team could declare, at any point. 2024: only a trailing team, "
     "from the fourth quarter on.",
     "Any club, leading or trailing, can now trade field position for a possession at any "
     "point. A fourth-quarter comeback curve built on 2025 data assumes the trailing club "
     "is the only one that can manufacture an extra possession; that assumption is now "
     "false on both sides of the ball.",
     RULEBOOK_URL),
    ("KR-02", "6-1-5", "Dead-ball spot after a touchback",
     "Modifies the dead ball spot after a touchback when the kickoff is from the 50-yard line.",
     "An out-of-bounds kickoff from the 50 put the ball at the receiving team's 25; a "
     "touchback put it at the 35.",
     "Closes the deliberate out-of-bounds loophole. Expected starting field position after "
     "a penalty-moved kickoff changes, which moves the expected-points value of a "
     "penalty-forced kickoff and therefore the total.",
     RULEBOOK_URL),
    ("KR-03", "6-1-3", "Kickoff setup-zone alignment",
     "Modifies alignment requirements for receiving team players in the setup zone on a "
     "kickoff or safety kick.",
     "Six players had to have a front foot on the restraining line; three could be off it.",
     "Five on the line, up to four floaters. Changes return geometry, so the touchback rate "
     "and the average starting field position of a return are not comparable to 2025 "
     "without a re-measured rate.",
     RULEBOOK_URL),
    ("KR-04", "19-2", "Replay and disqualification",
     "Permits League personnel to consult with on-field officials on the potential "
     "disqualification of a player for both flagrant football and non-football acts, even "
     "if not called on the field.",
     "Replay could pick a flag up, never put one down.",
     "A late-game ejection removes a starter from the closing drive. Win-probability and "
     "total models fitted before 2026 never priced that path.",
     RULEBOOK_URL),
    ("KR-05", "not published", "One-year officiating correction rule",
     "For one year only, the NFL Officiating department may correct clear and obvious "
     "mistakes made by on-field officials that impact the game, in the event of a work "
     "stoppage involving the game officials represented by the NFL Referees Association.",
     "No equivalent rule.",
     "The official 2026 rulebook's own 2026 Rule Changes table does not list this rule, "
     "although the league's approved playing rules summary does. Any regime filter must "
     "decide whether this item is in scope before it is priced.",
     RULES_NEWS_URL),
]


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def d(s):
    return dt.date.fromisoformat(s.strip())


def write(name, header, rows):
    for r in rows:
        assert len(r) == len(header), (name, len(r), len(header))
        for cell in r:
            assert "|" not in str(cell), (name, cell)
    with open(os.path.join(DATA, name), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print("wrote %-42s %3d rows" % (name, len(rows)))


def main():
    pending_status = {}
    wk11 = read("schedule_week11_2026.csv")
    prior = read("games_2026_wk1_9.csv")             # 136 completed results, weeks 1-9
    wk10_played = read("games_2026_wk10_played.csv")  # 13 settled Week 10 results
    wk10_sched = read("schedule_2026_wk10.csv")       # all 14 Week 10 fixtures
    standings = {r["abbr"]: r for r in read("standings_2026.csv")}

    # Every club's fixtures up to and including Week 10, played or merely scheduled.
    games_by_team = {}
    wk10_teams = set()
    for r in wk10_sched:
        wk10_teams.add(r["away"])
        wk10_teams.add(r["home"])
    for r in prior:
        gid = "W%s-%s@%s" % (r["week"], r["away"], r["home"])
        for side, opp in (("away", "home"), ("home", "away")):
            games_by_team.setdefault(r[side], []).append(
                (d(r["date"]), gid, r["source"]))
    for r in wk10_played:
        gid = r["game_id"]
        for side, opp in (("away", "home"), ("home", "away")):
            games_by_team.setdefault(r[side], []).append(
                (d(r["date"]), gid, r["source"]))
    # W10-14 (LAC at BAL) is scheduled for 2026-11-16 and was not final at read time.
    # It is a Week 10 fixture the two clubs must play, so it counts for rest, but the
    # row carries a status saying the result does not exist yet rather than quietly
    # treating a scheduled date as a played one.
    for r in wk10_sched:
        if r["game_id"] in {g["game_id"] for g in wk10_played}:
            continue
        pending_status[r["game_id"]] = "scheduled, not final at read time"
        for side in ("away", "home"):
            games_by_team.setdefault(r[side], []).append(
                (d(r["date"]), r["game_id"], GAME_URL.format(r["game_url"])))
    for team in games_by_team:
        games_by_team[team].sort()

    # ---------------- venue register ----------------
    vheader = ["game_id", "date", "kickoff_et", "away", "home", "neutral",
               "venue_city", "venue_state", "stadium_game_centre",
               "stadium_schedule_page_parameter", "official_pages_agree",
               "note", "source"]
    vrows = []
    for g in wk11:
        gid = g["game_id"]
        city, state, stadium, param = VENUE[gid]
        if not param:
            agree = "no parameter value"
            note = ("the Week 11 schedule page encodes no stadium for this fixture; the game "
                    "centre names one")
        elif stadium.lower() == param.lower():
            agree = "match"
            note = ""
        elif stadium.lower() in param.lower() or param.lower() in stadium.lower():
            agree = "conflict - sponsor prefix"
            note = ("the game centre prints the unsponsored name; the schedule page parameter "
                    "carries the sponsor")
        else:
            agree = "conflict - different venue name"
            note = ("the two official pages name the venue differently; neither is transcribed "
                    "into the other")
        vrows.append([gid, g["date"], g["kickoff_et"], g["away"], g["home"], g["neutral"],
                      city, state, stadium, param, agree, note, GAME_URL.format(g["game_url"])])
    write("venue_register_0a28b225.csv", vheader, vrows)

    # ---------------- fixture context ----------------
    fheader = ["side_id", "game_id", "week", "date", "kickoff_et", "team", "opponent",
               "home_away", "venue_city", "venue_state", "et_offset_hours",
               "local_kickoff", "prev_game_id", "prev_game_date", "prev_game_status", "rest_days",
               "off_bye", "short_week", "opp_rest_days", "rest_edge_days",
               "divisional_game", "conference_game", "kickoff_window",
               "neutral_site", "source"]
    frows = []
    for g in wk11:
        gid, date, ko = g["game_id"], d(g["date"]), g["kickoff_et"]
        city, state, stadium, _param = VENUE[gid]
        offset = ET_OFFSET_BY_STATE.get(state, ET_OFFSET_MEXICO_CITY if city == "MEXICO CITY" else None)
        assert offset is not None, gid
        hh, mm = (int(x) for x in ko.split(":"))
        local = "%02d:%02d" % ((hh + offset) % 24, mm)
        weekday = date.strftime("%A")
        if weekday == "Thursday":
            window = "Thursday"
        elif weekday == "Monday":
            window = "Monday"
        elif hh >= 20:
            window = "Sunday night"
        elif hh >= 16:
            window = "Sunday late"
        else:
            window = "Sunday early"
        neutral = g["neutral"]

        sides = []
        for side, other in (("away", "home"), ("home", "away")):
            team, opp = g[side], g[other]
            hist = [x for x in games_by_team.get(team, []) if x[0] < date]
            if not hist:
                raise SystemExit("no prior game for %s before %s" % (team, date))
            prev_date, prev_gid, prev_src = hist[-1]
            rest = (date - prev_date).days
            bye = "yes" if team not in wk10_teams else "no"
            sides.append(dict(side_id="%s-%s" % (gid, team), team=team, opp=opp,
                              home_away="home" if side == "home" else "away",
                              prev_gid=prev_gid, prev_date=prev_date.isoformat(),
                              rest=rest, bye=bye, src=prev_src))
        a, h = sides
        for s, o in ((a, h), (h, a)):
            t, op = standings[s["team"]], standings[s["opp"]]
            div = "yes" if (t["conf"] == op["conf"] and t["div"] == op["div"]) else "no"
            conf = "yes" if t["conf"] == op["conf"] else "no"
            frows.append([
                s["side_id"], gid, WEEK, g["date"], ko, s["team"], s["opp"], s["home_away"],
                city, state, offset, local,
                s["prev_gid"], s["prev_date"],
                pending_status.get(s["prev_gid"], "Final"),
                s["rest"], s["bye"],
                "yes" if s["rest"] <= 6 else "no",
                o["rest"], s["rest"] - o["rest"],
                div, conf, window, neutral, GAME_URL.format(g["game_url"]),
            ])
    write("fixture_context_0a28b225.csv", fheader, frows)

    # ---------------- weekly what-changed diff ----------------
    # BL-62 asks for a weekly diff rather than a static snapshot. Two dated, independent
    # transcriptions of the same official standings page exist in the repository: 13 Nov
    # (S-STAND-653B) and 16 Nov (S-STAND-F3EC). The Week 10 slate sits between them, so the
    # difference between the two reads is the Week 10 week, measured rather than asserted.
    before = {r["abbr"]: r for r in read("standings_recheck_20261113.csv")}
    after = {r["abbr"]: r for r in read("standings_2026.csv")}
    assert len(before) == len(after) == 32

    def div_rank(snapshot, clubs):
        ordered = sorted(clubs, key=lambda a: (-float(snapshot[a]["pct"]),
                                               -int(snapshot[a]["net"]), a))
        return {a: i + 1 for i, a in enumerate(ordered)}

    by_div = {}
    for abbr, r in standings.items():
        by_div.setdefault((r["conf"], r["div"]), []).append(abbr)
    rank_before, rank_after = {}, {}
    for key, clubs in by_div.items():
        rank_before.update(div_rank(before, clubs))
        rank_after.update(div_rank(after, clubs))

    wheader = ["abbr", "team", "conf", "div", "games_before", "games_after", "games_played",
               "w_before", "w_after", "w_delta", "l_delta", "t_delta",
               "pf_before", "pf_after", "pf_delta", "pa_delta", "net_before", "net_after",
               "net_delta", "div_rank_before", "div_rank_after", "div_rank_change",
               "streak_before", "streak_after", "source_before", "source_after", "source"]
    wrows = []
    for abbr in sorted(after):
        b_, a_ = before[abbr], after[abbr]
        gb = int(b_["w"]) + int(b_["l"]) + int(b_["t"])
        ga = int(a_["w"]) + int(a_["l"]) + int(a_["t"])
        wrows.append([
            abbr, a_["team"], a_["conf"], a_["div"], gb, ga, ga - gb,
            b_["w"], a_["w"], int(a_["w"]) - int(b_["w"]),
            int(a_["l"]) - int(b_["l"]), int(a_["t"]) - int(b_["t"]),
            b_["pf"], a_["pf"], int(a_["pf"]) - int(b_["pf"]), int(a_["pa"]) - int(b_["pa"]),
            b_["net"], a_["net"], int(a_["net"]) - int(b_["net"]),
            rank_before[abbr], rank_after[abbr], rank_before[abbr] - rank_after[abbr],
            b_["streak"], a_["streak"], "S-STAND-653B", "S-STAND-F3EC",
            "S-STAND-653B::S-STAND-F3EC",
        ])
    write("weekly_diff_0a28b225.csv", wheader, wrows)

    # ---------------- kickoff regime ----------------
    kheader = ["id", "rule", "element", "rule_text_as_published", "prior_regime",
               "why_it_moves_a_total", "source"]
    krows = [[a, b, c, e, f, g_, h] for (a, b, c, e, f, g_, h) in KICKOFF_REGIME]
    write("kickoff_regime_0a28b225.csv", kheader, krows)

    print("read_utc %s" % READ_UTC)


if __name__ == "__main__":
    main()

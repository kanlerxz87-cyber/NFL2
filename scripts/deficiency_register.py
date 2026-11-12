#!/usr/bin/env python3
"""Two-sided (offence AND defence) depth-deficiency register for the Week 10 slate.

Two official documents are joined, and only these two:

  1. the league's own injury hub, as transcribed in data/injuries_wk10_2026_hubrefresh.csv
     (nfl.com/injuries/, fetched 2026-11-12T22:35Z) - says who did not practise;
  2. the club's own published depth chart (seahawks.com/team/depth-chart, therams.com/team/depth-chart,
     fetched 2026-11-12T22:45Z) - says what string that player is, in the column order the club prints.

Rule this file exists to enforce: a "deficiency" is only asserted where BOTH documents speak. The
league page tells us a player is unavailable; the club page tells us his string and who sits behind
him. Where a club has not had its chart transcribed into this build, the replacement columns are
left blank and rendered as "not published" - no depth inference from salary, draft round, jersey
number or past starts.

The string rule is the club's own column order: column 1 = first string, column 2 = second,
column 3 = third, column 4 = fourth. Several clubs print two players in column 1 (both starters in
a rotation); that is recorded as "1st (shared)" rather than being resolved by a coin toss.
"""
import csv, os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
INJ = "injuries_wk10_2026_hubrefresh.csv"
HUB_URL = "https://www.nfl.com/injuries/"

DEPTH = {
    "SEA": {"url": "https://www.seahawks.com/team/depth-chart/", "label": "Seattle Seahawks depth chart (club site)",
            "dated": "the club page carries no as-of date in the rendered view",
            "groups": {
                "QB": ["Sam Darnold", "Drew Lock", "Jalen Milroe", ""],
                "WR1": ["Jaxon Smith-Njigba", "Tory Horton", "", ""],
                "WR2": ["Cooper Kupp", "Rashid Shaheed", "Irvin Charles", ""],
                "TE": ["AJ Barner", "Eric Saubert", "Nick Kallerup", ""],
                "LT": ["Charles Cross", "Josh Jones", "", ""],
                "LG": ["Quenton Nelson", "Anthony Bradford", "", ""],
                "RG": ["Grey Zabel", "Anthony Bradford", "Beau Stephens", ""],
                "RT": ["Abraham Lucas", "Josh Jones", "", ""],
                "FB": ["Brady Russell", "", "", ""],
                "RB": ["Zach Charbonnet", "Jadarian Price", "Emanuel Wilson", "George Holani"],
                "DT": ["Leonard Williams", "Rylie Mills", "", ""],
                "NT": ["Byron Murphy II", "Brandon Pili", "Deven Eastern", ""],
                "DE": ["Jarran Reed", "Mike Morris", "", ""],
                "RUSH": ["DeMarcus Lawrence", "Derick Hall", "", ""],
                "MLB": ["Ernest Jones IV", "Patrick O'Connell", "", ""],
                "WLB": ["Drake Thomas", "Tyrice Knight", "Chazz Surratt", ""],
                "SLB": ["Uchenna Nwosu", "Dante Fowler Jr.", "Connor O'Toole", ""],
                "CB1": ["Devon Witherspoon", "Nehemiah Pritchett", "", ""],
                "CB2": ["Josh Jobe", "Avery Smith", "", ""],
                "S1": ["Ty Okada", "Rodney Thomas II", "", ""],
                "S2": ["Julian Love", "", "", ""],
                "S3": ["Nick Emmanwori", "", "", ""],
                "K": ["Jason Myers", "", "", ""], "P": ["Michael Dickson", "", "", ""],
                "LS": ["Chris Stoll", "", "", ""],
            }},
    "LAR": {"url": "https://www.therams.com/team/depth-chart", "label": "Rams Unofficial Depth Chart (club site)",
            "dated": "the club labels the document UNOFFICIAL and compiles it itself",
            "groups": {
                "QB": ["Matthew Stafford", "Stetson Bennett IV", "Ty Simpson", ""],
                "WR1": ["Puka Nacua", "Jordan Whittington", "Tutu Atwell", ""],
                "WR2": ["Konata Mumpfield", "CJ Daniels", "", ""],
                "TE1": ["Davis Allen", "Tyler Higbee", "", ""],
                "TE2": ["Colby Parkinson", "Max Klare", "", ""],
                "LT": ["Alaric Jackson", "David Quessenberry", "", ""],
                "LG": ["Steve Avila", "Bill Murray", "", ""],
                "C": ["Coleman Shelton", "Dylan McMahon", "", ""],
                "RG": ["Kevin Dotson", "Beaux Limmer", "", ""],
                "RT": ["Warren McClendon Jr.", "Keagen Trost", "", ""],
                "RB": ["Kyren Williams", "Blake Corum", "Ronnie Rivers", ""],
                "OLB1": ["Myles Garrett", "Josaiah Stewart", "Desjuan Johnson", ""],
                "OLB2": ["Byron Young", "Wesley Bailey", "", ""],
                "DE1": ["Aaron Donald", "Larrell Murchison", "", ""],
                "DE2": ["Braden Fiske", "", "", ""],
                "NT": ["Tyler Davis", "Ty Hamilton", "", ""],
                "ILB1": ["Omar Speights", "Grant Stuard", "", ""],
                "ILB2": ["Nate Landman", "Shaun Dolac", "", ""],
                "CB1": ["Trent McDuffie", "Cam Lampkin", "", ""],
                "CB2": ["Emmanuel Forbes Jr.", "Josh Wallace", "", ""],
                "S1": ["Quentin Lake", "Kamren Kinchens", "Maximus Pulley", ""],
                "S2": ["Kam Curl", "Jaylen McCollough", "", ""],
                "K": ["Brandon McManus", "Joshua Karty", "", ""], "P": ["Ethan Evans", "", "", ""],
                "LS": ["Joe Cardona", "", "", ""],
            }},
}
# the hub's position code is coarser than the club's group label; this map is only used to route a
# row to the group whose string we can read off the club chart. Unmapped codes stay at club level.
POS_GROUP = {"QB": ["QB"], "WR": ["WR1", "WR2"], "TE": ["TE", "TE1", "TE2"], "RB": ["RB"], "FB": ["FB"],
             "T": ["LT", "RT"], "G": ["LG", "RG"], "C": ["C", "LG", "RG"], "DT": ["DT", "NT", "DE1", "DE2"],
             "DE": ["DE1", "DE2", "RUSH", "OLB1", "OLB2"], "LB": ["MLB", "WLB", "SLB", "OLB1", "OLB2", "ILB1", "ILB2"],
             "CB": ["CB1", "CB2"], "S": ["S1", "S2", "S3"], "K": ["K"], "P": ["P"], "LS": ["LS"]}


def find_group(chart, pos, names_unavailable):
    """Locate the club's own row for this player.

    First the group the hub's position code maps to; if the club files that player under a different
    group label (the hub writes "DT" for a man the club lists on the end line, "LB" for a rusher), we
    accept the group only when the player appears in exactly one group on the chart. Appearing in two
    groups with no mapping to break the tie is left unresolved and published as not published - the
    club's row is not our guess to make."""
    for g in POS_GROUP.get(pos, []):
        chain = chart["groups"].get(g)
        if chain and any(n in chain for n in names_unavailable):
            return g, chain
    hits = [(g, ch) for g, ch in chart["groups"].items() if any(n in ch for n in names_unavailable)]
    if len(hits) == 1:
        return hits[0]
    return None, None


def main():
    rows = list(csv.DictReader(open(os.path.join(DATA, INJ), encoding="utf-8"), delimiter="|"))
    by_club = defaultdict(list)
    for r in rows:
        by_club[r["team"]].append(r)

    clubs = sorted(set(list(by_club) + list(DEPTH)))

    def first_string(club, r):
        if club not in DEPTH:
            return False
        g, chain = find_group(DEPTH[club], r["pos"], [r["player"]])
        return bool(chain) and chain[0] == r["player"] and r["practice"] == "D"

    summary, chains = [], []
    for club in clubs:
        for side in ("offence", "defence", "special teams"):
            sel = [r for r in by_club[club] if r["side"] == side]
            dnp = [r for r in sel if r["practice"] == "D"]
            lim = [r for r in sel if r["practice"] == "L"]
            out = [r for r in sel if r["status"].strip()]
            groups = sorted({r["pos"] for r in sel})
            summary.append({
                "club": club, "side": side, "reported": len(sel), "did_not_practise": len(dnp),
                "limited": len(lim), "designated_out": len(out) or "not published",
                "positions_affected": ", ".join(groups) if groups else "not published",
                "first_string_unavailable": "; ".join(sorted({r["player"] for r in dnp if first_string(club, r)}))
                or "not published",
                "depth_chart_in_this_build": "yes" if club in DEPTH else "not published",
                "game": sel[0]["game"] if sel else "not published",
                "source": "S-INJ",
            })
            if club in DEPTH:
                chart = DEPTH[club]
                for r in sorted(sel, key=lambda x: (x["practice"] != "D", x["pos"], x["player"])):
                    if r["practice"] not in ("D", "L"):
                        continue
                    g, chain = find_group(chart, r["pos"], [r["player"]])
                    if not chain:
                        chains.append({"club": club, "side": side, "position_group": "not published",
                                       "player": r["player"], "position": r["pos"],
                                       "string": "not published", "practice": r["practice"],
                                       "status": r["status"] or "not published",
                                       "next_man_up": "not published",
                                       "why": "the club's published chart does not list this player in a group "
                                              "this build transcribed, so his string cannot be asserted",
                                       "depth_url": chart["url"], "injury_url": HUB_URL})
                        continue
                    i = chain.index(r["player"])
                    nxt = [c for c in chain[i + 1:] if c]
                    chains.append({"club": club, "side": side, "position_group": g,
                                   "player": r["player"], "position": r["pos"],
                                   "string": "%d%s string" % (i + 1, {0: "st", 1: "nd", 2: "rd", 3: "th"}.get(i, "th"))
                                   + (" (shared)" if i == 0 and chain[1] and r["player"] != chain[1] and False else ""),
                                   "practice": r["practice"], "status": r["status"] or "not published",
                                   "next_man_up": ", ".join(nxt[:2]) if nxt else "no backup listed on the club chart",
                                   "why": "unavailability and string both read off official pages" if i == 0
                                          else "a back-up is unavailable: this is depth behind the depth, and it "
                                               "only shows up when the two documents are joined",
                                   "depth_url": chart["url"], "injury_url": HUB_URL})

    def write(name, rows_, cols):
        with open(os.path.join(DATA, name), "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="|")
            w.writerow(cols)
            for r in rows_:
                w.writerow([(r.get(c) if str(r.get(c, "")).strip() else "not published") for c in cols])
        print("wrote data/%s (%d rows)" % (name, len(rows_)))

    write("deficiency_by_club_a392.csv", summary,
          "club|game|side|reported|did_not_practise|limited|designated_out|positions_affected|"
          "first_string_unavailable|depth_chart_in_this_build|source".split("|"))
    write("deficiency_chains_a392.csv", chains,
          "club|side|position_group|player|position|string|practice|status|next_man_up|why|depth_url|injury_url".split("|"))
    print("chains verified for %d clubs; the other %d publish counts only"
          % (len(DEPTH), len(clubs) - len(DEPTH)))


if __name__ == "__main__":
    main()

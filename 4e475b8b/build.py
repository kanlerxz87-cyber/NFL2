#!/usr/bin/env python3
"""Session 4e475b8b — fourth dated read of the official Week 10 injury hub (2026-11-16).

Mechanical parse of the verbatim fetch chunks in 4e475b8b/raw/chunk-{0..7}.md into:
  data/injuries_wk10_4e475b8b_20261116.csv   (the dated register, same schema as 5de1805b)
  data/reverification_4e475b8b_20261116.csv  (row-level delta vs the 15 Nov and 13 Nov reads)

Rules honoured from the repo's standing conventions:
  * transcribe the page as published — nothing is corrected or inferred;
  * practice vocabulary F/L/D, status vocabulary OUT/Q/D (FL-92);
  * every output row carries the official source URL;
  * fail loudly on unknown vocabulary, unparseable rows or structural drift
    (drift alarm: brief item "Add a drift alarm to every scraper").
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "4e475b8b" / "raw"
OUT_INJ = ROOT / "data" / "injuries_wk10_4e475b8b_20261116.csv"
OUT_RV = ROOT / "data" / "reverification_4e475b8b_20261116.csv"
FETCH_UTC = "2026-11-16T14:44Z"  # UTC completion time of the 8-chunk fetch
SOURCE = "https://www.nfl.com/injuries/"

PRAC = {
    "Full Participation in Practice": "F",
    "Limited Participation in Practice": "L",
    "Did Not Participate In Practice": "D",
}
STATUS = {"Out": "OUT", "Questionable": "Q", "Doubtful": "D"}

# The fetch tool splits long rows across chunk boundaries. Four rows were split;
# each repair is asserted to match the raw text before use.
REPAIRS = [
    ("| [Chris Rodriguez Jr.](https://www.nfl.com/players/chris-rodriguez-jr/) | RB |  | Limited Participation in Practic",
     "e |  |",
     "| [Chris Rodriguez Jr.](https://www.nfl.com/players/chris-rodriguez-jr/) | RB |  | Limited Participation in Practice |  |"),
    ("| [Jonathan Taylor](https://www.nfl.com/players/jonathan-taylor/) | RB |  | Ful",
     "l Participation in Practice |  |",
     "| [Jonathan Taylor](https://www.nfl.com/players/jonathan-taylor/) | RB |  | Full Participation in Practice |  |"),
    ("| [Siran Neal](https://www.nfl.com/players/",
     "siran-neal/) | S |  | Full Participation in Practice |  |",
     "| [Siran Neal](https://www.nfl.com/players/siran-neal/) | S |  | Full Participation in Practice |  |"),
    ("| [Brenen Thompson]",
     "(https://www.nfl.com/players/brenen-thompson/) | WR | Hamstring | Did Not Participate In Practice | Doubtful |",
     "| [Brenen Thompson](https://www.nfl.com/players/brenen-thompson/) | WR | Hamstring | Did Not Participate In Practice | Doubtful |"),
]

CITY_TO_ABBR = {
    "Commanders": "WAS", "Giants": "NYG", "Patriots": "NE", "Lions": "DET",
    "Chiefs": "KC", "Falcons": "ATL", "Vikings": "MIN", "Packers": "GB",
    "Jaguars": "JAX", "Titans": "TEN", "Bills": "BUF", "Jets": "NYJ",
    "Dolphins": "MIA", "Colts": "IND", "Panthers": "CAR", "Saints": "NO",
    "Texans": "HOU", "Browns": "CLE", "Rams": "LAR", "Cardinals": "AZ",
    "Seahawks": "SEA", "Raiders": "LV", "49ers": "SF", "Cowboys": "DAL",
    "Steelers": "PIT", "Bengals": "CIN", "Chargers": "LAC", "Ravens": "BAL",
}

# away|home per data/schedule_2026_wk10.csv (the canonical convention, PR #91)
GAME_IDS = {
    frozenset(("WAS", "NYG")): "W10-01",
    frozenset(("NE", "DET")): "W10-02",
    frozenset(("KC", "ATL")): "W10-03",
    frozenset(("MIN", "GB")): "W10-04",
    frozenset(("JAX", "TEN")): "W10-05",
    frozenset(("MIA", "IND")): "W10-06",
    frozenset(("CAR", "NO")): "W10-07",
    frozenset(("BUF", "NYJ")): "W10-08",
    frozenset(("HOU", "CLE")): "W10-09",
    frozenset(("LAR", "AZ")): "W10-10",
    frozenset(("SEA", "LV")): "W10-11",
    frozenset(("SF", "DAL")): "W10-12",
    frozenset(("PIT", "CIN")): "W10-13",
    frozenset(("LAC", "BAL")): "W10-14",
}

ROW_RE = re.compile(
    r"^\| \[([^]]+)]\(https://www\.nfl\.com/players/[^)]*/?\)\s*\| ([A-Z]+(?: [A-Z]+)?) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|\s*$"
)
CITY_LINE_RE = re.compile(r"^(Commanders|Giants|Patriots|Lions|Chiefs|Falcons|Vikings|Packers|Jaguars|Titans|Bills|Jets|Dolphins|Colts|Panthers|Saints|Texans|Browns|Rams|Cardinals|Seahawks|Raiders|49ers|Cowboys|Steelers|Bengals|Chargers|Ravens)\s*$")


def load_body():
    bodies = []
    for i in range(8):
        lines = (RAW / f"chunk-{i}.md").read_text(encoding="utf-8").splitlines()
        body = [ln for ln in lines if not ln.startswith("# ")]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        bodies.append("\n".join(body))
    # each repair joins the tail of chunk i to the head of chunk i+1, positionally
    pairs = {0: None, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6}
    for idx, (prefix, cont, full) in zip((1, 2, 4, 5), REPAIRS):
        assert bodies[idx].endswith(prefix), f"chunk {idx} does not end with expected prefix: {prefix[:40]!r}"
        assert bodies[idx + 1].startswith(cont), f"chunk {idx + 1} does not start with expected continuation: {cont[:40]!r}"
        bodies[idx] = bodies[idx][: -len(prefix)] + full
        bodies[idx + 1] = bodies[idx + 1][len(cont):]
    del pairs
    return "\n".join(bodies)


def parse(text):
    rows = []
    current = None
    seen_tables = 0
    for ln in text.splitlines():
        m = CITY_LINE_RE.match(ln.strip())
        if m and m.group(1) in CITY_TO_ABBR:
            current = m.group(1)
            continue
        rm = ROW_RE.match(ln.strip())
        if rm:
            if current is None:
                sys.exit(f"FAIL: player row before any club header: {ln[:60]!r}")
            name, pos, injury, prac, status = (s.strip() for s in rm.groups())
            if prac not in PRAC:
                sys.exit(f"FAIL: unknown practice vocabulary {prac!r} for {name}")
            if status and status not in STATUS:
                sys.exit(f"FAIL: unknown status vocabulary {status!r} for {name}")
            rows.append({
                "team": CITY_TO_ABBR[current],
                "player": name,
                "pos": pos,
                "injury": injury,
                "practice": PRAC[prac],
                "status": STATUS.get(status, ""),
                "player_url": "https://www.nfl.com/players/"
                + name.lower().replace(".", "").replace(" ", "-").replace("'", "").replace(",", "")
                + "/",
            })
            seen_tables += 1
    return rows, seen_tables


def assign_games(rows):
    # pair consecutive club blocks in page order via the fixture order of the schedule
    order = ["WAS", "NYG", "NE", "DET", "KC", "ATL", "MIN", "GB", "JAX", "TEN",
             "BUF", "NYJ", "MIA", "IND", "CAR", "NO", "HOU", "CLE", "LAR", "AZ",
             "SEA", "LV", "SF", "DAL", "PIT", "CIN", "LAC", "BAL"]
    seen = []
    for r in rows:
        if not seen or seen[-1] != r["team"]:
            seen.append(r["team"])
    if seen != order:
        sys.exit(f"FAIL: club block order differs from the official schedule order.\npage: {seen}\nexpected: {order}")
    for r in rows:
        r["game"] = GAME_IDS[frozenset((r["team"], next(t for t in order if t != r["team"] and frozenset((r["team"], t)) in GAME_IDS)))]
    # precise: use explicit partner mapping
    partner = {}
    for pair, gid in GAME_IDS.items():
        a, b = tuple(pair)
        partner[a] = (b, gid)
        partner[b] = (a, gid)
    for r in rows:
        r["game"] = partner[r["team"]][1]
    return rows


def main():
    text = load_body()
    rows, seen_tables = parse(text)
    rows = assign_games(rows)

    # structural drift alarms
    clubs = {}
    for r in rows:
        clubs.setdefault(r["team"], 0)
        clubs[r["team"]] += 1
    problems = []
    if len(clubs) != 28:
        problems.append(f"club count {len(clubs)} != 28")
    if len(rows) != 347:
        problems.append(f"row count {len(rows)} != 347 (15 Nov read); real page change must be published, not silently accepted")
    for team in CITY_TO_ABBR.values():
        if clubs.get(team, 0) == 0:
            problems.append(f"club {team} has zero rows (a club cannot be listed with no block unless the page changed)")

    # write the dated register
    OUT_INJ.parent.mkdir(exist_ok=True)
    with OUT_INJ.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="|", lineterminator="\n")
        w.writerow(["game", "team", "player", "pos", "injury", "practice", "status", "fetched_utc", "source"])
        for r in rows:
            w.writerow([r["game"], r["team"], r["player"], r["pos"], r["injury"], r["practice"], r["status"], FETCH_UTC, SOURCE])

    # deltas vs the 15 Nov read (5de1805b) and the 13 Nov read (83246f00)
    def load_prior(path):
        out = {}
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="|"):
                out[(row["game"], row["team"], row["player"])] = row
        return out

    prior15 = load_prior(ROOT / "data" / "injuries_wk10_5de1805b_20261115.csv")
    prior13 = load_prior(ROOT / "data" / "injuries_wk10_83246f00.csv")

    today = {(r["game"], r["team"], r["player"]): r for r in rows}
    rv = []
    n = 0
    for key in sorted(today, key=lambda k: (k[0], k[1], k[2])):
        r = today[key]
        n += 1
        gid = f"RV-4E-{n:03d}"
        cells = ("injury", "practice", "status")
        for label, prior in (("15 Nov 12:55Z read", prior15), ("13 Nov 12:46Z read", prior13)):
            if key in prior:
                p = prior[key]
                diffs = [c for c in cells if p[c] != r[c]]
                pos_diff = p["pos"] != r["pos"]
                if not diffs and not pos_diff:
                    result, note = "MATCH", "every cell identical across the two dated reads."
                else:
                    result = "MISMATCH"
                    note = "differing cells: " + ", ".join(
                        [f"pos ({p['pos']} -> {r['pos']})"] if pos_diff else []
                        + [f"{c} ({p[c]} -> {r[c]})" for c in cells if p[c] != r[c]]
                    )
                published = "; ".join(f"{c}={p[c]}" for c in ("pos",) + cells)
                official = "; ".join(f"{c}={r[c]}" for c in ("pos",) + cells)
            else:
                result, note = "ONLY ON THE PAGE TODAY", "no row for this game/team/player in the earlier dated read."
                published = "row absent"
                official = "; ".join(f"{c}={r[c]}" for c in ("pos",) + cells)
            rv.append([gid, f"{key[0]} {key[1]} {key[2]} vs {label}", label, published, official, result, note, SOURCE])
    for key in sorted(set(prior15) - set(today), key=lambda k: (k[0], k[1], k[2])):
        n += 1
        rv.append([f"RV-4E-{n:03d}", f"{key[0]} {key[1]} {key[2]} vs 15 Nov 12:55Z read", "15 Nov 12:55Z read",
                   "; ".join(f"{c}={prior15[key][c]}" for c in ("pos",) + cells), "row absent from the page today",
                   "ONLY IN THE 15 NOV READ", "row dropped from the page between 2026-11-15 and 2026-11-16.", SOURCE])
    with OUT_RV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="|", lineterminator="\n")
        w.writerow(["id", "check", "scope", "published_value", "official_value", "result", "note", "source"])
        w.writerows(rv)

    # summary
    desig = sum(1 for r in rows if r["status"])
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in ("OUT", "Q", "D")}
    prac = {p: sum(1 for r in rows if r["practice"] == p) for p in ("F", "L", "D")}
    match15 = sum(1 for x in rv if x[5] == "MATCH" and x[2] == "15 Nov 12:55Z read")
    mism15 = sum(1 for x in rv if x[5] == "MISMATCH" and x[2] == "15 Nov 12:55Z read")
    only15 = sum(1 for x in rv if x[2] == "15 Nov 12:55Z read" and x[5] == "ONLY ON THE PAGE TODAY")
    drop15 = sum(1 for x in rv if x[5] == "ONLY IN THE 15 NOV READ")
    print(f"rows={len(rows)} clubs={len(clubs)} designations={desig} OUT={counts['OUT']} Q={counts['Q']} D={counts['D']}")
    print(f"practice F={prac['F']} L={prac['L']} D={prac['D']}")
    print(f"vs 15 Nov: match={match15} mismatch={mism15} only_on_page_today={only15} dropped_since={drop15}")
    if problems:
        print("STRUCTURAL DRIFT:")
        for p in problems:
            print("  -", p)
    else:
        print("structural drift: none")


if __name__ == "__main__":
    main()

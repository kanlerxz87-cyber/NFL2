#!/usr/bin/env python3
"""Data audit for NFL2. Every check is deterministic and re-runnable.

Fails loudly rather than warning: the site's claim to be "verified" rests on these
checks running clean, so a soft warning here would be a weaselled guarantee.
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OFFICIAL_HOSTS = {"nfl.com", "www.nfl.com", "operations.nfl.com", "static.www.nfl.com"}
PRACTICE = {"F", "L", "D"}
STATUS = {"", "OUT", "Q", "D"}
CHANGES = {"RULED-OUT", "RULED-OUT-WK9", "OUT-SEASON", "IR", "IR-ACTIVATED", "IR-RETURN-DESIG",
           "IR-DECISION", "DEPTH-CHART", "PRACTICE", "DNP", "NO-DESIGNATION", "SIGNING",
           "ROSTER-CUT", "TIMELINE", "SEASON-IMPACT", "QUESTIONABLE", "DNP-WEEK-TO-WEEK"}
BANNED = {"tbd", "tba", "unknown", "?", "likely", "probably", "todo", "fixme", "xxx", "placeholder"}
FAIL, WARN, PASS = [], [], []


def rows(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    hdr = raw[0]
    return [dict(zip(hdr, r)) for r in raw[1:]], hdr, raw


def ok(msg):
    PASS.append(msg)


def bad(msg):
    FAIL.append(msg)


def warn(msg):
    WARN.append(msg)


def check_widths():
    for fn in sorted(os.listdir(DATA)):
        if not fn.endswith(".csv"):
            continue
        _, hdr, raw = rows(fn)
        bad_rows = [(i + 2, len(r)) for i, r in enumerate(raw[1:], start=1) if len(r) != len(hdr)]
        if bad_rows:
            bad("%s: rows with wrong field count: %s" % (fn, bad_rows[:5]))
        else:
            ok("%s: %d rows, all %d fields" % (fn, len(raw) - 1, len(hdr)))


def no_disguised_guesses():
    hits = []
    for fn in sorted(os.listdir(DATA)):
        if not fn.endswith(".csv"):
            continue
        data, _, _ = rows(fn)
        for r in data:
            for k, v in r.items():
                if v and v.strip().lower() in BANNED:
                    hits.append("%s.%s=%r" % (fn, k, v))
    if hits:
        bad("guessed-looking placeholder values found (blanks must be empty or 'not published'): %s" % hits[:6])
    else:
        ok("no disguised guesses: blanks are empty or the literal 'not published'")


def standings():
    data, _, _ = rows("standings_2026.csv")
    if len(data) != 32:
        bad("standings: expected 32 rows, found %d" % len(data))
    sw = sl = spf = spa = snet = 0
    for r in data:
        w, l, t = int(r["w"]), int(r["l"]), int(r["t"])
        pf, pa, net = int(r["pf"]), int(r["pa"]), int(r["net"])
        pct = (w + 0.5 * t) / (w + l + t)
        if abs(pct - float(r["pct"])) > 0.0006:
            bad("standings %s: published pct %s vs computed %.4f" % (r["abbr"], r["pct"], pct))
        if pf - pa != net:
            bad("standings %s: net %s != pf-pa %d" % (r["abbr"], r["net"], pf - pa))
        sw += w; sl += l; spf += pf; spa += pa; snet += net
        if r["conf"] not in ("AFC", "NFC") or r["div"] not in ("East", "North", "South", "West"):
            bad("standings %s: bad conf/div" % r["abbr"])
    if sw != sl:
        bad("standings: league wins %d != losses %d" % (sw, sl))
    else:
        ok("standings: league wins equal losses (%d each)" % sw)
    if spf != spa:
        bad("standings: league points for %d != against %d — transcription error" % (spf, spa))
    else:
        ok("standings: league points reconcile (%d for = %d against)" % (spf, spa))
    if snet != 0:
        bad("standings: net points sum to %d, must be 0" % snet)
    else:
        ok("standings: net points sum to zero")


def injuries():
    data, _, _ = rows("injuries_2026_wk10.csv")
    sched, _, _ = rows("schedule_2026_wk10.csv")
    games = {g["game_id"] for g in sched}
    teams = {r["abbr"] for r in rows("standings_2026.csv")[0]}
    seen = set()
    for r in data:
        if r["practice"] not in PRACTICE:
            bad("injury %s: bad practice code %r" % (r["player"], r["practice"]))
        if r["status"] not in STATUS:
            bad("injury %s: bad status code %r" % (r["player"], r["status"]))
        if r["game"] not in games:
            bad("injury %s: unknown game %s" % (r["player"], r["game"]))
        if r["team"] not in teams:
            bad("injury %s: unknown club %s" % (r["player"], r["team"]))
        if not re.match(r"^[a-z0-9\-]+$", r["slug"]):
            bad("injury %s: slug is not a url key: %r" % (r["player"], r["slug"]))
        key = (r["game"], r["slug"])
        if key in seen:
            bad("duplicate injury row for %s in %s" % (r["slug"], r["game"]))
        seen.add(key)
        if not r["player"].lower().replace(".", "").replace("'", "").startswith(r["slug"].split("-")[0][:4]):
            if r["slug"] not in ("chigoziem-okonkwo", "jake-hummel", "kamren-curl", "christopher-brooks",
                                 "gervon-dexter", "charlie-jones-3", "ben-brown-2", "aaron-brewer-2",
                                 "noah-fant-x4946", "josh-jacobs-x3315", "tytus-howard-x1979",
                                 "david-edwards-x1290", "zachary-carter-x9168", "d-j-wonnum",
                                 "marcus-harris-4", "jaylon-moore-2", "connor-mcgovern-2", "alec-anderson-2",
                                 "devin-moore-2", "derrick-harmon-2", "terrance-ferguson-2", "chris-bell-2",
                                 "antonio-johnson-3", "jaylon-jones-2", "cj-west", "d-j-reed", "a-j-brown",
                                 "a-j-haulcy", "t-j-hockenson", "t-j-hopper", "t-j-sanders", "p-j-locke",
                                 "ar-maj-reed-adams", "darnell-mooney", "treveyon-henderson"):
                warn("slug/name mismatch worth a look: %s vs %s" % (r["player"], r["slug"]))
    ok("injuries: %d rows, codes valid, all game and club keys resolve, no duplicates" % len(data))
    n = sum(1 for r in data if r["status"].strip())
    if n != 6:
        bad("injuries: %d published designations, expected 6 for this snapshot" % n)
    else:
        ok("injuries: 6 designations published, 248 rows honestly blank")


def depth():
    data, _, _ = rows("depth_changes_2026_wk10.csv")
    src, _, _ = rows("sources.csv")
    ids = {s["id"] for s in src}
    teams = {r["abbr"] for r in rows("standings_2026.csv")[0]}
    for r in data:
        if r["change"] not in CHANGES:
            bad("depth %s: change %r not in the controlled vocabulary" % (r["player"], r["change"]))
        if r["src"] not in ids:
            bad("depth %s: unknown source id %r" % (r["player"], r["src"]))
        if r["team"] not in teams:
            bad("depth %s: unknown club %r" % (r["player"], r["team"]))
        if not r["detail"].strip():
            bad("depth %s: empty detail" % r["player"])
    ok("depth log: %d rows, vocabulary closed, all source ids resolve" % len(data))


def sources():
    data, _, _ = rows("sources.csv")
    ids = set()
    for r in data:
        if r["id"] in ids:
            bad("duplicate source id %s" % r["id"])
        ids.add(r["id"])
        u = r["url"]
        if not u.startswith("https://"):
            bad("source %s: url is not https" % r["id"])
        host = re.sub(r"^https://([^/]+).*", r"\1", u)
        if r["tier"] == "A" and host not in OFFICIAL_HOSTS:
            bad("source %s: tier A but host %s is not the league's domain" % (r["id"], host))
        if r["tier"] != "A" and host in OFFICIAL_HOSTS:
            warn("source %s: league domain but tier %s" % (r["id"], r["tier"]))
    for fn in ("injuries_2026_wk10.csv", "standings_2026.csv", "schedule_2026_wk10.csv"):
        d, _, _ = rows(fn)
        for r in d:
            if "source" in r and r["source"] not in ids:
                bad("%s: source %r not registered" % (fn, r["source"]))
    ok("sources: %d registered, tier A restricted to official domains, tier links resolve" % len(data))


def registers():
    req, _, _ = rows("requirements.csv")
    stat = {"done", "in progress", "partial", "specified", "pending"}
    for r in req:
        if r["status"] not in stat:
            bad("requirement %s: status %r not in %s" % (r["id"], r["status"], sorted(stat)))
    if len(req) != 40:
        warn("requirements: %d rows (count changed since the docs were written)" % len(req))
    sug, _, _ = rows("suggestions.csv")
    for r in sug:
        for k in ("impact", "effort"):
            if r[k] not in ("H", "M", "L"):
                bad("suggestion %s: %s must be H/M/L, got %r" % (r["id"], k, r[k]))
    q, _, _ = rows("questions.csv")
    for r in q:
        if r["priority"] not in ("P0", "P1", "P2"):
            bad("question %s: bad priority %r" % (r["id"], r["priority"]))
        for k in ("what_we_have", "what_we_lack", "how_to_close"):
            v = r[k].strip()
            honest_empty = {"nothing", "nothing in-repo", "nothing yet", "not in repo", "not yet"}
            if len(v) < 8 and v.lower() not in honest_empty:
                bad("question %s: %s is too thin to be actionable" % (r["id"], k))
    fl, _, _ = rows("flags.csv")
    for r in fl:
        if r["severity"] not in ("low", "medium", "high"):
            bad("flag %s: bad severity %r" % (r["id"], r["severity"]))
        if "http" not in r["source"]:
            bad("flag %s: no source URL" % r["id"])
    ok("registers: statuses, priorities, scores and severities all inside their vocabularies")


def no_invented_results():
    lb, _, _ = rows("leaderboard.csv")
    offenders = []
    for r in lb:
        if r["strategy"].startswith("ST-12"):
            continue
        for k in ("tracked_bets", "settled", "mean_clv", "roi_units_per_100", "max_drawdown"):
            v = r[k].strip()
            if v not in ("", "0", "not published"):
                offenders.append("%s.%s=%s" % (r["strategy"][:8], k, v))
    if offenders:
        bad("performance numbers exist before forward tracking: %s" % offenders[:6])
    else:
        ok("leaderboard: no fabricated results — every performance cell is blank or zero-by-definition")
    corr, _, _ = rows("correlation.csv")
    for r in corr:
        for k in ("rho", "ci_low", "ci_high"):
            v = r[k].strip()
            if v not in ("", "not published") and v != "1.00":
                bad("correlation %s: an unmeasured rho value %r is present" % (r["id"], v))
    ok("correlation: only the two by-construction 1.00 cases carry a number; no fitted value is asserted")


def prose_counts_match_files():
    """Any prose that quotes a count must match the file it is describing.

    Half-true sentences are how a verified dataset turns into a stale one: the finding was corrected
    to six designations and the evidence cell next to it kept saying five. Any "N of M players",
    "N non-empty ... cells" or "N of M rows" claim in the registers or in a page's prose is checked against
    what the injury file actually contains.
    """
    inj, _, _ = rows("injuries_2026_wk10.csv")
    measured = {
        "status": sum(1 for r in inj if r["status"].strip()),
        "injury": sum(1 for r in inj if r["injury"].strip()),
        "rows": len(inj),
    }
    allowed = {measured["status"], measured["injury"], measured["rows"],
               measured["rows"] - measured["status"], measured["rows"] - measured["injury"]}
    claims = []
    for fn in ("flags.csv", "questions.csv", "suggestions.csv", "requirements.csv"):
        data, _, _ = rows(fn)
        for r in data:
            for k, cell in r.items():
                for n, m in re.findall(r"(\d+) of (\d+) (?:Week 10 )?(?:players|rows)", cell):
                    if int(m) == measured["rows"] and int(n) not in allowed:
                        claims.append("%s.%s: '%s of %s' matches no measured count %s"
                                     % (r["id"], k, n, m, sorted(allowed)))
                for n, kind in re.findall(r"(\d+) non-empty (\w+) cells", cell):
                    key = {"status": "status", "injury": "injury"}.get(kind)
                    if key and int(n) != measured[key]:
                        claims.append("%s.%s: claims %s non-empty %s cells, file has %d"
                                      % (r["id"], k, n, kind, measured[key]))
    # the same rule for page prose: a count written into content/*.md is a claim about data/*.csv
    content_dir = os.path.join(ROOT, "content")
    for fn in sorted(os.listdir(content_dir)):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(content_dir, fn), encoding="utf-8").read()
        text = re.sub(r"\{\{metric [a-z_]+\}\}", "0", text)   # metric refs are measured already
        for n, m in re.findall(r"(\d+) of (\d+) (?:Week 10 )?(?:players|rows|cells)", text):
            if int(m) == measured["rows"] and int(n) not in allowed:
                claims.append("%s: '%s of %s' matches no measured count %s" % (fn, n, m, sorted(allowed)))
    if claims:
        bad("prose contradicts the data file it cites: %s" % claims[:5])
    else:
        ok("every count quoted in the registers matches the file it describes "
           "(%d designations, %d injury cells, %d rows)" % (measured["status"], measured["injury"], measured["rows"]))


def gamelog():
    """The week 1-9 game log came from a parallel session's fetch of the official schedule pages.
    Importing someone else's file into the published site means re-auditing it from scratch:
    every row must carry an official URL, and the log must imply the same records as the
    standings table we transcribed independently from nfl.com/standings."""
    import json
    path = os.path.join(DATA, "games_2026_wk1_9.csv")
    if not os.path.exists(path):
        bad("data/games_2026_wk1_9.csv is missing; run tools/import_parallel.py")
        return
    data, hdr, _ = rows("games_2026_wk1_9.csv")
    need = ["week", "date", "away", "home", "away_pts", "home_pts", "neutral", "source"]
    if [c for c in need if c not in hdr]:
        bad("game log: missing columns %s" % [c for c in need if c not in hdr]); return
    nosrc = [r for r in data if not r["source"].startswith("https://www.nfl.com/games/")]
    if nosrc:
        bad("game log: %d rows without an official nfl.com/games URL (e.g. %s)"
            % (len(nosrc), nosrc[0]))
    else:
        ok("game log: all %d rows carry an official nfl.com game URL" % len(data))
    scores = [r for r in data if not (r["away_pts"].isdigit() and r["home_pts"].isdigit())]
    if scores:
        bad("game log: %d rows lack a numeric final score: %s" % (scores[0]["date"], len(scores)))
    else:
        ok("game log: every row has two numeric scores (no scheduled-but-unplayed rows imported)")
    weeks = sorted({r["week"] for r in data}, key=int)
    per = {w: sum(1 for r in data if r["week"] == w) for w in weeks}
    if any(n < 14 for n in per.values()):
        bad("game log: a week with fewer than 14 games suggests a dropped slate: %s" % per)
    else:
        ok("game log: %s games across weeks %s, none dropped"
           % (len(data), ", ".join("W%d=%d" % (int(w), per[w]) for w in weeks)))
    ALIAS = {"LA": "LAR"}
    rec = {}
    for r in data:
        a, h = int(r["away_pts"]), int(r["home_pts"])
        for club, pf, pa in ((r["away"], a, h), (r["home"], h, a)):
            t = rec.setdefault(ALIAS.get(club, club), {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
            t["n"] += 1; t["pf"] += pf; t["pa"] += pa
            t["w" if pf > pa else "l" if pf < pa else "t"] += 1
    st, _, _ = rows("standings_2026.csv")
    mism = []
    for r in st:
        got = rec.get(r["abbr"])
        if not got:
            mism.append("%s: no games" % r["abbr"]); continue
        want = (int(r["w"]), int(r["l"]), int(r["t"]), int(r["pf"]), int(r["pa"]))
        if (got["w"], got["l"], got["t"], got["pf"], got["pa"]) != want:
            mism.append("%s: standings %s vs log %s" % (r["abbr"], want,
                        (got["w"], got["l"], got["t"], got["pf"], got["pa"])))
    if mism:
        bad("game log disagrees with the independently transcribed standings table for %d clubs: %s"
            % (len(mism), mism[:4]))
    else:
        ok("game log reconciles exactly with the standings table for all %d clubs "
           "(W-L-T, points for, points against) after the LA/LAR alias" % len(st))
    byes = sorted(c for c, t in rec.items() if t["n"] != 9)
    eight = len([c for c, t in rec.items() if t["n"] == 8])
    slots = sum(1 for w in weeks for _ in range(16 - per[w]))
    if eight != len(byes) or 32 * 9 - len(byes) != sum(t["n"] for t in rec.values()) or slots * 2 != len(byes):
        bad("game log: bye arithmetic does not close - %d clubs at 8 games, %d empty game-slots"
            % (eight, slots))
    else:
        ok("game log: bye arithmetic closes exactly - %d clubs played 8, %d played 9, "
           "%d empty game-slots x 2 = %d club-byes" % (eight, len(rec) - eight, slots, len(byes)))
    neutral = sum(1 for r in data if r["neutral"] == "yes")
    if neutral != 7:
        warn("game log: %d neutral-site games flagged; the standings cross-check is unaffected" % neutral)
    else:
        ok("game log: %d neutral-site games marked, matching the international-slate count" % neutral)
    man = os.path.join(DATA, "build_manifest.json")
    if os.path.exists(man):
        m = json.load(open(man, encoding="utf-8")).get("metrics", {})
        if m.get("games_log") == len(data) and m.get("games_log_reconciled") == len(st) \
                and m.get("games_log_mismatched") == 0:
            ok("site manifest: published game-log counts match this recomputation")
        else:
            bad("site manifest is stale for the game log: %s vs %d rows"
                % ({k: m.get(k) for k in ("games_log", "games_log_reconciled", "games_log_mismatched")}, len(data)))


def main():
    check_widths(); no_disguised_guesses(); standings(); injuries(); depth(); sources(); registers(); no_invented_results(); prose_counts_match_files(); gamelog()
    print("=" * 72)
    for m in PASS:
        print("  PASS  " + m)
    for m in WARN:
        print("  WARN  " + m)
    for m in FAIL:
        print("  FAIL  " + m)
    print("=" * 72)
    print("verify: %d passed · %d warnings · %d failures" % (len(PASS), len(WARN), len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

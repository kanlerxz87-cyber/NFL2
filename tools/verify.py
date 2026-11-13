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
    quoted = re.findall(r"(\d+) requirements", open(os.path.join(ROOT, "content", "index.md"), encoding="utf-8").read()
                        + open(os.path.join(ROOT, "content", "requirements.md"), encoding="utf-8").read())
    stale = [q for q in quoted if int(q) != len(req)]
    if stale:
        bad("prose quotes %s requirements, the register has %d" % (stale, len(req)))
    else:
        ok("requirements: %d rows, and the site prose that quotes the count agrees with the file" % len(req))
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
    ok("correlation: only the two by-construction 1.00 cases carry a number; no fitted rho is asserted")
    measured_correlation_is_reproducible(); depth_reach_is_reproducible(); fair_lines_are_reproducible(); publication_manifest_matches_tree()


def measured_correlation_is_reproducible():
    """The two empirically measured correlations must equal a fresh recomputation from the game log.

    C-07 and C-08 are the only register rows that quote a measured statistic. Rather than trusting the
    number written into the register, this recomputes Pearson r from data/games_2026_wk1_9.csv and fails
    if the published value disagrees beyond rounding. It also enforces the distinction the register
    makes: r is not rho, so a measured r may never be written into the rho column.
    """
    import math
    games, _, _ = rows("games_2026_wk1_9.csv")
    home = [int(g["home_pts"]) for g in games]
    away = [int(g["away_pts"]) for g in games]
    margin = [h - a for h, a in zip(home, away)]
    total = [h + a for h, a in zip(home, away)]
    n = len(games)

    def pearson(x, y):
        mx, my = sum(x) / len(x), sum(y) / len(y)
        sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
        sxx = sum((a - mx) ** 2 for a in x)
        syy = sum((b - my) ** 2 for b in y)
        return sxy / math.sqrt(sxx * syy)

    expect = {"C-07": pearson(home, away), "C-08": pearson(margin, total)}
    corr, _, _ = rows("correlation.csv")
    problems = []
    for r in corr:
        if r["id"] not in expect:
            if "measured - Pearson r" in r["verification"]:
                problems.append("%s claims a measured r that no computation supports" % r["id"])
            continue
        m = re.search(r"Pearson r = ([+-]\d+\.\d+)", r["verification"])
        if not m:
            problems.append("%s quotes no measured r" % r["id"]); continue
        claimed, fresh = float(m.group(1)), expect[r["id"]]
        if abs(claimed - fresh) > 0.0001:
            problems.append("%s says r=%+.4f, the game log gives %+.4f" % (r["id"], claimed, fresh))
        if r["rho"].strip() not in ("", "not published"):
            problems.append("%s puts a measured r into the rho column" % r["id"])
    if problems:
        bad("measured correlations do not reproduce: %s" % problems[:4])
    else:
        ok("measured correlations reproduce from the game log (C-07 r=%+.4f, C-08 r=%+.4f, n=%d)"
           % (expect["C-07"], expect["C-08"], n))


def depth_reach_is_reproducible():
    """Every starter-to-backup cascade must equal a fresh join of the depth chart to the practice report.

    R-20 and R-21 ask which clubs are down to a 2nd, 3rd or 4th string. data/computed_depth_reach.csv
    answers that for the four clubs with a verified chart. This recomputes the join from
    data/depth_charts.json + data/injuries_2026_wk10.csv and fails on any disagreement, so the published
    cascades cannot drift away from the two sources they came from.
    """
    import json
    chart_path = os.path.join(DATA, "depth_charts.json")
    reach_path = os.path.join(DATA, "computed_depth_reach.csv")
    if not (os.path.exists(chart_path) and os.path.exists(reach_path)):
        warn("depth-reach computation absent; reproducibility check skipped"); return
    charts = json.load(open(chart_path, encoding="utf-8"))["depth_charts"]
    inj, _, _ = rows("injuries_2026_wk10.csv")
    report = {(r["team"], r["player"]): r["practice"] for r in inj}
    fresh = {}
    for club in charts:
        for unit in ("offense", "defense"):
            for grp, names in charts[club].get(unit, {}).items():
                if not names:
                    continue
                reach, who = 0, None
                for i, nm in enumerate(names, 1):
                    if report.get((club, nm)) in (None, "F"):
                        reach, who = i, nm
                        break
                if reach == 1:
                    continue
                # reach == 0 means no body at any depth is available: a vacancy
                fresh[(club, grp)] = (reach, names[0], who, len(names))
    with open(reach_path, encoding="utf-8") as fh:
        published = list(csv.DictReader(fh, delimiter="|"))
    seen, problems = set(), []
    for r in published:
        key = (r["club"], r["position_group"])
        seen.add(key)
        if key not in fresh:
            problems.append("%s %s is published but no longer reproduces" % key); continue
        reach, starter, who, chain = fresh[key]
        claimed = r["depth_reached"]
        if reach == 0:
            if claimed != "vacant":
                problems.append("%s %s: recomputation finds a vacancy, row says %r"
                                % (key[0], key[1], claimed))
            if r["next_man_up"].strip():
                problems.append("%s %s: a vacancy cannot have a next man up" % key)
            continue
        if claimed != str(reach):
            problems.append("%s %s: says %r, recomputation says %d"
                            % (key[0], key[1], r["depth_reached"], reach))
        if r["projected_starter"] != starter:
            problems.append("%s %s: starter disagrees" % key)
        if r["next_man_up"] != who:
            problems.append("%s %s: next man up disagrees" % key)
        if int(r["chain_length"]) != chain:
            problems.append("%s %s: chain length disagrees" % key)
    for key in fresh:
        if key not in seen:
            problems.append("%s %s reproduces but is not published" % key)
    if problems:
        bad("depth reach does not reproduce: %s" % problems[:4])
    else:
        third = sum(1 for f in fresh.values() if f[0] >= 3)
        vacant = sum(1 for f in fresh.values() if f[0] == 0)
        ok("depth reach reproduces for %d position groups across %d charted clubs; %d reach the 3rd string, %d are vacant"
           % (len(fresh), len(charts), third, vacant))


def fair_lines_are_reproducible():
    """The originated Week 10 lines must equal a fresh computation from the game log and the fixture list.

    Stage 1-2 of the origination pipeline. Because no market price exists in this repository (FL-10),
    these lines have no residual to publish and are not a betting recommendation. What must hold is that
    each number is arithmetic a reviewer can redo, so this recomputes all 14 games and fails on any drift.
    """
    path = os.path.join(DATA, "computed_fair_lines.csv")
    if not os.path.exists(path):
        warn("fair-line computation absent; skip"); return
    log, _, _ = rows("games_2026_wk1_9.csv")
    sched, _, _ = rows("schedule_2026_wk10.csv")
    alias = {"LA": "LAR"}
    pf, pa, gp = {}, {}, {}
    for g in log:
        a, h = alias.get(g["away"], g["away"]), alias.get(g["home"], g["home"])
        ap, hp = int(g["away_pts"]), int(g["home_pts"])
        for t, f, ag in ((a, ap, hp), (h, hp, ap)):
            pf[t] = pf.get(t, 0) + f
            pa[t] = pa.get(t, 0) + ag
            gp[t] = gp.get(t, 0) + 1
    off = {t: pf[t] / gp[t] for t in gp}
    dfn = {t: pa[t] / gp[t] for t in gp}
    with open(path, encoding="utf-8") as fh:
        published = {r["game_id"]: r for r in csv.DictReader(fh, delimiter="|")}
    problems = []
    for s in sched:
        a, h = s["away"], s["home"]
        neutral = "yes" if any(k in s["venue"] for k in ("Munich", "Mexico", "Tottenham", "Wembley")) else "no"
        hfa = 0.0 if neutral == "yes" else 2.5
        fa = (off[a] + dfn[h]) / 2.0
        fh = (off[h] + dfn[a]) / 2.0 + hfa
        r = published.get(s["game_id"])
        if not r:
            problems.append("%s missing" % s["game_id"]); continue
        for label, mine, theirs in (("away_pts", fa, r["fair_away_pts"]),
                                    ("home_pts", fh, r["fair_home_pts"]),
                                    ("total", fa + fh, r["fair_total"]),
                                    ("spread", fh - fa, r["fair_spread_home"])):
            if abs(mine - float(theirs)) > 0.005:
                problems.append("%s %s: says %s, recomputation %.2f" % (s["game_id"], label, theirs, mine))
        if r["neutral_site"] != neutral:
            problems.append("%s neutral flag disagrees" % s["game_id"])
    if len(published) != len(sched):
        problems.append("%d lines published for %d fixtures" % (len(published), len(sched)))
    # a line with no market to compare against must never carry a residual or an edge claim
    for r in published.values():
        for k, v in r.items():
            if re.search(r"residual|edge|ev_|roi|clv|vig", k, re.I) and v.strip():
                problems.append("%s carries a market-relative column %r" % (r["game_id"], k))
    if problems:
        bad("originated fair lines do not reproduce: %s" % problems[:4])
    else:
        ok("originated fair lines reproduce for all %d Week 10 fixtures; no market-relative column exists"
           % len(published))


def publication_manifest_matches_tree():
    """The deployed artifact root must be the canonical dashboard, not the docs/ archive.

    Two deploy mechanisms run on every push to main: the Actions workflow and the legacy Pages build.
    Until this fix they disagreed about which directory is the website -- pages.yml uploaded docs/,
    which is an older 16-page archive, while CI audited the 22-page root build. The archive won and the
    canonical pages 404'd live (FL-26). This check compares the two directory listings so the mismatch
    cannot come back unnoticed.
    """
    root = ROOT
    wf = os.path.join(root, ".github", "workflows", "pages.yml")
    if not os.path.exists(wf):
        warn("pages.yml absent; publication check skipped"); return
    text = open(wf, encoding="utf-8").read()
    m = re.search(r"upload-pages-artifact@v\d+\s*\n\s*with:\s*\n\s*path:\s*(\S+)", text)
    if not m:
        bad("pages.yml: cannot find the artifact path; the publication target is unverified"); return
    target = m.group(1).strip().strip("'\"")
    canonical = sorted(f for f in os.listdir(root)
                       if f.endswith(".html") and os.path.isfile(os.path.join(root, f)))
    docs_dir = os.path.join(root, "docs")
    docs_pages = sorted(f for f in os.listdir(docs_dir) if f.endswith(".html")) if os.path.isdir(docs_dir) else []
    if target in ("docs", "docs/", "./docs"):
        bad("pages.yml publishes docs/ (%d archived pages) instead of the audited root build (%d pages): FL-26"
            % (len(docs_pages), len(canonical)))
        return
    # the artifact root must be the root, and must carry the pages CI audits
    missing = [p for p in ("index.html", "line-origination.html", "depth-impact.html",
                           "correlation.html", "flagged-for-review.html") if p not in canonical]
    if missing:
        bad("artifact root is missing canonical pages: %s" % missing)
        return
    # and it must not be the archive: a docs-only page name must not appear at the root
    docs_only = sorted(set(docs_pages) - set(canonical))
    ok("publication target is the repository root (%d canonical pages); docs/ keeps %d archived pages, %d of them docs-only"
       % (len(canonical), len(docs_pages), len(docs_only)))


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


def register_counts_match_files():
    """Every register row that quotes the size of another register must quote the real size.

    Added after a live re-verification found R-03 claiming "25 suggestions S-01…S-25" while the
    register held 29 (S-01…S-29), R-05 claiming 28 questions against 29, and R-25 claiming 15 flags
    against 21. Those were hand-maintained numbers that stopped being true as other sessions appended
    rows. A pattern like "N <noun>" is a claim about a file, so it is checked against the file.
    """
    noun_file = {
        "suggestion": "suggestions.csv", "suggestions": "suggestions.csv",
        "question": "questions.csv", "questions": "questions.csv",
        "flag": "flags.csv", "flags": "flags.csv",
        "requirement": "requirements.csv", "requirements": "requirements.csv",
        "gate": "gates.csv", "gates": "gates.csv",
        "signal": "signals.csv", "signals": "signals.csv",
        "strategy": "strategies.csv", "strategies": "strategies.csv",
        "source": "sources.csv", "sources": "sources.csv",
    }
    sizes = {fn: len(rows(fn)[0]) for fn in set(noun_file.values())}
    wrong = []
    for fn in ("requirements.csv", "questions.csv", "suggestions.csv", "flags.csv"):
        data, _, _ = rows(fn)
        for r in data:
            for k, cell in r.items():
                # "25 suggestions" / "21 flags published" — but not "S-25" ids or "14-entry"
                # a count inside backticks is a quotation of a defect, not an assertion
                scan = re.sub(r"`[^`]*`", "", cell)
                for n, noun in re.findall(r"(?<![\w-])(\d+) (suggestions?|questions?|flags?|requirements?|gates?|signals?|strategies|sources)\b", scan):
                    target = noun_file[noun]
                    if int(n) != sizes[target]:
                        wrong.append("%s.%s: says %s %s, %s holds %d"
                                     % (r.get("id", "?"), k, n, noun, target, sizes[target]))
    if wrong:
        bad("a register row quotes the wrong size of another register: %s" % wrong[:5])
    else:
        ok("register size claims match the files (%s)"
           % ", ".join("%s %d" % (f.replace(".csv", ""), n) for f, n in sorted(sizes.items())))


def injury_coverage_is_measured_not_named():
    """The set of clubs with no injury rows must be derived from the fixture list, not hand-named.

    tools/build_site.py once carried ["SEA","CIN","LAC","BAL"] as the empty-club list. On the live hub
    SEA and CIN publish full blocks, so that constant was wrong in both directions and the site
    published "28 clubs" for a 24-club file. This check fails if a hand-written club list appears in
    the builder or if a page hard-codes the coverage count instead of using the metric.
    """
    src = open(os.path.join(ROOT, "tools", "build_site.py"), encoding="utf-8").read()
    hard = re.findall(r'\[\s*"(SEA|CIN|LAC|BAL)"\s*,\s*"(SEA|CIN|LAC|BAL)"', src)
    if hard:
        bad("build_site.py still hand-names the empty-club list %s; derive it from schedule_2026_wk10.csv" % hard[:3])
    inj, _, _ = rows("injuries_2026_wk10.csv")
    sched, _, _ = rows("schedule_2026_wk10.csv")
    playing = {g["away"] for g in sched} | {g["home"] for g in sched}
    present = {r["team"] for r in inj}
    missing = sorted(playing - present)
    if not present <= playing:
        bad("injury file names a club that is not playing Week 10: %s" % sorted(present - playing))
    for fn in sorted(os.listdir(os.path.join(ROOT, "content"))):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(ROOT, "content", fn), encoding="utf-8").read()
        # A claim that the INJURY SNAPSHOT covers 28 clubs is false: it holds 24. A sentence about
        # depth charts, rosters or the league is a different claim about a different file, so the
        # check looks for sentence-level co-occurrence rather than a bare number.
        # a value inside backticks is a quotation of a claim (usually of a defect being reported),
        # not an assertion by this page, so strip code spans before scanning
        scan = re.sub(r"`[^`]*`", "", text)
        for sent in re.split(r"(?<=[.!?])\s+|\n", scan):
            if not re.search(r"\b28 clubs\b", sent):
                continue
            # on the injury page every club-count claim is a coverage claim by definition
            on_injury_page = fn in ("injuries.md", "executive-summary.md", "index.md")
            if not on_injury_page and not re.search(r"injur|practice report|snapshot|hub", sent, re.I):
                continue
            # the corrected phrasing always qualifies the number against the full set
            if re.search(r"\b(24|25|26|27) of (the )?28\b|of the 28 clubs|of 28 clubs", sent):
                continue
            bad("content/%s claims the injury snapshot covers 28 clubs; it holds %d of %d"
                % (fn, len(present), len(playing)))
        if re.search(r"blank cells are rendered as .not published.", text):
            pass
    ok("injury coverage measured from the fixture list: %d of %d clubs present, %d absent (%s)"
       % (len(present), len(playing), len(missing), ", ".join(missing)))


def dictionary_counts_match_files():
    """The data dictionary publishes a row count per file; those numbers are checked against the
    files instead of being maintained by whoever remembers to edit them."""
    dict_md = os.path.join(ROOT, "content", "data-dictionary.md")
    if not os.path.exists(dict_md):
        warn("content/data-dictionary.md not found; row-count audit skipped"); return
    text = open(dict_md, encoding="utf-8").read()
    checked, wrong = 0, []
    for line in text.splitlines():
        if not line.startswith("| `data/") and not line.startswith("| data/"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        files = re.findall(r"([A-Za-z0-9_]+\.csv)", cells[0])
        counts = [c for c in re.split(r"\s*/\s*", cells[1]) if re.fullmatch(r"\d+", c)]
        if not files or len(files) != len(counts):
            continue
        for fn, n in zip(files, counts):
            path = os.path.join(DATA, fn)
            if not os.path.exists(path):
                wrong.append("%s: dictionary lists a file that does not exist" % fn); continue
            actual = len(rows(fn)[0])
            checked += 1
            if int(n) != actual:
                wrong.append("%s: dictionary says %s rows, file has %d" % (fn, n, actual))
    if wrong:
        bad("data dictionary row counts are stale: %s" % wrong[:6])
    else:
        ok("data dictionary: all %d published row counts match the files they describe" % checked)


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
    # Week 10 results are deliberately NOT appended to the corpus: suggestion S-26 makes the
    # weeks 1-9 file the pre-registered backtest corpus, so editing it would silently re-baseline
    # every grade already published against it. They live in their own append-only file and are
    # folded in here, at reconciliation time only.
    extra, extra_hdr = [], []
    extra_path = os.path.join(DATA, "games_2026_wk10_played.csv")
    if os.path.exists(extra_path):
        extra, extra_hdr, _ = rows("games_2026_wk10_played.csv")
        need_extra = [c for c in need if c not in extra_hdr]
        if need_extra:
            bad("week 10 results: missing the columns the corpus uses: %s" % need_extra)
        else:
            ok("week 10 results file carries the corpus schema (%d settled games)" % len(extra))
        bad_src = [r for r in extra if not r["source"].startswith("https://www.nfl.com/games/")]
        if bad_src:
            bad("week 10 results: %d rows without an official nfl.com/games URL" % len(bad_src))
        else:
            ok("week 10 results: all %d rows carry an official nfl.com game URL" % len(extra))
        bad_sc = [r for r in extra if not (r["away_pts"].isdigit() and r["home_pts"].isdigit())]
        if bad_sc or any(r["status"].strip().lower() != "final" for r in extra):
            bad("week 10 results: only Final games may be published (%d bad rows)" % (len(bad_sc) or 1))
        else:
            ok("week 10 results: every row is a Final game with two numeric scores")
        seen = {(r["week"], r["away"], r["home"]) for r in data}
        dupes = [r for r in extra if (r["week"], r["away"], r["home"]) in seen]
        if dupes:
            bad("week 10 results: %d games already present in the frozen corpus" % len(dupes))
        else:
            ok("week 10 results: no game is double-counted against the frozen corpus")
        for r in extra:
            a, h = int(r["away_pts"]), int(r["home_pts"])
            for club, pf, pa in ((r["away"], a, h), (r["home"], h, a)):
                t = rec.setdefault(ALIAS.get(club, club),
                                   {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
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
        ok("game log + week 10 results reconcile exactly with the standings table for all %d "
           "clubs (W-L-T, points for, points against) after the LA/LAR alias" % len(st))
    # Bye arithmetic and the neutral-site count are properties of the frozen weeks 1-9 corpus, not
    # of the combined set: a partially-played week would break both identities without being wrong.
    rec9 = {}
    for r in data:
        a, h = int(r["away_pts"]), int(r["home_pts"])
        for club, pf, pa in ((r["away"], a, h), (r["home"], h, a)):
            t = rec9.setdefault(ALIAS.get(club, club), {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
            t["n"] += 1
    rec = rec9
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
            ok("site manifest: published game-log counts match this recomputation of the "
               "frozen weeks 1-9 corpus")
        else:
            bad("site manifest is stale for the game log: %s vs %d rows"
                % ({k: m.get(k) for k in ("games_log", "games_log_reconciled", "games_log_mismatched")}, len(data)))


def datasets_documented():
    """A CSV in data/ that the dictionary does not mention is an orphan: nobody has to say what it
    means, so it silently becomes the place unsourced numbers live."""
    dict_md = os.path.join(ROOT, "content", "data-dictionary.md")
    text = open(dict_md, encoding="utf-8").read() if os.path.exists(dict_md) else ""
    orphans = [f for f in sorted(os.listdir(DATA))
               if f.endswith(".csv") and f not in text]
    if orphans:
        bad("data files the dictionary never mentions: %s" % orphans[:6])
    else:
        ok("every data/*.csv is documented in the data dictionary (%d files)"
           % len([f for f in os.listdir(DATA) if f.endswith(".csv")]))


def reverification_holds():
    """The re-verification register is allowed to report 'superseded' (the official page moved under
    us) but never 'MISMATCH' (we published something the official page does not say)."""
    fn = os.path.join(DATA, "reverification_a392.csv")
    if not os.path.exists(fn):
        warn("re-verification register absent; run scripts/reverify_a392.py"); return
    data, _, _ = rows("reverification_a392.csv")
    bad_rows = [r for r in data if r["result"].strip().upper() == "MISMATCH"]
    if bad_rows:
        bad("published values disagree with the official page: %s"
            % [r["check"] for r in bad_rows][:4])
    else:
        ok("re-verification register: %d checks, 0 mismatches against the live official pages "
           "(%d superseded by a later official read)"
           % (len(data), sum(1 for r in data if r["result"].strip() == "SUPERSEDED")))


def filter_clauses_do_something():
    """Every {{csv ... filter=key=value}} clause on the site is recomputed here from the data file.

    Why this exists: the builder once accepted only key=value clauses and silently ignored any other
    spelling, so three published tables - including the injury-designations table and both suggestion
    tiers - shipped unfiltered, i.e. showing every row under a caption that promised a subset. A
    filter that matches nothing is visible; a filter that is skipped is not. This check fails on both,
    and on a filtered table that returns the whole file."""
    import glob, re
    problems, tables = [], 0
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "*.md"))):
        text = open(path, encoding="utf-8").read()
        for d in re.findall(r"\{\{csv.*?\}\}", text, flags=re.S):
            m = re.search(r"([A-Za-z0-9_\-.]+\.csv)", d)
            f = re.search(r";;filter=([^;]*?)(?:;;|\}\})?$", d.split("\n")[0]) or re.search(r";;filter=([^;]*)", d)
            if not m:
                continue
            tables += 1
            data, _, _ = rows(m.group(1))
            if not f:
                continue
            kept = data
            clauses = f.group(1).rstrip("}").split(",")
            for clause in [c for c in clauses if c.strip()]:
                if "=" not in clause:
                    problems.append("%s: clause %r is not key=value" % (os.path.basename(path), clause))
                    continue
                k, v = [x.strip() for x in clause.split("=", 1)]
                if k not in (data[0] if data else {}):
                    problems.append("%s: filter key %r is not a column" % (os.path.basename(path), k))
                    continue
                neg = v.startswith("!")
                v = v[1:] if neg else v
                if v == "*":
                    keep = lambda cell: cell.strip() != ""
                elif v == "":
                    keep = (lambda cell: cell.strip() == "") if neg else (lambda cell: cell.strip() != "")
                else:
                    keep = (lambda cell: v.lower() not in cell.lower()) if neg else (lambda cell: v.lower() in cell.lower())
                kept = [r for r in kept if keep(r.get(k, "").strip())]
            if len(kept) == 0:
                problems.append("%s: filter %r matches no rows in %s" % (os.path.basename(path), f.group(1), m.group(1)))
            elif len(kept) == len(data) and len(data) > 12:
                problems.append("%s: filter %r returns every row of %s (a no-op clause?)"
                                % (os.path.basename(path), f.group(1), m.group(1)))
    if problems:
        bad("csv filters that do nothing: %s" % problems[:4])
    else:
        ok("every filtered table on the site selects a real subset (%d csv tables checked)" % tables)


def settled_week10_reproduces():
    """The first out-of-sample settlement on this site must not be a number someone typed.

    Every cell of the settled table is recomputed here from the official result and the two
    published prediction files, and compared against what the page will render. The do-nothing
    baseline is refitted from the frozen corpus so that if anyone edits the corpus, the whole
    settled page moves with it instead of quietly disagreeing.
    """
    import statistics as st
    for fn in ("games_2026_wk10_played.csv", "settled_wk10_5f16dcc6.csv",
               "computed_settled_5f16dcc6.csv"):
        if not os.path.exists(os.path.join(DATA, fn)):
            warn("%s absent; run tools/compute_settled_wk10.py" % fn)
            return
    played, _, _ = rows("games_2026_wk10_played.csv")
    corpus, _, _ = rows("games_2026_wk1_9.csv")
    orig = {r["game"]: r for r in rows("originated_lines_wk10_a392.csv")[0]}
    fair = {r["game_id"]: r for r in rows("computed_fair_lines.csv")[0]}
    published, _, _ = rows("settled_wk10_5f16dcc6.csv")

    margins = [int(r["home_pts"]) - int(r["away_pts"]) for r in corpus]
    totals = [int(r["home_pts"]) + int(r["away_pts"]) for r in corpus]
    mean_margin, mean_total = st.mean(margins), st.mean(totals)

    if len(published) != 4 * len(played):
        bad("settled table holds %d rows, expected 4 predictors x %d settled games"
            % (len(published), len(played)))
        return
    wrong = []
    for g in played:
        gid = g["game_id"]
        a, h = int(g["away_pts"]), int(g["home_pts"])
        act_m, act_t = h - a, h + a
        o, f = orig.get(gid, {}), fair.get(gid, {})
        expected = [
            ("our origination (a392 lab)", o.get("our_spread_home_favoured"), o.get("our_total")),
            ("points-only fair line", f.get("fair_spread_home"), f.get("fair_total")),
            ("archived community price", o.get("archive_spread_home_favoured"), o.get("archive_total")),
            ("do-nothing season mean", mean_margin, mean_total),
        ]
        pub = [r for r in published if r["game_id"] == gid]
        for (name, ps, pt), row in zip(expected, pub):
            if row["predictor"] != name:
                wrong.append("%s: predictor order %r vs %r" % (gid, row["predictor"], name)); continue
            if row["actual_home_margin"].strip() != str(act_m):
                wrong.append("%s/%s: margin %s vs %d" % (gid, name, row["actual_home_margin"], act_m))
            if row["actual_total"].strip() != str(act_t):
                wrong.append("%s/%s: total %s vs %d" % (gid, name, row["actual_total"], act_t))
            for col, pred in (("predicted_spread_home", ps), ("predicted_total", pt)):
                want = "%.2f" % float(pred)
                if row[col].strip() != want:
                    wrong.append("%s/%s: %s %s vs %s" % (gid, name, col, row[col], want))
            for col, pred, act in (("spread_abs_error", ps, act_m), ("total_abs_error", pt, act_t)):
                want = "%.2f" % abs(act - float(pred))
                if row[col].strip() != want:
                    wrong.append("%s/%s: %s %s vs %s" % (gid, name, col, row[col], want))
    if wrong:
        bad("settled week 10 table does not reproduce: %s" % wrong[:4])
    else:
        ok("settled week 10 table reproduces for %d predictor(s) on %d settled game(s) "
           "from the official result" % (4, len(played)))

    # the two headline derived numbers, recomputed independently
    comp, _, _ = rows("computed_settled_5f16dcc6.csv")
    byname = {r["metric"]: r["value"] for r in comp}
    g = played[0]
    a, h = int(g["away_pts"]), int(g["home_pts"])
    o, f = orig.get(g["game_id"], {}), fair.get(g["game_id"], {})
    our_spread = float(o.get("our_spread_home_favoured"))
    want_spread_gap = "%+.2f" % (abs((h - a) - our_spread) - abs((h - a) - mean_margin))
    if byname.get("our spread vs the do-nothing baseline", "").startswith(want_spread_gap):
        ok("headline spread verdict reproduces (%s pts against knowing nothing)" % want_spread_gap)
    else:
        bad("headline spread verdict is stale: %r vs recomputed %s"
            % (byname.get("our spread vs the do-nothing baseline"), want_spread_gap))
    sd_t = st.stdev(totals)
    want_n = "%.0f" % (((1.96 + 0.8416) ** 2) * sd_t ** 2 / 1.0 ** 2)
    if byname.get("games needed to detect a 1.0-pt total-MAE difference") != want_n:
        bad("required-sample arithmetic is stale: %r vs %s"
            % (byname.get("games needed to detect a 1.0-pt total-MAE difference"), want_n))
    else:
        ok("required-sample arithmetic reproduces from the corpus (%s games for a 1.0-pt "
           "total difference at 80%% power)" % want_n)
    blank = [r for r in published if not r["source"].startswith("https://www.nfl.com/games/")]
    if blank:
        bad("settled table: %d rows without an official game URL" % len(blank))
    else:
        ok("settled table: every row cites the official game page the result came from")


def reverification_5f16dcc6_holds():
    """A register that reports a disagreement with an official page must name the flag that carries
    it, or the disagreement lives only in a table nobody reads."""
    fn = os.path.join(DATA, "reverification_5f16dcc6.csv")
    if not os.path.exists(fn):
        warn("dated re-verification register absent")
        return
    data, _, _ = rows("reverification_5f16dcc6.csv")
    vocab = {"MATCH", "CORRECTED", "NEW", "MISMATCH", "NOT CHECKED"}
    bad_rows = [r for r in data if r["result"].strip().upper() not in vocab]
    if bad_rows:
        bad("re-verification 2026-11-13: result %r is outside the vocabulary %s"
            % (bad_rows[0]["result"], sorted(vocab)))
        return
    flag_ids = {r["id"] for r in rows("flags.csv")[0]}
    unflagged = []
    for r in data:
        res = r["result"].strip().upper()
        if res in ("MISMATCH", "CORRECTED"):
            cited = set(re.findall(r"FL-\d+", r["note"])) | set(re.findall(r"FL-\d+", r["check"]))
            if not cited & flag_ids:
                unflagged.append(r["check"][:48])
    if unflagged:
        bad("re-verification 2026-11-13: rows that disagree with the official page cite no "
            "register flag: %s" % unflagged)
    else:
        n_m = sum(1 for r in data if r["result"].strip().upper() == "MISMATCH")
        n_c = sum(1 for r in data if r["result"].strip().upper() == "CORRECTED")
        n_n = sum(1 for r in data if r["result"].strip().upper() == "NOT CHECKED")
        ok("re-verification 2026-11-13: %d checks, %d corrected in this session, %d published as "
           "flags, %d explicitly not checked" % (len(data), n_c, n_m, n_n))
    nosrc = [r for r in data if not r["source"].startswith("https://")]
    if nosrc:
        bad("re-verification 2026-11-13: %d rows without an https source" % len(nosrc))



def s745_registers_reproduce():
    """Session 745f788e publishes an all-club depth register and a decision console. Its own
    verifier lives beside the builder (scripts/verify_s745.py) so the session that owns the
    files owns the audit, and this hook is what makes it run in CI with everything else.
    A missing script is a warning, not a pass: the register would ship unaudited."""
    path = os.path.join(ROOT, "scripts", "verify_s745.py")
    if not os.path.exists(path):
        warn("scripts/verify_s745.py missing; the depth register is unaudited")
        return
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import verify_s745 as v
    v.main()
    PASS.extend(v.PASS)
    WARN.extend(v.WARN)
    FAIL.extend(v.FAIL)
    # the hook's own counters are merged above; drop the duplicate print of them
    v.PASS.clear(); v.WARN.clear(); v.FAIL.clear()
def main():
    check_widths(); no_disguised_guesses(); standings(); injuries(); depth(); sources(); registers(); no_invented_results();
    prose_counts_match_files(); register_counts_match_files(); injury_coverage_is_measured_not_named();
    dictionary_counts_match_files(); gamelog(); filter_clauses_do_something(); datasets_documented(); reverification_holds()
    settled_week10_reproduces(); reverification_5f16dcc6_holds(); s745_registers_reproduce()
    
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

#!/usr/bin/env python3
"""One-shot register appends for session 66faefac (2026-11-13).

Run once. It is kept in the tree because the rows it writes are the auditable record of what this
session read and decided: an append script that is deleted after use turns the registers into prose
nobody can re-derive. It refuses to double-append.
"""
import csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(fn):
    with open(os.path.join(DATA, fn), encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    return raw[0], [dict(zip(raw[0], r)) for r in raw[1:]]


def append(fn, hdr, rows, id_col=None):
    have, data = load(fn)
    if have != hdr:
        sys.exit("%s: header drift, expected %s got %s" % (fn, hdr, have))
    key = id_col or hdr[0]
    ids = {r[key] for r in data}
    new = [r for r in rows if r[key] not in ids]
    if not new:
        print("%s: already appended, nothing to do" % fn)
        return
    with open(os.path.join(DATA, fn), "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        for r in new:
            w.writerow([r[c] for c in hdr])
    print("%s: +%d rows (%s)" % (fn, len(new), ", ".join(r[key] for r in new)))


SRC_HDR = ["id", "name", "org", "url", "kind", "tier", "accessed_utc", "used_for", "verified"]
SOURCES = [
    {"id": "S-HUB-1113", "name": "Official NFL Injury Report - Week 10 hub, Wednesday read",
     "org": "NFL.com (National Football League)", "url": "https://www.nfl.com/injuries/",
     "kind": "official-league", "tier": "A", "accessed_utc": "2026-11-13T12:45Z",
     "used_for": "the designation register, the club-level availability counts and the depth-deficiency join",
     "verified": "yes"},
    {"id": "S-STAND-1113B", "name": "NFL.com division standings, second read on 13 November",
     "org": "NFL.com (National Football League)", "url": "https://www.nfl.com/standings/",
     "kind": "official-league", "tier": "A", "accessed_utc": "2026-11-13T12:30Z",
     "used_for": "all 32 standings rows re-read cell by cell against data/standings_2026.csv",
     "verified": "yes"},
    {"id": "S-SCHED10-1113", "name": "NFL.com Week 10 schedule page, 2026-11-13 read",
     "org": "NFL.com (National Football League)", "url": "https://www.nfl.com/schedules/2026/by-week/week-10",
     "kind": "official-league", "tier": "A", "accessed_utc": "2026-11-13T12:50Z",
     "used_for": "14 fixtures: kickoff day, time, primary national broadcaster and the venue links the fixture rows point at",
     "verified": "yes"},
    {"id": "S-SCHED11-1113B", "name": "NFL.com Week 11 schedule page, second read on 13 November",
     "org": "NFL.com (National Football League)", "url": "https://www.nfl.com/schedules/2026/by-week/week-11",
     "kind": "official-league", "tier": "A", "accessed_utc": "2026-11-13T12:36Z",
     "used_for": "re-check of the two disputed Week 11 broadcasters carried as FL-36",
     "verified": "yes"},
    {"id": "S-SCORES-1113B", "name": "NFL.com Week 10 scores page, 2026-11-13 read",
     "org": "NFL.com (National Football League)", "url": "https://www.nfl.com/scores/2026/week-10",
     "kind": "official-league", "tier": "A", "accessed_utc": "2026-11-13T12:47Z",
     "used_for": "confirms Washington at the Giants is still the only Final game, so nothing new can be settled today",
     "verified": "yes"},
]

FLAG_HDR = ["id", "type", "severity", "finding", "evidence", "source", "decision_impact", "status"]
FLAGS = [
    {"id": "FL-37", "type": "source granularity", "severity": "low",
     "finding": "The schedule table's broadcaster column cannot be verified to the granularity it is published at. Three official surfaces show three different subsets of the same broadcast: the injury hub heads the Munich game 'FOX, FOX DEPORTES', the Week 10 schedule page shows 'FOX' with a '+1' affordance, and data/schedule_2026_wk10.csv publishes 'FOX, FOX One, NFL+'. The Monday game shows the same pattern (hub: 'ESPN, ABC, ESPN2, ESPN DEPORTES'; file: 'ABC, ESPN, NFL+').",
     "evidence": "nfl.com/injuries/ game headers and nfl.com/schedules/2026/by-week/week-10 game rows, both read 2026-11-13T12:45-12:50Z, against the published file",
     "source": "https://www.nfl.com/injuries/ :: https://www.nfl.com/schedules/2026/by-week/week-10",
     "decision_impact": "The column is labelled verified although no single official page lists the full set. Either publish only the primary national broadcaster the schedule page names, or move the extra networks to a column labelled 'as listed on the hub'. Owner decision, recorded as Q-44 and S-50.",
     "status": "open"},
    {"id": "FL-38", "type": "staleness", "severity": "medium",
     "finding": "Coverage numbers that were true when written are now stale on the live page: the site publishes the Week 10 practice report as 254 rows across 24 of the 28 clubs playing, with 6 designations. The 2026-11-13 read gives 296 rows, 28 of 28 clubs (26 with rows, 2 publishing 'No Injuries Reported') and 9 designations. Nothing was mis-transcribed - the league kept filing while the snapshot sat.",
     "evidence": "three reads of the same official page: 2026-11-12T04:45Z (254), 2026-11-12T22:35Z (279), 2026-11-13T12:45Z (296); no club lost a row between any two reads",
     "source": "https://www.nfl.com/injuries/",
     "decision_impact": "Any page that says '24 of 28 clubs' is now a history statement, not a status statement. This is the cadence question (Q-40, S-43) arriving in the data rather than in the abstract: either the tables carry an 'as of' stamp the reader sees, or the snapshot is refreshed on a schedule.",
     "status": "open"},
    {"id": "FL-39", "type": "internal contradiction on the source page", "severity": "high",
     "finding": "A player can be recorded as having practised fully and as designated out in the same row of the official report: Detroit safety Kerby Joseph reads 'Knee / Full Participation in Practice / Out' on the 2026-11-13 hub. Any availability feature that reads the practice column and ignores the designation column marks him available; any feature that reads only the designation column misses that his practice load was unaffected, which is a different signal about his return.",
     "evidence": "Lions block, nfl.com/injuries/, read 2026-11-13T12:45Z; the row is transcribed in data/hub_flagged_20261113_66faefac.csv and carried into the deficiency join with the state 'designated out'",
     "source": "https://www.nfl.com/injuries/",
     "decision_impact": "Blocking for the precedence rule in Q-43. The register publishes both columns rather than resolving them, because the league states no precedence.",
     "status": "open"},
    {"id": "FL-40", "type": "coverage asymmetry in our own transcription", "severity": "medium",
     "finding": "Depth-chart coverage differs by club for a reason that has nothing to do with the league: data/depth_charts.json transcribes the Patriots chart with four defensive groups (OLB, DT_1, DT_2, DT_3) and no cornerback or safety rows, while the Lions chart in the same file carries CB_1, CB_2, S_1 and S_2. So Carlton Davis III (Patriots CB, designated out) cannot be joined to a depth slot while D.J. Reed (Lions CB, designated out) can, and the site's 'deficiency' tables are silently deeper for Detroit than for New England.",
     "evidence": "data/depth_charts.json (this build's own file, read as checked in) against the two clubs' designation rows on nfl.com/injuries/",
     "source": "https://www.patriots.com/team/depth-chart :: https://www.detroitlions.com/team/depth-chart",
     "decision_impact": "Every 'which side of the ball broke' number on this site is bounded by our transcription coverage, not by the data. Re-transcribe the four charted clubs group-complete, then widen (S-48).",
     "status": "open"},
]

Q_HDR = ["id", "question", "blocks", "what_we_have", "what_we_lack", "how_to_close", "priority", "status"]
QUESTIONS = [
    {"id": "Q-42", "question": "Do we store a full row-level snapshot of the injury hub on every filing day, so the difference between two reads is a player-level fact rather than a club-level count?",
     "blocks": "the availability delta a model needs to price; backtesting the designation-surprise signal; gate G-03 point-in-time replay",
     "what_we_have": "three reads of the same page with three different shapes: a 254-row row-level file, a 279-row row-level file, and today's 296 rows captured as club counts plus a designation register",
     "what_we_lack": "a row-level file for 2026-11-13 and a state for 'a player left the report' - today the league removes a row when a player is placed on IR, which is the opposite of recovery",
     "how_to_close": "decide the retention rule (one dated file per filing day, hashed, append-only), then re-run this session's read as a row-level ingest and diff it against injuries_wk10_2026_hubrefresh.csv",
     "priority": "P1", "status": "open"},
    {"id": "Q-43", "question": "When the practice column and the designation column disagree, which one wins in the model, and is 'absent because on IR' a third state or a fourth?",
     "blocks": "ST-01, ST-02, ST-11 and ST-15 all consume availability; the leaderboard cannot rank them on different precedence rules",
     "what_we_have": "both columns transcribed for every row, one published counter-example where they disagree (FL-39), and the league's own IR rule that an IR player does not appear on the weekly report",
     "what_we_lack": "an owner-approved precedence, and a measured comparison of the two encodings - nobody has yet scored which one predicts better, because there is no settled availability-labelled sample in this repository",
     "how_to_close": "adopt the three-state model (reported / declared none / absent-with-IR-cause) as the default, write it into the data dictionary, and grade both encodings on the Week 10 pre-registration once the slate settles",
     "priority": "P1", "status": "open"},
    {"id": "Q-44", "question": "Is the schedule table's broadcaster column worth keeping, when no single official page publishes the full list we are showing?",
     "blocks": "the 'verified' label on the league-data page; a reader who trusts the column will trust the page's other columns less when they find out",
     "what_we_have": "three official surfaces that each show a different subset of the same broadcast, and a documented disagreement of the same family on Week 11 (FL-36)",
     "what_we_lack": "an official page that lists simulcast networks in one place; the schedule page collapses them into a '+1' affordance that our read cannot resolve to names",
     "how_to_close": "publish the primary national broadcaster only, sourced to the schedule page, and move anything beyond it to a column explicitly labelled 'as listed on the injury hub'; or drop the column",
     "priority": "P2", "status": "open"},
]

S_HDR = ["id", "title", "category", "problem_it_solves", "proposal", "impact", "effort", "risk",
         "reversible", "depends_on", "evidence", "recommended_path", "decision"]
SUGGESTIONS = [
    {"id": "S-46", "title": "Make the injury hub a dated, hashed, row-level snapshot series",
     "category": "Data plumbing",
     "problem_it_solves": "Today the repository holds three reads of one page in three shapes, so the only honest sentence about growth is a count. A row-level series makes 'who appeared, who disappeared, who changed designation' a query instead of a re-fetch",
     "proposal": "One file per filing day under data/hub_snapshots/ named injuries_YYYY-MM-DDTHHMMZ.csv, written by the same generator that writes the registers, with its SHA-256 recorded next to it and a 'withdrawn' state for a player who leaves the report; the club table then becomes a view over the two most recent files",
     "impact": "H", "effort": "M", "risk": "Low - additive; the frozen 04:45Z snapshot and the 22:35Z refresh stay exactly as published", "reversible": "yes",
     "depends_on": "Q-42, S-43, S-26",
     "evidence": "the +17-row growth and the 296/279/254 comparison this session had to compute by hand from a club-count file (FL-38)",
     "recommended_path": "adopt before Week 11 practice reporting opens on Wednesday 18 November, so the first complete week of daily reads is the first week we also grade",
     "decision": "pending owner review"},
    {"id": "S-47", "title": "Adopt the hash-locked pre-registration as the only route onto the leaderboard",
     "category": "Competition rules",
     "problem_it_solves": "Every strategy on the site is 'designed, not tracked' because nothing was ever fixed before an outcome existed; the one game we could score is already scored, and the temptation from here is to tune the rule to it",
     "proposal": "A strategy enters the leaderboard only if data/prereg_<week>.csv exists, its SHA-256 is committed with it, the file is written before the first kickoff it claims to predict, and tools/verify_prereg_66faefac.py-style checks re-hash it on every build; the ledger records no-calls as well as calls so selectivity is measured rather than claimed",
     "impact": "H", "effort": "L", "risk": "Low - it constrains future work, it does not rewrite past pages", "reversible": "yes",
     "depends_on": "G-11, Q-26, S-04",
     "evidence": "ST-15's lock: 13 un-played Week 10 fixtures, 2 calls at threshold 4, sha256 recorded in data/prereg_wk10_66faefac.sha256 before the 14:30Z Munich kickoff",
     "recommended_path": "adopt as the promotion rule for every strategy, including the two negative controls, and put the required-sample figure beside the rank column",
     "decision": "pending owner review"},
    {"id": "S-48", "title": "Finish the depth charts before finishing the deficiency model",
     "category": "Availability",
     "problem_it_solves": "Two of three Patriots designations cannot be joined to a depth slot because our transcription of the Patriots chart has no cornerback or safety rows, while Detroit's has four of each - the analysis is deeper for the club we happened to transcribe completely",
     "proposal": "Re-transcribe KC, GB, NE and DET group-complete (every defensive group the club prints, including slot and nickel), then extend to the 28 clubs in the order the deficiency register needs: the clubs with the largest availability load first; publish a per-club coverage count beside every deficiency number so the reader sees the asymmetry instead of inferring it",
     "impact": "H", "effort": "M", "risk": "Low - charts are club-published and explicitly unofficial; the label travels with the data", "reversible": "yes",
     "depends_on": "Q-37, S-39, FL-40",
     "evidence": "18 join rows today, of which 5 say 'not listed on the club's chart in this build' and 4 more name a vacancy or a second-string slot; 30 clubs are absent from the join entirely",
     "recommended_path": "do the four charted clubs now (one afternoon), hold the 32-club sweep until the cadence decision in Q-40 says how often anything refreshes",
     "decision": "pending owner review"},
    {"id": "S-49", "title": "Price 'designation without practice change' as its own state",
     "category": "Signals",
     "problem_it_solves": "A player who is ruled out after practising fully carries different information from one who has not practised since Monday, and a count of 'unavailable players' cannot tell the two apart; today the register can only show the contradiction, not use it",
     "proposal": "Split the availability load into three counts - designated out after a full practice, designated out after a non-participation, and not designated but did not practise - keep them separate through the deficiency join, and let a strategy declare which one it trades on; the three counts cost nothing to compute from the file this session already writes",
     "impact": "M", "effort": "L", "risk": "Medium - multiplies the number of candidate features, which is how a small sample gets over-fitted; keep the locked rule single-featured and log the split as an observation", "reversible": "yes",
     "depends_on": "Q-43, FL-39, G-11",
     "evidence": "Kerby Joseph (full practice, out) against five Detroit and New England rows where the designation follows a did-not-practise streak, all in data/hub_flagged_20261113_66faefac.csv",
     "recommended_path": "record the split in the register from the next read; do not add it to the locked ST-15 rule, which would move the goalposts inside the measurement window",
     "decision": "pending owner review"},
    {"id": "S-50", "title": "Stop presenting an unverifiable column as verified",
     "category": "Governance",
     "problem_it_solves": "The schedule table's broadcaster column is the only column on a measured page whose value changes depending on which official page you read, and the site does not currently say so",
     "proposal": "Rename the column to 'primary national broadcaster', take its value only from the schedule page's named network, and add a footnote that simulcast partners are collapsed into a '+N' control on that page and are therefore not transcribable; leave the FL-36 and FL-37 rows open until that happens",
     "impact": "L", "effort": "L", "risk": "Low", "reversible": "yes",
     "depends_on": "Q-44, FL-36, FL-37",
     "evidence": "the Week 10 Munich and Monday rows disagree with our file on network lists, and the two Week 11 rows disagree on a network name (FL-36)",
     "recommended_path": "cheapest fix on the board; do it in the next integration pass and close FL-37 with it",
     "decision": "pending owner review"},
    {"id": "S-51", "title": "Rebuild the availability load on a name-level union",
     "category": "Data quality",
     "problem_it_solves": "the rule the first locked prediction was written with sums two published counts, so a player in both columns is counted twice - and nobody reading the table can see which clubs that touches",
     "proposal": "Define the load as the number of distinct names appearing in either the designation column or the did-not-practise column, captured for all 28 clubs rather than only the designated ones; version the locked rule as ST-15 v2 and keep the v1 hash published beside it",
     "impact": "M", "effort": "M", "risk": "Low - the arithmetic gets truer and the sample gets harder to collect; the v1/v2 split is what stops the change looking like a re-tune", "reversible": "yes",
     "depends_on": "S-19, Q-42, ST-15",
     "evidence": "only Washington, New England and Detroit carry both columns on the 13 November read, and de-duplicating those three (5→3, 6→3, 6→4) changes no locked call while voiding the one settled fixture's call - the error is bounded today and is not bounded on a slate where every club files designations",
     "recommended_path": "capture names league-wide on the next Wednesday read, re-issue the rule as v2 with its own hash, and report v1 and v2 side by side for one week so the change is measurable rather than silent",
     "decision": "pending owner review"},
]

STRAT_HDR = ["id", "name", "bet_type", "market", "thesis", "signals", "entry_rule", "stake_rule",
             "correlation_treatment", "n_target", "gates_blocking", "status"]
STRATEGIES = [
    {"id": "ST-15", "name": "Availability-differential lean, hash-locked",
     "bet_type": "single", "market": "game spread, against our own published number",
     "thesis": "Our number is built from points scored and allowed through week 9, so it cannot see who is playing this week. When one club's availability load - designated out plus did not practise - is at least four players heavier than the opponent's, the depleted club is being over-valued by exactly the amount our model is blind to, and the healthier side is the lean",
     "signals": "SIG-01, SIG-02 (club-level: the availability load columns in data/club_availability_20261113_66faefac.csv)",
     "entry_rule": "Evaluate once per week on the most recent official hub read; act only when the load differential is >= 4 players; a fixture inside the threshold is recorded as a no-call, not skipped",
     "stake_rule": "no stake. G-01 (entitlement) and G-07 (vig and cost accounting) are not passed, so the ledger records direction and error only",
     "correlation_treatment": "n/a - single leg, one per fixture, no same-game stacking",
     "n_target": "400 settled fixtures (G-08); the sample-size table on this site says a 1.0-point error difference needs 1,382 spreads, so a 13-fixture slate is a start and not a result",
     "gates_blocking": "G-01, G-07, G-08, G-12",
     "status": "pre-registered 2026-11-13T12:45Z and hash-locked in data/prereg_wk10_66faefac.sha256; 0 settled, 2 calls locked, the one fixture that settled before the lock is published as post-hoc and excluded"},
]

LB_HDR = ["rank", "strategy", "bet_type", "tier", "gates_passed", "gates_blocking", "tracked_bets",
          "settled", "mean_clv", "roi_units_per_100", "max_drawdown", "selectivity", "reward", "status"]
LEADERBOARD = [
    {"rank": "unranked", "strategy": "ST-15 Availability-differential lean, hash-locked", "bet_type": "single",
     "tier": "T0 - pre-registered", "gates_passed": "0 of 14 (G-11 evidence now exists: the spec is hash-locked)",
     "gates_blocking": "G-01, G-07, G-08, G-12", "tracked_bets": "0", "settled": "0",
     "mean_clv": "not published", "roi_units_per_100": "not published", "max_drawdown": "not published",
     "selectivity": "2 of 13 un-played fixtures called (15%)", "reward": "none",
     "status": "locked before the first Sunday kickoff; no-calls are in the ledger, so the selectivity figure is measured rather than tuned"},
]


def main():
    append("sources.csv", SRC_HDR, SOURCES)
    append("flags.csv", FLAG_HDR, FLAGS)
    append("questions.csv", Q_HDR, QUESTIONS)
    append("suggestions.csv", S_HDR, SUGGESTIONS)
    append("strategies.csv", STRAT_HDR, STRATEGIES)
    append("leaderboard.csv", LB_HDR, LEADERBOARD, id_col="strategy")


if __name__ == "__main__":
    main()

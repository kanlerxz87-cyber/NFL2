#!/usr/bin/env python3
"""Build the brief-backlog register for session 58e9c708.

The owner's full brief contains a line-item backlog of 70 directives that the shared
requirements register (``data/requirements.csv``) does not track. This module is the
durable copy: it is the only place those 70 lines are written down, and it is what
``content/backlog.md`` renders.

Rules this module obeys, because the rest of the site obeys them:

* every directive is transcribed from the brief, not paraphrased into something easier;
* every row names the official page that would have to be read to satisfy it, and that
  page is a real URL, never a placeholder;
* the ``verified_2026_11_15`` column says exactly what was re-read on 15 November 2026
  and what was not. "not re-read today" is a real value and is not a claim;
* a directive the brief itself rejects is recorded with kind ``rejected`` and status
  ``rejected`` so it cannot be re-proposed later as if it were open;
* gate references use only the 14 ids in ``data/gates.csv``.

Run:  python3 tools/build_backlog_58e9c708.py
"""
from __future__ import annotations

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

INJ = "https://www.nfl.com/injuries/"
SCORES10 = "https://www.nfl.com/scores/2026/week-10"
SCHED11 = "https://www.nfl.com/schedules/2026/by-week/week-11"
SCHED = "https://www.nfl.com/schedules/2026/REG/"
TXN = "https://www.nfl.com/transactions/"
RESERVE = "https://www.nfl.com/transactions/league/reserve-list/2026/11"
TRADES = "https://www.nfl.com/transactions/league/trades/2026/11"
STAND = "https://www.nfl.com/standings/"
OPS = "https://operations.nfl.com/"
GB = "https://www.packers.com/team/depth-chart"
HOU = "https://www.houstontexans.com/team/depth-chart"
SEA = "https://www.seahawks.com/team/depth-chart/"
WAS = "https://www.commanders.com/team/depth-chart"
BAL = "https://www.baltimoreravens.com/team/depth-chart"
GAMEBOOK = ("https://static.www.nfl.com/image/upload/v1789038923/gamecenter/"
            "a8fb0d78-4feb-11f1-abca-2c54536568a9.pdf")
NWS = "https://www.weather.gov/"
GAMECENTRE = "https://www.nfl.com/games/commanders-at-giants-2026-reg-10"

READ = "re-read 2026-11-15"
NOTREAD = "not re-read today"
NONE = "no official source exists"

HEADER = ["id", "brief_code", "directive", "theme", "kind", "status",
          "blocks", "clears_with", "dependency", "verified_2026_11_15",
          "evidence_in_repo", "note"]

# (brief_code, directive, theme, kind, status, blocks, clears_with, dependency,
#  verified, evidence_in_repo, note)
ITEMS = [
    ("", "Add a price-snapshot store that records opening and closing numbers for every market we originate",
     "Prices", "backlog", "blocked", "G-01, G-07",
     "Every originated market carries at least one opening and one closing price row, each with a capture timestamp and a source id; zero markets with a price but no vintage",
     OPS, NONE,
     "data/price_archive_a392.csv",
     "The league publishes no betting lines, so the store cannot be filled from an official source. Every price file in the register is a community archive with no vintage."),

    ("", "Add a verified results feed so backtests and ROI can be computed at all",
     "Results", "backlog", "partial", "G-03, G-04",
     "One immutable result row per game carrying the official game-centre URL and a capture time, replayable for every week in the sample",
     SCORES10, READ,
     "data/games_2026_wk1_9.csv, data/games_2026_wk10_played.csv",
     "Official scores page re-read today: W10-01 Commanders 24 Giants 21 is Final; the other 13 Week 10 fixtures show kickoff times only. 136 weeks 1-9 results plus one Week 10 result, all hand-read, no scheduled capture."),

    ("", "Originate the side first, then the total, then the moneyline",
     "Origination", "backlog", "partial", "G-06",
     "All three markets published per fixture in that order, or a stated reason why a market is withheld",
     SCHED11, READ,
     "data/originated_lines_wk11_0a113a24.csv, data/computed_fair_lines.csv",
     "Week 10 and Week 11 files publish a spread and a total. No moneyline is derived, so the third market in the brief's ordering does not exist yet."),

    ("", "Publish the model's fair line, the market line, and the difference as separate columns",
     "Origination", "backlog", "partial", "G-06, G-07",
     "Three separate columns per market per fixture, with the difference column never left to the reader to subtract",
     SCHED11, READ,
     "data/originated_lines_wk11_0a113a24.csv, data/computed_fair_lines.csv",
     "Week 11 carries spread_gap_vs_archive and total_gap_vs_archive as explicit difference columns. computed_fair_lines.csv publishes a fair line with no market line beside it."),

    ("", "Separate signal from staking in the leaderboard so a lucky staking run cannot mask a bad signal",
     "Leaderboard", "backlog", "specified", "G-12, G-14",
     "Two ranked columns per entry, signal skill and staking outcome, published so that neither can be read without the other",
     SCHED, NOTREAD,
     "data/leaderboard.csv, data/strategies.csv",
     "The leaderboard has one populated row, the do-nothing control, and every performance cell is not published. The split is a design change with nothing yet to split."),

    ("", "Track the depth of the replacement, not just the fact of a replacement",
     "Depth", "backlog", "partial", "G-02, G-03",
     "Every replacement row names the string reached (1st through 4th) and the number of players skipped, with the club page cited",
     GB, READ,
     "data/s745_depth_deficiencies.csv, data/depth_cascade_verdicts_6539b6a0.csv",
     "Depth reached and chain length are published for the clubs whose charts were transcribed. Packers chart re-read today confirms the club prints four strings per unit, so the data to count depth exists on the official page."),

    ("", "Compute correlations only from officially sourced numbers and publish n with each value",
     "Correlation", "backlog", "partial", "—",
     "Every published correlation carries its n, its interval and the official file it was computed from; zero rows with an asserted magnitude",
     SCORES10, READ,
     "data/measured_correlations_a392.csv, data/computed_correlation.csv",
     "Both correlation registers publish n with each value. Every measured interval spans zero, so no magnitude is claimed. The dependency page is the official source of the 136-game corpus."),

    ("", "Define a demotion gate that sends a live strategy back to paper",
     "Governance", "backlog", "not started", "G-08, G-12",
     "A written threshold, registered before any strategy goes live, that returns an entry to paper when breached",
     SCHED, NOTREAD,
     "data/gates.csv",
     "The gate register defines 12 hard and 2 soft gates, all of them promotion gates. Nothing in it moves an entry back down."),

    ("", "Pre-register every strategy and forbid backtest numbers from ever appearing on the leaderboard",
     "Governance", "backlog", "partial", "G-11",
     "Every entry carries a registration hash recorded before its first tracked bet; zero backtest-derived cells on the leaderboard",
     SCHED11, READ,
     "data/prereg_wk10_66faefac.csv, data/prereg_week11_0a113a24.csv, data/leaderboard.csv",
     "Week 10 and Week 11 lines are hash-locked before kickoff and the leaderboard publishes no backtest number. Coverage is two weeks, not every strategy."),

    ("", "Build the availability graph as a first-class dataset: who was expected to start, who actually did",
     "Availability", "backlog", "not started", "G-02, G-03",
     "One row per club-position per game with an expected starter, a confirmed starter and the official document that confirms each",
     GAMEBOOK, NOTREAD,
     "data/availability_deficiency_66faefac.csv",
     "No confirmed-starter column exists anywhere in the repo. The official Game Book is the document that would supply it, and only two 2026 Game Books are registered."),

    ("", "Do not model depth from jersey order; model it from playing time",
     "Depth", "adopted-rule", "done", "—",
     "Zero depth slots in the repository inferred from jersey number, experience or salary; every slot transcribed from a published document",
     GB, READ,
     "data/s745_depth_charts.csv",
     "Held. The Packers chart re-read today prints jersey numbers ahead of names, which is exactly the trap this rule forbids; the register stores the raw string rather than reading an order from it."),

    ("", "Make the injury signal a surprise, never a level",
     "Availability", "backlog", "partial", "G-03",
     "Every availability feature entering a model is a difference between two dated reads, never a single read's level",
     INJ, READ,
     "data/injury_delta_a392.csv, data/availability_watch_practice_deltas_c3ec1487.csv",
     "Delta files exist for two reads. A surprise needs a timestamped series, which is a separate item on this register, so the feature is designed but not fed."),

    ("", "Run the 32-team roster and IR sweep before any team-level model is trusted",
     "Availability", "backlog", "not started", "G-02",
     "All 32 clubs present in the roster and reserve read for the week, with any club that cannot be read named rather than assumed empty",
     RESERVE, READ,
     "data/depth_changes_2026_wk10.csv",
     "No roster or IR sweep file exists. The official reserve list read today is league-wide and dated, which is the source such a sweep would use."),

    ("", "Add a fixture-context feature set built only from published schedule facts",
     "Origination", "backlog", "not started", "G-01, G-03",
     "A named feature set whose every column is a field the official schedule page publishes, with the page cited per column",
     SCHED11, READ,
     "data/schedule_2026_wk10.csv, data/schedule_week11_2026.csv",
     "The Week 10 schedule carries date, kickoff, venue and broadcast. The Week 11 file carries site as not published, so the same feature set is not yet buildable for the live week."),

    ("", "Store every model output as a probability plus its inputs, not just a pick",
     "Modelling", "backlog", "not started", "G-04, G-06",
     "Every published model row carries the probability, the input vector and the spec hash that produced it",
     SCHED11, READ,
     "data/originated_lines_wk11_0a113a24.csv",
     "Week 11 publishes ratings inputs beside the line but no probability. No calibration is possible without the probability column."),

    ("", "Compute and publish the removal-of-luck panel on the site dashboard",
     "Luck", "backlog", "partial", "G-08",
     "A dashboard panel that separates the part of each result attributable to the model from the part attributable to variance, with the split recomputed every build",
     STAND, NOTREAD,
     "data/computed_luck.csv, data/s2268_luck.csv",
     "Two luck files exist and the skill-vs-luck page publishes them. The landing page carries no luck removal panel."),

    ("", "Add a two-sided what-would-change-our-mind field to every strategy entry",
     "Governance", "backlog", "not started", "G-11",
     "Every registered strategy names in advance both the result that would confirm it and the result that would kill it",
     SCHED, NOTREAD,
     "data/strategies.csv",
     "The strategy register has a thesis and an entry rule but no falsification field in either direction."),

    ("", "Price a line ourselves and publish the residual against the market, on a schedule, from day one",
     "Origination", "backlog", "partial", "G-06, G-07",
     "A residual published on a fixed weekly schedule for every fixture, from the first week the model runs, with the schedule itself published",
     SCHED11, READ,
     "data/originated_lines_wk11_0a113a24.csv, data/price_archive_a392.csv",
     "Two weeks of residuals exist. There is no published schedule and no licensed market price, so the residual is measured against a community archive."),

    ("", "Turn the 136-game log into the pre-registered backtest corpus",
     "Results", "backlog", "partial", "G-03, G-10",
     "The weeks 1-9 corpus frozen with a hash, split into train, validation and final holdout, and the split published before any result is read from it",
     SCORES10, READ,
     "data/games_2026_wk1_9.csv, data/s2268_holdout_decisions.csv",
     "The 136 games are transcribed from official pages and a walk-forward holdout has been run on them. The corpus itself is not hash-frozen as a corpus."),

    ("", "Decide the price-data policy before any backtest is published",
     "Prices", "backlog", "not started", "G-01",
     "A written, committed decision on which price sources are entitled to enter the system of record, recorded before any backtest is published",
     OPS, NONE,
     "data/price_archive_a392.csv, data/questions.csv",
     "Owner decision, not a research question. The register holds the inventory that the decision has to rule on and no decision has been recorded."),

    ("", "Store every injury-hub read with its clock time and publish the delta, never the level",
     "Availability", "backlog", "partial", "G-03",
     "Every hub read stored with a UTC clock time, and every published availability number expressed as a delta against the previous read",
     INJ, READ,
     "data/injuries_wk10_83246f00.csv, data/injuries_wk10_e733834d_20261115.csv",
     "Dated reads carry a fetched_utc field. The canonical Week 10 injury table on the site still renders the 12 November read with no timestamp on the page."),

    ("", "Put a decision-readiness table on the landing page: one row per requirement, with the gate that blocks it and the number that would clear it",
     "Governance", "already tracked", "done", "—",
     "One landing-page row per register requirement, carrying status, blocking gate and clearing condition",
     SCHED, NOTREAD,
     "content/index.md, tools/verify_readiness_ac2dd497.py",
     "Already R-46 and marked done. Reproduced here so the brief and the register cannot disagree about whether it was requested."),

    ("", "Transcribe the venue of every fixture from the official game centre and publish it",
     "Venue", "backlog", "partial", "G-01",
     "A venue string for 100 per cent of fixtures on a slate, transcribed from the official game centre rather than from a fixture list",
     SCHED11, READ,
     "data/schedule_2026_wk10.csv, data/schedule_week11_2026.csv, data/computed_fair_lines.csv",
     "Week 10 carries a venue for all 14 fixtures. Week 11 carries site as not published for all of them, although the official Week 11 schedule page re-read today names the stadium for every fixture."),

    ("", "Publish the league's dated schedule announcement beside the live schedule page",
     "Venue", "backlog", "not started", "G-01, G-03",
     "The dated announcement the league published, shown beside the live schedule it produced, with both dates visible",
     SCHED, NOTREAD,
     "data/schedule_2026_wk10.csv",
     "No dated announcement is stored. Only the live schedule page is transcribed, so a change to the schedule would be invisible."),

    ("", "Use official NFL Game Books for actual starters and game-day status; do not infer depth rank or snaps",
     "Availability", "backlog", "not started", "G-02, G-03",
     "Confirmed starters and game-day status read from the official Game Book for every settled game in the sample; zero inferred starters",
     GAMEBOOK, NOTREAD,
     "data/sources.csv (S-GAMEBOOK-NESEA-653B, S-GAMEBOOK-NYGWAS-653B)",
     "Two 2026 Game Books are registered as official tier A. Neither the 136-game corpus nor any settled Week 10 game has a Game Book read attached."),

    ("", "Ingest game-level results to make the ratings opponent-aware",
     "Modelling", "backlog", "not started", "G-06",
     "Ratings fitted with an opponent term, and the in-sample and holdout error published before and after the term is added",
     SCORES10, READ,
     "data/computed_fair_lines.csv, data/s2268_model_coefficients.csv",
     "The published fair line says in its own input note that it applies no opponent adjustment. The official results needed to fit one are in the corpus."),

    ("", "Add injury and personnel ablations instead of fixed penalties",
     "Modelling", "backlog", "not started", "G-06, G-10",
     "The same model fitted with and without the personnel features, with the difference and its uncertainty reported rather than a fixed points penalty",
     INJ, READ,
     "data/strategies.csv",
     "No ablation has been run. The strategy register's personnel strategies assume a effect size that has never been estimated."),

    ("", "Add injury and depth ablations, not fixed penalties, using chronological holdouts",
     "Modelling", "backlog", "not started", "G-06, G-10",
     "Identical models compared with and without verified availability features on a chronological holdout, with the difference and an interval published",
     INJ, READ,
     "data/s2268_holdout_decisions.csv, data/s2268_predictor_correlations.csv",
     "A chronological holdout harness exists and has been run on ten candidates. Availability features have not been ablated through it."),

    ("", "Automate immutable multi-day availability snapshots",
     "Availability", "backlog", "not started", "G-03",
     "Captures taken at least daily with retained hashes, replayable so a practice designation can be read as it was known",
     INJ, READ,
     "data/availability_fingerprints.csv",
     "The fingerprint ledger is header-only with zero captures. The site therefore holds one capture, which cannot support a multi-day replay."),

    ("", "Build immutable official availability snapshots with raw hashes, timestamps and conflict flags",
     "Availability", "backlog", "not started", "G-03, G-04",
     "Injury report, club depth pages and inactive evidence captured with a raw hash, a timestamp and a conflict flag per capture",
     INJ, READ,
     "data/availability_fingerprints.csv",
     "Scheduled metadata-only capture is registered in the workflow list but the ledger holds no rows, so nothing is replayable yet."),

    ("", "Capture official inactive lists and snap counts",
     "Availability", "backlog", "not started", "G-02, G-03",
     "The official inactive list and snap share captured per game, so a backup's replacement of a starter can be confirmed rather than suspected",
     GAMEBOOK, NOTREAD,
     "data/injuries_wk10_83246f00.csv",
     "Six of 254 report rows carry a game designation and no active list or snap share is captured anywhere. Nothing in the repo can confirm a replacement actually took the snaps."),

    ("", "Fix the two depth-parsing failures before widening coverage",
     "Depth", "backlog", "in progress", "G-02",
     "Both failing clubs parsed or formally declared unparseable, before any new club is added to the register",
     GB, READ,
     "data/s745_depth_summary.csv",
     "Packers: re-read today, the club prepends jersey numbers and the site's raw-string rule already covers it. Texans: re-read today, the club publishes the chart as an image with no HTML table, so no amount of parsing recovers it."),

    ("", "Model depth slots as groups, not a single starter",
     "Depth", "backlog", "partial", "G-02",
     "Every slot that a club prints with more than one rank-1 player stored as a group, never resolved to a single starter",
     GB, READ,
     "data/s745_depth_charts.csv",
     "149 club, unit and position slots list more than one rank-1 player. The register stores both names at that depth, so the group is represented."),

    ("", "Treat roster turnover as a first-class data event",
     "Depth", "backlog", "not started", "G-02, G-03",
     "Depth, availability and lineup evidence versioned against the last official roster event, with the event dated",
     TRADES, READ,
     "data/depth_changes_2026_wk10.csv",
     "Official trades page re-read today confirms the two Colts receiver trades dated 11/10 that the brief cites: Keenan Allen to San Francisco and Josh Downs to Kansas City. No versioning against roster events exists."),

    ("", "Start with a singles-only shadow baseline",
     "Leaderboard", "backlog", "partial", "G-08, G-11",
     "A simple pre-registered team-strength model recording forecasts before kickoff on singles only, with versions frozen",
     SCHED11, READ,
     "data/prereg_week11_0a113a24.csv, data/originated_lines_wk11_0a113a24.csv",
     "Week 11 is pre-registered and singles-only. Versions are frozen week by week but no shadow baseline runs unattended."),

    ("", "Keep parlays and prop combos behind a joint-evidence gate",
     "Leaderboard", "backlog", "not started", "G-05, G-06",
     "A combo ranked only when a directly validated joint probability and the operator's void and push rules are both available",
     SCHED, NOTREAD,
     "data/computed_parlays.csv, data/strategies.csv (ST-06 to ST-10)",
     "Five parlay and combo strategies are designed. Every joint probability in the correlation register is unverified, so none may be ranked."),

    ("", "Use proper-score leaderboard divisions",
     "Leaderboard", "backlog", "not started", "G-06, G-12",
     "Separate divisions for singles, game parlays, same-game parlays and prop combos, each ranked by benchmark-relative skill with uncertainty",
     SCHED, NOTREAD,
     "data/leaderboard.csv",
     "The leaderboard is a single flat table with a bet-type column, not divisions, and it ranks nothing."),

    ("", "Rank with proper scores and uncertainty, not win rate",
     "Leaderboard", "backlog", "not started", "G-06, G-08, G-12",
     "Ranking by benchmark-relative Brier skill with a game-cluster lower bound and a multiplicity adjustment for the number of trials",
     SCORES10, READ,
     "data/s2268_forecast_scores.csv, data/s2268_pick_scores.csv",
     "Proper-score scoring exists in the 2268bfb2 tree and has been run on 596 decisions. It is not the ranking method of the canonical leaderboard."),

    ("", "Add durable snapshot storage and alerts",
     "Governance", "backlog", "not started", "G-04",
     "Immutable captures stored outside the static site, with freshness monitored and an alert raised on a source or schema change",
     INJ, READ,
     "data/availability_fingerprints.csv",
     "No capture store exists outside the repository. Every capture in the repo is a committed CSV with no retention policy behind it."),

    ("", "Split the site into a public analysis layer and a private data layer",
     "Governance", "backlog", "not started", "G-01",
     "Public pages carry derived analysis and links to the official page only; raw row-level data held privately until the terms are read",
     INJ, READ,
     "content/index.md, data/price_archive_a392.csv",
     "The site publishes raw row-level transcriptions of official pages on public pages. The terms question is registered and unanswered."),

    ("", "Add a per-team view: starters out, replacements named, net injury count",
     "Depth", "backlog", "partial", "G-02, G-03",
     "One row per club per week with the starters ruled out, the replacement each club names, and a net count",
     WAS, NOTREAD,
     "data/deficiency_by_club_a392.csv, data/availability_deficiency_66faefac.csv",
     "Per-club counts exist. The replacements-named column is not published for most clubs because the club chart does not name one."),

    ("", "Add an announced-starter evidence field, not an inferred replacement",
     "Availability", "backlog", "not started", "G-02, G-03",
     "A field holding the dated official announcement of a starter change, with the article cited; blank where no announcement exists",
     TRADES, READ,
     "data/injuries_wk10_83246f00.csv",
     "The blank replacement columns are correct for the report page. The league publishes dated starter changes and no field stores them."),

    ("VR-24, VR-25; VQ-05", "Same as the previous line, for the Lock, McCord and Brissett starter changes the brief names",
     "Availability", "backlog", "not started", "G-02, G-03",
     "One evidence row per named starter change, each citing the dated official announcement",
     TRADES, READ,
     "data/depth_changes_2026_wk10.csv",
     "Official trades page re-read today confirms Jacoby Brissett traded from Arizona to Baltimore on 11/06. The Lock and McCord announcements were not re-read today and no row cites them."),

    ("", "Add an official depth-chart register with date and source per row",
     "Depth", "backlog", "partial", "G-02",
     "One row per chart slot carrying the date the club published it and the URL it came from",
     GB, READ,
     "data/s745_depth_charts.csv, data/s745_depth_summary.csv",
     "31 of 32 club charts transcribed as read on 2026-11-13, each row linked to the club page. The Packers chart re-read today is dated Nov. 10, 2026 by the club itself, and that date is not stored per row."),

    ("", "Calibrate what Questionable means empirically instead of using old percentages",
     "Availability", "backlog", "not started", "G-02, G-03",
     "Play rate per designation measured on joined official data with a confidence interval, replacing any imported percentage",
     INJ, READ,
     "data/injuries_wk10_83246f00.csv",
     "The official page publishes no percentages. No designation has been joined to an official active or inactive list, so no play rate can be measured."),

    ("", "Interactive Offense vs Defense Matchup Deficiency Matrix, 1st through 4th string",
     "Depth", "backlog", "not started", "G-02, G-03",
     "One screen showing trench and coverage mismatches by string, with every cell traceable to a club chart and a league filing",
     GB, READ,
     "data/deficiency_chains_a392.csv, data/s745_depth_deficiencies.csv",
     "The deficiency chains exist as tables. No offense-versus-defense matrix joins the two sides of the ball."),

    ("VR-17, VR-26; VQ-07", "Flag stale depth rows against the official transactions log",
     "Depth", "backlog", "not started", "G-02, G-03",
     "Every depth row checked against the official transactions log and marked stale where the log contradicts it",
     TRADES, READ,
     "data/s745_depth_charts.csv",
     "UNBLOCKED: the official transactions hub exists and was re-read today. It confirms Jacoby Brissett traded from Arizona to Baltimore on 11/06, which is the replacement the brief says Baltimore's depth chart does not reflect. No staleness check runs."),

    ("", "Point-in-Time Snapshot Ledger for Injuries, Depth Charts and Inactives",
     "Availability", "backlog", "not started", "G-03, G-04",
     "One append-only ledger covering injuries, depth charts and inactives, replayable to any past timestamp",
     INJ, READ,
     "data/availability_fingerprints.csv",
     "No ledger rows exist. Without it, backtests of originated lines leak future information by construction."),

    ("VR-08, VR-12", "Populate the three missing Lions game-status designations",
     "Availability", "backlog", "partial", "G-02",
     "Kerby Joseph, Cade Mays and D.J. Reed carrying the designation the official page publishes",
     INJ, READ,
     "data/injuries_2026_wk10.csv, data/injuries_wk10_e733834d_20261115.csv",
     "Official hub re-read today: all three are Out, with Knee, Ankle and Hip respectively. Already correct in the 13 November and 15 November dated files. Still blank on the canonical Week 10 injury table, which renders the 12 November read."),

    ("VR-04, VR-05, VR-06, VR-07", "Re-capture and republish the Week 10 injury tables",
     "Availability", "backlog", "partial", "G-03",
     "The canonical injury table republished from the current official read, with the row count and no-injury section count stated",
     INJ, READ,
     "data/injuries_2026_wk10.csv, data/injuries_wk10_83246f00.csv",
     "The dated 13 November read holds 296 rows and two no-injury markers. The canonical page still publishes 254 rows. The gap the brief describes is still live on the page a reader sees first."),

    ("SG-05", "Reject: deriving depth order from jersey number, experience or salary",
     "Rejected", "rejected", "rejected", "—",
     "Not applicable: the brief rejects this proposal outright",
     GB, READ,
     "data/s745_depth_charts.csv",
     "Rejected in the brief. The Packers chart re-read today shows why: it prepends jersey numbers, so a jersey-order heuristic would read a printing convention as a depth order."),

    ("VR-21, VR-23; VQ-08", "Represent shared and empty depth slots faithfully",
     "Depth", "backlog", "partial", "G-02",
     "A slot with two players stored as two players, and an empty slot stored as empty, neither collapsed into a ranked list",
     SEA, NOTREAD,
     "data/s745_depth_charts.csv",
     "The register stores both names where a club prints two. The Packers chart re-read today also shows empty printed slots and a fourth running back in a row with a blank position cell, which the current schema has no vocabulary for."),

    ("", "Resolve the depth-order source before building the backup-deficiency feature",
     "Depth", "backlog", "not started", "G-02",
     "One route verified for all 32 clubs: per-club official depth pages, or snap counts if an official snap source exists",
     HOU, READ,
     "data/s745_depth_summary.csv",
     "Neither route is verified for 32 clubs. The Texans chart re-read today is an image, so route (a) cannot cover all 32 and route (b) has no official snap source registered."),

    ("", "Score injury-designation reliability before using it as a feature",
     "Availability", "backlog", "not started", "G-02, G-03",
     "Play rate per designation measured over several seasons against the official inactive lists, with confidence intervals, before the label becomes a model input",
     INJ, READ,
     "data/correlation.csv, data/signals.csv",
     "No historical designation archive exists, so the measurement the brief asks for cannot be made. It is the same blocker as the designation-archive item below."),

    ("", "Snapshot the nfl.com injury report every Wednesday, Thursday and Friday and keep a dated history",
     "Availability", "backlog", "not started", "G-03",
     "At least three dated captures per week retained, so a Questionable to Out change and the DNP to LP to FP trend are visible",
     INJ, READ,
     "data/injuries_wk10_83246f00.csv, data/injuries_wk10_e733834d_20261115.csv",
     "Two dated reads exist for Week 10, taken on 13 and 15 November. Neither is a Wednesday, Thursday or Friday capture and no history is retained."),

    ("", "Treat the injury report as a timestamped series, not a weekly snapshot",
     "Availability", "backlog", "partial", "G-03",
     "Captures from Wednesday to kickoff with a fetch timestamp, so designation evolution is measurable",
     INJ, READ,
     "data/injury_delta_a392.csv, data/availability_watch_movement_c3ec1487.csv",
     "Two reads have been differenced. A series needs daily capture, which is a separate item above."),

    ("", "Use snap counts as the starter proxy when the depth chart is unavailable",
     "Depth", "backlog", "not started", "G-02",
     "A measurable starter and backup split from snap counts for clubs whose chart cannot be read",
     GAMEBOOK, NOTREAD,
     "data/s745_depth_summary.csv",
     "No snap counts are captured anywhere. The Texans image means this is the only remaining route for that club, and it has not been built."),

    ("", "Add a control baseline of random picks and favourites only to every leaderboard run",
     "Leaderboard", "backlog", "partial", "G-08",
     "Random and favourites-only controls scored on every leaderboard run, so skill is separated from luck",
     SCORES10, READ,
     "data/strategies.csv (ST-12, ST-13), data/leaderboard.csv",
     "Two controls are registered, ST-12 do-nothing and ST-13 public-news echo. Neither is a random or favourites-only control, and neither has been scored on a run."),

    ("", "Stadium roof and surface with NWS hourly wind and precipitation overlay",
     "Venue", "backlog", "not started", "G-01, G-03",
     "Each fixture joined to an official stadium roof and surface designation and to the NWS hourly grid for its kickoff hour",
     NWS, NOTREAD,
     "data/schedule_2026_wk10.csv",
     "The schedule carries a venue but no roof or surface field. weather.gov is a federal official source, not a league source, so this site's host rule tags it non-official."),

    ("", "Two-Stage Skill Leaderboard: proper-score qualification then prospective CLV and ROI escrow",
     "Leaderboard", "backlog", "not started", "G-06, G-08, G-12",
     "Stage one qualifies on calibrated probabilistic skill, stage two escrows prospective CLV and ROI over multi-week samples",
     SCHED11, READ,
     "data/leaderboard.csv, data/s2268_strategy_register.csv",
     "Neither stage exists on the canonical leaderboard. The 2268bfb2 tree runs a related two-part competition in its own namespace."),

    ("", "Vig-Free Market Consensus vs Originated Fair-Line Decomposition View",
     "Prices", "backlog", "not started", "G-01, G-07",
     "Origination alpha separated from operator margin before any bet structure is considered, on a published decomposition",
     OPS, NONE,
     "data/computed_vig.csv, data/price_archive_a392.csv",
     "Vig arithmetic is published from assumed prices. No market consensus exists to decompose, because no entitled price feed does."),

    ("", "Publish a weekly what-changed diff instead of a static snapshot",
     "Reporting", "backlog", "not started", "G-03",
     "Each weekly snapshot stored and a diff column rendered: rank change, rating change, availability change",
     INJ, READ,
     "data/availability_watch_movement_c3ec1487.csv",
     "Movement is computed once, between two reads. There is no recurring weekly diff published on a schedule."),

    ("", "Publish every model total twice until one wins",
     "Modelling", "backlog", "not started", "G-06, G-10",
     "Both estimators published side by side with a gap column, collapsing to one only after a walk-forward comparison",
     SCORES10, READ,
     "data/settled_wk10_5f16dcc6.csv, data/computed_fair_lines.csv",
     "Two estimators exist and have both been scored against the one settled game. Neither is published as a pair with a gap column."),

    ("", "Add a drift alarm to every scraper",
     "Governance", "backlog", "not started", "G-04",
     "Every parser pinned to expected row counts and required fields, failing the build loudly when a field goes missing",
     INJ, READ,
     "tools/verify.py, scripts/check_reproducible.py",
     "The verifiers check reconstructed outputs after the fact. No parser is pinned to an expected row count at read time."),

    ("VR-25; VQ-06", "Capture the reserve list so not listed never means available",
     "Availability", "backlog", "not started", "G-02, G-03",
     "The official reserve list captured per week so a player absent from the injury report can be marked on reserve rather than healthy",
     RESERVE, READ,
     "data/flags.csv (FL-52)",
     "UNBLOCKED: the official reserve-list page exists and was re-read today. It names Malik Willis, Miami, Reserve/Injured on 11/10, which is exactly the case FL-52 could only source to a news article. No capture exists in the repo."),

    ("SG-03", "Reject: ranking strategies by season-long ROI",
     "Rejected", "rejected", "rejected", "—",
     "Not applicable: the brief rejects this proposal outright",
     SCORES10, READ,
     "data/leaderboard.csv",
     "Rejected in the brief. The leaderboard publishes no ROI at all, so the rejected ranking cannot currently be applied."),

    ("Q-06", "Archive weekly injury reports for past seasons",
     "Availability", "backlog", "not started", "G-02, G-03",
     "Historical weekly injury reports archived so designation reliability can be measured over more than one season",
     INJ, READ,
     "data/injuries_2026_wk10.csv",
     "Only the current season is held. The official hub exposes a season selector back to 1965 on the page re-read today, so the archive is addressable if the entitlement question is settled."),

    ("", "Pre-register each strategy: definition frozen before results are seen",
     "Governance", "backlog", "partial", "G-11",
     "Every strategy carrying a registration hash recorded before the first result of its measurement window",
     SCHED11, READ,
     "data/prereg_wk10_66faefac.csv, data/prereg_week11_0a113a24.csv",
     "Two weeks are hash-locked. Ten of the fifteen registered strategies have no registration record."),

    ("", "2026 Kickoff and Declared Onside-Kick Regime Priors Filter",
     "Origination", "backlog", "not started", "G-01, G-03",
     "Kickoff and onside-kick regime priors read from the official rulebook and applied to totals and fourth-quarter win-probability curves",
     OPS, NOTREAD,
     "data/nfl-rules-operations-2026.json",
     "A 2026 rules file is registered in the repo. No kickoff or onside-kick regime prior has been extracted from it."),

    ("", "Freeze a rule before it sees data: commit the rule text, sample window and gates before the evaluation window opens",
     "Governance", "backlog", "partial", "G-11",
     "Rule text, sample window and gates committed to git before the window opens, with the commit hash as the registration",
     SCHED11, READ,
     "data/prereg_week11_0a113a24.csv",
     "The Week 11 pre-registration is committed before kickoff and uses a recorded hash. The practice is two weeks old and not yet applied to strategies."),

    ("", "Split data into train, validation and final holdout seasons",
     "Modelling", "backlog", "partial", "G-10",
     "A published three-way split of seasons, with the final holdout untouched until the declared moment",
     SCORES10, READ,
     "data/s2268_holdout_decisions.csv, data/games_2026_wk1_9.csv",
     "A chronological holdout has been used inside the 2268bfb2 tree. The canonical corpus publishes no train, validation and holdout split."),
]


# What was actually re-read on 15 November 2026, and what each page showed. Kept as data so the
# page cannot claim a read that was not performed.
READS = [
    ("Official NFL Injury Report hub", INJ,
     "Still labelled Week 10 on 15 November. The Detroit block lists Kerby Joseph (knee), Cade Mays (ankle) and D.J. Reed (hip) as did not participate and Out. The New England block lists seven Questionable and three Out.",
     "BL-21, BL-48, BL-49, BL-54", "none"),
    ("Official NFL Week 11 schedule page", SCHED11,
     "Week 11 runs 19 to 22 November 2026. The page names a stadium for every fixture it lists through its hotel links: NRG Stadium for Houston, Highmark Stadium for Buffalo, Bank of America Stadium for Carolina, Soldier Field for Chicago, AT&T Stadium for Dallas.",
     "BL-14, BL-23", "none"),
    ("Official NFL Week 10 scores page", SCORES10,
     "Commanders 24, Giants 21 is Final. The other thirteen Week 10 fixtures show kickoff times on 15 and 16 November with no result.",
     "BL-02, BL-19, BL-26", "none"),
    ("Official NFL league transactions hub", TXN,
     "Six dated transaction tabs, including a Reserve List. The November trades table lists twelve moves, among them Keenan Allen from Indianapolis to San Francisco and Josh Downs from Indianapolis to Kansas City on 11/10, and Jacoby Brissett from Arizona to Baltimore on 11/06.",
     "BL-34, BL-42, BL-46", "none"),
    ("Official NFL trades tab, November 2026", TRADES,
     "Twelve dated trades. Jacoby Brissett from Arizona to Baltimore on 11/06. Keenan Allen from Indianapolis to San Francisco and Josh Downs from Indianapolis to Kansas City, both on 11/10. The same twelve rows appear on the transactions hub.",
     "BL-34, BL-42, BL-46", "none"),
    ("Official NFL reserve list, November 2026", RESERVE,
     "Dated Reserve/Injured rows. Malik Willis, Miami, on 11/10. Puka Nacua, Rams, on 11/12. TreVeyon Henderson, New England, on 11/14. The page carries further rows that were not read.",
     "BL-13, BL-64", "FL-78"),
    ("Green Bay Packers depth chart", GB,
     "Printed as 'Unofficial, Nov. 10, 2026'. Jersey numbers are printed ahead of every name. Several printed slots are empty, and a fourth running back appears in a row with a blank position cell.",
     "BL-11, BL-32, BL-33, BL-43, BL-51", "none"),
    ("Houston Texans depth chart", HOU,
     "Printed as 'Unofficial Depth Chart' and published as an image, with no HTML table of players behind it.",
     "BL-32, BL-43, BL-52, BL-56", "none"),
]

# Irregularities this session found by re-reading those pages. Published, not silently corrected.
FINDINGS = [
    ("BF-01", "stale published table", "high",
     "The Week 10 injury table a reader sees first still renders the 12 November 2026 read: 254 rows, with Kerby Joseph, Cade Mays and D.J. Reed carrying a blank game status. The official hub re-read on 15 November publishes all three as Out, and the repository's own 13 November and 15 November dated files already agree with the official page.",
     "https://www.nfl.com/injuries/ :: https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/injuries_2026_wk10.csv",
     "The brief's Lions item (VR-08, VR-12) reads as open on the canonical page and as closed in the dated files. Nothing on the site says which table is authoritative.",
     "BL-48, BL-49"),
    ("BF-02", "missing value the official page publishes", "medium",
     "data/schedule_week11_2026.csv carries site as not published for every Week 11 fixture, while the official Week 11 schedule page names the stadium for each one.",
     "https://www.nfl.com/schedules/2026/by-week/week-11 :: https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/schedule_week11_2026.csv",
     "The fixture-context feature set the brief asks for cannot be built for the live week from the repository copy, although the official source publishes the field.",
     "BL-14, BL-23"),
    ("BF-03", "unblocked by an official page", "high",
     "Flag FL-52 records that the NFL transactions hub was not read, and leaves four injured-reserve placements sourced to news articles, with Puka Nacua marked only as likely. The hub exists at nfl.com/transactions/ with a dated Reserve List tab. It names Malik Willis, Miami, Reserve/Injured on 11/10 and Puka Nacua, Rams, Reserve/Injured on 11/12.",
     "https://www.nfl.com/transactions/league/reserve-list/2026/11 :: https://www.nfl.com/transactions/",
     "The reserve-list item (VR-25, VQ-06) and the stale-depth item (VR-17, VR-26, VQ-07) were treated as blocked. Both have an official, dated, structured source that no session had read.",
     "BL-46, BL-64, BL-13"),
    ("BF-04", "conflict between two official pages", "medium",
     "The official reserve list names TreVeyon Henderson, New England, as Reserve/Injured on 11/14. The official injury hub, read the same day, lists TreVeyon Henderson, New England, with Illness, did not participate in practice, and Out.",
     "https://www.nfl.com/transactions/league/reserve-list/2026/11 :: https://www.nfl.com/injuries/",
     "A player on the reserve list does not appear on the weekly injury report. Both pages are official and dated the same week, so any availability model that reads one and not the other will mis-state this club.",
     "BL-64, BL-44"),
    ("BF-05", "date granularity", "medium",
     "The Packers depth chart is dated by the club itself as 'Unofficial, Nov. 10, 2026', but the depth register stores a single read date, 2026-11-13, for every club it transcribed.",
     "https://www.packers.com/team/depth-chart :: https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/s745_depth_summary.csv",
     "The brief asks for a date and source per depth-chart row. Storing our read date instead of the club's publication date makes every chart look fresher than it is.",
     "BL-43, BL-46"),
]


# The eight pages actually fetched on 15 November 2026. A row may only claim
# "re-read 2026-11-15" if its dependency is one of these, so the register cannot drift into
# claiming reads nobody performed.
FETCHED = {INJ, SCORES10, SCHED11, TXN, TRADES, RESERVE, GB, HOU}


def check_gates():
    """Refuse to build if a directive cites a gate the register does not define."""
    with open(os.path.join(DATA, "gates.csv"), encoding="utf-8") as fh:
        known = {r["id"].strip() for r in csv.DictReader(fh, delimiter="|")}
    bad = []
    for item in ITEMS:
        blocks = item[5]
        if blocks.strip() == "—":
            continue
        refs = set(re.findall(r"G-\d{2}", blocks))
        residue = re.sub(r"G-\d{2}", "", blocks).strip(" /,;")
        if not refs or residue or (refs - known):
            bad.append((item[1][:40], blocks))
    return bad


def main():
    bad = check_gates()
    if bad:
        print("FAIL backlog: malformed or unknown gate references: %s" % bad, file=sys.stderr)
        return 1

    rows = []
    for i, (code, directive, theme, kind, status, blocks, clears, dep, verified, repo, note) in enumerate(ITEMS, start=1):
        for value in (directive, theme, kind, status, blocks, clears, dep, verified, repo, note, code):
            if "|" in value:
                raise SystemExit("pipe character in backlog cell: %r" % value)
            if "\n" in value:
                raise SystemExit("newline in backlog cell: %r" % value)
        if verified == READ and dep not in FETCHED:
            raise SystemExit("%s claims a 2026-11-15 read of %s, which was not fetched"
                             % ("BL-%02d" % i, dep))
        rows.append({
            "id": "BL-%02d" % i,
            "brief_code": code,
            "directive": directive,
            "theme": theme,
            "kind": kind,
            "status": status,
            "blocks": blocks,
            "clears_with": clears,
            "dependency": dep,
            "verified_2026_11_15": verified,
            "evidence_in_repo": repo,
            "note": note,
        })

    out = os.path.join(DATA, "brief_backlog_58e9c708.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER, delimiter="|", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # Summary counts, computed rather than typed, so the page cannot drift from the register.
    themes, statuses = {}, {}
    for r in rows:
        themes[r["theme"]] = themes.get(r["theme"], 0) + 1
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
    summary = os.path.join(DATA, "backlog_summary_58e9c708.csv")
    with open(summary, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(["grouping", "bucket", "count", "share_pct"])
        n = len(rows)
        for k in sorted(themes):
            w.writerow(["theme", k, themes[k], "%.1f" % (100.0 * themes[k] / n)])
        for k in sorted(statuses):
            w.writerow(["status", k, statuses[k], "%.1f" % (100.0 * statuses[k] / n)])
        w.writerow(["total", "directives on this register", n, "100.0"])

    reads_path = os.path.join(DATA, "backlog_reads_58e9c708.csv")
    with open(reads_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(["page", "url", "what_the_official_page_shows", "unblocks", "flag"])
        w.writerows(READS)

    find_path = os.path.join(DATA, "backlog_findings_58e9c708.csv")
    with open(find_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(["id", "type", "severity", "finding", "evidence", "decision_impact", "directives"])
        w.writerows(FINDINGS)

    print("wrote %s (%d rows), %s (%d rows), %s (%d rows), %s"
          % (os.path.relpath(out, ROOT), len(rows),
             os.path.relpath(summary, ROOT), len(themes) + len(statuses) + 1,
             os.path.relpath(reads_path, ROOT), len(READS),
             os.path.relpath(find_path, ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

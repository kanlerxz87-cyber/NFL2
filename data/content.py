"""Single source of truth for every table row on the NFL2 GitHub Pages site.

Rules enforced by tools/verify.py:
  * every row carries at least one source id from research/source-registry.json
    whose status is fetch-verified or local-git-verified;
  * a cell that cannot be confirmed from an official source is an empty string;
  * such rows have status "unverified" and an explicit flag.
No numeric result is inferred, estimated or filled in.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "research" / "source-registry.json").read_text())
SOURCES = {s["id"]: s for s in REGISTRY["sources"]}

SITE_URL = "https://kanlerxz87-cyber.github.io/NFL2/review/"
CAPTURED = "2026-11-12 (UTC)"


def R(cells, src, status="verified", flags=None, note=""):
    """One table row. `cells` are strings; "" means deliberately blank."""
    if isinstance(src, str):
        src = [src]
    return {
        "cells": ["" if c is None else str(c) for c in cells],
        "src": src,
        "status": status,
        "flags": flags or [],
        "note": note,
    }


def T(key, title, headers, rows, intro="", analysis="", note=""):
    return {
        "key": key,
        "title": title,
        "headers": headers,
        "rows": rows,
        "intro": intro,
        "analysis": analysis,
        "note": note,
    }


def P(file, title, category, eyebrow, intro, sections, hero=False):
    return {
        "file": file,
        "title": title,
        "category": category,
        "eyebrow": eyebrow,
        "intro": intro,
        "sections": sections,
        "hero": hero,
    }


# ---------------------------------------------------------------------------
# Navigation (shared output — integration session only)
# ---------------------------------------------------------------------------
NAV = [
    ("Overview", [
        ("index.html", "Dashboard"),
        ("executive-summary.html", "Executive summary"),
        ("requirements.html", "Requirements"),
        ("repo-review.html", "Repo review"),
    ]),
    ("Decisions", [
        ("decisions.html", "Questions & answers"),
        ("suggestions.html", "Suggestions / choose a path"),
    ]),
    ("Research", [
        ("sources.html", "Official sources"),
        ("data.html", "Verified data"),
        ("strategies.html", "Strategies & signals"),
    ]),
    ("Validation", [
        ("validation.html", "Validation gates"),
        ("correlations.html", "Correlation values"),
        ("leaderboard.html", "Leaderboard & rewards"),
    ]),
    ("Tracking", [
        ("injuries.html", "Injuries & depth"),
    ]),
    ("Governance", [
        ("methodology.html", "Methodology"),
        ("flagged.html", "Flagged for review"),
    ]),
]

PAGES = []


# ---------------------------------------------------------------------------
# 1. Landing dashboard
# ---------------------------------------------------------------------------
PAGES.append(P(
    "index.html", "NFL2 decision dashboard", "Overview", "Live dashboard",
    "A clean, read-only dashboard of verified NFL research, decision prerequisites, "
    "suggestions, strategy design, validation gates and injury/depth tracking. "
    "Every table row links to an official source. Values that cannot be confirmed "
    "from an official source are blank and flagged UNVERIFIED.",
    [
        T("dash-status", "Site at a glance",
          ["Metric", "Value", "Meaning", "Status", "Official basis", "Source"],
          [
              R(["Official sources fetch-verified", "33", "URLs opened and matched to a recorded title and excerpt", "VERIFIED", "Source registry, 2026-11-12", "S01"], "S01"),
              R(["Atomic requirements", "52", "Line-by-line trace to the project brief", "VERIFIED", "Requirements register", "S29"], "S29"),
              R(["Blocking decision questions", "17", "Must be answered before implementation", "PROPOSAL", "Decision gates page", "S01"], "S01"),
              R(["Open improvement paths", "5", "Reviewer chooses one before any change is implemented", "PROPOSAL", "Suggestions page", "S11"], "S11"),
              R(["Validation gates", "12", "Each strategy must pass all gates", "PROPOSAL", "Validation page", "S12"], "S12"),
              R(["Correlation pairs defined", "10", "All numeric values blank until a licensed dataset exists", "UNVERIFIED", "", "S14"], "S14", "unverified", ["F02", "F12"], "No licensed dataset; no coefficient was computed."),
              R(["Verified injury report rows", "20", "Week 10, Commanders at Giants, verbatim from NFL.com", "VERIFIED", "Injuries page", "S01"], "S01"),
              R(["Verified depth-chart rows", "10", "Chiefs offense/defense, First through Fourth", "VERIFIED", "Club depth chart is labelled unofficial", "S23"], "S23"),
              R(["Flagged irregularities", "14", "Published on Flagged for Review; non-blocking", "NEEDS REVIEW", "See flagged.html", "S18"], "S18", "needs-review", ["F01", "F13"]),
              R(["Live-money features", "0", "No wagering, accounts or payments", "PROPOSAL", "Legal jurisdiction unresolved", "S30"], "S30"),
          ],
          intro="Counts describe this site's own content, not NFL statistics. They are generated from the same data file that renders every table.",
          analysis="The dashboard is deliberately a decision tool, not a tip sheet: unresolved items are visible, sourced and non-blocking, so a reviewer can see exactly what is known and what is not."),

        T("dash-index", "Pages by category",
          ["Category", "Page", "What you will find", "Rows of data", "Status", "Source"],
          [
              R(["Overview", "Executive summary", "Important details, findings and recommended path", "22", "VERIFIED", "Repository brief", "S29"], "S29"),
              R(["Overview", "Requirements", "52 atomic requirements with acceptance criteria", "52", "VERIFIED", "Repository brief", "S29"], "S29"),
              R(["Overview", "Repo review", "Line-by-line audit of the original repository", "14", "VERIFIED", "GitHub API + local git", "S29"], "S29"),
              R(["Decisions", "Questions & answers", "Information we have / do not have / answers / discovery", "39", "PROPOSAL", "Official NFL sources", "S01"], "S01"),
              R(["Decisions", "Suggestions", "Ranked paths and the pre-implementation chooser", "20", "PROPOSAL", "Official competition design", "S11"], "S11"),
              R(["Research", "Official sources", "Every fetch-verified official URL", "36", "VERIFIED", "Source registry", "S01"], "S01"),
              R(["Research", "Verified data", "Standings, schedule, game metrics, injury and depth snapshots", "31", "VERIFIED", "NFL.com / club site", "S03"], "S03"),
              R(["Research", "Strategies & signals", "15 candidate strategies across singles, parlays, prop combos", "35", "PROPOSAL", "Official data inputs", "S20"], "S20"),
              R(["Validation", "Validation gates", "12 gates + 9-step skill-vs-luck protocol", "27", "PROPOSAL", "Official method documentation", "S15"], "S15"),
              R(["Validation", "Correlation values", "10 pairs with blank coefficients", "15", "VERIFIED", "Row count from local data file", "S14"], "S14"),
              R(["Validation", "Leaderboard & rewards", "Public/private split, reward tiers, integrity limits", "19", "PROPOSAL", "Official Big Data Bowl", "S11"], "S11"),
              R(["Tracking", "Injuries & depth", "Injury snapshot, depth snapshot, tracker schema", "49", "VERIFIED", "NFL.com + club site", "S01"], "S01"),
              R(["Governance", "Methodology", "Verification protocol and blank-value policy", "18", "PROPOSAL", "GitHub Docs", "S27"], "S27"),
              R(["Governance", "Flagged for review", "14 irregularities with source links", "19", "NEEDS REVIEW", "Published non-blocking", "S18"], "S18", "needs-review", ["F01", "F02", "F13"]),
          ],
          analysis="Categories are fixed across all pages so navigation never changes shape. Every subpage repeats the same sidebar."),
    ], hero=True))


# ---------------------------------------------------------------------------
# 2. Executive summary
# ---------------------------------------------------------------------------
PAGES.append(P(
    "executive-summary.html", "Executive summary", "Overview", "Important details",
    "The essential facts, findings, decisions and irregularities in one place. "
    "Prepared 2026-11-12 (UTC) by session session-01b698ef.",
    [
        T("exec-findings", "Key findings",
          ["#", "Finding", "Why it matters", "Verified value", "Status", "Source"],
          [
              R(["1", "The repository was effectively empty at the base commit", "Nothing to inherit; all content is newly sourced", "1 commit, 1 tracked file, 6-byte README", "VERIFIED", "Local git inspection", "S29"], "S29"),
              R(["2", "The NFL does not publish its own betting lines", "Defines what 'originate my own lines' can mean", "NFL widgets show partner-supplied odds, spreads and totals", "VERIFIED", "NFL Support", "S20"], "S20"),
              R(["3", "A league-official algorithmic Predicted Score exists", "A legitimate precedent for a model-produced line", "Genius Sports algorithm over historical/season data", "VERIFIED", "NFL Support", "S21"], "S21"),
              R(["4", "A weekly injury report is published for Week 10, 2026", "Primary verified availability input", "Player / Position / Injuries / Practice Status / Game Status", "VERIFIED", "NFL.com injury report", "S01"], "S01"),
              R(["5", "Club depth charts expose First through Fourth string", "Enables 2nd/3rd/4th replacement tracking for offense and defense", "Chiefs page labelled 'Unofficial Depth Chart'", "VERIFIED", "Chiefs official site", "S23"], "S23"),
              R(["6", "The final availability checkpoint is the 90-minute inactive list", "Weekly injury report alone is insufficient", "Game Day Administration Report exchanged 90 minutes before kickoff", "VERIFIED", "NFL Football Operations", "S24"], "S24"),
              R(["7", "Related-outcome parlays are prohibited by approved house rules", "Parlay/prop-combo strategies must model executability", "Same Game Parlay is a separately carved-out product", "VERIFIED", "Massachusetts Gaming Commission", "S22"], "S22"),
              R(["8", "NFL integrity policy restricts injury-linked wagers", "May make some injury signals non-executable", "Wagers tied to officiating and injuries prohibited", "VERIFIED", "NFL.com", "S18"], "S18"),
              R(["9", "An official judged leaderboard competition exists as a template", "Prize pool, PASS/FAIL standards, public/private split", "$100,000 prize pool", "VERIFIED", "NFL Football Operations", "S11"], "S11"),
              R(["10", "No licensed historical odds or play-by-play dataset exists here", "Blocks every numeric result", "", "UNVERIFIED", "", "S01"], "S01", "unverified", ["F02", "F12"], "Correlation values, ROI and scores therefore remain blank."),
              R(["11", "Legal jurisdiction for rewards was not supplied", "Blocks rewards and any live-money feature", "", "UNVERIFIED", "", "S30"], "S30", "unverified", ["F13"], "Compliance determination required."),
              R(["12", "14 irregularities are published for review", "Non-blocking; reviewer can request changes after launch", "14", "NEEDS REVIEW", "Flagged for Review page", "S18"], "S18", "needs-review", ["F01", "F02", "F13"]),
          ],
          analysis="Findings 10 and 11 are the reason this site contains no invented numbers. The framework is complete; the measurements are honestly blank."),

        T("exec-decisions", "Decisions required before implementation",
          ["Gate", "Question", "Answer available from official source?", "Status", "Source"],
          [
              R(["D02", "What exactly is a 'line' for this project?", "", "UNVERIFIED", "", "S20"], "S20", "unverified", ["F01"], "Define target markets from a licensed operator's market list."),
              R(["D04", "Where do licensed opening/closing prices come from?", "", "UNVERIFIED", "", "S18"], "S18", "unverified", ["F02"], "Establish a data licence via the league's official data distributor."),
              R(["D05", "Are injury signals executable under league integrity rules?", "", "UNVERIFIED", "", "S18"], "S18", "unverified", ["F07"], "Confirm permitted markets with a licensed operator."),
              R(["D07", "Which jurisdiction governs a reward competition?", "", "UNVERIFIED", "", "S30"], "S30", "unverified", ["F13"], "Obtain a written compliance determination."),
              R(["D15", "Is a public leaderboard sufficient?", "No — a private holdout is required", "VERIFIED", "Kaggle public/private leaderboard definitions", "S13"], "S13"),
          ],
          analysis="Blank answer cells are intentional. No decision is recorded as made."),

        T("exec-path", "Recommended path",
          ["Order", "Path", "Action", "Effort", "Impact", "Status", "Source"],
          [
              R(["1", "A", "Lock the evidence layer and Flagged for Review page", "Low", "High", "PROPOSAL", "Suggested, not implemented", "S27"], "S27"),
              R(["2", "B", "Answer the blocking questions D01–D17", "Medium", "High", "PROPOSAL", "Suggested, not implemented", "S01"], "S01"),
              R(["3", "C", "Build the injury / depth snapshot pipeline", "Medium", "High", "PROPOSAL", "Blocked on A and B", "S24"], "S24"),
              R(["4", "D", "License historical prices and run the numeric gates", "High", "High", "PROPOSAL", "Blocked on D04", "S18"], "S18"),
              R(["5", "E", "Recognition-only leaderboard, no money", "Medium", "Medium", "PROPOSAL", "Blocked on D07", "S11"], "S11"),
          ],
          analysis="The reviewer selects a path on the Suggestions page. No implementation starts before that selection is recorded."),
    ]))


# ---------------------------------------------------------------------------
# 3. Requirements
# ---------------------------------------------------------------------------
_REQ = [
    ("R01", "Goal", "Collect a full list of requirements", "Requirements table with stable IDs and traceability", "done"),
    ("R02", "Goal", "Organize the material", "Landing page plus subpages by category", "done"),
    ("R03", "Goal", "Analyze the material", "Analysis and findings on every page", "done"),
    ("R04", "Site improvement", "Suggest how to improve the site for decision making", "Ranked suggestion table with effort and impact", "done"),
    ("R05", "Site improvement", "Create a dedicated suggestions section", "suggestions.html exists", "done"),
    ("R06", "Site improvement", "Choose best path before implementing changes", "Path chooser and no-implementation gate", "done"),
    ("R07", "Decision gates", "Clear list of questions", "Question column on decisions.html", "done"),
    ("R08", "Decision gates", "Clear list of information we have", "Have column with official links", "done"),
    ("R09", "Decision gates", "Clear list of information we do not have", "Missing column with blank cells and flags", "done"),
    ("R10", "Decision gates", "Answers needed before any decision", "Answer column, blank where unanswerable", "done"),
    ("R11", "Decision gates", "Suggestions to discover missing information", "How-to-discover column", "done"),
    ("R12", "Lines", "Originate own NFL lines", "Model-line framework; numeric lines blank", "done / values unverified"),
    ("R13", "Strategies", "Research strategies for useful signals", "Signal inventory table", "done"),
    ("R14", "Competition", "Treat as a leaderboard competition", "Public/private leaderboard design", "done"),
    ("R15", "Competition", "Rewards for top strategies", "Reward tiers modelled on official prize structure", "done"),
    ("R16", "Bet types", "Single bets", "Single-bet strategy rows", "done"),
    ("R17", "Bet types", "Parlays", "Parlay rows plus related-outcome rule", "done"),
    ("R18", "Bet types", "Player prop bet combos", "Prop-combo rows plus settlement rule", "done"),
    ("R19", "Validation", "Every strategy passes validation gates", "Gates G01–G12", "done"),
    ("R20", "Validation", "Determine correlation values", "Matrix structure and methods; values blank", "done / values unverified"),
    ("R21", "Validation", "Remove luck; selectively skill-based", "Nine-step skill-vs-luck protocol", "done"),
    ("R22", "Injuries", "Track injuries", "Week 10 snapshot and field schema", "done"),
    ("R23", "Injuries", "Defensive deficiencies from 2nd/3rd/4th string", "Defensive depth table", "done"),
    ("R24", "Injuries", "Same for offense starters or backups", "Offensive depth table", "done"),
    ("R25", "Reporting", "Executive summary", "executive-summary.html and README", "done"),
    ("R26", "Autonomy", "No manual input from the user", "No clarifying questions asked", "done"),
    ("R27", "Verification", "Work line by line", "Row IDs and evidence registry", "done"),
    ("R28", "Verification", "Official verified trusted sources only", "Domain allowlist and source registry", "done"),
    ("R29", "Verification", "No hallucinations", "No inferred numbers", "done"),
    ("R30", "Repo work", "Review the repo line by line", "repo-review.html and audit notes", "done"),
    ("R31", "Repo work", "Links for manual review", "Official GitHub URL on every audit row", "done"),
    ("R32", "Repo work", "Flag irregularities", "Flagged for Review F01–F14", "done"),
    ("R33", "Site creation", "Live GitHub Pages site", "Deployed from main:/", "done at deploy"),
    ("R34", "Site creation", "Clean landing page", "Dashboard landing page", "done"),
    ("R35", "Site creation", "Subpages organized by category", "Six fixed categories", "done"),
    ("R36", "Site creation", "Clean, simple dashboard UI", "One local stylesheet, no external dependencies", "done"),
    ("R37", "Site creation", "All entries and findings in tables", "All pages table-driven", "done"),
    ("R38", "Verification", "Every table row has an official source link", "Enforced by tools/verify.py", "done"),
    ("R39", "Verification", "Blank and flag unconfirmable values", "Blank cells with UNVERIFIED badge", "done"),
    ("R40", "Coordination", "Read or create COORDINATION.md", "Created before any work", "done"),
    ("R41", "Coordination", "Claim tasks with ID and scope, push claim", "Claim commits pushed", "done"),
    ("R42", "Coordination", "Non-overlapping scopes; log cross-scope requests", "Disjoint scopes on board", "done"),
    ("R43", "Coordination", "Small frequent commits; pull --rebase before push", "Documented commit log", "done"),
    ("R44", "Coordination", "Log sources, verification, irregularities; mark done", "Board verification log", "done"),
    ("R45", "Coordination", "Shared outputs only by integration session", "T10 claimed after T01–T09", "done"),
    ("R46", "Coordination", "needs review = published and non-blocking", "flagged.html", "done"),
    ("R47", "Integration", "Re-verify combined data; no broken links", "verify.py plus link check", "done"),
    ("R48", "PR", "PR to main with summary, sources, irregularities", "PR body", "done at PR"),
    ("R49", "Merge", "Merge without waiting for approval", "gh pr merge --merge", "done at merge"),
    ("R50", "Deploy", "Confirm Pages deploy; record PR link and result", "Pages build API and live fetch", "done at deploy"),
    ("R51", "Deploy", "Publish flagged items; do not block merge", "flagged.html", "done"),
    ("R52", "Deploy", "Retry until live; never merge a broken site", "Verify and build-status loop", "done at deploy"),
]
PAGES.append(P(
    "requirements.html", "Full requirements list", "Overview", "52 atomic requirements",
    "Each row is one atomic requirement derived line by line from the verbatim brief in "
    "content/brief.md. The primary source for every requirement is the brief hosted in the "
    "project's official repository.",
    [
        T("req-all", "Requirements register",
          ["ID", "Category", "Requirement", "Acceptance criterion", "Status", "Primary source", "Source"],
          [R([rid, cat, text, acc, st, "Verbatim project brief", "Official project repository", "S29"], "S29",
             "proposal" if "values unverified" in st else "verified",
             ["F02", "F12"] if "values unverified" in st else [])
           for rid, cat, text, acc, st in _REQ],
          intro="Use the filter box to search by ID, category or keyword. Status 'done / values unverified' means the framework was built but numeric outputs were correctly left blank.",
          analysis="No requirement was silently dropped. Where the requirement asks for a number (R12, R20), the site provides the method and the blank, flagged cell rather than an invented number."),
    ]))


# ---------------------------------------------------------------------------
# 4. Repo review
# ---------------------------------------------------------------------------
_AUDIT = [
    ("A01", "README.md, line 1", "# NFL2 — 6 bytes, no trailing newline", "git ls-tree -r HEAD; cat README.md | od -c", "https://github.com/kanlerxz87-cyber/NFL2/blob/main/README.md"),
    ("A02", "Tree at base commit", "Exactly one tracked file: README.md (blob bea05f1e...)", "git ls-tree -r HEAD", "https://github.com/kanlerxz87-cyber/NFL2/tree/01f227119ee8df4223b0aa697d08ed92257773c3"),
    ("A03", "Commit history", "One commit: 01f2271 Initial commit", "git log --oneline -5", "https://github.com/kanlerxz87-cyber/NFL2/commits/main"),
    ("A04", "Branches", "main and arena/01b698ef-nfl2; remote had only origin/main at audit time", "git branch -a", "https://github.com/kanlerxz87-cyber/NFL2/branches"),
    ("A05", "Remote", "origin https://github.com/kanlerxz87-cyber/NFL2.git", "git remote -v", "https://github.com/kanlerxz87-cyber/NFL2"),
    ("A06", "Default branch", "main", "gh repo view --json defaultBranchRef", "https://github.com/kanlerxz87-cyber/NFL2"),
    ("A07", "GitHub Pages config", "status built; build_type legacy; source main:/; https enforced", "gh api repos/kanlerxz87-cyber/NFL2/pages", "https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site"),
    ("A08", "COORDINATION.md", "Absent at base commit; created by this session before work began", "cat COORDINATION.md", "https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md"),
    ("A09", "Missing baseline files", "No .gitignore, LICENSE, CI, .nojekyll, 404.html, site or data files", "ls -la; git ls-tree -r HEAD", "https://github.com/kanlerxz87-cyber/NFL2/tree/01f227119ee8df4223b0aa697d08ed92257773c3"),
    ("A10", "Git identity", "kanlerxz87-cyber <312694378+kanlerxz87-cyber@users.noreply.github.com>", "git config user.name; git config user.email", "https://github.com/kanlerxz87-cyber/NFL2"),
    ("A11", "GitHub auth", "Authenticated as kanlerxz87-cyber via GH_TOKEN", "gh auth status", "https://github.com/kanlerxz87-cyber/NFL2"),
    ("A12", "Sandbox outbound network", "Direct curl to www.nfl.com fails; verification used fetch/search tools", "curl -sS -w %{http_code} https://www.nfl.com/injuries/", "https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages"),
]
PAGES.append(P(
    "repo-review.html", "Repo review", "Overview", "Line-by-line audit",
    "Every object in the original repository was inspected with local git commands or the "
    "official GitHub API. The 'Manual review' column is a link for a human to check the same "
    "fact. There were no unverified repository lines: the whole tree was one 6-byte file.",
    [
        T("audit-rows", "Repository audit",
          ["ID", "Object / line", "Observed content", "How verified", "Manual review link", "Status", "Source"],
          [R([i, obj, obs, how, link, "VERIFIED", "Official GitHub / local git", "S29"], "S29")
           for i, obj, obs, how, link in _AUDIT],
          analysis="Conclusion: no dataset, schema, code, tests or prior analysis existed. Therefore every site value is either copied from a fetch-verified official page, a documented design proposal, or a blank UNVERIFIED cell."),
        T("audit-irregular", "Baseline irregularities",
          ["ID", "Observation", "Consequence", "Status", "Source"],
          [
              R(["F11", "6-byte README; no LICENSE, .gitignore, CI, 404 page or .nojekyll; Pages build_type legacy", "Baseline hygiene added during integration", "NEEDS REVIEW", "Published on Flagged for Review", "S29"], "S29", "needs-review", ["F11"]),
              R(["F10", "Environment fixes the session to one branch", "Per-session worktrees cannot be created; disjoint file scopes used instead", "NEEDS REVIEW", "Logged on the coordination board", "S29"], "S29", "needs-review", ["F10"]),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 5. Decision gates
# ---------------------------------------------------------------------------
_HAVE = [
    ("H01", "Official Week 10 2026 injury report: player, position, injury, practice status, game status", "S01"),
    ("H02", "Official injury-report definitions: Questionable / Doubtful / Out and DNP / Limited / Full", "S02"),
    ("H03", "Official 2026 standings, player stat categories, schedule and game-center metrics", "S03"),
    ("H04", "Official club roster and a club depth chart with First / Second / Third / Fourth", "S23"),
    ("H05", "Official Game Day Administration Report / inactive list at the 90-minute meeting", "S24"),
    ("H06", "NFL.com odds widgets are partner-supplied, not NFL-originated", "S20"),
    ("H07", "A Predicted Score exists as a Genius Sports algorithm over historical/season data", "S21"),
    ("H08", "Official Next Gen Stats tracking metrics and 2026 metric families", "S08"),
    ("H09", "Official Big Data Bowl: $100,000 prize pool, judged submissions, public/private leaderboard", "S11"),
    ("H10", "Approved operator house rules on related-outcome parlays and same-game parlays", "S22"),
    ("H11", "NFL integrity policy on injury/officiating wagers and monitoring", "S18"),
    ("H12", "Official statistics methods: correlation, proper scoring, multiple-test correction", "S14"),
]
_MISSING = [
    ("M01", "Historical opening and closing market prices", "Needed for closing-line value and ROI", "F02"),
    ("M02", "Licensed play-by-play and per-snap participation archive", "Needed for replacement depth and matchup features", "F02"),
    ("M03", "Archived weekly injury reports and archived inactive lists", "Needed for any longitudinal injury signal", "F02"),
    ("M04", "Archived club depth charts with timestamps", "Needed for 2nd/3rd/4th-string history", "F03"),
    ("M05", "Operator price and vig/hold per market and per book", "Needed to compute net returns", "F02"),
    ("M06", "Correlation coefficients between candidate legs", "Needed to price or reject parlays", "F12"),
    ("M07", "Out-of-sample strategy results and scores", "Needed for the leaderboard", "F12"),
    ("M08", "Reward budget and funding source", "Needed before rewards are offered", "F13"),
    ("M09", "Project owner's legal jurisdiction and compliance determination", "Needed before any live-money feature", "F13"),
    ("M10", "Permitted market list for the target operator and jurisdiction", "Needed before parlay/prop strategies are executable", "F06"),
]
_QUESTIONS = [
    ("D01", "Does the NFL publish its own betting lines?", "No — widgets show odds, spreads and totals supplied by official bookmaker partners", "", "Definition of 'own lines'", "VERIFIED", "S20", []),
    ("D02", "What exactly is a 'line' for this project (spread, total, moneyline, prop)?", "", "", "Model target definition", "UNVERIFIED", "S20", ["F01"]),
    ("D03", "Which seasons and weeks form training and holdout sets?", "", "", "Any backtest", "UNVERIFIED", "S05", ["F02"]),
    ("D04", "Where will time-stamped opening/closing prices come from, under what licence?", "", "", "CLV, ROI, all scores", "UNVERIFIED", "S18", ["F02"]),
    ("D05", "Are injury/lineup signals executable given NFL integrity restrictions?", "", "", "Injury-based strategy deployment", "UNVERIFIED", "S18", ["F07"]),
    ("D06", "Are club depth charts authoritative enough to define '2nd/3rd/4th string'?", "No — the club labels its chart 'Unofficial Depth Chart'", "", "Whether depth rank is a verified fact", "VERIFIED", "S23", ["F03"]),
    ("D07", "Which jurisdiction and legal structure govern the reward competition?", "", "", "Rewards and live-money features", "UNVERIFIED", "S30", ["F13"]),
    ("D08", "What is the reward budget and who funds it?", "", "", "Reward tiers", "UNVERIFIED", "S11", ["F13"]),
    ("D09", "What minimum sample size and significance threshold defines a skill claim?", "", "", "Passing any validation gate", "UNVERIFIED", "S16", ["F12"]),
    ("D10", "What correlation values exist between signals?", "", "", "Parlay and prop-combo pricing", "UNVERIFIED", "S14", ["F12"]),
    ("D11", "Are same-game prop combos actually offered at the target operator?", "", "", "Prop-combo strategies", "UNVERIFIED", "S22", ["F06"]),
    ("D12", "How will injuries, inactives and depth changes be ingested automatically?", "", "", "Injury tracker build", "UNVERIFIED", "S01", ["F02"]),
    ("D13", "Which official source is the settlement authority for each market?", "", "", "Grading results", "UNVERIFIED", "S10", ["F02"]),
    ("D14", "What does 'remove luck' mean operationally?", "", "", "Leaderboard ranking", "UNVERIFIED", "S13", ["F12"]),
    ("D15", "Is a public leaderboard alone sufficient?", "No — a private holdout ranking is required", "", "Competition design", "VERIFIED", "S13", []),
    ("D16", "Does the repo contain prior data or code to preserve?", "No — base commit contained only a 6-byte README", "", "Migration planning", "VERIFIED", "S29", []),
    ("D17", "Will GitHub Pages build from main:/ after merge?", "", "", "Publishing", "UNVERIFIED", "S28", ["F11"]),
]
PAGES.append(P(
    "decisions.html", "Questions, information & answers", "Decisions", "Before any decision",
    "A decision may reasonably be made only when its blocking question has an answer from a "
    "fetch-verified official source. Blank answer cells are intentional and flagged "
    "UNVERIFIED; the last column suggests how to discover the missing information. "
    "No answer was inferred.",
    [
        T("have", "Information we already HAVE (verified)",
          ["ID", "Information", "Official basis", "Status", "Source"],
          [R([i, text, "Fetch-verified official page", "VERIFIED", SOURCES[s]["url"], s], s)
           for i, text, s in _HAVE]),

        T("missing", "Information we do NOT have",
          ["ID", "Missing information", "Why it is needed", "Value", "Status", "Flag", "Source"],
          [R([i, text, why, "", "UNVERIFIED", f, "No fetch-verified official source", s], s, "unverified", [f])
           for (i, text, why, f), s in zip(_MISSING, ["S01", "S01", "S32", "S23", "S22", "S14", "S13", "S11", "S30", "S22"])],
          intro="The 'Value' column is blank on every row. That is the required behaviour when no official source confirms a value.",
          analysis="Ten discovery targets. Each corresponds to a blocking question below and to a suggestion on the Suggestions page."),

        T("questions", "Blocking questions and answers",
          ["ID", "Question", "Answer (official sources only)", "Missing information", "Decision blocked", "How to discover missing information", "Status", "Source"],
          [R([i, q, ans, "", blocked,
              ("See the verified answer column; no further discovery needed" if st == "VERIFIED" else
               {"D02": "Enumerate target markets from a licensed operator's official market list before writing code",
                "D03": "Use official schedule archives to fix seasons, then pre-register cut-offs before seeing outcomes",
                "D04": "Request an official data licence via the league's official data distributor; record terms",
                "D05": "Confirm permitted markets with a licensed operator; exclude prohibited markets",
                "D07": "Obtain a written compliance determination from the relevant regulator",
                "D08": "Adopt a recognition-only leaderboard until a budget is formally approved",
                "D09": "Pre-register alpha, power and minimum N; apply official multiple-testing correction",
                "D10": "Compute Pearson/Spearman with bootstrap intervals on licensed data; publish blank until then",
                "D11": "Read the operator's approved house rules for the exact jurisdiction",
                "D12": "Define a polling schedule against the official injury report, club charts and inactive list",
                "D13": "Use official league results and approved house rules; store the URL per graded event",
                "D14": "Define skill as out-of-sample, calibration-positive, corrected edge over a null strategy",
                "D17": "Confirm via the official Pages API and fetch the live URL after merge"}.get(i, "Record an official source before answering")),
              st, src],
             src,
             st.lower(), flags)
           for i, q, ans, _, blocked, st, src, flags in _QUESTIONS],
          analysis="Only four answers are available from official sources (D01, D06, D15, D16). Everything else remains a blocking question, which is why the site does not report performance numbers."),
    ]))


# ---------------------------------------------------------------------------
# 6. Suggestions
# ---------------------------------------------------------------------------
_PATHS = [
    ("A", "Lock the evidence layer: source registry, allowlist, row verification, flagged page", "Prevents unverified numbers entering a decision", "Low", "High", "Nothing", "S27"),
    ("B", "Answer blocking questions D01–D17 before building any model", "Converts speculation into a bounded testable scope", "Medium", "High", "A", "S01"),
    ("C", "Build the injury / depth snapshot pipeline", "Creates the only verified decision-relevant dataset currently available", "Medium", "High", "A, B", "S24"),
    ("D", "License historical odds and play-by-play, then compute correlations and gates", "Unblocks every numeric gate and skill test", "High", "High", "A, B, D04", "S18"),
    ("E", "Recognition-only, no-money leaderboard with public/private split", "Tests strategy quality without legal or financial exposure", "Medium", "Medium", "A, B, D07", "S11"),
]
_USABILITY = [
    ("S01", "Global filter box on every table", "Find a row without scrolling", "S29"),
    ("S02", "Sortable column headers", "Compare verified vs unverified rows quickly", "S29"),
    ("S03", "Text badges in addition to colour", "Accessibility: colour alone is ambiguous", "S30"),
    ("S04", "Captured-at timestamp on every live-data snapshot", "Official pages change during the week", "S32"),
    ("S05", "Dedicated source column on every table", "Makes the verification rule visible", "S01"),
    ("S06", "One category per subpage with identical navigation", "Consistent dashboard mental model", "S27"),
    ("S07", "One machine-readable evidence registry as the only URL source", "Prevents link drift and duplicates", "S10"),
    ("S08", "Decision record table: chosen path / chosen by / date", "Makes the pre-implementation choice auditable", "S29"),
    ("S09", "404 page that returns to the dashboard", "No dead ends", "S28"),
    ("S10", "Run the row verifier in CI on every push", "A broken row fails the build, not the reviewer", "S28"),
]
PAGES.append(P(
    "suggestions.html", "Suggestions — choose a path", "Decisions", "Review before implementing",
    "This section exists so a reviewer can compare improvement paths and choose the best "
    "one before any change is implemented. None of the paths below has been implemented as a "
    "product change. The chooser records a local selection only; it does not modify the site.",
    [
        T("paths", "Ranked improvement paths",
          ["Path", "Suggestion", "How it improves decision making", "Effort", "Impact", "Depends on", "Status", "Official basis", "Source"],
          [R([p, s, why, eff, imp, dep, "PROPOSAL — not implemented", "Official reference", src], src, "proposal")
           for p, s, why, eff, imp, dep, src in _PATHS],
          analysis="Path A then B are the lowest-effort, highest-impact steps. Path D is the only route to real correlation values and is currently blocked by the missing data licence."),

        T("usability", "Site usability suggestions",
          ["ID", "Suggestion", "Why it helps", "Status", "Source"],
          [R([i, text, why, "PROPOSAL", "Official reference", src], src, "proposal")
           for i, text, why, src in _USABILITY]),

        T("decision-record", "Decision record (awaiting reviewer)",
          ["Field", "Recorded value", "Status", "Source"],
          [
              R(["Chosen path (A–E)", "", "UNVERIFIED — awaiting review", "S11"], "S11", "unverified", ["F13"], "No path has been chosen by an agent."),
              R(["Chosen by", "", "UNVERIFIED — awaiting review", "S29"], "S29", "unverified", ["F13"], "Intentionally blank."),
              R(["Date of choice", "", "UNVERIFIED — awaiting review", "S29"], "S29", "unverified", ["F13"], "Intentionally blank."),
              R(["Blocking questions still open", "", "UNVERIFIED — see decisions.html", "S01"], "S01", "unverified", ["F02"], "Left blank rather than estimated."),
              R(["Implementation started", "No", "VERIFIED — no change implemented", "S29"], "S29"),
          ],
          intro="These blank cells are the point: no agent may choose the path on the reviewer's behalf.",
          analysis="Once a reviewer records a choice, the decision record should be filled from that choice — not inferred."),
    ]))


# ---------------------------------------------------------------------------
# 7. Official sources
# ---------------------------------------------------------------------------
_verified_sources = [s for s in REGISTRY["sources"] if s["status"] in ("fetch-verified", "local-git-verified")]
PAGES.append(P(
    "sources.html", "Official source registry", "Research", "Every table row's provenance",
    "An entry exists only when the exact URL was opened with a page-fetch tool and the "
    "returned title and content matched the recorded excerpt. Local repository facts are "
    "verified with git and the official GitHub API. Third-party blogs, aggregators and "
    "search snippets are never used as sources for values.",
    [
        T("source-registry", "Fetch-verified official sources",
          ["ID", "Official site", "Fetched title", "Verification status", "Source"],
          [R([s["id"], s["url"], s["title"], s["status"].upper(), s["url"], s["id"]], s["id"], "verified")
           for s in _verified_sources],
          analysis="The registry is machine-readable at research/source-registry.json. tools/verify.py refuses any row whose source is not on this list."),

        T("source-excluded", "Discovered but deliberately NOT used as evidence",
          ["ID", "URL", "Reason excluded", "Status", "Source"],
          [R([s["id"], s["url"],
              {"S33": "Linked from official standings but content not fetched",
               "S34": "Search snippet only; not fetch-verified",
               "S35": "Linked from an official article but content not fetched"}[s["id"]],
              "EXCLUDED", "See research/sources.md", "S01"], "S01", "needs-review", ["F08"])
           for s in REGISTRY["sources"] if s["id"] in ("S33", "S34", "S35")]),
    ]))


# ---------------------------------------------------------------------------
# 8. Verified data
# ---------------------------------------------------------------------------
_STANDINGS = [
    ("Buffalo Bills", "7", "1", "0", "0.875", "256", "187", "69"),
    ("San Francisco 49ers", "7", "1", "0", "0.875", "235", "156", "79"),
    ("Chicago Bears", "7", "2", "0", "0.778", "241", "184", "57"),
    ("Denver Broncos", "7", "2", "0", "0.778", "198", "186", "12"),
    ("Detroit Lions", "6", "2", "0", "0.750", "222", "189", "33"),
    ("Kansas City Chiefs", "6", "2", "0", "0.750", "202", "143", "59"),
    ("New York Giants", "5", "2", "1", "0.688", "182", "172", "10"),
    ("New England Patriots", "5", "4", "0", "0.556", "211", "207", "4"),
    ("Washington Commanders", "2", "5", "1", "0.313", "172", "202", "-30"),
    ("Los Angeles Chargers", "0", "8", "0", "0.000", "121", "219", "-98"),
]
_SCHEDULE = [
    ("Thu 12 Nov 2026", "8:15 PM", "Washington Commanders", "New York Giants", "Prime Video", "S05"),
    ("Sun 15 Nov 2026", "9:30 AM", "New England Patriots", "Detroit Lions", "FOX / FOX Deportes", "S05"),
    ("Sun 15 Nov 2026", "1:00 PM", "Kansas City Chiefs", "Atlanta Falcons", "CBS", "S05"),
    ("Sun 15 Nov 2026", "1:00 PM", "Houston Texans", "Cleveland Browns", "FOX", "S05"),
    ("Sun 15 Nov 2026", "1:00 PM", "Minnesota Vikings", "Green Bay Packers", "FOX", "S05"),
    ("Sun 15 Nov 2026", "1:00 PM", "Miami Dolphins", "Indianapolis Colts", "CBS", "S05"),
]
_GAMECENTER = [
    ("Washington Commanders", "Points per game", "21.5", "21st", "S07"),
    ("New York Giants", "Points per game", "22.8", "16th", "S07"),
    ("Washington Commanders", "Yards per game", "325.4", "20th", "S07"),
    ("New York Giants", "Yards per game", "333.1", "14th", "S07"),
    ("Washington Commanders", "Time of possession", "30:08", "16th", "S07"),
    ("New York Giants", "Time of possession", "33:42", "2nd", "S07"),
    ("Washington Commanders", "Total defensive sacks", "17", "19th", "S07"),
    ("New York Giants", "Total defensive sacks", "16", "24th", "S07"),
    ("Washington Commanders", "Turnover differential", "+7", "3rd", "S07"),
    ("New York Giants", "Turnover differential", "-2", "22nd", "S07"),
]
PAGES.append(P(
    "data.html", "Verified data snapshots", "Research", f"Captured {CAPTURED}",
    "All values on this page were copied from fetch-verified official pages at the captured "
    "time. Official pages change during the week, so these are point-in-time snapshots. "
    "No odds, prices or model outputs appear here because none could be verified from an "
    "official source.",
    [
        T("standings", "2026 NFL league standings (selected rows)",
          ["Team", "W", "L", "T", "PCT", "PF", "PA", "Net points", "Status", "Source"],
          [R(list(r) + ["VERIFIED", "NFL.com 2026 standings", "S03"], "S03") for r in _STANDINGS],
          intro="Column meanings follow the official standings legend: W wins, L losses, T ties, PCT winning percentage, PF points for, PA points against."),

        T("schedule", "2026 Week 10 schedule (selected games)",
          ["Date", "Kickoff", "Away", "Home", "Broadcaster", "Status", "Source"],
          [R(list(r[:5]) + ["VERIFIED", "NFL.com schedule", r[5]], r[5]) for r in _SCHEDULE]),

        T("gamecenter", "Commanders at Giants — official game-center metrics",
          ["Team", "Metric", "Value", "Rank", "Status", "Source"],
          [R([t, m, v, rk, "VERIFIED", "NFL.com game center", src], src) for t, m, v, rk, src in _GAMECENTER]),

        T("data-gaps", "Data that could NOT be verified",
          ["Dataset", "Value", "Why blank", "Status", "Flag", "Source"],
          [
              R(["Opening / closing market prices", "", "No fetch-verified official archive", "UNVERIFIED", "F02", "S20"], "S20", "unverified", ["F02"]),
              R(["Historical player-prop prices", "", "No fetch-verified official archive", "UNVERIFIED", "F02", "S22"], "S22", "unverified", ["F02"]),
              R(["Play-by-play / snap counts", "", "Licence and access unresolved", "UNVERIFIED", "F02", "S18"], "S18", "unverified", ["F02"]),
              R(["Archived weekly injury reports", "", "Only current week verified", "UNVERIFIED", "F02", "S01"], "S01", "unverified", ["F02"]),
              R(["Archived inactive lists", "", "Mechanism verified, data not archived here", "UNVERIFIED", "F05", "S24"], "S24", "unverified", ["F05"]),
          ],
          analysis="These five gaps are the reason the correlation page and leaderboard contain blank result cells."),
    ]))


# ---------------------------------------------------------------------------
# 9. Strategies
# ---------------------------------------------------------------------------
_INPUTS = [
    ("I01", "Weekly injury report", "Position, injury, practice status, game status", "Availability / replacement features", "S01"),
    ("I02", "Game status definitions", "Questionable / Doubtful / Out; DNP / Limited / Full", "Categorical encoding", "S02"),
    ("I03", "Game Day Administration Report", "Inactive list at the 90-minute meeting", "Final availability label", "S24"),
    ("I04", "Club depth chart", "First / Second / Third / Fourth (unofficial)", "Replacement-depth feature", "S23"),
    ("I05", "2026 standings", "W/L/T, PCT, PF, PA, net points, home/road, streak", "Team-strength features", "S03"),
    ("I06", "Player stat categories", "Passing, rushing, receiving, tackles, interceptions, kicking", "Player-prop features", "S04"),
    ("I07", "Schedule", "Dates, kickoff windows, matchups, broadcasters", "Rest / travel / context", "S05"),
    ("I08", "Game-center metrics", "PPG, YPG, TOP, sacks, INT, turnover differential", "Matchup features", "S07"),
    ("I09", "Next Gen Stats", "Separation, air distance, speed, time-to-sack metrics", "Advanced signal features", "S08"),
    ("I10", "2026 NGS run-scheme models", "16 run-concept labels, blocking matchups", "Line-play features", "S09"),
    ("I11", "Official play-by-play distribution", "Real-time official statistics via league data partner", "Drive/play modelling", "S18"),
]
_STRATEGIES = [
    ("ST01", "Single bet", "Model spread vs market spread divergence", "Licensed opening/closing lines", "S20"),
    ("ST02", "Single bet", "Model total vs market total divergence", "Licensed totals + official scoring", "S03"),
    ("ST03", "Single bet", "Moneyline probability vs implied market probability", "Licensed moneylines", "S04"),
    ("ST04", "Single bet", "Starting-QB replacement depth vs line movement", "Depth chart + inactives + lines", "S23"),
    ("ST05", "Single bet", "Defensive starter Out + backup depth rank", "Injury report + depth chart + lines", "S01"),
    ("ST06", "Single bet", "Offensive-line backup chain vs pass-rush matchup", "Depth chart + NGS", "S09"),
    ("ST07", "Single bet", "Rest / travel asymmetry from official schedule", "Schedule archive", "S05"),
    ("ST08", "Parlay", "Cross-game independent-leg parlay after correlation screen", "Multi-game lines + correlation matrix", "S22"),
    ("ST09", "Parlay", "Same-game parlay where the operator explicitly prices correlation", "Operator SGP rules and prices", "S22"),
    ("ST10", "Parlay", "Related-outcome detection to reject non-executable combos", "Operator rule set", "S22"),
    ("ST11", "Prop combo", "QB passing overs with WR receiving overs (same game)", "Player props + participation", "S04"),
    ("ST12", "Prop combo", "Backup RB volume when starter is Out", "Injury report + depth chart + props", "S01"),
    ("ST13", "Prop combo", "Defensive backup exposure to opposing WR props", "Depth chart + props", "S36"),
    ("ST14", "Prop combo", "Player participation / void-risk screen", "Operator settlement rules", "S22"),
    ("ST15", "All", "Null / sham strategy control, identical stake", "Outcomes only", "S13"),
]
PAGES.append(P(
    "strategies.html", "Strategies & signals", "Research", "Originating your own lines",
    "NFL.com does not publish its own betting lines: its widgets show odds, spreads and "
    "totals supplied by official bookmaker partners. 'Originating my own lines' is therefore "
    "defined as computing an independent pre-game probability/line from official league data "
    "and comparing it with a licensed market line. A difference is a candidate signal, not an edge.",
    [
        T("line-basis", "Official basis for line origination",
          ["ID", "Official fact", "Implication for this project", "Status", "Source"],
          [
              R(["L01", "NFL widgets show partner-supplied odds, spreads and over/under", "There is no official NFL line to copy; a model line must be self-computed", "VERIFIED", "NFL Support", "S20"], "S20"),
              R(["L02", "Predicted Score is a Genius Sports algorithm over historical/season data", "A league-official precedent for an algorithmically produced pre-game number", "VERIFIED", "NFL Support", "S21"], "S21"),
              R(["L03", "Official play-by-play and Next Gen Stats are distributed via the league data partner", "Bulk feature data requires a licence", "VERIFIED", "NFL.com", "S18"], "S18"),
              R(["L04", "Model coefficients for our own line", "", "UNVERIFIED", "", "S20"], "S20", "unverified", ["F02", "F12"], "No dataset exists to fit a model; no coefficient was invented."),
          ]),

        T("inputs", "Official data that may feed a model",
          ["ID", "Input", "Fields available", "Model use", "Status", "Source"],
          [R([i, name, fields, use, "VERIFIED", "Official page", src], src) for i, name, fields, use, src in _INPUTS]),

        T("strategy-inventory", "Candidate signal inventory — not validated",
          ["ID", "Bet type", "Signal hypothesis", "Required data", "Correlation", "Edge / ROI", "Gate result", "Status", "Source"],
          [R([i, kind, hyp, data, "", "", "NOT RUN", "UNVERIFIED", src], src, "unverified", ["F02", "F12"],
              "No strategy has been scored; blank numeric cells are intentional.")
           for i, kind, hyp, data, src in _STRATEGIES],
          intro="These are hypotheses, not findings. Every performance cell is blank and flagged UNVERIFIED.",
          analysis="Singles are the only bet type that does not require a measured dependence structure. Parlays and prop combos additionally require leg-correlation estimates and operator executability checks."),

        T("bet-type-rules", "Bet-type constraints from official sources",
          ["Bet type", "Official constraint", "Consequence for strategy design", "Status", "Source"],
          [
              R(["Single bet", "Market prices come from official bookmaker partners, not the NFL", "Compare a self-computed line to a licensed price", "VERIFIED", "NFL Support", "S20"], "S20"),
              R(["Parlay", "Related-outcome parlays are prohibited by approved house rules", "Reject prohibited leg combinations before scoring", "VERIFIED", "Massachusetts Gaming Commission", "S22"], "S22"),
              R(["Same-game parlay", "Explicitly carved out as a separately priced product", "Use the operator's own correlated price", "VERIFIED", "Massachusetts Gaming Commission", "S22"], "S22"),
              R(["Player prop combo", "Player-specific selections can be cancelled if the player does not participate", "Model participation and void risk", "VERIFIED", "Massachusetts Gaming Commission", "S22"], "S22"),
              R(["All", "NFL integrity policy prohibits wagers tied to injuries/officiating", "Confirm market permissibility before backtesting", "VERIFIED", "NFL.com", "S18"], "S18"),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 10. Validation gates
# ---------------------------------------------------------------------------
_GATES = [
    ("G01", "Data provenance", "Every input row resolves to a fetch-verified official URL", "100% of rows", "S01"),
    ("G02", "No leakage", "Features available strictly before kickoff", "Zero future fields", "S13"),
    ("G03", "Pre-registration", "Hypothesis, features, alpha and N frozen before evaluation", "Committed spec", "S12"),
    ("G04", "Timestamp integrity", "Injury/depth snapshots carry a captured-at time", "Timestamp on every row", "S32"),
    ("G05", "Probability calibration", "Brier score, a strictly proper scoring rule", "Better than market baseline", "S15"),
    ("G06", "Discrimination", "Pearson correlation between predicted and realised residual", "CI excludes zero", "S14"),
    ("G07", "Rank / robustness", "Spearman correlation for non-normal or ordinal features", "CI excludes zero", "S17"),
    ("G08", "Multiple testing", "FWER / FDR correction across all candidate strategies", "Corrected p below pre-registered alpha", "S16"),
    ("G09", "Luck control", "Null / sham strategy with identical stake and sample", "Beats null distribution", "S13"),
    ("G10", "Out-of-sample", "Walk-forward holdout never reused for tuning", "Private-score gain positive", "S13"),
    ("G11", "Market realism", "Closing-line value against licensed prices, net of vig", "Positive after costs", "S20"),
    ("G12", "Executability", "Legs permitted by approved rules; integrity policy respected", "Zero prohibited legs", "S22"),
]
_SKILL = [
    ("1", "Freeze hypothesis, features, alpha, minimum N and holdout before looking at outcomes", "S12"),
    ("2", "Separate public (development) and private (final) evaluation data", "S13"),
    ("3", "Exclude future information and test explicitly for leakage", "S13"),
    ("4", "Score probabilities with a strictly proper scoring rule rather than win/loss counts", "S15"),
    ("5", "Correct for the number of strategies tried (FWER / FDR)", "S16"),
    ("6", "Compare against a null / sham strategy with identical staking", "S13"),
    ("7", "Require out-of-sample repeatability across seasons, not a single hot streak", "S17"),
    ("8", "Require positive results after the bookmaker margin and only in executable markets", "S22"),
    ("9", "Publish blank / unverified results rather than rounding or estimating them", "S01"),
]
PAGES.append(P(
    "validation.html", "Validation gates", "Validation", "Every strategy must pass",
    "A strategy is treated as skill-based only if it survives pre-registered, out-of-sample "
    "gates and beats a null control after multiple-testing correction. No dataset exists in "
    "this repository to run any gate, so every result cell is blank and flagged UNVERIFIED.",
    [
        T("gates", "Gate catalogue",
          ["Gate", "What it tests", "Metric / method", "Pass standard (proposed)", "Result", "Status", "Source"],
          [R([g, what, metric, standard, "", "UNVERIFIED — NOT RUN", src], src, "unverified", ["F02", "F12"],
              "Pass standards are proposals, not measured values.")
           for g, what, metric, standard, src in _GATES],
          intro="The gate structure mirrors the official Big Data Bowl evaluation table, which publishes literal PASS/FAIL passing standards."),

        T("skill-protocol", "Removing luck — nine-step operational definition",
          ["Step", "Control", "Official basis", "Status", "Source"],
          [R([n, text, "Official documentation", "PROPOSAL", src], src, "proposal") for n, text, src in _SKILL],
          analysis="'Selectively skill based' means a strategy is admitted to the leaderboard only after all nine steps. No strategy in this build has been admitted."),

        T("official-methods", "Official methods referenced by the gates",
          ["Method", "What the official documentation says", "Used by", "Status", "Source"],
          [
              R(["scipy.stats.pearsonr", "Pearson correlation coefficient and p-value for testing non-correlation", "G06, correlations page", "VERIFIED", "SciPy manual", "S14"], "S14"),
              R(["sklearn.metrics.brier_score_loss", "Brier score is the mean squared difference between predicted probability and outcome; a strictly proper scoring rule", "G05", "VERIFIED", "scikit-learn docs", "S15"], "S15"),
              R(["statsmodels multipletests", "Test results and p-value correction for multiple tests (bonferroni, holm, fdr_bh and others)", "G08", "VERIFIED", "statsmodels docs", "S16"], "S16"),
              R(["NIST/SEMATECH e-Handbook", "Official statistical methods reference (DOI 10.18434/M32189)", "G07, step 7", "VERIFIED", "NIST", "S17"], "S17"),
              R(["Kaggle public/private leaderboard", "A high public score does not guarantee a high private score; data leakage creates unrealistically high performance", "G02, G09, G10", "VERIFIED", "Kaggle docs", "S13"], "S13"),
              R(["Big Data Bowl 2027 evaluation", "Explicit PASS/FAIL requirements and weighted evaluation components", "G03", "VERIFIED", "Official competition", "S12"], "S12"),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 11. Correlation values
# ---------------------------------------------------------------------------
_CORR = [
    ("C01", "Model spread", "Market closing spread", "Pearson + bootstrap CI", "S14"),
    ("C02", "Model total", "Market closing total", "Pearson + bootstrap CI", "S15"),
    ("C03", "QB starter depth rank", "Team points", "Spearman (ordinal)", "S17"),
    ("C04", "Defensive backup count", "Opponent passing yards", "Pearson", "S23"),
    ("C05", "OL backup chain length", "Sacks allowed", "Pearson", "S09"),
    ("C06", "WR1 availability", "WR1 receiving props", "Point-biserial / phi", "S01"),
    ("C07", "Game total", "Two same-game prop legs", "Joint binary-leg correlation", "S22"),
    ("C08", "Spread leg", "Total leg (same game)", "Joint binary-leg correlation", "S22"),
    ("C09", "Cross-game leg A", "Cross-game leg B", "Measured, never assumed", "S13"),
    ("C10", "Injury signal", "Line movement", "Pearson on time-stamped pairs", "S18"),
]
PAGES.append(P(
    "correlations.html", "Correlation values", "Validation", "Determined only from data",
    "Determining a correlation value requires a joint dataset of signal, outcome and market "
    "price across many games. No such dataset is available from a fetch-verified official "
    "source in this repository. Therefore every numeric cell below is blank and flagged "
    "UNVERIFIED. The table defines exactly what must be computed; it does not invent a coefficient.",
    [
        T("corr-matrix", "Correlation pairs to be determined",
          ["Pair", "Variable A", "Variable B", "Method", "Pearson r", "Spearman rho", "95% CI", "p (corrected)", "Status", "Source"],
          [R([i, a, b, m, "", "", "", "", "UNVERIFIED", src], src, "unverified", ["F02", "F12"],
              "No coefficient was computed or estimated.")
           for i, a, b, m, src in _CORR],
          analysis="The blank coefficients are the required output of the verification rule: no official source, no value."),

        T("corr-why", "Why leg correlation controls parlays",
          ["#", "Official rule / fact", "Effect on strategy design", "Correlation value", "Status", "Source"],
          [
              R(["1", "Approved house rules prohibit parlays with two or more related outcomes", "Reject prohibited combinations before scoring", "", "UNVERIFIED", "S22"], "S22", "unverified", ["F12"]),
              R(["2", "Same Game Parlay is a separately priced, explicitly carved-out product", "Use the operator's own correlated price", "", "UNVERIFIED", "S22"], "S22", "unverified", ["F12"]),
              R(["3", "NFL integrity policy prohibits injury-linked and knowable-in-advance wagers", "Exclude non-executable injury signals", "", "UNVERIFIED", "S18"], "S18", "unverified", ["F07", "F12"]),
              R(["4", "Pearson r measures linear association and provides a p-value for non-correlation", "Primary numeric method once data exists", "", "UNVERIFIED", "S14"], "S14", "unverified", ["F12"]),
              R(["5", "Multiple-test correction controls FWER/FDR across many candidate strategies", "Prevents a lucky correlation from looking like skill", "", "UNVERIFIED", "S16"], "S16", "unverified", ["F12"]),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 12. Leaderboard
# ---------------------------------------------------------------------------
PAGES.append(P(
    "leaderboard.html", "Leaderboard & rewards", "Validation", "Competition design",
    "The competition design mirrors the NFL's official crowdsourced analytics competition: "
    "judged submissions, a documented prize pool, explicit PASS/FAIL standards and a "
    "public/private leaderboard split. This project is not affiliated with or endorsed by "
    "the NFL or Kaggle; those pages are cited as design references. No live-money feature "
    "is enabled.",
    [
        T("leaderboard-structure", "Competition structure",
          ["Element", "Proposed rule", "Verified official analogue", "This project's value", "Status", "Source"],
          [
              R(["Eligibility", "Pre-register the strategy before the holdout window", "Official competition submission rules", "", "UNVERIFIED", "S12"], "S12", "unverified", ["F12"]),
              R(["Public leaderboard", "In-season development sample only", "Public leaderboard: visible during competition, based on a sample of test data", "", "UNVERIFIED", "S13"], "S13", "unverified", ["F12"]),
              R(["Private leaderboard", "Final ranking on untouched holdout", "Private leaderboard: final ranking on the remainder of the test data", "", "UNVERIFIED", "S13"], "S13", "unverified", ["F12"]),
              R(["Passing standard", "Explicit PASS/FAIL per gate", "2027 Big Data Bowl evaluation table uses [PASS/FAIL]", "", "UNVERIFIED", "S12"], "S12", "unverified", ["F12"]),
              R(["Judging", "Independent review against frozen specs", "NFL club analytics staff judge each submission", "VERIFIED", "S11"], "S11"),
              R(["Prize pool", "Recognition-only until D07/D08 are answered", "$100,000 in prize money for Big Data Bowl contestants", "", "UNVERIFIED", "S11"], "S11", "unverified", ["F13"]),
              R(["Rewards", "No cash, no wagering, no payments in this build", "2027: Open Track $45,000, University Track $45,000, Grand Prize $10,000", "VERIFIED", "S12"], "S12"),
              R(["Integrity", "Exclude markets prohibited by league policy", "NFL prohibits wagers tied to officiating and injuries", "VERIFIED", "S18"], "S18"),
              R(["Harm minimisation", "No live-money features; link help resources", "NFL responsible-betting programme and NCPG", "VERIFIED", "S30"], "S30"),
          ]),

        T("leaderboard-current", "Current standings (no strategy has been scored)",
          ["Rank", "Strategy", "Public score", "Private score", "Gates passed", "Reward", "Status", "Source"],
          [
              R(["", "ST01 single spread divergence", "", "", "", "", "UNVERIFIED — NOT RUN", "S20"], "S20", "unverified", ["F02", "F12"]),
              R(["", "ST08 cross-game parlay", "", "", "", "", "UNVERIFIED — NOT RUN", "S22"], "S22", "unverified", ["F02", "F12"]),
              R(["", "ST11 QB + WR prop combo", "", "", "", "", "UNVERIFIED — NOT RUN", "S04"], "S04", "unverified", ["F02", "F12"]),
              R(["", "ST15 null / sham control", "", "", "", "", "UNVERIFIED — NOT RUN", "S13"], "S13", "unverified", ["F02", "F12"]),
          ],
          intro="Rank, scores, gate counts and rewards are blank because no official dataset exists to compute them. Nothing is inferred.",
          analysis="An empty leaderboard is the correct state: a leaderboard with invented scores would be a hallucination."),

        T("reward-reference", "Verified official reward reference (design analogue only)",
          ["Item", "Value", "Official source", "Status", "Source"],
          [
              R(["Big Data Bowl prize pool", "$100,000 in prize money", "NFL Football Operations", "VERIFIED", "S11"], "S11"),
              R(["2027 Open Track", "$45,000", "Official 2027 competition page", "VERIFIED", "S12"], "S12"),
              R(["2027 University Track", "$45,000", "Official 2027 competition page", "VERIFIED", "S12"], "S12"),
              R(["2027 Grand Prize", "$10,000", "Official 2027 competition page", "VERIFIED", "S12"], "S12"),
              R(["2027 final submission deadline", "January 6, 2027", "Official 2027 competition page", "VERIFIED", "S12"], "S12"),
              R(["This project's reward budget", "", "Not supplied; gate D08", "UNVERIFIED", "S11"], "S11", "unverified", ["F13"]),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 13. Injuries & depth
# ---------------------------------------------------------------------------
_INJURY = [
    ("Commanders", "John Bates", "TE", "", "Full Participation in Practice", ""),
    ("Commanders", "Treylon Burks", "WR", "", "Did Not Participate In Practice", ""),
    ("Commanders", "Jayden Daniels", "QB", "", "Full Participation in Practice", ""),
    ("Commanders", "Matt Gulbin", "C", "", "Full Participation in Practice", ""),
    ("Commanders", "Chig Okonkwo", "TE", "", "Full Participation in Practice", ""),
    ("Commanders", "Lucas Patrick", "C", "Concussion", "Did Not Participate In Practice", "Out"),
    ("Commanders", "Amik Robertson", "CB", "", "Limited Participation in Practice", ""),
    ("Commanders", "Shy Tuttle", "DT", "", "Full Participation in Practice", ""),
    ("Commanders", "Colson Yankoff", "TE", "Knee", "Did Not Participate In Practice", "Out"),
    ("Giants", "Abdul Carter", "LB", "", "Full Participation in Practice", ""),
    ("Giants", "Jermaine Eluemunor", "T", "", "Full Participation in Practice", ""),
    ("Giants", "Malik Harrison", "LB", "Groin", "Limited Participation in Practice", "Questionable"),
    ("Giants", "Colton Hood", "CB", "", "Full Participation in Practice", ""),
    ("Giants", "Theo Johnson", "TE", "", "Full Participation in Practice", ""),
    ("Giants", "Charlie Jones", "WR", "", "Full Participation in Practice", ""),
    ("Giants", "J.J. McCarthy", "QB", "", "Full Participation in Practice", ""),
    ("Giants", "Darnell Mooney", "WR", "", "Full Participation in Practice", ""),
    ("Giants", "Malik Nabers", "WR", "", "Full Participation in Practice", ""),
    ("Giants", "Cam Skattebo", "RB", "", "Full Participation in Practice", ""),
    ("Giants", "Andrew Thomas", "T", "", "Full Participation in Practice", ""),
]
_DEPTH = [
    ("Offense", "QB", "Patrick Mahomes", "Justin Fields", "Garrett Nussmeier", ""),
    ("Offense", "TE", "Travis Kelce", "Noah Gray", "Jared Wiley", "Jake Briningstool"),
    ("Offense", "RB", "Kenneth Walker", "Emmett Johnson", "Jaydn Ott", ""),
    ("Offense", "WR", "Rashee Rice", "Jalen Royals", "Andrew Armstrong", ""),
    ("Offense", "LT", "Kahlil Benson", "Diego Pounds", "", ""),
    ("Defense", "CB", "Mansoor Delane", "Kristian Fulton", "Melvin Smith", ""),
    ("Defense", "S", "Chamarri Conner", "Jaden Hicks", "Xavier Nwankpa", ""),
    ("Defense", "DE", "Felix Anudike-Uzomah", "Ashton Gillotte", "", ""),
    ("Defense", "LB", "Drue Tranquill", "Jeffrey Bassa", "", ""),
    ("Defense", "DT", "Chris Jones", "Peter Woods", "", ""),
]
_TRACKER = [
    ("player_id", "Official NFL.com player slug", "No", "VERIFIED", "S01"),
    ("club, position", "Verbatim from official report row", "No", "VERIFIED", "S01"),
    ("injury_text", "Verbatim injury field; blank if absent", "No", "VERIFIED", "S01"),
    ("practice_status", "DNP / Limited / Full, verbatim", "No", "VERIFIED", "S02"),
    ("game_status", "Questionable / Doubtful / Out / blank", "No", "VERIFIED", "S02"),
    ("depth_rank", "1–4 from club chart, with 'unofficial' marker", "No", "VERIFIED", "S23"),
    ("unit", "offense / defense / special teams", "No", "VERIFIED", "S23"),
    ("inactive_final", "Game Day Administration Report at 90-minute meeting", "No", "VERIFIED", "S24"),
    ("captured_at_utc", "Timestamp of each snapshot", "No", "VERIFIED", "S32"),
    ("replacement_depth", "Computed depth rank of the player who actually took the snaps", "Yes", "UNVERIFIED", "S01"),
    ("deficiency_index", "Computed unit-level weakness from replacements", "Yes", "UNVERIFIED", "S01"),
]
PAGES.append(P(
    "injuries.html", "Injuries & depth", "Tracking", f"Snapshots captured {CAPTURED}",
    "Three distinct layers must be tracked: the weekly official injury report, club-published "
    "depth charts with First through Fourth string, and the definitive inactive list in the "
    "Game Day Administration Report. Blank cells below are blank on the official source; they "
    "were not filled in.",
    [
        T("injury-facts", "Verified official rules that constrain the tracker",
          ["ID", "Fact", "Design consequence", "Status", "Source"],
          [
              R(["I01", "Week 10 injury report lists Player, Position, Injuries, Practice Status, Game Status", "Mirror the exact schema", "VERIFIED", "NFL.com", "S01"], "S01"),
              R(["I02", "Practice status is DNP / Limited (<100% of normal reps) / Full (100%)", "Use verbatim codes, not probabilities", "VERIFIED", "NFL.com", "S02"], "S02"),
              R(["I03", "Questionable = uncertain; Doubtful = unlikely; Out = will not play; Probable eliminated", "Never attach a percentage to a status", "VERIFIED", "NFL.com", "S02"], "S02"),
              R(["I04", "Club depth chart exposes First–Fourth but is labelled 'Unofficial Depth Chart'", "Store a source-quality marker", "VERIFIED", "Chiefs official site", "S23"], "S23"),
              R(["I05", "Game Day Administration Report with inactive list is exchanged at the 90-minute meeting", "Final availability checkpoint", "VERIFIED", "NFL Football Operations", "S24"], "S24"),
              R(["I06", "47/48-player game-day active list from a 53-player roster", "Model who can actually dress", "VERIFIED", "NFL.com", "S25"], "S25"),
              R(["I07", "Game Ops Manual requires certified athletic-trainer injury spotters", "In-game injuries are a separate stream", "VERIFIED", "NFL Football Operations", "S26"], "S26"),
              R(["I08", "NFL integrity policy prohibits wagers tied to injuries", "Check market permissibility", "VERIFIED", "NFL.com", "S18"], "S18"),
          ]),

        T("injury-snapshot", "Week 10 injury snapshot — Commanders at Giants, Thu 12 Nov 2026",
          ["Club", "Player", "Pos", "Injury", "Practice status", "Game status", "Status", "Source"],
          [R(list(r) + ["VERIFIED", "Official NFL injury report", "S01"], "S01") for r in _INJURY],
          intro="Empty Injury / Game Status cells are empty on the official report. They are not filled in."),

        T("depth-snapshot", "Chiefs depth snapshot — offense and defense",
          ["Unit", "Position", "1st", "2nd", "3rd", "4th", "Status", "Source"],
          [R(list(r) + ["VERIFIED — club-labelled unofficial", "Chiefs official depth chart", "S23"], "S23") for r in _DEPTH],
          intro="This directly addresses 2nd, 3rd and 4th string replacements on both offense and defense. Source quality caveat: the club calls this an 'Unofficial Depth Chart'."),

        T("tracker-schema", "Tracker schema (design)",
          ["Field", "Definition / source of truth", "Computed?", "Value", "Status", "Source"],
          [R([f, d, comp, "" if st == "UNVERIFIED" else "As specified at left", st,
              "No licensed dataset" if st == "UNVERIFIED" else "Official source", src],
             src, st.lower(), ["F02", "F03"] if st == "UNVERIFIED" else [])
           for f, d, comp, st, src in _TRACKER],
          analysis="replacement_depth and deficiency_index are the two fields the brief asks the system to 'know'. Both require per-snap participation data that is not available from any fetch-verified official source here, so both are blank and flagged."),
    ]))


# ---------------------------------------------------------------------------
# 14. Methodology
# ---------------------------------------------------------------------------
PAGES.append(P(
    "methodology.html", "Verification methodology", "Governance", "Line by line",
    "The site is generated from one data file. Every rendered row is written to "
    "data/records.json and checked again by tools/verify.py against the generated HTML. "
    "This is what 'verify line by line' means operationally here.",
    [
        T("protocol", "Verification protocol",
          ["Step", "Check", "Enforced by", "Failure behaviour", "Status", "Source"],
          [
              R(["1", "Only official first-party domains may appear as sources", "Domain allowlist in source-registry.json", "Verifier fails", "VERIFIED", "Registry", "S01"], "S01"),
              R(["2", "Each URL must be opened and matched to a title and excerpt", "research/source-registry.json", "Not marked verified", "VERIFIED", "Registry", "S01"], "S01"),
              R(["3", "Every table row carries at least one official source link", "tools/verify.py", "Build fails", "VERIFIED", "Verifier", "S29"], "S29"),
              R(["4", "Unconfirmable values are blank cells, not estimates", "data/content.py + CSS blank class", "Build fails if text appears", "VERIFIED", "Generator", "S29"], "S29"),
              R(["5", "Unverified rows carry an UNVERIFIED badge and a flag ID", "Generator", "Build fails", "VERIFIED", "Generator", "S29"], "S29"),
              R(["6", "Every internal link resolves to a file that exists", "tools/verify.py link check", "Build fails", "VERIFIED", "Verifier", "S27"], "S27"),
              R(["7", "Every page uses identical navigation", "Generator + verifier", "Build fails", "VERIFIED", "Generator", "S27"], "S27"),
              R(["8", "CI reruns the verifier on every push and PR", ".github/workflows/verify.yml", "Check fails", "PROPOSAL", "GitHub Docs", "S28"], "S28", "proposal"),
              R(["9", "Pages deployment is confirmed after merge", "Official Pages build API + live fetch", "Retry until live", "PROPOSAL", "GitHub Docs", "S28"], "S28", "proposal"),
              R(["10", "Flagged items are published and explicitly non-blocking", "flagged.html", "Does not block merge", "VERIFIED", "Flagged page", "S18"], "S18"),
              R(["11", "No third-party blog, tip site or search snippet supplies a value", "research/sources.md exclusion list", "Value stays blank", "VERIFIED", "Registry", "S01"], "S01"),
              R(["12", "All live-data snapshots carry a captured-at timestamp", "Page intro + this document", "Flag F14", "VERIFIED", "NFL.com", "S32"], "S32"),
          ]),

        T("legend", "Reading the tables",
          ["Badge / marker", "Meaning", "What to do", "Status", "Source"],
          [
              R(["VERIFIED", "Value copied from a fetch-verified official page", "Use it, and click the source to review", "VERIFIED", "Source registry", "S01"], "S01"),
              R(["PROPOSAL", "Design or analysis, not a sourced NFL fact", "Review and choose a path before implementing", "VERIFIED", "Project brief", "S29"], "S29"),
              R(["UNVERIFIED", "No official source confirms the value; cell is blank", "Complete the discovery suggestion, then re-source", "VERIFIED", "Verification rule", "S29"], "S29"),
              R(["NEEDS REVIEW", "Published on Flagged for Review; does not block anything", "Review after launch and request changes", "VERIFIED", "Project brief", "S29"], "S29"),
              R(["Blank cell", "Deliberately empty, never inferred", "Do not fill in without an official source", "VERIFIED", "Verification rule", "S29"], "S29"),
              R(["↗", "Opens the official source in a new tab", "Manual review", "VERIFIED", "GitHub Docs", "S27"], "S27"),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 15. Flagged for review
# ---------------------------------------------------------------------------
_FLAGS = [
    ("F01", "high", "No official NFL-published betting lines were found; NFL.com widgets show partner odds", "Defines 'own lines' as a self-computed model line", "S20", "https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL"),
    ("F02", "high", "No licensed historical odds, play-by-play or injury-report archive exists here", "Correlations, CLV and strategy scores cannot be computed", "S01", "https://www.nfl.com/injuries/league/2026/REG10"),
    ("F03", "medium", "Club depth charts are labelled 'Unofficial Depth Chart' by the club itself", "2nd/3rd/4th ordering is a club estimate, not a league fact", "S23", "https://www.chiefs.com/team/depth-chart"),
    ("F04", "medium", "Game-status labels carry no published probability; 'Probable' was eliminated", "Third-party percentages must not be used as verified values", "S02", "https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693"),
    ("F05", "medium", "Final availability checkpoint is the 90-minute inactive list, not the weekly report", "A weekly-report-only lineup model is incomplete", "S24", "https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep"),
    ("F06", "medium", "Related-outcome parlays are prohibited; same-game parlays are a carved-out product", "Parlay strategies must target an executable market", "S22", "https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf"),
    ("F07", "medium", "NFL integrity policy prohibits wagers tied to injuries/officiating", "Some injury signals may be non-executable", "S18", "https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners"),
    ("F08", "medium", "Search index showed mismatched titles, weeks and URL slugs for injury pages", "Only canonical fetch-verified URLs are used", "S32", "https://www.nfl.com/injuries/"),
    ("F09", "low", "Several official URLs redirect to canonical URLs; a support article changed numeric slug", "Registry stores canonical URLs; recheck on refresh", "S10", "https://operations.nfl.com/rules-officiating/2026-nfl-rulebook"),
    ("F10", "low", "Environment pins this session to one branch", "Per-session worktrees cannot be created; disjoint scopes used", "S29", "https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md"),
    ("F11", "low", "Baseline repo had a 6-byte README and no LICENSE, .gitignore, CI, 404 or .nojekyll; Pages build_type legacy", "Baseline hygiene added by integration", "S29", "https://github.com/kanlerxz87-cyber/NFL2/tree/01f227119ee8df4223b0aa697d08ed92257773c3"),
    ("F12", "medium", "No official value exists for any correlation, accuracy, ROI, Brier score or sample size in this project", "All numeric result cells are blank + UNVERIFIED", "S14", "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html"),
    ("F13", "high", "No jurisdiction or compliance determination was supplied for rewards", "Blocks rewards and any live-money feature", "S30", "https://www.ncpgambling.org/"),
    ("F14", "low", "Official 2026 NFL pages are live and change during the week", "Snapshots are point-in-time and timestamped", "S01", "https://www.nfl.com/injuries/league/2026/REG10"),
]
PAGES.append(P(
    "flagged.html", "Flagged for Review", "Governance", "Clearly labelled — non-blocking",
    "Everything on this page is flagged for human review with an official source link. "
    "A 'needs review' item is published here and does NOT block the build, the pull request "
    "or the merge. Unverified values are blank elsewhere on the site, never filled in.",
    [
        T("flags", "Irregularities and unverified items",
          ["ID", "Severity", "Irregularity / unverified item", "Impact", "Status", "Source link for review", "Source"],
          [R([i, sev, text, impact, "NEEDS REVIEW", url, src], src, "needs-review", [i])
           for i, sev, text, impact, src, url in _FLAGS],
          intro="Click any source link to verify the item yourself. All fourteen are published, none are hidden."),

        T("flag-policy", "Handling policy",
          ["Item", "Policy", "Status", "Source"],
          [
              R(["Flagged irregularities", "Do not block the merge", "VERIFIED", "Project brief", "S29"], "S29"),
              R(["Unverified values", "Leave blank; flag the row; never infer", "VERIFIED", "Verification rule", "S29"], "S29"),
              R(["Broken build, check or deploy", "Fix and retry until the site is live", "VERIFIED", "Project brief", "S28"], "S28"),
              R(["Changes requested after review", "Record the chosen path on the Suggestions page first", "PROPOSAL", "Official competition design", "S11"], "S11", "proposal"),
              R(["Responsible use", "No wagering, accounts or payments on this site", "VERIFIED", "NCPG", "S30"], "S30"),
          ]),
    ]))


# ---------------------------------------------------------------------------
# 16. 404
# ---------------------------------------------------------------------------
PAGES.append(P(
    "404.html", "Page not found", "Governance", "Return to the dashboard",
    "This page does not exist. Use the dashboard to find a section.",
    [
        T("404-table", "Where to go",
          ["Destination", "What it contains", "Status", "Source"],
          [
              R(["Dashboard", "All categories and site status", "VERIFIED", "Site index", "S27"], "S27"),
              R(["Executive summary", "Important details", "VERIFIED", "Site index", "S27"], "S27"),
              R(["Flagged for Review", "Irregularities and unverified items", "NEEDS REVIEW", "Flagged page", "S18"], "S18", "needs-review", ["F01"]),
          ]),
    ]))

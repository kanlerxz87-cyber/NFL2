# Executive Summary — NFL 2026 verified analytics

**Current through:** official reads of 2026-11-16 (Week 11 schedule page; Week 10 injury hub re-read; November reserve-list and trades tabs). Generated site: 45 pages + 404, every page regenerated from `content/` and `data/` on each build, served from GitHub Pages (source `main /`).

> **Bottom line up front:** every number on this site either traces to an official NFL page, linked row by row, or is left blank and flagged. The dataset is verified, the build is deterministic and byte-reproducible, and **no strategy has passed its validation gates — no edge is claimed.** The input that blocks everything money-related — a licensed, timestamped price feed with book identity — is an open owner decision (Q-01/Q-02, priority P0), not a modelled assumption.

## 1. The register at a glance (counted from its own file on every build)

| Measure | Value | File |
| --- | --- | --- |
| Traced requirements | 46 — 37 done, 5 partial, 3 specified, 1 in progress | `data/requirements.csv` |
| Validation gates | 15 — G-01…G-15, including G-15 demotion to paper (defined 16 Nov) | `data/gates.csv` |
| Registered flags | 114 — 85 open, 11 needs review, remainder resolved/closed/superseded | `data/flags.csv` |
| Open questions | 64 — 22 P0, 35 P1, 7 P2 | `data/questions.csv` |
| Suggestions | 72 | `data/suggestions.csv` |
| Registered official reads | 99 — 63 tier A (official league), 18 B, 9 C, 9 D | `data/sources.csv` |
| Brief clauses traced | 84 | `data/brief_traceability.csv` |
| Generated pages | 45 + 404 | `tools/build_site.py` |
| Tracked files | 754 | `git` |

Each page carries a badge: **measured** (generated from `data/`, official link on every row), **specified** (design, not a result), **decision** (register awaiting the owner), or **program** (policy/process).

## 2. What is verified — and what each verification does not establish

### Standings (official, re-read 16 Nov)

All 32 clubs × 8 published fields (W/L/T/PCT/PF/PA/net/streak) match an independent transcription; two reads seven minutes apart on 16 Nov (14:50Z and 14:57Z) agree cell for cell, so the published refresh to the newer read is cross-validated, not asserted. League identities hold: wins = losses, two ties, points for = points against.

Does not establish: split-record columns the league omits — nothing is inferred to fill them.

### Week 11 fixture slate (official schedule page, read 16 Nov)

Thirteen fixtures confirmed against https://www.nfl.com/schedules/2026/by-week/week-11: Indianapolis at Houston (Thu Nov 19, 8:15 PM, PRIME); Miami at Buffalo, Baltimore at Carolina, New Orleans at Chicago, Tennessee at Dallas and Tampa Bay at Detroit (Sun Nov 22, 1:00 PM); Arizona at Kansas City and Pittsburgh at Philadelphia (Sun Nov 22, 1:00 PM, CBS); Jets at Chargers (4:05 PM, FOX); Jaguars at Giants and Raiders at Broncos (4:25 PM, CBS); Vikings at 49ers in Mexico City (Sun 8:20 PM, NBC, neutral site); Bengals at Commanders (Mon Nov 23, 8:15 PM, ESPN). Six clubs on bye: Atlanta, Cleveland, Green Bay, LA Rams, New England, Seattle.

Venues: the official page prints stadium names only inside its own hotel-link parameters, not as visible text. Per the blank policy the site's venue cells stay `not published`; the parameter transcription (NRG Stadium, Highmark Stadium, Bank of America Stadium, Soldier Field, AT&T Stadium, Ford Field, Arrowhead, Lincoln Financial, SoFi, Empower Field at Mile High, MetLife; FedEx Field carried verbatim for Cincinnati at Washington — may not be the current sponsored name) is held in [FL-112](flagged-for-review.html), not in a data cell. Source: https://www.nfl.com/schedules/2026/by-week/week-11.

Does not establish: anything about venues beyond what the page displays.

### Week 10 results (official scores page, read 16 Nov)

Thirteen of fourteen Week 10 games are final and verified against official game-centre pages, each row linked to its own game page. The fourteenth — Chargers at Ravens, Monday night — is recorded nowhere: it is not final and not guessed. The twelve Sunday finals were appended to the append-only played file under a dated pre-registration amendment that preserves the decision-time hash; the grader recomputes every hash before grading and refuses to grade if any pinned artefact changes. The remaining governance question is [FL-114](flagged-for-review.html): the owner's ratification of that append protocol. Sources: https://www.nfl.com/scores/2026/week-10 plus the per-row game-centre links.

### Injury hub — a series, not a snapshot (nfl.com/injuries/)

The official Week 10 page keeps filing between reads, so the site keeps every read, dated, and publishes deltas:

| Read | Rows | Clubs | Game-status designations |
| --- | --- | --- | --- |
| Primary Week 10 file | 254 | 24 | 6 (12 Nov 04:45Z) |
| Full hub re-read | 279 | 26 | not published at that read (12 Nov 22:35Z) |
| Full-hub snapshot | 296 | 26 | 9 (13 Nov 12:46Z) |
| Full hub re-read | 347 | 28 | 171 — 70 Out, 90 Questionable, 11 Doubtful (15 Nov 12:55Z) |
| Full hub re-read (retained capture) | 347 | 28 | 171, cell-for-cell identical to 15 Nov (16 Nov 14:44Z) |

The live page keeps moving: a chunk read this session on 16 Nov shows designations populating for Washington, the Giants, New England, Detroit and Kansas City rows — the signal is the change between reads, never the level. Two retained raw captures exist (14:39:21Z SHA-256 e2b4074a…; 14:44:29Z SHA-256 2877f2c8…); one capture is not a series ([FL-97](flagged-for-review.html)), and the eight earlier hand transcriptions remain unretained ([FL-90](flagged-for-review.html)). [FL-94](flagged-for-review.html) — the Lions designations (Kerby Joseph, Cade Mays, D.J. Reed, all Out) now publish on the page a reader reaches first — is resolved; [FL-96](flagged-for-review.html) (TreVeyon Henderson on both the hub and the Reserve/Injured list in the same week) stays open.

Does not establish: a stable practice-to-designation model input — that play rate per designation is what inactive-list joins would measure, and inactive lists do not exist in this repo ([Q-07](questions.html), [C-29 uncovered](backlog.html)).

### Reserve list and trades (official transactions hub, read 16 Nov)

November 2026 reserve list: 25 dated Reserve/Injured rows, read in full — the four placements [FL-52](flagged-for-review.html) could previously source only to news articles now have league rows (resolved in this build). November trades: 12 rows. The reserve-list capture is a window (Aug/Sep/early-Oct not yet returned by the extractor — [FL-109](flagged-for-review.html)), so "not listed" still cannot be read as "available" outside the window. Sources: https://www.nfl.com/transactions/league/reserve-list/2026/11 ; https://www.nfl.com/transactions/league/trades/2026/11.

### Depth — no official league depth chart exists

nfl.com/teams/<club>/depth-chart returns the league's 404 page; every club chart is club-published and labelled unofficial, most without a date. Four club charts are transcribed and verified (Kansas City, Green Bay, New England, Detroit); a separate register transcribes 31 of 32 club charts ([FL-60](flagged-for-review.html): Houston's chart is a single image). No snap counts and no official inactive lists are stored anywhere ([C-29 uncovered](backlog.html)); two official game books (NE at SEA Week 1, NYG at WAS Week 5) were inspected for structure only — each carries an NFL notice requiring written permission for other use, so no game-book data is stored and bulk reuse stays blocked ([Q-50](questions.html), [S-58](suggestions.html)).

## 3. What the analysis layer shows (computed from official results, never market-priced)

- **136-game walk-forward ratings study** (weeks 1–9 official results): originated spread MAE 9.278 vs 10.455 do-nothing baseline; paired against the archived third-party price +0.295 pts with a bootstrap CI spanning zero — no provable edge, none claimed. Originated totals MAE 11.165 vs 11.078 league mean — worse than do-nothing, published as diagnostic only ([S-37](suggestions.html)).
- **Home field on 2026 games**: +0.50 pts, 95% CI [−1.80, +2.80]. The customary +2.5 prior sits outside the interval, but 149 games cannot settle it — the model prints +0.50 with its interval wherever it appears.
- **Correlations**, computed only from officially sourced inputs with n and interval beside each value: same-game holdout pairings up to φ = 0.945 (one bet sold twice); prop-level correlations are blank — no prop-line archive exists ([Q-12](questions.html)).
- **Leaderboard**: empty by design. Zero strategies carry stakes; ranking is proper-score (Brier skill with a game-cluster lower bound and multiplicity adjustment); control baselines (random picks, favorites only) are scored in every run; the best raw hit rate (79.2% on 24 decisions) is published in full and deliberately not promoted. Signal and staking are separate columns; staking allocation exists as a column family but carries no allocation until [G-14](validation-gates.html).
- **Pre-registration**: hash-stamped ledger; the Week 11 fair lines were hashed before kickoff and the grader recomputes every hash before grading — tested, a one-cell edit reports BROKEN and exits 1. The forward grade stays empty until games settle.

## 4. What is blocked — owner decisions, not code gaps

| Block | Missing input | Decision needed |
| --- | --- | --- |
| [Q-01](questions.html), P0 | Price feed: vendor tier, latency, licence cost | Choose among the three documented paths in [`docs/PRICE-DATA-POLICY-d304c6fe.md`](docs/PRICE-DATA-POLICY-d304c6fe.md); none is chosen ([S-29](suggestions.html)) |
| [Q-02](questions.html), P0 | Player-level entitlement (snaps, routes, targets) | Compare Next Gen Stats terms against open alternatives; version the pick |
| [Q-07](questions.html) / [C-29](backlog.html) | Official inactive lists and snap counts | Decide entitlement and source before any depth model ships |
| [Q-40](questions.html) | Injury-hub read cadence | Wednesday-to-kickoff series with fetch time on every read |
| [Q-42](questions.html) | Canonical injury register | Which dated read is canonical while the page moves intra-week |
| [CR-58E9-04](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md) | Pre-registration append protocol ratification | Dated amendment vs prefix-hash pin — this is [FL-114](flagged-for-review.html) |
| [CR-58E9-06](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md) | Deterministic flag-id allocator | Next-free-id so concurrent sessions stop colliding on flag numbers |

## 5. Flagged and published — never silently fixed

85 flags are open and 11 need review on the [Flagged for Review page](flagged-for-review.html), each with its source link. Notable open items: [FL-01](flagged-for-review.html) (LAC/BAL read "No Injuries Reported" while SEA/CIN publish full blocks — absence is a collection gap, not health); [FL-10](flagged-for-review.html) / [FL-21](flagged-for-review.html) (the price archive is a historical exhibit, not a price source); [FL-60](flagged-for-review.html) (Houston depth chart image untranscribed); [FL-112](flagged-for-review.html) (venue names exist only in link parameters); [FL-114](flagged-for-review.html) (pre-registration append protocol awaiting owner ratification). Flags do not block a merge; the build fails on any unsourced row, any stale output, or a drifted manifest.

## 6. Earlier dated reads (retained as history)

All reads below remain in the repo under their capture dates; none was overwritten.

| What | Capture | Rows | Clubs | Designations |
| --- | --- | --- | --- | --- |
| Week 10 primary injury file | 2026-11-12 04:45Z | 254 | 24 | 6 |
| Full hub re-read | 2026-11-12 22:35Z | 279 | 26 | not published |
| Full-hub snapshot | 2026-11-13 12:46Z | 296 | 26 | 9 |
| Full hub re-read | 2026-11-15 12:55Z | 347 | 28 | 171 |
| Full hub re-read (retained capture) | 2026-11-16 14:44Z | 347 | 28 | 171 (cell-identical to 15 Nov) |
| Standings re-read | 2026-11-16 14:50Z | 32 clubs × 8 fields | — | identical to the 14:57Z snapshot |

## Delivery

This summary is rendered from `content/executive-summary.md`; nothing in it is typed into HTML by hand. Every factual claim above names its source page; anything that cannot be confirmed from an official source is blank on the site and listed on Flagged for Review. No manual input from the owner was required to produce it.

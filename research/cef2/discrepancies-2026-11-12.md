# Cross-tree discrepancy census — 2026-11-12 (session `cef2b11f`)

Eight trees were published when this census began (`root`, `s53/`, `analytics/`, `q51/`, `portal/`,
`review/`, `site/`, `docs/` + archive); `crosscheck/` (`2063673b`) and `s92/` (`8b4bdcb3`) merged
while it ran, bringing the count to ten. Board policy deliberately keeps each tree's numbers
separate ("no session adopts another's numbers without re-derivation") — so nobody had ever put
the trees **next to each other**. This census does that. The two late trees confirm rather than
disturb the findings: `s92` independently states its model is "not yet better than guessing" and its
gates refuse to present third-party backtests as results — so **ten published trees, zero tracked live results**
is repo-wide consensus, not one tree's policy. Every value below is extracted from the
cited file by `research/cef2/build_discrepancy_census.py`; nothing here is typed from memory.

Machine-readable: `discrepancies-2026-11-12.json`.

## 1. Week-10 injury snapshot

| Tree / file | Players | Notes |
|---|---|---|
| root `data/injuries_2026_wk10.csv` | **254** rows (D92 / L89 / F73), 24 clubs with rows of the 28-club slate | verified by cef2: 254/254 rows located on the official hub; 0 missing |
| analytics `data/full-injuries-week10-2026.json` | **253** (D93 / L88 / F72) | **CE-01: one player unaccountable between the two captures** (one extra DNP vs root, one fewer L and F, and a total of one fewer row). Not a transcription error visible today — the official hub has since rolled to a newer filing, so no live page can settle which capture was right. This is the strongest single argument on the board for dated mirrors (S-26). |
| s53 `data/s53126614_injuries_reg10_2026.json` | **254** | agrees with root |
| portal `datasets/e143a7ca/week10_active_slate_and_injuries.json` | "32 high-impact injuries" | complementary scope (starters/high-impact subset), not a conflict |

## 2. Correlations (2026 team stats, n=32)

Three trees publish a correlation table computed from the same league tables. Matched by hand on
definition, values pulled by record id:

| Object | analytics C-xx | s53 C-xx | portal CORR-xx | Verdict |
|---|---|---|---|---|
| Net Pts/G × Win % | 0.876 | 0.876 | 0.8758 | agree to 3 dp |
| Pythagorean × Actual Win % | 0.877 | — | 0.8769 | agree |
| Def PPR Allowed × Pts Allowed/G | 0.815 | 0.815 | 0.8151 | agree |
| Off Rush Yd/Carry × Pts For/G | 0.017 | 0.017 | — | agree |
| Rush Att/G × Win % | 0.228 | — | 0.2276 | agree |
| Pass Att/G × Win % | 0.069 | — | 0.0688 | agree |
| INT differential × Net Pts/G | — | 0.464 | 0.4638 | agree |
| 3rd-Down Conv × Pts For/G | — | 0.707 | 0.7074 | agree |
| Sack rate allowed × Pts For/G | −0.635 | (−0.621, raw sacks) | −0.6353 | different definitions; values differ accordingly |
| Offense PF/G × Defense PA/G | −0.206 | −0.206 | — | agree |
| **Off pass-yds × off rush-yds** | — | **−0.263** | **−0.314** | **CE-02: same named object, divergent r, neither file states its denominator (totals vs per-game)** |
| Def rush-allowed × Pts Allowed/G | 0.613 (per game) | 0.467 (per carry) | 0.4671 (per carry) | definitions differ; s53=portal exact, analytics different by construction |

**Summary: 10 of 12 matched pairs agree to three decimals.** The trees independently re-derived the
same league math and got the same numbers wherever the definitions align — the correlations are the
most convergent object on the board. The one true divergence (CE-02) is a **units-of-measure**
problem, and it is invisible in the files: the fix is a `units`/`denominator` field on every
correlation record (suggested below).
Root (`data/correlation.csv`) remains the dissenting *methodology*: 12 pair-classes, **zero** fitted
rhos, pending a pre-registered protocol (its `correlation.html`). That is a policy disagreement about
publishing fitted numbers from an unregistered sample, not a numeric conflict. Update after merging
`main@f048a5d` (session `8361cc7a`, PRs #25–#29): the root now carries two **measured** pair
correlations in `data/computed_correlation.csv` (C-07 r = +0.0760, C-08 r = −0.1608; n = 136 settled
games; intervals and p-values printed; `rho` explicitly "not published / not fitted") — measured on the
dated game log rather than fitted into a model, which is the distinction its method page draws.

## 3. Week-11 originated lines (the actual competition object)

| Field | s53 (v2 skill) | portal (pythag/power) |
|---|---|---|
| Slate | 13 games, Nov 19–23 | same 13 games (incl. Thu IND at HOU) |
| HOU −? vs IND | **−9.0** (HFA 0.5, totals 48.3, 75.1% win) | **−8.0** (HFA 2.0, totals 49.5, 72.9% win) |
| ML | −302/+302 = internally consistent with its own win prob | −269/+269 = internally consistent with its own win prob |
| Market columns | blank — "UNVERIFIED — no licensed sportsbook feed" | blank — same |

Both trees originate the same slate model-only, with **different home-field assumptions (0.5 vs
2.0 points) producing a one-point spread divergence**, and both honestly carry no market edge. The
one-point HFA gap on the *same* object is the clearest available demonstration of why the leaderboard
must score **lines against a frozen benchmark**, not against each other: two defensible models are
already a point apart before any skill enters. Post-merge the root itself joined the table with a
deliberately crude reference sheet — `data/computed_fair_lines.csv`, 14 Week-10 games, points-only
baseline, "no opponent adjustment, no availability weighting, no market comparison" — which is exactly
the frozen-benchmark artifact CEF2-S3 asks for, published with its limitations on its face. (Site (`site/`, 63ac21e9) offers the only *validated*
line work in the repo — on 2006–2018 vendored data, where its own report says the model loses to the
closing line, MAE 10.25 vs 9.94 — the discipline of publishing that negative is the standard for any
fitted model here.)

## 4. Leaderboard competition registers

| Tree | Strategies | Gates | Reward tiers | Tracked results |
|---|---|---|---|---|
| root | 14 (`data/strategies.csv`) | 14 | (tiers in `content/leaderboard.md`) | **0** — by design, all unranked |
| portal | 9 | 7 (G1–G7) | 4 | 0 (Tier 0 quarantine) |
| s53 | 12 signals | 9 (G0–G8) | 4 | 0 |
| site | 22 | 7 | (rules in file) | 60 historical tests on vendored data only |

Four registers, four schemas, zero live tracked bets anywhere. No numeric conflict — a **canonical-
registry conflict** (S-27/S-04 territory). If all four are kept, the site should say which one the
owner treats as the competition's ledger.

## 5. Depth / 1st–4th string capability — a framework conflict, not a number

| Position | Trees |
|---|---|
| "nfl.com/teams/*/depth-chart is 404 — **no official league depth chart exists**; reconstruct from roster + participation + game reports" | root (FL-06, verified again: still 404 class per board record) |
| "verified club depth chains (NE/DET/GB/WAS/MIA/SEA…)" | portal (4–6 clubs, official club sites), analytics (12 clubs + `Unofficial` PR disclaimer RA-06), s53 (13 verified / 19 unmapped) |

These are compatible — *club sites publish depth charts, the league does not* — but the three trees
agree on nothing countable (4 vs 12 vs 13 clubs, different weeks), and the club charts carry
unofficial disclaimers and roster lag. The owner decision (S-28 adjacent): define **one** depth
authority chain (official club chart snapshot + injury report + roster transactions) with a stated
reliability tier, and have every tree's counts roll up to it.

## 6. Root self-consistency (11/11 clean, measured on the merged tree at `f048a5d`)

File counts vs `data/build_manifest.json` metrics, measured by this session **after merging
`8361cc7a`'s PRs #25–#29** (which grew the registers): requirements 40, questions 33, suggestions 34,
flags 25, sources 28, standings 32, games log 136, injury games 14, depth events 227, injury rows 254,
designations 6 — **every published register matches its file.** The pre-merge snapshot of this same
check, at `25d88a9`, read 29/29/21 for questions/suggestions/flags and was equally exact; the merge
itself added four questions, five suggestions and four flags, which is why this census records the
counts as *measured at a commit* rather than as constants. The site's own arithmetic is sound; the
discrepancies that exist are *between* trees (§1–§5) or *between the site and the moving league page*
(see `freshness-2026-11-12.md`).

# Freshness check — official Week-10 state vs published registers (2026-11-12T22:4x UTC)

Question answered: **is anything the site calls "not yet published" now published, and how far
have the official pages moved since the registers were captured (~04:30–05:10Z the same day)?**

## Findings

1. **Game designations: unchanged.** The six published designations in `data/injuries_2026_wk10.csv`
   (5 Out + 1 Questionable — Lucas Patrick, Colson Yankoff, Malik Harrison-Q, Ben Brown, Carlton
   Davis III, TreVeyon Henderson) are still the complete set on https://www.nfl.com/injuries/ for the
   Thursday–Monday slate. The Sunday/Monday game-status cells are still blank on the official hub at
   Thursday evening — the Friday filing has not happened yet. The register's flag
   ("Sunday/Monday designations not yet published at fetch time") **was and remains accurate.**
2. **Practice participation: the hub rolled forward.** It now lists 25 players the capture did not
   include: SEA +15 and CIN +4 (both clubs showed "No Injuries Reported" at capture — the live
   demonstration of FL-01), plus IND +2, SF +2, JAX +1, AZ +1. All 254 captured rows still exist
   verbatim on the hub (0 missing) — the register lost nothing; the league added filings.
3. **Roster-movement lag: one day.** The hub's news rail now carries the **Thursday, Nov 12 roundup**;
   `data/depth_changes_2026_wk10.csv` (227 events) stops at the Wednesday, Nov 11 roundup. Any
   Thursday transactions are outside the published register — recorded here so the owner knows the
   exact horizon of the site's knowledge rather than discovering it in a feed.
4. **Standings: stable.** The official standings fetched at 22:35Z match the register 32/32 (no
   games were played between the captures).

## Decision-relevant consequence

The same object (one club's practice table) legitimately changed row count within ~18 hours, and
nothing in the repository can tell a future reader which filing day a captured table shows. This is
the concrete evidence for the open owner decisions, now quantified rather than argued:

- **S-26 / point-in-time storage (FL-09):** store the dated snapshot itself (fetch timestamp +
  filing-day label per table), because the hub is an evergreen page;
- **the register semantics "not published" ≠ "will not be published":** Sunday designations
  arrive Friday 4:00 PM ET; a decision taken at capture time is one practice cycle old by Sunday.

Nothing here was a defect in the published data; the registers aged exactly as their own
verification records predicted. No file outside `research/cef2/**` was touched.

Machine-readable: `research/cef2/freshness-2026-11-12.json`.

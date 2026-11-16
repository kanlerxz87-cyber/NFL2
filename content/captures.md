# Official Capture (retained, hashed)
> The first retained copy of the official NFL injury hub, stored as the raw bytes the league served, with a SHA-256 and a UTC fetch time. Every number on this page is taken from those bytes, and every row links to its official player page on nfl.com.

## What was captured, and when

The capture ran on a GitHub-hosted runner, because the analysis sandbox cannot reach nfl.com (FL-90). The first response was HTTP 200 at **2026-11-16 14:39:21 UTC**. The stored file holds 399,895 bytes; its SHA-256 is `e2b4074a9837a93e0d38ae8a8aac7b7b668b96fdd41d7caf86269a650cd981a3`. The page title reads "Official Latest NFL Injury Report for Players - Week 10 of the 2026 Season | NFL.com". The page carries 28 club tables and 347 player rows.

Source: [https://www.nfl.com/injuries/](https://www.nfl.com/injuries/) · the stored file is `data/captures/injuries_hub/20261116T143921Z_e2b4074a9837.bin` · the ledger is `data/capture_manifest.csv` (append-only).

The ledger is [data/capture_manifest.csv](data/capture_manifest.csv): one row per fetch, append-only, pipe-delimited, with the UTC fetch time, the official URL, the HTTP status, the byte count, the SHA-256 and the stored file. A fetch whose bytes are identical to a stored one is logged but not stored again. A page that answers but fails the structure check is kept as evidence and marked `no`. This page does not render the ledger, so each daily run leaves the published page unchanged.

### A second capture, and why the hash is per response

A second runner capture ran at **2026-11-16 14:44:29 UTC** (`data/captures/injuries_hub/20261116T144429Z_2877f2c8a1a2.bin`, SHA-256 `2877f2c8a1a28acb7024708cf103f2154d0d3f0231e9748b4b5d9480fec6c5fb`). Its length is the same, 399,895 bytes, but its hash is different. A byte-level comparison of the two files finds **29 differing bytes, all inside one block**: the `data-jsonid` attribute of a carousel module, which is a random identifier generated for each page render. No injury value differs. The hash therefore identifies one response, and two hashes do not by themselves show a change in the league's designations. The change evidence has to come from the parsed rows. The second capture's 347 rows also reconcile 347 of 347 with the 15 November file (summary run with `--capture`; the committed table below stays pinned to the first capture).



## Row-by-row reconciliation with the 15 November file (first capture)

The 347 rows of the retained bytes were compared with `data/injuries_wk10_5de1805b_20261115.csv` (the 15 November 12:55Z read, 347 rows). The comparison matches each player's club, position, injury, practice status and game status. The club key needed one alias, disclosed here: the repository writes the Los Angeles Rams as `LAR`, and the page's own logo code is `LA`. No other alias was used, and no value was changed.

| Result | Rows |
| --- | --- |
| Captured rows | 347 |
| Matched on all five fields | 347 |
| Mismatched in both files | 0 |
| In the capture only | 0 |
| In the repository file only | 0 |

What this shows: the 15 November read and the 16 November retained bytes agree on every row. What it does not show: whether the league changed anything between those two times, or whether the page will change before kickoff. A matching pair of reads is evidence of agreement, not of a stable designation.

Practice codes follow the league's own vocabulary: **F** = Full Participation in Practice, **L** = Limited Participation, **D** = Did Not Participate In Practice. Game status: **Q** = Questionable, **D** = Doubtful, **OUT** = Out. A blank cell means the official page shows no entry in that column. Each row links to the player's official nfl.com page.

{{csv data/capture_reconciliation_7c23f22f.csv;;cols=club:Club,player:Player,pos_capture:Pos,injury_capture:Injury (capture),practice_capture:Practice (capture),status_capture:Game status (capture),match:Matches repository,mismatch_fields:Differences;;source_col=player_url;;group=club;;caption=Reconciliation of the 16 Nov 14:39Z retained capture against data/injuries_wk10_5de1805b_20261115.csv. Repository-side columns are in the CSV. Differences are listed by field name; none is non-empty.}}

## What is still open

- **FL-94** — [injuries.html](injuries.html) still renders the 12 November read, in which the three Detroit designations are blank. The retained capture above shows all three as Out. The published page has not been changed by this session.
- **FL-90** — stays open until more captures exist. One capture shows one moment; the daily workflow now adds one row per run, and the change between two runs is the evidence the project needs (FL-88).
- **FL-97** — the workflow is scheduled daily at 14:17 UTC, and it also runs when the capture code itself changes on `main`. Two captures are retained so far, five minutes apart on the same day. No daily series exists yet.
- **FL-99** — the byte hash changes between reads of the same content (the random carousel identifier above). Change detection has to compare parsed rows, not hashes.

Flags: [Flagged for Review](flagged-for-review.html) (FL-90, FL-94, FL-97, FL-98, FL-99). Sources: [Source Registry](sources.html) (S-CAP-7C). Method: `tools/capture_official.py`, `tools/reconcile_capture_7c23f22f.py`, `tools/verify_capture_7c23f22f.py`.

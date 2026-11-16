# Official Capture (retained, hashed)
> Two official NFL injury-hub responses were retained on 2026-11-16, five minutes apart. This page shows capture metadata and aggregate checks only—not player-level rows. The raw responses and reconciliation CSV remain accessible in the public repository without a recorded source-terms review (FL-99). Hash integrity does not grant republication rights.

## What was captured, and when

The captures ran on GitHub-hosted runners because the analysis sandbox cannot reach nfl.com (FL-90). The append-only manifest records HTTP 200 responses at **14:39:21 UTC** and **14:44:29 UTC**, each 399,895 bytes. Their SHA-256 hashes are `e2b4074a9837a93e0d38ae8a8aac7b7b668b96fdd41d7caf86269a650cd981a3` and `2877f2c8a1a28acb7024708cf103f2154d0d3f0231e9748b4b5d9480fec6c5fb`. Each response passed the structure check: 28 club tables, 347 player rows, 347 practice-status hits and 171 game-status hits.

The responses have the same length but different byte hashes. A byte comparison found 29 differing bytes, all in one carousel block's randomly generated `data-jsonid` attribute; no injury value differed. A response hash identifies a specific set of bytes, not a distinct injury state. Change detection for an injury series must compare parsed rows, not hashes alone (FL-99).

Source: [NFL injury hub](https://www.nfl.com/injuries/) · retained files: `data/captures/injuries_hub/20261116T143921Z_e2b4074a9837.bin` and `data/captures/injuries_hub/20261116T144429Z_2877f2c8a1a2.bin` · append-only ledger: `data/capture_manifest.csv`.

The ledger has one row per fetch. Byte-identical fetches are logged but not stored again; responses that fail the structure check are retained and marked `no`. The daily workflow and append-only ledger do not establish a multi-day history: these two responses are only five minutes apart and cannot replay earlier reports.

## Aggregate reconciliation with the 15 November file

The 14:44 UTC response was summarized against `data/injuries_wk10_5de1805b_20261115.csv` (the 15 November 12:55Z read, 347 rows). The comparison covers club, position, injury, practice status and game status. One club-key alias was needed: the repository uses `LAR` for the Los Angeles Rams and the official page uses `LA`. No other alias was used and no value was changed.

| Check (aggregate only) | Rows | Official source |
| --- | ---: | --- |
| Captured player rows | 347 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows matched on all five compared fields | 347 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows mismatched in both files | 0 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows present only in the capture | 0 | [NFL injury hub](https://www.nfl.com/injuries/) |
| Rows present only in the 15 Nov repository transcription | 0 | [NFL injury hub](https://www.nfl.com/injuries/) |

This establishes agreement between the 15 November transcription and the 14:44 UTC response, not that the league's designations were stable between reads or will remain so before kickoff. Practice codes in the source are F (Full Participation), L (Limited Participation) and D (Did Not Participate); game designations include Out, Questionable and Doubtful. Blank fields were preserved as blank.

**Player-level rows are not rendered here.** The row-by-row file, `data/capture_reconciliation_7c23f22f.csv`, remains in the public repository pending the source-use decision in FL-99; hiding rows on this page does not make that file private.

## What is still open

- **FL-90** — the two captures are five minutes apart, not a multi-day series, and cannot replay earlier reports (FL-88).
- **FL-94** — the canonical injury page still shows blank Detroit designations from its older read, although the retained capture contains them as Out.
- **FL-97** — the store contains two verified captures, but future daily cadence remains to be demonstrated.
- **FL-98** — the Rams club key differs (`LAR` in the repository, `LA` on the official page); the reconciliation discloses the alias.
- **FL-99** — both the public retention/republication rights question and the hash-versus-content change-detection method remain open. Review source terms and choose a private-store/removal path; compare parsed injury rows for series changes.

Flags: [Flagged for Review](flagged-for-review.html) (FL-90, FL-94, FL-97, FL-98, FL-99). Source: [NFL injury hub](https://www.nfl.com/injuries/) and [Source Registry](sources.html) (S-CAP-7C). Methods: `tools/capture_official.py`, `tools/reconcile_capture_7c23f22f.py`, `tools/verify_capture_7c23f22f.py`.

# Requirements and gate-map audit — 2026-11-15

## Scope and source class

This integration audits the 46-row `data/requirements.csv` against the 14 gates in `data/gates.csv`, distinguishes the two depth-coverage measures, and verifies that the landing table renders the current register. Requirement wording, statuses, gate assignments and pass thresholds are **project design**, not official NFL facts. `S-BRIEF` is an owner-instruction reference; `Origin` on the register identifies later session/audit additions. A `done` status means the project artefact was checked, not that its associated NFL facts or validation gates passed.

No new NFL measurements, source-registry rows or flag rows were added. FL-73 and FL-74 were already present on main with dated evidence from the 2026-11-15 four-club re-read; FL-44 and FL-60 already describe the separate depth-coverage gaps. Existing flag/source rows were left unchanged.

## Gate-map decisions

All gate references in the register resolve to `data/gates.csv`. The rows below record the mapping review and changes made; `—` means the gate register does not define a relevant technical gate or numeric threshold.

| Requirement(s) | Mapping after review | Audit result |
|---|---|---|
| R-01 | G-03 | Point-in-time inputs and byte-identical replay match the gate test and pass criterion. |
| R-08 | G-06 | Calibration is the gate that blocks publication of a line residual; the pass value remains the existing <= 2.0-point maximum absolute calibration error. |
| R-09 | G-01 | The source-entitlement gate matches use of inputs in strategy research. |
| R-10 | G-11 | Pre-registration, pre-bet spec hash and no in-window edits match the gate. |
| R-11 | G-13 / G-14 | Family deduplication governs reward allocation; drawdown/capacity governs staking allocation. |
| R-12 | G-07 | Executed and benchmark prices match the price-accounting gate. |
| R-13 / R-14 | G-05 / G-07 | The clearing condition now explicitly includes both 100% settlement reconciliation (G-05) and executed-plus-benchmark prices (G-07); prop joint-probability claims still require sourced observations. |
| R-15 | G-01 through G-12, as applicable | Expanded from G-11 alone. These are the hard promotion gates. G-13 and G-14 remain scoped to reward allocation and staking, not promotion; narrower bet-type and tier scopes remain in force. A documented gate is not a passed gate. |
| R-16 | — | Removed G-06: it tests line-probability calibration, not descriptive correlation estimation. No gate in the root register specifies a correlation-estimation threshold. |
| R-17 | G-12 / G-07 | The clearing condition now includes the CLV interval criterion and the gate's 100% executed/benchmark-price requirement. |
| R-18 | G-12 / G-14 | CLV and drawdown/capacity criteria match the gates. |
| R-19 | G-03 | The clearing condition now includes both timestamped event sourcing and byte-identical replay. |
| R-20 / R-21 / R-44 | G-02 / G-03 | The clearing condition now includes zero unresolved player/team IDs across a full week and byte-identical point-in-time replay, alongside the existing roster/ID/timestamp requirements. |
| R-41 | G-03 | Row-level re-verification remains tied to reproducible point-in-time inputs. |
| R-42 | G-06 | Calibration is the gate for publishing line residuals. The requirement's no-information and archived-price comparisons remain explicit artifact checks; no “must beat baseline” threshold was invented. |
| R-43 | — | Removed G-06 and G-12: calibration and CLV are not correlation-estimation gates. Prop pairs remain blank without a prop archive; any later estimate needs source-linked joint observations and an interval. No numeric correlation threshold is defined. |
| R-45 | G-01 / G-07 | Source approval and market-price accounting remain the relevant gates for price-data use. |
| R-46 | — | The landing-table coverage criterion is project verification, not an NFL statistical gate; its clearing condition now uses dynamic N-of-N coverage rather than a hard-coded 46. |

No new gate or performance threshold was added. Existing numeric criteria remain those already recorded in `data/gates.csv`.

## Depth coverage: separate files and operations

The numbers were recomputed from the two independent in-repository registers:

- `data/personnel_relief_club_83246f00.csv` has chart URLs for **10** clubs, across its dated join to the full 2026-11-13 Week 10 injury snapshot. It records **85 of 296** injury filings resolved to a listed chart slot. Eight of the ten have at least one filing resolved; BAL and LAC have no listed player rows in that snapshot. The 296 is the dated league-hub snapshot's row count; 85 is the repository's join result, not an NFL statistic. See [Personnel Relief](../personnel-relief.html), [the dated availability table](../availability-1113.html), [FL-44](../flagged-for-review.html), and the [official NFL injury hub](https://www.nfl.com/injuries/).
- `data/s745_depth_summary.csv` has 32 club rows, with **31** marked chart-published; `data/s745_depth_charts.csv` contains the corresponding chart-slot transcriptions. The separately registered S745 read is dated 2026-11-13. This is a count of club-published, explicitly unofficial chart pages transcribed in the repository, not a count of injury-to-starter joins. Houston is the untranscribed chart: its [official club page](https://www.houstontexans.com/team/depth-chart) labels the page “Unofficial Depth Chart” and renders the chart as an image. The limitation is already recorded in [FL-60](../flagged-for-review.html); the [Depth Register](../depth-deficiencies.html) carries per-row chart links.

Thus, the 10-chart/85-of-296 join and the 31-of-32 chart transcription are not competing coverage totals and must not be presented as equivalent. Neither implies 31 of 32 verified point-in-time starter replacements.

## Official-page review performed for this integration

- Fetched [NFL.com/injuries](https://www.nfl.com/injuries/) on 2026-11-15. It still labels the page Week 10 and renders the WAS, NYG, NE and DET tables used by the existing 44-row re-verification. The page's current rows agree with the dated transcription represented by `data/injuries_wk10_e733834d_20261115.csv`; the existing comparison reports 31 matches and 13 differences from the 2026-11-13 file, recorded as FL-73/FL-74. The fetched page was not retained as a new capture or hash, and this check does not re-read all clubs or rewrite the 296-row snapshot.
- Fetched the [Patriots club depth chart](https://www.patriots.com/team/depth-chart) on 2026-11-15. It calls the chart “Unofficial” and says it reflects Patriots.com writers' opinions, not necessarily those of the organization. This confirms the source class used for club charts; it does not re-verify all 31 transcriptions.
- Fetched the [Houston Texans depth-chart page](https://www.houstontexans.com/team/depth-chart) on 2026-11-15. It is headed “Unofficial Depth Chart” and presents the chart as an image, so no player slots were transcribed or inferred.

The official pages above support the statements attributed to those pages. Aggregate coverage counts are computed from the dated repository tables and are labelled as such. This audit does not claim a fresh line-by-line re-read of all 31 chart pages.

## Verification artifacts

`tools/verify_readiness_ac2dd497.py` runs after the site build in `.github/workflows/validate.yml`. It checks exact landing-table ID/order coverage, per-row source-link/source-class display, valid gate references, the correlation-gate exceptions, and separate recomputation of the 10/85/296 and 31/32 depth figures. The broader build, data, link and model suite remains required before publication.

# Injury, lineup and depth-chart tracking (T08)

## Verified official facts that constrain the design

| ID | Fact | Official source |
| --- | --- | --- |
| I01 | The Week 10, 2026 official injury report lists Player, Position, Injuries, Practice Status, Game Status for each club | https://www.nfl.com/injuries/league/2026/REG10 |
| I02 | Practice status = Did Not Participate / Limited Participation (<100% of normal repetitions) / Full Participation (100%) | https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 |
| I03 | Game status = Questionable (uncertain) / Doubtful (unlikely) / Out (will not play); "Probable" eliminated; a player certain to play is not listed on the game status report | https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 |
| I04 | A club depth chart can expose First / Second / Third / Fourth string, but the club labels it "Unofficial Depth Chart" | https://www.chiefs.com/team/depth-chart |
| I05 | The definitive availability checkpoint is the Game Day Administration Report (inactive list) exchanged at the 90-minute officiating meeting | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep |
| I06 | Active game-day list is 47/48 players; the 53-player roster is the eligibility base | https://www.nfl.com/news/nfl-emergency-third-quarterback-rule-questions-and-answers |
| I07 | Game Operations Manual requires certified athletic-trainer injury spotters and an injury video review system | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-ops-manual |
| I08 | NFL integrity policy prohibits wagers tied to injuries and those knowable in advance | https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners |

## Verified snapshot — Week 10, Thursday 12 November 2026, Commanders at Giants

Captured 2026-11-12 (UTC) from the official injury report. Blank cells mean the official
source shows a blank field; they are not filled in.

| Club | Player | Position | Injury | Practice status | Game status | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Commanders | John Bates | TE |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Treylon Burks | WR |  | Did Not Participate In Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Jayden Daniels | QB |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Matt Gulbin | C |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Chig Okonkwo | TE |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Lucas Patrick | C | Concussion | Did Not Participate In Practice | Out | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Amik Robertson | CB |  | Limited Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Shy Tuttle | DT |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Commanders | Colson Yankoff | TE | Knee | Did Not Participate In Practice | Out | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Abdul Carter | LB |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Jermaine Eluemunor | T |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Malik Harrison | LB | Groin | Limited Participation in Practice | Questionable | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Colton Hood | CB |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Theo Johnson | TE |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Charlie Jones | WR |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | J.J. McCarthy | QB |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Darnell Mooney | WR |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Malik Nabers | WR |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Cam Skattebo | RB |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |
| Giants | Andrew Thomas | T |  | Full Participation in Practice |  | https://www.nfl.com/injuries/league/2026/REG10 |

## Verified depth snapshot — Kansas City Chiefs (club-published, "unofficial")

Blank 4th-string cells are blank on the source. Both offense and defense are represented,
as requested. Source: https://www.chiefs.com/team/depth-chart

| Unit | Position | 1st | 2nd | 3rd | 4th | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Offense | QB | Patrick Mahomes | Justin Fields | Garrett Nussmeier |  | https://www.chiefs.com/team/depth-chart |
| Offense | TE | Travis Kelce | Noah Gray | Jared Wiley | Jake Briningstool | https://www.chiefs.com/team/depth-chart |
| Offense | RB | Kenneth Walker | Emmett Johnson | Jaydn Ott |  | https://www.chiefs.com/team/depth-chart |
| Offense | WR | Rashee Rice | Jalen Royals | Andrew Armstrong |  | https://www.chiefs.com/team/depth-chart |
| Offense | LT | Kahlil Benson | Diego Pounds |  |  | https://www.chiefs.com/team/depth-chart |
| Defense | CB | Mansoor Delane | Kristian Fulton | Melvin Smith |  | https://www.chiefs.com/team/depth-chart |
| Defense | S | Chamarri Conner | Jaden Hicks | Xavier Nwankpa |  | https://www.chiefs.com/team/depth-chart |
| Defense | DE | Felix Anudike-Uzomah | Ashton Gillotte |  |  | https://www.chiefs.com/team/depth-chart |
| Defense | LB | Drue Tranquill | Jeffrey Bassa |  |  | https://www.chiefs.com/team/depth-chart |
| Defense | DT | Chris Jones | Peter Woods |  |  | https://www.chiefs.com/team/depth-chart |

## Tracker design (proposal, not yet built)

| Field | Definition | Source of truth | Computed? | Status |
| --- | --- | --- | --- | --- |
| player_id | Official NFL.com player slug | https://www.nfl.com/players/ | no | proposal |
| club, position | From official report row | https://www.nfl.com/injuries/league/2026/REG10 | no | proposal |
| injury_text | Verbatim injury field, blank if absent | https://www.nfl.com/injuries/league/2026/REG10 | no | proposal |
| practice_status | DNP / LP / FP, verbatim | https://www.nfl.com/news/competition-committee-approves-revisions-to-injury-report-0ap3000000688693 | no | proposal |
| game_status | Questionable / Doubtful / Out / blank | https://www.nfl.com/injuries/league/2026/REG10 | no | proposal |
| depth_rank | 1–4 from club chart, with "unofficial" marker | https://www.chiefs.com/team/depth-chart | no | proposal |
| unit | offense / defense / special teams | https://www.chiefs.com/team/depth-chart | no | proposal |
| inactive_final | From Game Day Administration Report at 90-minute meeting | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep | no | proposal |
| replacement_depth | Computed depth rank of the player who actually took the snaps | play-by-play / snap counts (not licensed) | yes | UNVERIFIED — data unavailable |
| deficiency_index | Computed unit-level weakness from replacements | derived | yes | UNVERIFIED — data unavailable |
| captured_at_utc | Timestamp of each snapshot | local ingestion clock | no | proposal |

## Irregularities / limitations

* Club depth charts are "unofficial" (F03); ranking is a club estimate, not a league fact.
* The weekly injury report is not the final lineup; the 90-minute inactive list is (F05).
* Injury-linked wagering markets may be prohibited by league integrity policy (F07).
* The injury report is live and changes during the week; all snapshots are point-in-time (F14).
* No per-snap participation data was available, so `replacement_depth` and
  `deficiency_index` are blank + `UNVERIFIED` rather than estimated.

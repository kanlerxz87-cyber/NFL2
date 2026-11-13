# Depth & deficiency register — all 32 clubs
> The brief asks the system to *know* when a defense or an offense is running a 2nd, 3rd or 4th string body in place of a starter. Before this page the root register could answer that for **4 of 32 clubs** (`data/depth_charts.json` charts KC, GB, NE, DET; the other 28 were left blank and flagged as FL-10). This page closes it to **31 of 32**, using the only official chart that exists for a club — the one its own site publishes — joined to the official league injury report.

## What this page is, in one sentence

Every position group on every club depth chart, with the starter's official practice and game status beside it, and the name of the man the club would have to turn to next.

## The two sources, and why two

| Input | Source | What it proves | Tier |
| --- | --- | --- | --- |
| Depth slot (1st / 2nd / 3rd / 4th string) | the club's own official site, e.g. [patriots.com/team/depth-chart](https://www.patriots.com/team/depth-chart) | the order the club itself prints | B — official club site, not league-operated |
| Practice and game status | [nfl.com/injuries](https://www.nfl.com/injuries/) (Week 10, read 2026-11-13) | the league's own filing | A — official league |

`nfl.com/teams/<club>/depth-chart` returns **404**. That was verified in an earlier session and published as [FL-05](flagged-for-review.html). There is no league-operated depth chart to download, so the club's own page is the best official source that exists — and the site says so on every row rather than pretending otherwise.

**Every one of these charts is labelled *unofficial* by the club that prints it.** Most are compiled by the club's communications staff. They can lag a coaching decision by days. That is the single biggest limitation of this page and it is not smoothed over anywhere below.

**How the join works, in the one place it can go wrong.** A chart and an injury report name the same man differently — the Patriots' chart prints *Kevin Byard III*, the league's report prints *Kevin Byard*. The join is a normalised exact match first and a unique last-name match inside the club second; it never guesses across clubs and never resolves an ambiguous name. Every row therefore carries **both** spellings: `projected_starter` is what the club printed, `starter_injury_name` is what the league printed, and `scripts/verify_s745.py` re-checks every one of the {{metric s745_matched}} matched starters against the report they came from.

## Coverage

| Measure | Value |
| --- | --- |
| Clubs with a transcribed chart | **31 of 32** |
| Depth slots transcribed | **{{metric s745_slots}}** |
| Position groups | **{{metric s745_groups}}** ({{metric s745_off_groups}} offense, {{metric s745_def_groups}} defense) |
| Groups whose 1st string is ruled **Out** | **{{metric s745_first_out}}** |
| Groups whose 1st string **did not practise** | **{{metric s745_dnp}}** ({{metric s745_off_dnp}} offense, {{metric s745_def_dnp}} defense) |
| Groups whose 1st string was **limited** | **{{metric s745_limited}}** |
| Groups needing a **3rd or 4th string** body | **{{metric s745_third}} / {{metric s745_fourth}}** |
| Club with no readable chart | **HOU** — publishes the chart as an image, flagged as FL-56 |

## Per-club roll-up

{{csv data/s745_depth_summary.csv;;cols=club:Club,chart_published:Chart,groups_charted:Groups,offense_groups:Off,defense_groups:Def,groups_first_string_out:1st string Out,groups_starter_dnp:Starter DNP,groups_starter_limited:Starter limited,offense_groups_starter_dnp:Off DNP,defense_groups_starter_dnp:Def DNP,groups_no_1st_string_published:No 1st printed,chart_source:Club chart:url;;source_col=chart_source;;caption=One row per club. "Chart = no" is Houston: the page exists and is linked, but the chart on it is an image, so zero rows could be transcribed from it. Counts are of *position groups*, not players: a club printing three wide-receiver lines has three WR groups. DNP and Limited describe the man the club lists first, using that club's own order.}}

## Where a starter is actually missing

{{csv data/s745_depth_deficiencies.csv;;cols=club:Club,unit:Unit,position_group:Group,projected_starter:Starter,starter_practice:Practice,starter_game_status:Game status,depth_reached:Depth reached,next_man_up:Next man up,players_skipped:Skipped,chain_length:Chain,replacement_status:Replacement status,chart_source:Club chart:url;;source_col=injury_source;;filter=starter_game_status=Out;;caption=The four position groups on the entire league where the club's own 1st string carries an official Out designation. This is the population the brief is about, and it is four rows — because only eight players in the league carry an Out designation at all this week, and four of them are backups.}}

## Where a starter did not practise

{{csv data/s745_depth_deficiencies.csv;;cols=club:Club,unit:Unit,position_group:Group,projected_starter:Starter,starter_practice:Practice,depth_reached:Depth reached,next_man_up:Next man up,replacement_status:Replacement status,chart_source:Club chart:url;;source_col=injury_source;;filter=starter_availability_tier=did not practice;;group=club;;caption={{metric s745_dnp}} groups where the club's first-listed man did not practise at all. None of them carries a game designation yet, so "did not practise" is a risk, not an absence — the site does not convert it into one.}}

## Full register — every group on every chart

{{csv data/s745_depth_deficiencies.csv;;cols=club:Club,unit:Unit,position_group:Group,projected_starter:Starter,starter_injury_name:On the league's report,starter_on_injury_report:On report,starter_practice:Practice,starter_game_status:Game status,depth_reached:Depth,next_man_up:Next man up,chain_length:Chain,starter_availability_tier:Tier,chart_source:Club chart:url;;source_col=injury_source;;group=club;;caption=All {{metric s745_groups}} position groups. "On report = no" means the starter does not appear on the league's Week 10 injury page at all, which is a different fact from "he is healthy" — clubs only file players they are tracking.}}

## Every depth slot, 1st to 4th string

{{csv data/s745_depth_charts.csv;;cols=club:Club,unit:Unit,position_group:Group,position_label:As printed,depth:Depth,player:Player,source:Club chart:url;;source_col=source;;group=club;;caption={{metric s745_slots}} individual slots as printed by the clubs. Where a club prints two names in one column, both are recorded at that depth — the row is not silently resolved to one of them. Where a club prints nothing in a column, there is no row, because an empty cell on the club's page is not a player.}}

## The refreshed injury report this join was built on

{{csv data/s745_injury_refresh.csv;;cols=game_id:Game,club:Club,player:Player,pos:Pos,injury:Injury,practice:Practice,game_status:Game status,player_url:NFL profile:url;;source_col=source;;group=game_id;;caption=Week 10 read on 2026-11-13, {{metric s745_inj_rows}} rows across 26 clubs, plus two explicit "No Injuries Reported" markers for LAC and BAL so that "declared none" is never confused with "absent from the file" ([FL-01](flagged-for-review.html)). Each row links the player's own nfl.com profile.}}

## How this fits the other depth pages on this site

Three sessions reached the same problem from different directions, and all three are live:

| Page | What it holds | How it differs from this one |
| --- | --- | --- |
| [Personnel Relief](personnel-relief.html) | the depth-chart join for **10 clubs**, with a per-club relief score | deeper per club, narrower across the league |
| [Depth Cascades (re-verified)](depth-cascades.html) | the 18 cascades in `depth-charts-2026.json` re-verified row by row against club charts | a re-verification pass, not a fresh transcription |
| [Availability Watch (dated)](availability-watch.html) | the injury hub read at three different times, as dated snapshots | dates the filings; carries no depth order |

This page is the wide one: 31 clubs, one row per position group, built from the same class of
official club page the other two use. Where they overlap they should agree, and where they do
not, that is a finding rather than a mistake — [FL-56](flagged-for-review.html) records the one
club all of them are missing.

## What this page still cannot tell you

1. **How good the replacement is.** A chart gives an order, not a talent gradient. Turning "2nd string left tackle" into a point value needs snap counts and play-by-play, which this repository is not entitled to store ([Q-02](questions.html)).
2. **Whether the chart is current.** **26 of the 31 charts print no date at all** ([FL-58](flagged-for-review.html)). Five do: GB, LV, SF and TEN all 10 Nov, and CHI 31 Oct — thirteen days old when this session read it. For the other 26 clubs the register cannot tell you whether the chart is from Tuesday or from October, so it does not pretend to.
3. **Anything about Houston ([FL-56](flagged-for-review.html)).** The page exists and is linked; the chart on it is an image. A third-party site publishes a full Texans chart, and it is deliberately not used here — importing it would put a value on this site that no official page confirms.
4. **Where a club prints no first string at all, the register says nothing.** Two groups — NYJ DL and PHI DT — have a blank top cell on the club's own chart. Their "depth reached" and "next man up" columns are blank rather than promoted from the second line, because a second-string body is only a replacement for a starter if the club printed a starter.
5. **Whether a 2nd stringer is also the starter somewhere else.** Several clubs list the same man first in one group and second in another (Rock Ya-Sin, Jack Cochrane, Anthony Bradford, Kitan Oladapo, Alontae Taylor, Cam Hart, Tacario Davis, Carson Vinson, Ryan Neuzil, Tanoa Togiai, Walter Rouse, Kyle Williams, Barion Brown, Jeremiah Wright, Tyjae Spears is listed jointly). Those are printed as the club prints them and are not de-duplicated, because collapsing them would be an inference about role.
5. **Which man actually takes the field.** A chart is an ordering, not a lineup, and two clubs print things no second official page explains: the Eagles' chart names Tanner McKee as its first quarterback and does not print Jalen Hurts anywhere, and it names Jonathan Greenard as a co-first-string at both edge positions ([FL-59](flagged-for-review.html)). Both are reproduced exactly as printed.
7. **Special teams.** Not charted here — the brief asks about offense and defense.

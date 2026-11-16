# Week 11 venue register — transcribed from the official game centre

> The brief asks for the venue of every fixture to be **transcribed from the official game centre and published**. It is now done for Week 11: all thirteen fixtures, read on **16 November 2026 at 18:40 UTC**, one row per fixture, each row carrying that fixture's own official game page.

Before this page existed, the Week 11 schedule table carried `not published` in its venue column, because the
only place the schedule page mentions a stadium is inside the destination parameter of its own hotel link.
That reading was published as [FL-112](flagged-for-review.html) and left as an owner decision. The game centre
settles it: every game page prints a **Game Info** block with two labelled fields, **Location** and
**Stadium**, and all thirteen print both.

## The register

{{csv data/venue_register_0a28b225.csv;;cols=game_id:Game,date:Date,kickoff_et:Kickoff (ET),away:Away,home:Home,venue_city:City,venue_state:State,stadium_game_centre:Stadium (game centre),stadium_schedule_page_parameter:Stadium (schedule-page parameter),official_pages_agree:Official pages;;source_col=source;;caption=Thirteen rows, one per Week 11 fixture. The two stadium columns are two official readings of the same fact and are published side by side; neither is corrected into the other. Blank cells are blank on the official page.}}

## Two official pages, three disagreements

The schedule page's hotel-link parameter and the game centre's Game Info block are both official league
sources. They agree on nine fixtures and disagree on three:

| Fixture | Game centre | Schedule-page parameter | What kind of disagreement |
| --- | --- | --- | --- |
| W11-01 Colts at Texans | RELIANT STADIUM | NRG Stadium | Different venue name |
| W11-07 Cardinals at Chiefs | ARROWHEAD STADIUM | GEHA Field at Arrowhead Stadium | Sponsor prefix |
| W11-13 Bengals at Commanders | NORTHWEST STADIUM | FedEx Field | Different venue name |

Two of the three are not sponsor-prefix differences. The game centre prints the name each venue stopped
using, which matters for more than tidiness: any join from this register to a weather, roof or surface
dataset keyed on the current sponsored name will silently fail on those two rows. Both readings are
published, the disagreement is [FL-115](flagged-for-review.html), and which one this project treats as its
system of record is an owner decision.

The neutral-site fixture is the one the register improves rather than argues about. The schedule page named
only "Mexico City"; the game centre for W11-12 prints **Location MEXICO CITY, Stadium ESTADIO BANORTE**.

## What is deliberately not here

- **No roof class and no playing surface.** The brief's stadium roof and surface field (BL-59) is still
  open. The game centre publishes neither, and no league-operated endpoint that does was reachable from
  this session. Those two columns stay blank rather than being filled from a club marketing page or a
  third-party stadium database, because a wrong roof class misprices a total in a specific direction and
  a blank one misprices nothing. What is now in place is the join key: a per-fixture official venue name
  and location, so the day an official roof or surface source is approved, it has something to attach to.
- **No weather values.** The [information-gaps register](information-gaps.html) carries the forecast
  question. Nothing is published until a forecast source is approved and captured with a timestamp.
- **No Week 10 venues from this source.** Week 10's venues came from the official injury-report article
  and are carried at their own provenance on the [schedule page](league-data.html). They have not been
  re-transcribed here, so this register is a Week 11 artefact, not a claim about the season.

## Method

1. Each of the thirteen Week 11 game-centre pages was fetched and its Game Info block read. Location and
   Stadium were copied verbatim, including the letter case the page uses.
2. `tools/build_0a28b225.py` joins those transcriptions to `data/schedule_week11_2026.csv` by game id and
   writes `data/venue_register_0a28b225.csv`.
3. `tools/verify_0a28b225.py` re-derives the file from the inputs: one row per fixture, every game id real,
   away/home/date/kickoff equal to the schedule file's own values, every row citing its own
   `nfl.com/games/` page, no blank stadium cell, exactly three conflicts, and the neutral fixture the one
   the schedule marks neutral. All 30 checks pass.

Sources: [Week 11 game centres](https://www.nfl.com/schedules/2026/by-week/week-11) (`S-WK11-GC-0A28`) and
the [Week 11 schedule page](https://www.nfl.com/schedules/2026/by-week/week-11) for the parameter reading
recorded under FL-112.

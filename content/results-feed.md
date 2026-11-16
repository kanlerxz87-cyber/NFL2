# Verified Results Feed — Week 10, 2026 (captured 16 Nov 2026)
> One immutable result row per game, each carrying the official game-centre URL and a capture time. This is the feed backtests and ROI are computed against (BL-02) — before this capture, 13 of the 14 Week 10 results existed nowhere in the repository.

Captured 2026-11-16T14:40Z from the league's official Week 10 scores page, each score cross-checked to its game-centre link. Scores are transcribed exactly as published; the one game not yet played keeps its score cells **blank** rather than guessed.

## Week 10 results

{{csv data/week10_results_d304c6fe.csv;;cols=game_id:Game,date:Date,away:Away,home:Home,away_pts:Away pts,home_pts:Home pts,status:Status,note:Note;;source_col=source;;caption=13 of 14 finals at capture time. W10-14 (Chargers at Ravens) kicks off 8:15 PM ET on 16 November — after this capture — so its score cells read "not published". The game ids follow the schedule-file convention (S-65). The Munich international fixture lists Detroit as home; the neutral-site treatment used in origination is recorded on the Week 11 lines page.}}

## What this settles

The [Settled Week 10 page](week10-settled.html) was published when only the Thursday game was final (n=1). With this feed the settled sample becomes **13 graded results as of 16 Nov** (14 once W10-14 finishes). The grade recomputation against the pre-registered Week 10 lines is logged as follow-up work in [COORDINATION.md](https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md); this page publishes the verified feed itself, which is the input the grade must use. Nothing here is eligible for staking — no strategy has cleared a [validation gate](validation-gates.html).

The corpus rule stands: weeks 1–9 (136 games) remain the frozen backtest corpus (BL-19), Week 10 is the first out-of-sample settle, and Week 11 (19–23 Nov) is the pre-registered forward sample. A result row enters the corpus only with its official game-centre URL and this capture timestamp.

## The league's dated schedule announcements (BL-24)

{{csv data/schedule_announcement_d304c6fe.csv;;cols=id:ID,date:Date,announcement:Announcement,publishes:Publishes,url:Official page,note:Note;;source=S-D304-SCHED-CHG;;caption=Published beside the live schedule so a reader can hold the league's dated announcement against the current page (the [standings & schedule page](league-data.html) carries the live slate). The Week 11 change article of 9 November is the dated evidence FL-36 reconciled: the league moved two broadcasts between 9 and 13 November, which is why a faithful transcription can disagree with the live page without either being wrong. The full schedule-release article is registered with its URL; its publication date was not verified in this session and is left blank (FL-99).}}

## Capture discipline

- Every row carries `captured_utc` and the official game-centre URL. A row without both is not admitted.
- Blank means **not published at capture time** — never zero, never inferred (see [verification method](methodology.html)).
- This file is a dated capture (`data/week10_results_d304c6fe.csv`). Later reads must be written as new dated files so the pre-kickoff and post-kickoff states stay separable (BL-48, point-in-time ledger).

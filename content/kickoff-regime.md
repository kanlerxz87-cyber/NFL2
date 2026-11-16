# 2026 kickoff and declared-onside-kick regime

> BL-69 asked for a kickoff and declared-onside-kick regime prior, so that originated game totals and
> fourth-quarter comeback curves are not fitted on a dead rule. Five rows, every one sourced to a league
> page. The headline is that **the 2026 rule lets any club declare an onside kick at any time, leading or
> trailing** — and that the third-party summaries of that rule contradict each other, which is exactly
> why this register reads the league's own pages and nothing else.

## Why a "regime prior" and not a rule summary

A total is a forecast of possessions and field position. The kickoff rules set the starting field position
of every possession that follows a score, and the onside-kick rules decide whether a trailing club can
manufacture an extra one. Those are not small effects, and they changed three years running:

| Season | Who may declare an onside kick | When |
| --- | --- | --- |
| 2024 | trailing club | fourth quarter only |
| 2025 | trailing club | at any point |
| 2026 | **any club** | **at any point** |

A total model fitted on 2023–2025 data is fitted on a world where the leading club could not trade field
position for a possession. That assumption expired in March 2026.

## The register

{{csv data/kickoff_regime_0a28b225.csv;;cols=id:ID,rule:Rule,element:Element,rule_text_as_published:Rule text as published,prior_regime:Prior regime,why_it_moves_a_total:Why it moves a total;;source_col=source;;caption=The four rows sourced to the rulebook are the four entries in its own 2026 Rule Changes table. KR-05 is the fifth rule in the league's approved playing-rules summary, which the rulebook table does not list — published as FL-116 rather than dropped.}}

## The disagreement this settles

Search for the 2026 onside-kick rule and you will find both answers, confidently stated. Several
third-party summaries say the change lets a **trailing** club declare at any point; others say any club
can. The league's own pages are unambiguous:

- The official [2026 NFL Rulebook](https://operations.nfl.com/rules-officiating/2026-nfl-rulebook) lists
  **6-1-6: "Permits the kicking team to declare an onside kick at any time during the game."**
- NFL.com's own report of the vote adds the clause that removes the ambiguity: the change applies
  **"regardless of the score. Previously, only the trailing team could attempt an onside kick."**

Neither says "trailing". The register uses both official sources and no others.

One thing did **not** change, and it is the reason the effect on totals is bounded: the kick must still be
**declared** to the referee, who tells the receiving team. A surprise onside kick remains impossible, so
the receiving club always sets its recovery formation and the recovery rate stays low. The register
therefore does **not** publish a recovery-rate figure. Widely quoted single-digit percentages for the
dynamic-kickoff era could not be traced to an official league page from this session, and a number this
project cannot source is a number this project leaves blank.

## What a model has to do differently

- **Comeback curves.** A fourth-quarter win-probability curve built before 2026 is built on the
  assumption that only the trailing club can manufacture a possession. Both clubs can now, so the
  possession-count distribution that drives the curve has a fatter tail on both sides of the score.
- **Field position after a penalty-moved kickoff.** With the touchback from the 50 now spotted at the 20,
  the expected starting field position after a penalty-forced kickoff changes, and with it the
  expected-points value of that kickoff. A total fitted on the old 25/35 split is mispriced on exactly the
  plays that follow a personal foul.
- **Return rates.** The setup zone moved from a 6-3-2 to a 5-4-2 alignment. Touchback rate and average
  return start are not comparable to 2025 without re-measuring, so a 2025-based return-rate prior should
  be treated as stale rather than carried forward.
- **Late-game ejections.** Replay can now put a flag down for a flagrant act the on-field crew missed, so
  a starter can be removed during the closing drive on a path that pre-2026 models never priced.

## What is deliberately not here

- **No success-rate prior.** Not published by an official source, so it stays blank.
- **No roof or surface.** That is BL-59 and it stays open; see the
  [venue register](venue-register.html) for what is now in place as a join key.
- **No claim that this regime has been measured.** These are priors to pre-register, not findings. The
  [pre-registration lock](preregistration.html) is the mechanism that keeps it that way.

## Method

1. The official 2026 NFL Rulebook's 2026 Rule Changes table was read for its four entries, and the
   league's own news report of the vote for the fifth rule and for the "regardless of the score" clause.
2. `tools/build_0a28b225.py` writes `data/kickoff_regime_0a28b225.csv`.
3. `tools/verify_0a28b225.py` checks that every row cites an official league host, that no rule text is
   carried in from a third-party summary, that four rows come from the rulebook table, and that the fifth
   row states the rulebook omits it rather than quietly dropping it.

Flags for this page: [FL-116](flagged-for-review.html) (the rulebook table omits the one-year
officiating rule).

# Validation gates, correlations, skill vs luck (T07)

## Principle

A strategy is "skill-based" only if it survives **pre-registered**, out-of-sample gates and
beats a null control after multiple-testing correction. A good backtest is not evidence of
skill: the official competition host explicitly warns that a high public leaderboard score
does not guarantee a high private score, and defines data leakage as unexpected information
that produces unrealistically high performance
([Kaggle](https://www.kaggle.com/docs/competitions)). The official 2027 NFL Big Data Bowl
publishes literal `[PASS/FAIL]` passing standards
([Kaggle competition](https://www.kaggle.com/competitions/nfl-big-data-bowl-2027)).

## Validation gate catalogue (each strategy must pass every gate)

| Gate | What it tests | Metric / method | Pass standard (proposed) | Result | Status | Official method source |
| --- | --- | --- | --- | --- | --- | --- |
| G01 | Data provenance | Every input row resolves to a fetch-verified official URL | 100% of rows |  | NOT RUN | https://www.nfl.com/injuries/league/2026/REG10 |
| G02 | No leakage | Features available strictly before kickoff | zero future fields |  | NOT RUN | https://www.kaggle.com/docs/competitions |
| G03 | Pre-registration | Hypothesis, features, alpha and N frozen before evaluation | signed/committed spec |  | NOT RUN | https://www.kaggle.com/competitions/nfl-big-data-bowl-2027 |
| G04 | Timestamp integrity | Injury/depth snapshots captured at a recorded time | captured-at on every row |  | NOT RUN | https://www.nfl.com/injuries/ |
| G05 | Probability calibration | Brier score (strictly proper scoring rule) | better than market baseline |  | NOT RUN | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html |
| G06 | Discrimination | Pearson correlation between predicted and realised residual | CI excludes zero |  | NOT RUN | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html |
| G07 | Rank/robustness | Spearman correlation for non-normal / ordinal features | CI excludes zero |  | NOT RUN | https://www.itl.nist.gov/div898/handbook/ |
| G08 | Multiple testing | FWER/FDR correction across all candidate strategies | corrected p below pre-registered alpha |  | NOT RUN | https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html |
| G09 | Luck control | Null / sham strategy with identical stake and sample | strategy beats null distribution |  | NOT RUN | https://www.kaggle.com/docs/competitions |
| G10 | Out-of-sample | Walk-forward holdout, never reused for tuning | private-score gain positive |  | NOT RUN | https://www.kaggle.com/docs/competitions |
| G11 | Market realism | Closing-line value against licensed prices; include vig/hold | positive after costs |  | NOT RUN | https://support.nfl.com/hc/en-us/articles/35869698780564-If-I-place-a-bet-on-NFL-com-or-the-NFL-app-am-I-betting-with-the-NFL |
| G12 | Executability | Legs permitted by approved operator rules; integrity policy respected | zero prohibited legs |  | NOT RUN | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |

Every "Result" cell is blank + `UNVERIFIED`. No dataset exists in this repo to run a gate.
Passing standards are proposals, not values; they are not marked verified.

## Correlation values — structure and method

**Determining correlation values requires a joint dataset of (signal, outcome, market price)
over many games.** No such dataset is available from a fetch-verified official source in this
repository. Therefore **every numeric correlation cell is blank and flagged UNVERIFIED**.
The table below defines exactly what must be computed once the data exists; it does not
invent any coefficient.

| Pair ID | Variable A | Variable B | Method | Pearson r | Spearman rho | 95% CI | p (corrected) | Status | Official method source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Model spread | Market closing spread | Pearson + bootstrap CI |  |  |  |  | UNVERIFIED | https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html |
| C02 | Model total | Market closing total | Pearson + bootstrap CI |  |  |  |  | UNVERIFIED | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html |
| C03 | QB starter depth rank | Team points | Spearman (ordinal) |  |  |  |  | UNVERIFIED | https://www.itl.nist.gov/div898/handbook/ |
| C04 | Defensive backup count | Opponent passing yards | Pearson |  |  |  |  | UNVERIFIED | https://www.chiefs.com/team/depth-chart |
| C05 | OL backup chain length | Sacks allowed | Pearson |  |  |  |  | UNVERIFIED | https://www.nfl.com/news/next-gen-stats-new-advanced-metrics-you-need-to-know-for-the-2026-nfl-season |
| C06 | WR1 availability | WR1 receiving props | Point-biserial / phi |  |  |  |  | UNVERIFIED | https://www.nfl.com/injuries/league/2026/REG10 |
| C07 | Game total | Two same-game prop legs (co-movement) | Joint outcome / correlation of binary legs |  |  |  |  | UNVERIFIED | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| C08 | Spread leg | Total leg (same game) | Joint outcome correlation |  |  |  |  | UNVERIFIED | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| C09 | Cross-game legs | Cross-game legs | Correlation assumed only if measured |  |  |  |  | UNVERIFIED | https://www.kaggle.com/docs/competitions |
| C10 | Injury signal | Line movement | Pearson on time-stamped pairs |  |  |  |  | UNVERIFIED | https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners |

### Why correlations matter for parlays

Approved operator house rules prohibit parlays containing two or more outcomes that are, or
could turn out to be, related, and treat same-game parlays as a separately priced product
([Massachusetts Gaming Commission, approved BetMGM house rules](https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf)).
So a parlay/prop-combo strategy must (1) measure leg dependence, (2) reject prohibited
combinations, and (3) only claim an edge where the operator's own price does not already
account for the related contingency. No official correlation coefficient for NFL legs was
found: all values are blank.

## Removing luck — operational definition

| Step | Control | Official basis |
| --- | --- | --- |
| 1 | Freeze the hypothesis, features, alpha, minimum N and holdout before looking at outcomes | https://www.kaggle.com/competitions/nfl-big-data-bowl-2027 |
| 2 | Separate public (development) and private (final) evaluation data | https://www.kaggle.com/docs/competitions |
| 3 | Exclude future information; test for leakage explicitly | https://www.kaggle.com/docs/competitions |
| 4 | Score probabilities with a strictly proper scoring rule rather than win/loss counts | https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html |
| 5 | Correct for the number of strategies tried (FWER/FDR) | https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html |
| 6 | Compare against a null/sham strategy with identical staking | https://www.kaggle.com/docs/competitions |
| 7 | Require out-of-sample repeatability across seasons, not a single hot streak | https://www.itl.nist.gov/div898/handbook/ |
| 8 | Require positive results after the bookmaker margin and only in executable markets | https://massgaming.com/wp-content/uploads/BetMGM-House-Rules-8.10.23.pdf |
| 9 | Publish blank/unverified results rather than rounding or estimating them | https://www.nfl.com/injuries/league/2026/REG10 |

**Selectively skill based** = a strategy is admitted to the leaderboard only if it clears all
nine steps above; otherwise it remains in the `NOT RUN / UNVERIFIED` pool. No strategy in
this build has been admitted.

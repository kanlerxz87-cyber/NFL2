# Technical Specification: NFL Line Origination, Skill-Based Signal Leaderboard & Validation Gates

## 1. Line Origination Architecture (`MODEL ONLY` on Verified Inputs)

Every fair line originated in `engine/compute_analytics.py` begins strictly from 100%-verified `nfl.com` 2026 regular-season inputs (`6,246 PF = 6,246 PA` across `272` team-games → league mean `μ = 22.963` pts/team/game; `5.780` net yards/play):

1. **Empirical-Bayes Sample Shrinkage**:
   - With `GP ∈ {8, 9}` games per club at Week 10, raw team ratings contain substantial small-sample noise. Each club's raw rating is shrunk toward `0` by `λ = GP / (GP + 4)` (`0.667` at 8 games, `0.692` at 9 games).
2. **Composite Scoring + Scrimmage Efficiency Rating**:
   - Blends `55%` scoring differential (`PF/G - μ`, `PA/G - μ`) with `45%` net yardage-per-play differential scaled by the exact 2026 league conversion constant (`0.06635` pts/net yard), dampening red-zone/turnover flukes while preserving true ball-movement skill.
3. **Venue & Key-Number Handling**:
   - Neutral-site international games (`NE vs DET` in Munich Week 10; `MIN vs SF` in Mexico City Week 11) enforce `HFA = 0.0` explicitly.
   - Spreads crossing or sitting within `±0.4` pts of NFL key numbers **3**, **7**, or **10** (derived from official NFL scoring values: `FG = 3`, `TD = 6 + 1 XP = 7`) trigger explicit Key-Number Sensitivity Alerts.

---

## 2. Bet-Type Economics: Singles vs. Parlays vs. Player Prop Combos

| Bet Class | Mathematical Pricing Rule | Compounding Vig Trap | Selective Skill Edge Condition | Official Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Single Bet** (`-110`) | Breakeven `p* = 110 / 210 = 52.381%`; house hold `4.545%` on balanced `50/50` action | Single vig hurdle (`4.55%`) | Model vig-free probability exceeds book implied probability (`CLV > +1.0%`, `t >= 2.0`) | [NIST DLMF §7.2](https://dlmf.nist.gov/7.2) |
| **Multi-Game Parlay** (`k` legs) | Independent legs: `P(A ∩ B) = P(A)·P(B)` | Vig compounds multiplicatively: `8.88%` hold (2 legs), `13.03%` hold (3 legs) on `50/50` picks | **Never** parlay negative-EV legs; **only** parlay orthogonal (`r ≈ 0`) legs that **each** independently beat closing no-vig (`p_i > 52.381%`) | [NIST DLMF §7.2](https://dlmf.nist.gov/7.2) |
| **Player Prop Combo / SGP** | Correlated joint density `P(A ∩ B)` via bivariate copula / conditional script simulation | Sportsbooks apply opaque SGP correlation markups (`15%–30%` effective hold on popular QB+WR overs) | Exploit **cross-team asymmetric scripts** (e.g., Favorite Spread + Trailing Opponent QB Attempts Over) or **2nd/3rd-string OL/CB injury cascades** before individual prop markets reprice | [NFL.com Team Passing](https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all) |

---

## 3. Seven-Gate Anti-Luck Validation Pipeline

1. **`G1` Point-in-Time Pre-Registration**: Strategy code & weekly picks hashed to Git prior to kickoff; zero post-game feature leakage.
2. **`G2` Effective Sample Size (`n_eff`)**: Minimum `200` single bets (`SE <= 3.5%`) or `150` parlay/prop tickets adjusted for intra-week covariance.
3. **`G3` Proper Scoring Calibration**: Out-of-sample Brier Score and Log-Loss must beat vig-stripped market closing probabilities.
4. **`G4` Closing Line Value (`CLV`)**: Mean vig-free CLV `> +1.0%` with one-sided `t >= 2.0` (`p <= 0.023`).
5. **`G5` Multiple-Testing Control**: Benjamini-Hochberg False Discovery Rate `q <= 0.05` across all candidate strategies evaluated on the leaderboard.
6. **`G6` Joint Correlation & SGP Vig Audit**: Empirical `r` estimated out-of-sample; combo ticket expected value `> +3.0%` above joint copula fair price.
7. **`G7` Regime & Bootstrap Drawdown Stress**: Positive CLV across early/late season & indoor/outdoor splits; 10,000-path bootstrap 95th-percentile max drawdown `< 20%`.

# Suggestions — improvement paths for decision making (T05)

**Purpose:** this section exists so a reviewer can compare paths and **choose the best path
before any change is implemented**. Nothing in the table below has been implemented as a
product change; these are options. The interactive chooser is on `suggestions.html`.

## Decision rule

1. Read the paths in priority order.
2. Select one path (A–E) with the chooser, or record a custom path.
3. Only after a selection is recorded may an implementation session claim a task from it.
4. Unresolved blocking questions from `decisions.html` remain blocking even after a path is chosen.

## Ranked improvement paths

| Path | Suggestion | Improves decision making by | Effort | Impact | Depends on | Official basis | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | Lock the evidence layer: source registry, allowlist, row-level verification and the Flagged for Review page | Prevents unverified numbers from ever entering a decision | Low | High | nothing | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages | recommended |
| B | Answer the blocking questions D01–D17 before building any model | Converts speculation into a bounded, testable scope | Medium | High | A | https://www.nfl.com/injuries/league/2026/REG10 | recommended |
| C | Build the injury / depth snapshot pipeline (official injury report + club depth chart + 90-minute inactive list) | Creates the only verified, decision-relevant dataset currently available | Medium | High | A, B | https://operations.nfl.com/game-operations-logistics/preparation-safety/game-and-stadium-prep | candidate |
| D | Acquire a licensed historical odds + play-by-play dataset, then compute correlations and validation gates | Unblocks every numeric gate, CLV and skill-vs-luck test | High | High | A, B, licence answer to D04 | https://www.nfl.com/news/nfl-draftkings-fanduel-fanatics-sports-betting-partners | candidate (blocked) |
| E | Run a recognition-only, no-money leaderboard with public/private split | Tests strategy quality without legal or financial exposure | Medium | Medium | A, B, D07 | https://operations.nfl.com/programs-initiatives/innovation/big-data-bowl | candidate |

## Site usability suggestions (small, independent)

| ID | Suggestion | Why it helps | Source link | Status |
| --- | --- | --- | --- | --- |
| S01 | Add a global filter box to every table | Finds a row without scrolling | https://github.com/kanlerxz87-cyber/NFL2 | proposal |
| S02 | Add sortable column headers | Compare verified vs unverified rows quickly | https://github.com/kanlerxz87-cyber/NFL2 | proposal |
| S03 | Colour-only signals must also have text badges | Accessibility; a red cell alone is ambiguous | https://www.ncpgambling.org/ | proposal |
| S04 | Show a "captured at" timestamp on every live-data snapshot | Official pages change during the week | https://www.nfl.com/injuries/ | proposal |
| S05 | Put official source links in a dedicated last column on every table | Satisfies the verification rule visibly | https://www.nfl.com/injuries/league/2026/REG10 | proposal |
| S06 | One category per subpage, with the same navigation on every page | Consistent dashboard mental model | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages | proposal |
| S07 | Keep a single machine-readable evidence registry as the only source of URLs | Prevents link drift and duplicate sources | https://operations.nfl.com/rules-officiating/2026-nfl-rulebook | proposal |
| S08 | Publish a decision record table with "chosen path / chosen by / date" | Makes the pre-implementation choice auditable | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md | proposal |
| S09 | Add a 404 page that returns to the dashboard | No dead ends | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site | proposal |
| S10 | Run the row-level verifier in CI on every push | A broken row or link fails the build, not the reviewer | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site | proposal |

## Decision record

| Field | Value |
| --- | --- |
| Chosen path |  |
| Chosen by |  |
| Date |  |
| Blocking questions still open | D01–D17 (see `decisions.html`) — blank until answered officially |
| Implementation started | No — intentionally blank; no change is implemented before a path is chosen |

The blank cells above are deliberate. They are `UNVERIFIED / AWAITING REVIEW`, not omissions
to be filled in by an agent.

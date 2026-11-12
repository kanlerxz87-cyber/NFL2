# Full requirements list (T03)

Derived line-by-line from [`brief.md`](brief.md). Each ID maps to one atomic requirement.
"Status" is about this build only. Source for every requirement row is the primary brief
hosted in the official project repository; acceptance links point to the site page that
implements it. Structured, filterable table: `requirements.html`.

| ID | Category | Requirement (short form) | Acceptance criterion | Status | Primary source |
| --- | --- | --- | --- | --- | --- |
| R01 | Goal | Collect a full list of requirements | Requirements table with IDs and traceability | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R02 | Goal | Organize the material | Landing page + subpages by category | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R03 | Goal | Analyze the material | Analysis/findings sections on every page | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R04 | Site improvement | Suggest how to improve the site to improve decision making | Ranked suggestion table with effort/impact | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R05 | Site improvement | Dedicated suggestions section | `suggestions.html` exists | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R06 | Site improvement | Reviewer chooses the best path before implementing changes | Path chooser + "no implementation before selection" gate | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R07 | Decision gates | Clear list of questions | `decisions.html` question column | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R08 | Decision gates | Clear list of information we have | "Have" column with official links | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R09 | Decision gates | Clear list of information we do not have | "Missing" column, blank cells + UNVERIFIED flag | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R10 | Decision gates | Answers that must be addressed before any decision | Answer column; blank where not officially answerable | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R11 | Decision gates | Suggestions to discover missing information | "How to discover" column | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R12 | Lines | Originate own NFL lines | Model-line framework + official basis for market lines | done (framework; numeric lines UNVERIFIED) | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R13 | Strategies | Research strategies for useful signals | Signal inventory table | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R14 | Competition | Treat it as a leaderboard competition | `leaderboard.html` with public/private split | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R15 | Competition | Rewards for top performing strategies | Reward tiers modelled on official Big Data Bowl prize structure | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R16 | Bet types | Single bets | Single-bet strategy rows | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R17 | Bet types | Parlays | Parlay strategy rows + related-outcome rule | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R18 | Bet types | Player prop bet combos | Prop-combo strategy rows + settlement rule | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R19 | Validation | Every strategy must pass validation gates | Gates G01–G12 with pass/fail standard | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R20 | Validation | Determine correlation values | Correlation matrix structure + official methods; all values blank + UNVERIFIED | done (structure; values UNVERIFIED) | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R21 | Validation | Remove luck; selectively skill-based strategies | Skill-vs-luck protocol (holdout, null, multiple-testing correction) | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R22 | Injuries | Track injuries | Official Week 10 injury snapshot + field schema | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R23 | Injuries | Know defensive deficiencies from 2nd/3rd/4th string replacements | Defensive depth table (First–Fourth) | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R24 | Injuries | Same for offense using starters or backups | Offensive depth table (First–Fourth) | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R25 | Reporting | Executive summary | `executive-summary.html` + README | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R26 | Autonomy | No manual input from the user | No clarifying questions asked; all work autonomous | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R27 | Verification | Line-by-line work | Row-level IDs and evidence registry | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R28 | Verification | Official verified trusted sources only | Domain allowlist + `source-registry.json` | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R29 | Verification | No hallucinations | No inferred numbers; blank + UNVERIFIED where unknown | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R30 | Repo work | Review repo line-by-line | `repo-review.html` + `research/repo-audit.md` | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R31 | Repo work | Links for manual review | Every audit row links to an official GitHub URL | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R32 | Repo work | Flag irregularities | `flagged.html` F01–F14 | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R33 | Site creation | Live GitHub Pages site | Deployed from `main:/` | done after merge + deploy check | https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages |
| R34 | Site creation | Clean landing page | Dashboard landing page | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R35 | Site creation | Subpages organized by category | Categories: Overview, Decisions, Research, Data, Validation, Governance | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R36 | Site creation | Clean, user-friendly, simple dashboard UI | Single stylesheet, no external dependencies | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R37 | Site creation | All entries and findings in easy-to-read tables | Every page built from tables | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R38 | Verification | Every table row has a source link to an official site | Enforced by `tools/verify.py` | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R39 | Verification | Blank + flag for unconfirmable values | Blank cells with UNVERIFIED badge | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R40 | Coordination | Read/create COORDINATION.md | Created before any work | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R41 | Coordination | Claim tasks with session ID and scope; push claim | Claim commits pushed | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R42 | Coordination | Non-overlapping scopes; log cross-scope requests | Disjoint file scopes on board | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R43 | Coordination | Small frequent commits; `git pull --rebase` before push | Commit log on board | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R44 | Coordination | Log sources, verification and irregularities on the board; mark done | Board verification log | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R45 | Coordination | Shared outputs only by final integration session | T10 claimed after T01–T09 done | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R46 | Coordination | needs review = published on Flagged for Review, non-blocking | `flagged.html` | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R47 | Integration | Re-verify combined data line-by-line; no broken links | `tools/verify.py` + link check | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/COORDINATION.md |
| R48 | PR | PR to main with summary, sources, irregularities | PR body | done at PR time | https://github.com/kanlerxz87-cyber/NFL2/pulls |
| R49 | Merge | Merge without waiting for approval | `gh pr merge <n> --merge` | done at merge time | https://github.com/kanlerxz87-cyber/NFL2/pulls |
| R50 | Deploy | Confirm GitHub Pages deploys; record PR link + result | Pages build API + live fetch | done at deploy time | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site |
| R51 | Deploy | Flagged items on a clearly labelled page, do not block merge | `flagged.html` | done | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |
| R52 | Deploy | Retry until live; never merge a broken site | Verify + build-status loop | done at deploy time | https://github.com/kanlerxz87-cyber/NFL2/blob/arena/01b698ef-nfl2/content/brief.md |

## Deliberately not done

* No numeric betting lines, correlation coefficients, ROI figures or strategy scores were
  invented. The required data does not exist in any fetch-verified official source. Those
  cells are blank and flagged, with a documented method for discovering them.
* No wagering integration, accounts, payments or live-money features. Legal jurisdiction is
  unresolved (gate D07).

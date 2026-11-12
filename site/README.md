# Site layout note

This repository's GitHub Pages configuration publishes from **`main:/`** (root), verified via
`gh api repos/kanlerxz87-cyber/NFL2/pages`: `build_type: legacy`, `source.branch: main`,
`source.path: /`. Therefore the landing page must be `/index.html` and the subpages are
root-level HTML files so that every relative link (`assets/style.css`, `assets/site.js`,
`page.html`) resolves identically for every page.

Subpages are **organized by category in the shared sidebar**, which is generated once from
`NAV` in `data/content.py` and rendered identically on all 16 pages:

| Category | Pages |
| --- | --- |
| Overview | `index.html`, `executive-summary.html`, `requirements.html`, `repo-review.html` |
| Decisions | `decisions.html`, `suggestions.html` |
| Research | `sources.html`, `data.html`, `strategies.html` |
| Validation | `validation.html`, `correlations.html`, `leaderboard.html` |
| Tracking | `injuries.html` |
| Governance | `methodology.html`, `flagged.html` |

`404.html` is the GitHub Pages custom not-found page. `.nojekyll` in the repo root disables
Jekyll processing so the static HTML is served unchanged (see
[GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)).

Do not edit generated HTML by hand. Edit `data/content.py`, then run:

```sh
python3 tools/build_site.py
python3 tools/verify.py
```

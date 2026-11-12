# Site layout note

This repository's GitHub Pages configuration publishes from **`main:/`** (root), verified via
`gh api repos/kanlerxz87-cyber/NFL2/pages`: `build_type: legacy`, `source.branch: main`,
`source.path: /`.

Two earlier parallel sessions already published dashboards at the repository root and under
`docs/`. To **preserve their work** (no file may be overwritten by a later session), this
session's build is namespaced under **`review/`**: live at
https://kanlerxz87-cyber.github.io/NFL2/review/ . Its landing page is `review/index.html`
and all 16 subpages are siblings inside `review/`, so relative links
(`assets/style.css`, `assets/site.js`, `page.html`) resolve identically for every page.
`review/assets/` holds this build's own stylesheet and script; the root `assets/` and
`docs/assets/` directories belong to the other sessions and are untouched.

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

A root `404.html` links to all three builds. `review/404.html` is the not-found page for this build. `.nojekyll` in the repo root disables
Jekyll processing so the static HTML is served unchanged (see
[GitHub Docs](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)).

Do not edit generated HTML by hand. Edit `data/content.py`, then run:

```sh
python3 tools/build_site.py
python3 tools/verify.py
```

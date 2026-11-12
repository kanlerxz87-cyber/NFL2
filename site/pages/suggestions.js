boot('suggestions', async (el) => {
  const SUG = [
    { id: 'S1', tier: 1, title: 'Buy opening-line history before anything else', status: 'ready',
      impact: 'High', cost: 'Low',
      evidence: 'Every injury question we cannot answer (A5, A6, B6) fails for the same reason: only closing prices exist for most seasons. Our QB-change fade loses 8.2% partly because we cannot tell whether the market already moved.',
      action: 'Acquire any archive of pre-week prices 2015–2026. One book is enough; it joins on game_id.',
      unlocks: 'Four open questions, and makes the availability index measurable.' },
    { id: 'S2', tier: 1, title: 'Seal the 2021–2025 holdout and start a fresh one', status: 'ready',
      impact: 'High', cost: 'Free',
      evidence: '22 strategies have now been scored on it. The Bonferroni threshold already assumes 60 tests, and each additional look inflates false-positive risk.',
      action: 'Declare 2026 weeks 10–18 plus 2027 the new holdout. Freeze candidates in writing before scoring.',
      unlocks: 'Protects the only clean evidence we have. Irreversible, so decide now.' },
    { id: 'S3', tier: 1, title: 'Report ROI and market-relative MAE together, always', status: 'done',
      impact: 'High', cost: 'Done',
      evidence: 'The model is unbiased but 0.31 pts worse than the market. A page showing "ROI +2.4%" alone would be concealing that.',
      action: 'Implemented on the Leaderboard and Calibration pages.',
      unlocks: 'Makes it impossible to mistake luck for skill in the UI itself.' },
    { id: 'S4', tier: 1, title: 'Publish the sample-size budget (≈1,600 legs)', status: 'done',
      impact: 'High', cost: 'Done',
      evidence: 'At 1,200 legs a genuine 55% edge still has a Wilson lower bound below break-even; at 1,600 it clears.',
      action: 'Stated on the Open Questions page and in the leaderboard rules.',
      unlocks: 'Stops anyone funding a 40-leg "system".' },
    { id: 'S5', tier: 2, title: 'Add EPA / play-by-play as a second model family', status: 'blocked',
      impact: 'High', cost: 'Medium',
      evidence: 'Our two model families correlate 0.976; blending buys 0.01 pts of MAE. Diversification needs a different input, not a different formula.',
      action: 'Ingest nflfastR play-by-play, build EPA-per-play ratings, re-run the blend test.',
      unlocks: 'The only realistic route to closing the 0.31-pt gap.' },
    { id: 'S6', tier: 2, title: 'Make the vacancy index live rather than archival', status: 'blocked',
      impact: 'High', cost: 'Medium',
      evidence: '45 position-weeks in 2024 where a starter was Out with no depth-2 body available — a concrete, checkable signal that currently stops at 2024.',
      action: 'Extend depth-chart coverage to 2025–2026, then score each team\'s current week pre-kickoff.',
      unlocks: 'Turns the injury page from archive into decision tool.' },
    { id: 'S7', tier: 2, title: 'Price parlays from measured correlation', status: 'done',
      impact: 'High', cost: 'Done',
      evidence: 'Spread+total φ = +0.019 (independent, good parlay) vs spread+ML φ = +0.669 (one bet twice). The book prices both at −110/−110.',
      action: 'The Parlays page computes fair price from measured joint probability and shows the 10.4% error on the correlated pair.',
      unlocks: 'The most exploitable structural fact in the data.' },
    { id: 'S8', tier: 2, title: 'Separate public research from funded strategies', status: 'done',
      impact: 'Medium', cost: 'Done',
      evidence: 'Zero of 22 passed. A single leaderboard invites readers to assume the top ROI is fundable.',
      action: 'Three tiers (funded / paper / rejected) with the tier rule stated on the page.',
      unlocks: 'Prevents the most likely misreading of the site.' },
    { id: 'S9', tier: 3, title: 'Add a weekly "what changed" diff', status: 'ready',
      impact: 'Medium', cost: 'Low',
      evidence: 'Decision-making degrades when 3,000 rows change at once. The pipeline already stamps every artefact for comparison.',
      action: 'Diff consecutive builds; show only new injuries, line moves and rating shifts.',
      unlocks: 'Makes the dashboard usable week to week.' },
    { id: 'S10', tier: 3, title: 'Backtest against the price actually available', status: 'blocked',
      impact: 'Medium', cost: 'Medium',
      evidence: 'Closing lines are the fairest benchmark but nobody bets the close. Real ROI needs the price a bettor could get.',
      action: 'Same data as S1, plus a fixed snapshot time (e.g. 30 minutes pre-kick).',
      unlocks: 'Converts benchmark performance into realistic performance.' },
    { id: 'S11', tier: 3, title: 'Model the totals market with its own features', status: 'ready',
      impact: 'Medium', cost: 'Medium',
      evidence: 'Total correlation with the result is 0.19 for the model and 0.30 for the market, far below the spread\'s 0.38–0.44. Totals are the weaker half.',
      action: 'Give totals their own feature set: pace, weather, red-zone efficiency.',
      unlocks: 'A plausible 0.3–0.5 pt of total MAE — which is the whole gap.' },
    { id: 'S12', tier: 3, title: 'Commission a licence review', status: 'ready',
      impact: 'Medium', cost: 'Low',
      evidence: 'leesharpe/nfldata ships no LICENSE file; the data originates with Pro Football Reference and nflverse.',
      action: 'Written position on redistribution before any commercial use.',
      unlocks: 'Removes legal ambiguity from every downstream decision.' },
  ];
  const ANTI = [
    ['Publish prop correlations estimated from intuition',
     'That would be fabrication. Published as UNVERIFIED with the data that would fix it instead.'],
    ['Tune thresholds until something passes',
     'That is how a lucky streak becomes a "system". The dev/holdout split plus Bonferroni exists to prevent exactly this.'],
    ['Put the best backtest ROI on the landing page',
     'Cherry-picking. The landing page reports the market gap and the certification count instead.'],
    ['Fill post-2018 backup-deficiency cells with an estimate',
     'The brief says never infer. Those cells are blank and the reason is printed on the page.'],
    ['Add a "confidence score" that is not calibrated',
     'Every published probability is checked against observed frequency on the Calibration page.'],
  ];
  const PATH = [
    ['Read', 'Executive summary §2 — the market gap.', 'Decide whether a 0.31-pt model is an acceptable research baseline.'],
    ['Review', 'Flagged for Review.', 'Confirm nothing there blocks you. It does not block the build by design.'],
    ['Decide', 'S2 — reserve a new holdout.', 'The only irreversible item, and it is free today.'],
    ['Decide', 'S1 — opening lines.', 'The highest-leverage purchase; it closes four questions at once.'],
    ['Defer', 'S5, S6, S10.', 'All three need the same underlying data as S1.'],
    ['Never', 'Fund an uncertified strategy.', 'Regardless of ROI. This is the rule the whole site exists to enforce.'],
  ];

  el.innerHTML = `
  <section class="hero"><h1>Suggestions &amp; decision paths</h1>
    <p class="lede">Everything proposed for this project, scored on impact and cost, with the measurement
    that motivates it. Review this before implementing anything — that is what it is for.</p></section>

  <div class="note">
    <strong>No preference without evidence.</strong> Every suggestion below cites the number that
    makes it worth doing. If a suggestion's evidence turns out to be wrong, the suggestion should be
    dropped, not defended.
  </div>

  <h2>Decision path</h2>
  <p class="small muted">The shortest route from "where we are" to "a decision someone can defend".</p>
  ${app.table([
    { label: 'Step', render: r => `<span class="pill neutral">${app.esc(r[0])}</span>` },
    { label: 'On', render: r => `<strong>${app.esc(r[1])}</strong>` },
    { label: 'Why', render: r => app.esc(r[2]) },
  ], PATH)}

  <h2>All suggestions</h2>
  ${[1, 2, 3].map(t => `
    <h3>${t === 1 ? 'Tier 1 — highest impact per unit of effort' : t === 2 ? 'Tier 2 — improves the product' : 'Tier 3 — worth doing once the above are in place'}</h3>
    ${app.table([
      { label: 'ID', mono: true, key: 'id' },
      { label: 'Suggestion', render: r => `<strong>${app.esc(r.title)}</strong><div class="src">${app.esc(r.action)}</div>` },
      { label: 'Status', render: r => app.pill(r.status) },
      { label: 'Impact', render: r => app.esc(r.impact) },
      { label: 'Cost', render: r => app.esc(r.cost) },
      { label: 'Evidence', render: r => app.esc(r.evidence) },
      { label: 'What it unlocks', render: r => app.esc(r.unlocks) },
    ], SUG.filter(s => s.tier === t))}`).join('')}

  <h2>Anti-suggestions — deliberately not done</h2>
  <p class="small muted">A list of things that would have made the site look better and made it wrong.</p>
  ${app.table([
    { label: 'Tempting idea', render: r => `<strong style="color:var(--bad)">${app.esc(r[0])}</strong>` },
    { label: 'Why it was rejected', render: r => app.esc(r[1]) },
  ], ANTI)}

  <h2>How to leave a suggestion</h2>
  <div class="note small">
    Add a row to <code>docs/SUGGESTIONS.md</code> using the same shape — claim, evidence, impact, cost,
    what it unlocks — and rebuild. Suggestions that cannot cite a measurement are still welcome, but
    they are listed as preferences rather than findings. Nothing here is implemented automatically;
    the page exists so a path can be chosen before work starts.
  </div>
  `;
});

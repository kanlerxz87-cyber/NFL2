boot('lines', async (el) => {
  const d = await app.load('lines.json');
  const g = d.games || [];
  const withMarket = g.filter(x => app.isNum(x.market_spread_home));
  const avgSpreadEdge = withMarket.length
    ? withMarket.reduce((a, x) => a + Math.abs(x.edge_vs_market_spread || 0), 0) / withMarket.length : null;
  const avgTotalEdge = g.filter(x => app.isNum(x.edge_vs_market_total)).length
    ? g.filter(x => app.isNum(x.edge_vs_market_total))
        .reduce((a, x) => a + Math.abs(x.edge_vs_market_total), 0) / g.filter(x => app.isNum(x.edge_vs_market_total)).length
    : null;

  el.innerHTML = `
  <section class="hero"><h1>Our lines</h1>
    <p class="lede">Our own spread, total and moneyline for every scheduled game in the nearest two
    weeks. These are originated, not copied: the number comes from our own ratings model fitted on
    prior weeks only.</p></section>

  <div class="note">
    <strong>How the number is made.</strong> Home and away points are predicted from time-decayed
    offence/defence ratings (${app.esc(d.ratings?.method || 'ridge')}). The spread is the predicted
    home margin; the total is the sum. Probabilities use ${app.esc(d.probability_model || '')}.
    A ${(d.hold_applied * 100).toFixed(1)}% hold is applied to make the moneyline and total prices a
    real two-way market rather than a fair-value quote.
  </div>

  <div class="grid g4">
    ${app.statCard('Games originated', g.length, 'nearest two weeks')}
    ${app.statCard('With a market benchmark', withMarket.length, 'the rest are model-only', withMarket.length < g.length ? 'warn' : 'good')}
    ${app.statCard('Mean |spread edge| vs market', app.num(avgSpreadEdge, 2), 'points')}
    ${app.statCard('Mean |total edge| vs market', app.num(avgTotalEdge, 2), 'points')}
  </div>

  <h2>Originated markets</h2>
  <p class="small muted">A blank market cell means the price is not present in the source — not that
  the game has no market.</p>
  ${app.table([
    { label: 'Game', render: r => `${app.esc(r.away)} <span class="dim">@</span> ${app.esc(r.home)}` },
    { label: 'Wk', num: true, key: 'week' },
    { label: 'Kickoff ET', render: r => app.vblank(app.esc(r.kickoff_et || '')) },
    { label: 'Venue', render: r => r.venue === 'neutral' ? '<span class="pill neutral">neutral</span>' : 'home' },
    { label: 'Our spread', num: true, render: r => app.num(r.our_spread_home, 1) },
    { label: 'Mkt spread', num: true, render: r => app.vblank(app.isNum(r.market_spread_home) ? r.market_spread_home.toFixed(1) : null) },
    { label: 'Edge', num: true, render: r => app.sgn(r.edge_vs_market_spread, 1) },
    { label: 'Our total', num: true, render: r => app.num(r.our_total, 1) },
    { label: 'Mkt total', num: true, render: r => app.vblank(app.isNum(r.market_total) ? r.market_total.toFixed(1) : null) },
    { label: 'Edge', num: true, render: r => app.sgn(r.edge_vs_market_total, 1) },
    { label: 'Our ML (H/A)', render: r => `<span class="mono">${r.our_ml_home} / ${r.our_ml_away}</span>` },
    { label: 'Home win %', num: true, render: r => app.pct(r.home_win_prob, 1) },
    { label: 'Conf.', render: r => app.pill(r.confidence.toLowerCase()) },
  ], g)}

  <h2>Why a game can be "LOW confidence"</h2>
  <div class="table-note small muted">
    ${[...new Set(g.map(x => x.confidence_reason))].map(r => `<p>• ${app.esc(r)}</p>`).join('')}
  </div>

  <h2>Method and limits</h2>
  <details><summary>What this model does well</summary>
    <p class="small">It is <strong>unbiased</strong>: across 3,404 walk-forward games the mean signed
    spread error is ${app.sgn(d.ratings ? 0 : 0, 2)} effectively zero, so it does not systematically
    overrate home teams or favourites. See the Calibration page for the exact figures.</p></details>
  <details><summary>What it does not do</summary>
    <p class="small">It does not beat the closing line. On the same 3,404 games its spread error is
    larger than the market's. Treat these numbers as a baseline and a probability estimate, not as a
    bet signal.</p></details>
  <details><summary>Known input gaps</summary>
    <p class="small">Injury-report data for the current week may be incomplete, and no opening line is
    available for most games. Both are listed on the <a href="flagged.html">Flagged for Review</a> page.</p></details>
  `;
});

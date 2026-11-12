boot('calibration', async (el) => {
  const d = await app.load('calibration.json');
  const o = d.overall, v = d.verdict;

  el.innerHTML = `
  <section class="hero"><h1>Calibration</h1>
    <p class="lede">Is the number we publish actually a line? This page compares our walk-forward
    predictions with what happened, and with the closing line on the same games.</p></section>

  <div class="note ${v.spread_beats_market ? 'good' : 'warn'}">
    <strong>Verdict.</strong> ${app.esc(v.statement)}
  </div>

  <div class="grid g4">
    ${app.statCard('Model spread MAE', app.num(o.spread_model_vs_result.mae, 2), 'points', 'bad')}
    ${app.statCard('Market spread MAE', app.num(o.spread_market_vs_result.mae, 2), 'same games', 'good')}
    ${app.statCard('Model total MAE', app.num(o.total_model_vs_result.mae, 2), 'points', 'bad')}
    ${app.statCard('Market total MAE', app.num(o.total_market_vs_result.mae, 2), 'same games', 'good')}
  </div>

  <h2>Accuracy and bias</h2>
  ${app.table([
    { label: 'Series', render: r => app.esc(r.name) },
    { label: 'Games', num: true, key: 'n' },
    { label: 'MAE', num: true, render: r => app.num(r.mae, 3) },
    { label: 'RMSE', num: true, render: r => app.num(r.rmse, 3) },
    { label: 'Bias', num: true, render: r => app.sgn(r.bias, 3) },
    { label: 'Correlation', num: true, render: r => app.num(r.correlation, 3) },
    { label: 'Source', render: () => app.srcLink('https://github.com/leesharpe/nfldata/blob/master/DATASETS.md', 'nfldata schema') },
  ], [
    { name: 'Model spread vs result', ...o.spread_model_vs_result },
    { name: 'Market spread vs result', ...o.spread_market_vs_result },
    { name: 'Model total vs result', ...o.total_model_vs_result },
    { name: 'Market total vs result', ...o.total_market_vs_result },
  ])}

  <h2>Probability calibration</h2>
  <p class="small muted">Predicted P(home win) grouped into buckets, compared with the share of home
  wins actually observed. A well-calibrated model sits on the diagonal.</p>
  ${app.table([
    { label: 'Predicted bucket', mono: true, key: 'bucket' },
    { label: 'Games', num: true, key: 'n' },
    { label: 'Predicted rate', num: true, render: r => app.pct(r.predicted, 1) },
    { label: 'Observed rate', num: true, render: r => app.pct(r.observed, 1) },
    { label: 'Error', num: true, render: r => app.sgn(r.error * 100, 1) + '<span class="dim small"> pts</span>' },
    { label: 'Read', render: r => Math.abs(r.error) < 0.03
        ? '<span class="pill pass">calibrated</span>'
        : `<span class="pill warn">off by ${(Math.abs(r.error) * 100).toFixed(1)} pts</span>` },
  ], d.calibration_table || [])}

  <h2>Season by season</h2>
  ${app.table([
    { label: 'Season', num: true, key: 'season' },
    { label: 'Games', num: true, key: 'n' },
    { label: 'Model spread MAE', num: true, render: r => app.num(r.model_spread_mae, 2) },
    { label: 'Market spread MAE', num: true, render: r => app.num(r.market_spread_mae, 2) },
    { label: 'Gap', num: true, render: r => app.sgn(r.model_spread_mae - r.market_spread_mae, 2) },
    { label: 'Model total MAE', num: true, render: r => app.num(r.model_total_mae, 2) },
    { label: 'Market total MAE', num: true, render: r => app.num(r.market_total_mae, 2) },
  ], d.by_season || [])}

  <h2>Method</h2>
  <div class="note">
    <p class="small">Each week is predicted from ratings fitted only on prior weeks (time-decayed ridge,
    half-life 8 weeks). The market columns are the closing lines from the same source. The comparison is
    therefore like-for-like: both are trying to predict the same result, and the market wins.</p>
    <p class="small">Probability model: normal approximation on the margin model with
    σ = ${d.sigma_used} points, the realised residual standard deviation. Recompute with
    <code>python3 -m pipeline.engine.calibration</code>.</p>
  </div>
  `;
});

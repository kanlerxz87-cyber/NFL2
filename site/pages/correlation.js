boot('correlation', async (el) => {
  const d = await app.load('correlation.json');
  const pairs = d.outcomes?.pairs || [];
  const sig = d.signals || {};
  const label = { spread_home: 'Home covers spread', total_over: 'Game total over', home_ml: 'Home moneyline', away_ml: 'Away moneyline' };

  el.innerHTML = `
  <section class="hero"><h1>Correlations</h1>
    <p class="lede">A parlay is priced as if its legs are independent. These are the measured
    correlations that decide whether that assumption is true, and by how much the price is wrong.</p></section>

  <div class="note">
    <strong>How to read φ.</strong> φ is the Pearson correlation between two binary outcomes.
    φ = 0 means the legs really are independent, so a same-game parlay is fairly priced.
    Positive φ means the legs win together more often than the book assumes — the parlay is
    <em>underpriced</em>. Negative φ means one leg tends to kill the other — the parlay is
    <em>overpriced</em>.
  </div>

  <h2>Measured outcome correlations</h2>
  <p class="small muted">${app.esc(d.outcomes?.source || '')}</p>
  ${app.table([
    { label: 'Leg A', render: r => app.esc(label[r.leg_a] || r.leg_a) },
    { label: 'Leg B', render: r => app.esc(label[r.leg_b] || r.leg_b) },
    { label: 'Games', num: true, key: 'n' },
    { label: 'φ', num: true, render: r => {
      const v = r.phi;
      const c = Math.abs(v) > 0.4 ? 'bad' : Math.abs(v) > 0.15 ? 'warn' : 'good';
      return `<span class="${c}">${app.num(v, 4)}</span>`;
    }},
    { label: 'P(both) observed', num: true, render: r => app.pct(r.p_joint_observed, 2) },
    { label: 'P(both) if independent', num: true, render: r => app.pct(r.p_joint_independent, 2) },
    { label: 'Fair price if observed', num: true, render: r => app.vblank(r.parlay?.fair_american_if_observed) },
    { label: 'Book price (independent)', num: true, render: r => app.vblank(r.parlay?.independent_american) },
    { label: 'Pricing error', num: true, render: r => app.sgn(r.parlay?.price_error_pct, 1) + '<span class="dim small">%</span>' },
    { label: 'Verdict', render: r => Math.abs(r.phi) < 0.15
        ? '<span class="pill pass">independent — fair</span>'
        : r.phi > 0 ? '<span class="pill warn">underpriced parlay</span>' : '<span class="pill bad">overpriced parlay</span>' },
  ], pairs)}

  <h2>Practical consequences</h2>
  <div class="grid g2">
    <div class="card">
      <div class="k">Good parlay</div>
      <h3>Spread + total</h3>
      <p class="small muted">φ is essentially zero (${app.num(pairs.find(p => p.leg_a === 'spread_home' && p.leg_b === 'total_over')?.phi, 4)}).
      Combining them genuinely diversifies: the two legs are driven by different things (who wins vs
      how much is scored).</p>
    </div>
    <div class="card">
      <div class="k">Bad parlay</div>
      <h3>Spread + home moneyline</h3>
      <p class="small muted">φ is very high (${app.num(pairs.find(p => p.leg_a === 'spread_home' && p.leg_b === 'home_ml')?.phi, 4)}).
      A team that covers is usually winning, so this is close to betting the same thing twice — and
      the book prices the second leg as though it were independent.</p>
    </div>
  </div>

  <h2>Signal correlation</h2>
  <p class="small">Correlation between the model's own spread edge and its total edge across
  ${app.vblank(sig.n)} games: <strong>${app.num(sig.spread_edge_vs_total_edge, 4)}</strong>.</p>
  <div class="note">${app.esc(sig.interpretation || '')}</div>

  <h2>Limitations — read before using these numbers</h2>
  ${app.table([{ label: 'Limitation', key: 'v' }], (d.limitations || []).map(v => ({ v })))}
  <p class="small"><a href="parlays.html">See how these correlations price a parlay →</a></p>
  `;
});

boot('luck', async (el) => {
  const d = await app.load('luck.json');
  const S = d.strategies || [];

  el.innerHTML = `
  <section class="hero"><h1>Luck vs skill</h1>
    <p class="lede">Four independent tests, applied to every strategy. A rule is only described as
    skill-based when the edge survives all of them.</p></section>

  <div class="grid g4">
    <div class="card tight"><div class="k">Test 1</div><h3 style="font-size:.92rem">Variance ratio</h3>
      <p class="small muted">Observed spread of results versus the spread pure chance implies. Near 1.0
      means indistinguishable from coin flips.</p></div>
    <div class="card tight"><div class="k">Test 2</div><h3 style="font-size:.92rem">Binomial exactness</h3>
      <p class="small muted">One-sided p-value against the break-even rate. This is what kills
      "7 of the last 9" stories.</p></div>
    <div class="card tight"><div class="k">Test 3</div><h3 style="font-size:.92rem">Split-half</h3>
      <p class="small muted">The holdout is cut chronologically in two. A real edge keeps its sign
      across both halves.</p></div>
    <div class="card tight"><div class="k">Test 4</div><h3 style="font-size:.92rem">Persistence</h3>
      <p class="small muted">Does the edge in season <em>t</em> predict the edge in season
      <em>t+1</em>? Reported with a confidence interval on the correlation.</p></div>
  </div>

  <h2>Every strategy, every test</h2>
  ${app.table([
    { label: 'ID', mono: true, key: 'id' },
    { label: 'Strategy', render: r => `${app.esc(r.name)}<div class="src">${app.esc(r.family)}</div>` },
    { label: 'Legs', num: true, render: r => app.vblank(r.legs) },
    { label: 'Hit', num: true, render: r => app.pct(r.hit_rate, 1) },
    { label: 'Excess over break-even', num: true, render: r => app.sgn((r.excess ?? 0) * 100, 2) + '<span class="dim small"> pts</span>' },
    { label: 'SD ratio', num: true, render: r => app.num(r.variance_test?.sd_ratio, 3) },
    { label: 'Split-half ROI', render: r => `
        <span class="mono small">${app.sgn((r.split_half?.first_half?.roi ?? 0) * 100, 1)}% → ${app.sgn((r.split_half?.second_half?.roi ?? 0) * 100, 1)}%</span>
        ${r.split_half?.same_sign_roi === false ? '<span class="pill warn">flips</span>' : ''}` },
    { label: 'Persistence r', num: true, render: r => app.vblank(app.isNum(r.persistence?.correlation) ? r.persistence.correlation.toFixed(2) : null) },
    { label: 'Skill share', num: true, render: r => app.vblank(app.isNum(r.persistence?.skill_share) ? (r.persistence.skill_share * 100).toFixed(0) + '%' : null) },
    { label: 'Verdict', render: r => r.luck_verdict?.startsWith('SKILL')
        ? '<span class="pill certified">skill-consistent</span>'
        : `<span class="pill fail">luck-dominated</span>` },
  ], S)}

  <h2>Why the verdicts are so blunt</h2>
  <div class="note warn">
    <p class="small">With 100 bets, the standard deviation of your win count under pure chance is
    about 5 wins. A 55% record over 100 bets is therefore a little over one standard deviation above
    break-even — it will happen by accident to roughly one in nine people who try. The persistence
    test is the tiebreaker: a genuinely good rule repeats next season, a lucky one does not.</p>
    <p class="small">Across all 22 strategies here, <strong>no correlation between one season's edge
    and the next is positive and distinguishable from zero</strong>. Whatever edge exists in this
    sample does not survive the winter.</p>
  </div>

  <h2>Detailed verdicts</h2>
  ${S.map(s => `<details><summary>${app.esc(s.id)} · ${app.esc(s.name)} — ${app.esc(s.luck_verdict || '')}</summary>
    ${app.table([
      { label: 'Test', key: 't' }, { label: 'Value', key: 'v' },
    ], [
      { t: 'Variance test — theoretical SD', v: app.num(s.variance_test?.theoretical_sd, 2) },
      { t: 'Variance test — observed SD', v: app.num(s.variance_test?.observed_sd, 2) },
      { t: 'Variance test — ratio', v: app.num(s.variance_test?.sd_ratio, 3) },
      { t: 'Wilson 95% lower bound', v: app.num(s.ci_low, 4) },
      { t: 'Break-even rate', v: app.num(s.break_even, 4) },
      { t: 'Split-half: first half ROI', v: app.pct(s.split_half?.first_half?.roi, 2) },
      { t: 'Split-half: second half ROI', v: app.pct(s.split_half?.second_half?.roi, 2) },
      { t: 'Split-half: same sign', v: s.split_half?.same_sign_roi === null ? app.blank : String(s.split_half?.same_sign_roi) },
      { t: 'Persistence correlation', v: app.isNum(s.persistence?.correlation) ? s.persistence.correlation.toFixed(3) : app.blank },
      { t: 'Persistence 95% CI', v: app.isNum(s.persistence?.ci_low) ? `[${s.persistence.ci_low.toFixed(2)}, ${s.persistence.ci_high.toFixed(2)}]` : app.blank },
    ])}
  </details>`).join('')}
  `;
});

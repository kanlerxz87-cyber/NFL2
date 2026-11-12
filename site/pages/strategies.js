boot('strategies', async (el) => {
  const d = await app.load('strategies.json');
  const S = d.strategies || [];
  const gateKeys = Object.keys(d.gate_definitions || {});

  el.innerHTML = `
  <section class="hero"><h1>Strategy library &amp; validation gates</h1>
    <p class="lede">Twenty-two fully specified rules, evaluated identically on a development window and
    a locked holdout, then put through seven gates. Nothing is tuned after the fact, and nothing is
    deleted when it fails.</p></section>

  <div class="note">
    <strong>Why a locked holdout.</strong> Any rule can be made to look profitable by trying enough
    thresholds on the same data. Parameters are chosen on ${d.windows.development[0]}–${d.windows.development[1]};
    the verdict comes from ${d.windows.holdout[0]}–${d.windows.holdout[1]}, which is scored once.
    Multiplicity is then accounted for with a Bonferroni threshold of 0.05 / ${d.tests_run}.
  </div>

  <h2>Gate results by strategy</h2>
  <p class="small muted">A dot means the gate passed. Expanded detail under each strategy.</p>
  ${app.table([
    { label: 'ID', mono: true, key: 'id' },
    { label: 'Strategy', render: r => `${app.esc(r.name)}<div class="src">${app.esc(r.desc)}</div>` },
    { label: 'Legs', num: true, render: r => app.vblank(r.holdout?.legs) },
    ...gateKeys.map(g => ({
      label: g.split('_')[0], num: true,
      render: r => (r.gates?.[g]?.pass ? '<span class="pill pass">✓</span>' : '<span class="pill fail">✗</span>')
    })),
    { label: 'Verdict', render: r => app.pill(r.verdict) },
  ], S)}

  <h2>Development versus holdout</h2>
  <p class="small muted">If a rule works in development and collapses in the holdout, that gap is the
  overfitting. It is shown rather than hidden.</p>
  ${app.table([
    { label: 'ID', mono: true, key: 'id' },
    { label: 'Strategy', render: r => app.esc(r.name) },
    { label: 'Dev legs', num: true, render: r => app.vblank(r.development?.legs) },
    { label: 'Dev ROI', num: true, render: r => app.sgn((r.development?.roi ?? 0) * 100, 1) + '<span class="dim small">%</span>' },
    { label: 'Hold legs', num: true, render: r => app.vblank(r.holdout?.legs) },
    { label: 'Hold ROI', num: true, render: r => app.sgn((r.holdout?.roi ?? 0) * 100, 1) + '<span class="dim small">%</span>' },
    { label: 'Decay', num: true, render: r => {
      const a = r.development?.roi, b = r.holdout?.roi;
      if (!app.isNum(a) || !app.isNum(b)) return app.blank;
      const dd = (b - a) * 100;
      return `<span class="${dd < -5 ? 'bad' : dd > 5 ? 'good' : 'muted'}">${dd > 0 ? '+' : ''}${dd.toFixed(1)} pts</span>`;
    }},
    { label: 'Failed gates', render: r => (r.failed_gates || []).map(f => `<span class="pill fail">${app.esc(f.split('_')[0])}</span>`).join(' ') || '<span class="pill certified">none</span>' },
  ], S)}

  <h2>Full gate detail</h2>
  ${S.map(s => `<details><summary>${app.esc(s.id)} · ${app.esc(s.name)} — ${app.pill(s.verdict)}</summary>
    ${app.table([
      { label: 'Gate', mono: true, key: 'k' },
      { label: 'Result', render: r => app.pill(r.pass ? 'pass' : 'fail') },
      { label: 'Detail', render: r => app.esc(r.detail) },
    ], gateKeys.map(k => ({ k, pass: s.gates?.[k]?.pass, detail: s.gates?.[k]?.detail })))}
    <p class="small muted">Development: ${app.vblank(s.development?.legs)} legs,
    ROI ${app.sgn((s.development?.roi ?? 0) * 100, 2)}%. Holdout: ${app.vblank(s.holdout?.legs)} legs,
    ROI ${app.sgn((s.holdout?.roi ?? 0) * 100, 2)}%, max drawdown
    ${app.num(s.holdout?.max_drawdown, 1)} units.</p>
  </details>`).join('')}

  <h2>Gate definitions</h2>
  ${app.table([
    { label: 'Gate', mono: true, key: 'g' }, { label: 'Requirement', key: 'v' },
  ], Object.entries(d.gate_definitions || {}).map(([g, v]) => ({ g, v })))}
  `;
});

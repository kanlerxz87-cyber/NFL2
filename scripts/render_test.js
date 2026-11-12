/* Executes each page module in a minimal DOM shim, against the real JSON files,
   and fails loudly on any runtime error or on a row rendered without a source.
   Usage: node scripts/render_test.js */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SITE = path.join(__dirname, '..', 'site');
const DATA = path.join(SITE, 'data');
const scripts = fs.readdirSync(path.join(SITE, 'pages')).filter(f => f.endsWith('.js'));

let failures = 0;
const results = [];

function makeEl() {
  const el = {
    _html: '', innerHTML: '', textContent: '', classList: { add() {}, remove() {} },
    set id(v) {}, get id() { return 'el'; },
  };
  return el;
}

async function runOne(file) {
  const name = file.replace('.js', '');
  const el = makeEl();
  const errors = [];
  const ctx = {
    console: { log() {}, error: (...a) => errors.push(a.join(' ')), warn() {} },
    document: {
      getElementById: (id) => (id === 'app' ? el : makeEl()),
      querySelectorAll: () => [],
      addEventListener() {},
    },
    window: {},
    URL,
    fetch: async (u) => {
      const f = path.join(SITE, u.replace(/^\.\//, ''));
      if (!fs.existsSync(f)) throw new Error('missing data file: ' + u);
      const body = fs.readFileSync(f, 'utf8');
      return { ok: true, status: 200, json: async () => JSON.parse(body), text: async () => body };
    },
    setTimeout, clearTimeout, Promise, Object, Array, Math, JSON, String, Number, Boolean,
    isFinite, isNaN, Intl, Set, Map, Error,
  };
  ctx.window = ctx;
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(SITE, 'app.js'), 'utf8'), ctx, { filename: 'app.js' });

  const code = fs.readFileSync(path.join(SITE, 'pages', file), 'utf8');
  try {
    vm.runInContext(code, ctx, { filename: file });
    // boot() schedules an async page render; wait for microtasks
    await new Promise(r => setTimeout(r, 60));
  } catch (e) {
    errors.push('THROW: ' + e.message);
  }
  const html = el.innerHTML || '';
  const bad = /Could not load data|undefined|NaN|\[object Object\]/.test(html);
  const noSource = (html.match(/no source/g) || []).length;
  const rows = (html.match(/<tr>/g) || []).length;
  if (errors.length) failures++;
  if (bad) failures++;
  results.push({
    page: name, bytes: html.length, rows, noSource,
    status: errors.length ? 'ERROR' : bad ? 'BAD_OUTPUT' : 'ok',
    detail: errors.slice(0, 2).join(' | '),
    suspicious: bad ? (html.match(/.{0,60}(undefined|NaN|\[object Object\]).{0,60}/) || [''])[0] : '',
  });
}

(async () => {
  for (const f of scripts) await runOne(f);
  const pad = (s, n) => String(s).padEnd(n);
  console.log(pad('PAGE', 16), pad('KB', 8), pad('ROWS', 6), pad('NO-SOURCE', 10), 'STATUS');
  for (const r of results) {
    console.log(pad(r.page, 16), pad((r.bytes / 1024).toFixed(1), 8), pad(r.rows, 6), pad(r.noSource, 10), r.status,
      r.detail ? '\n   ' + r.detail : '', r.suspicious ? '\n   >>' + r.suspicious : '');
  }
  console.log(`\n${results.length} pages, ${failures} failure(s)`);
  process.exit(failures ? 1 : 0);
})();

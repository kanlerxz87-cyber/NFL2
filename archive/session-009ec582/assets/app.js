// Shared table renderer + tiny helpers. Every page builds its tables from
// the JSON in /data, so no figure on the site is hand-typed twice.
const $ = (s, r = document) => r.querySelector(s);
const fmt = (v, d = 1) =>
  v === null || v === undefined || v === "" ? null : Number(v).toFixed(d);
const sign = (v, d = 1) => {
  const n = Number(v);
  return (n > 0 ? "+" : "") + n.toFixed(d);
};
const esc = (s) =>
  String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// A blank cell is never rendered as 0 — it is rendered as an explicit gap.
const BLANK = '<span class="blank" title="Not published: no official source confirms this value">—</span>';

function badge(text, kind = "dim") {
  return `<span class="b b-${kind}">${esc(text)}</span>`;
}
function srcLink(url, label = "source") {
  if (!url) return "";
  return `<span class="src"><a href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a></span>`;
}

/* renderTable(container, {columns, rows, caption, empty})
   columns: [{key,label,num?,tiny?,render?(row)=html,w?}] */
function renderTable(el, { columns, rows, caption = "", empty = "No rows." }) {
  if (!el) return;
  if (!rows || !rows.length) {
    el.innerHTML = `<div class="tblwrap"><table><caption>${caption}</caption><tbody><tr><td class="blank">${empty}</td></tr></tbody></table></div>`;
    return;
  }
  const head = columns
    .map((c) => `<th class="${c.num ? "num" : ""} ${c.tiny ? "tiny" : ""}"${c.w ? ` style="width:${c.w}"` : ""}>${esc(c.label)}</th>`)
    .join("");
  const body = rows
    .map((r) => {
      const tds = columns
        .map((c) => {
          const html = c.render ? c.render(r) : r[c.key] === null || r[c.key] === undefined ? BLANK : esc(r[c.key]);
          return `<td class="${c.num ? "num" : ""} ${c.tiny ? "tiny" : ""}">${html}</td>`;
        })
        .join("");
      return `<tr${r._cls ? ` class="${r._cls}"` : ""}>${tds}</tr>`;
    })
    .join("");
  el.innerHTML = `<div class="tblwrap"><table>${caption ? `<caption>${caption}</caption>` : ""}<thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

async function loadJSON(path) {
  const r = await fetch(path, { cache: "no-cache" });
  if (!r.ok) throw new Error(`${path} → HTTP ${r.status}`);
  return r.json();
}

// nav highlight + interactive table filter + calculators
addEventListener("DOMContentLoaded", () => {
  const here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll("nav.main a").forEach((a) => {
    const href = a.getAttribute("href");
    if (href === here || (here === "" && href === "index.html")) a.setAttribute("aria-current", "page");
  });

  document.querySelectorAll("[data-filter-input]").forEach((inp) => {
    const target = document.querySelector(inp.getAttribute("data-filter-input"));
    if (!target) return;
    inp.addEventListener("input", () => {
      const q = inp.value.trim().toLowerCase();
      target.querySelectorAll("tbody tr").forEach((tr) => {
        tr.style.display = !q || tr.textContent.toLowerCase().includes(q) ? "" : "none";
      });
    });
  });

  const form = $("#lines-calc");
  if (form) {
    const out = $("#lines-out");
    const phi = (z) => {
      const t = 1 / (1 + 0.2316419 * Math.abs(z));
      const d = 0.3989422804014327 * Math.exp((-z * z) / 2);
      const p = d * t * (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
      return z > 0 ? 1 - p : p;
    };
    const numVal = (id, def) => {
      const el = $(id);
      const v = parseFloat(el && el.value);
      return Number.isNaN(v) ? def : v;
    };
    const run = () => {
      const g = Math.max(1, numVal("#g", 8));
      const hPF = numVal("#hPF", 0), hPA = numVal("#hPA", 0), aPF = numVal("#aPF", 0), aPA = numVal("#aPA", 0);
      const hfa = numVal("#hfa", 0.5), sd = Math.max(1, numVal("#sd", 13.32));
      const projHome = (hPF / g + aPA / g) / 2 + hfa;
      const projAway = (aPF / g + hPA / g) / 2;
      const spread = projHome - projAway;
      const total = projHome + projAway;
      const pHome = phi(spread / sd);
      const mlHome = pHome >= 0.5 ? (-100 * pHome) / (1 - pHome) : (100 * (1 - pHome)) / pHome;
      const mlAway = 1 - pHome >= 0.5 ? (-100 * (1 - pHome)) / pHome : (100 * pHome) / (1 - pHome);
      const fmtML = (v) => (v > 0 ? "+" : "") + Math.round(v);
      out.textContent =
        "MODEL ONLY — baseline from points for/against (not a market line, not betting advice)\n" +
        `Games assumed: ${g} each\n` +
        `Home proj: ${projHome.toFixed(1)} pts  |  Away proj: ${projAway.toFixed(1)} pts\n` +
        `Fair spread (home): ${spread >= 0 ? "home -" : "home +"}${Math.abs(spread).toFixed(1)}\n` +
        `Fair total: ${total.toFixed(1)}\n` +
        `P(home win) ≈ ${(pHome * 100).toFixed(1)}%  →  fair ML home ${fmtML(mlHome)} / away ${fmtML(mlAway)}\n` +
        `Assumptions: HFA=${hfa} pts, margin SD=${sd}. Replace with opponent-adjusted ratings before any use.`;
    };
    form.addEventListener("submit", (e) => { e.preventDefault(); run(); });
    run();
  }

  const corrForm = $("#corr-calc");
  if (corrForm) {
    const corrOut = $("#corr-out");
    corrForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const parse = (id) => {
        const v = ($(id)?.value || "").trim();
        return v ? v.split(/[\s,;]+/).map(Number).filter((n) => !Number.isNaN(n)) : [];
      };
      const x = parse("#corr-x"), y = parse("#corr-y");
      if (x.length !== y.length || x.length < 3) {
        corrOut.textContent = "Enter two equal-length lists with at least 3 paired numbers (e.g. one per game).";
        return;
      }
      const n = x.length;
      const mx = x.reduce((a, b) => a + b, 0) / n, my = y.reduce((a, b) => a + b, 0) / n;
      let numSum = 0, dx = 0, dy = 0;
      for (let i = 0; i < n; i++) {
        const a = x[i] - mx, b = y[i] - my;
        numSum += a * b; dx += a * a; dy += b * b;
      }
      const r = dx === 0 || dy === 0 ? NaN : numSum / Math.sqrt(dx * dy);
      corrOut.textContent =
        `n=${n}  Pearson r = ${Number.isNaN(r) ? "undefined (zero variance)" : r.toFixed(3)}\n` +
        "Interpretation: |r|<0.10 negligible, 0.10–0.30 weak, 0.30–0.50 moderate, >0.50 strong.";
    });
  }
});

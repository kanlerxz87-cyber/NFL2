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

// nav highlight
addEventListener("DOMContentLoaded", () => {
  const here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll("nav.main a").forEach((a) => {
    const href = a.getAttribute("href");
    if (href === here || (here === "" && href === "index.html")) a.setAttribute("aria-current", "page");
  });
});

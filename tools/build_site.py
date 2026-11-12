#!/usr/bin/env python3
"""Render the NFL2 static dashboard from data/content.py.

Also emits data/records.json: one record per rendered table row, used by
tools/verify.py to re-verify the combined data line by line.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
import content  # noqa: E402

# The final integration output lives under review/ so that the pre-existing
# dashboards published by the other parallel sessions (repo root and docs/) are
# preserved untouched. GitHub Pages publishes main:/ so review/ is reachable at
# https://kanlerxz87-cyber.github.io/NFL2/review/.
OUT = ROOT / "review"
RECORDS: list[dict] = []


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def status_kind(text: str) -> str | None:
    t = text.strip().upper()
    if t.startswith("UNVERIFIED") or t == "EXCLUDED":
        return "unverified"
    if t.startswith("NEEDS REVIEW"):
        return "review"
    if t.startswith("PROPOSAL"):
        return "proposal"
    if t.startswith("VERIFIED"):
        return "verified"
    return None


def normalize_table(table: dict) -> dict:
    """Align historical column/row counts without dropping any cell."""
    headers = list(table["headers"])
    rows = table["rows"]
    lengths = {len(r["cells"]) for r in rows}
    n = len(headers)
    if table["key"] == "leaderboard-structure":
        fixed = []
        for r in rows:
            cells = list(r["cells"])
            if len(cells) == 5:
                cells.insert(3, "")
            r = dict(r)
            r["cells"] = cells
            fixed.append(r)
        rows = fixed
        lengths = {len(r["cells"]) for r in rows}
    if lengths == {n + 1}:
        assert headers[-1] == "Source", f"unexpected header layout: {table['key']}"
        headers = headers[:-1] + ["Official basis", "Source"]
    elif lengths == {n}:
        pass
    else:
        raise AssertionError(f"{table['key']}: header/row mismatch {n} vs {sorted(lengths)}")
    out = dict(table)
    out["headers"] = headers + ["Official link"]
    out["rows"] = rows
    return out


def render_cell(value: str) -> str:
    if value == "":
        return '<td class="blank" data-blank="1" aria-label="Unverified - value left blank"></td>'
    value = str(value)
    if value.startswith("https://") and " " not in value:
        return f'<td><a href="{esc(value)}" target="_blank" rel="noopener noreferrer">{esc(value)}</a></td>'
    kind = status_kind(value)
    if kind:
        return f'<td><span class="badge badge-{kind}">{esc(value)}</span></td>'
    return f"<td>{esc(value)}</td>"


def source_links(ids: list[str]) -> str:
    parts = []
    for sid in ids:
        s = content.SOURCES[sid]
        parts.append(
            f'<a class="src-link" href="{esc(s["url"])}" target="_blank" '
            f'rel="noopener noreferrer" title="{esc(s["title"])}">{esc(sid)} ↗</a>'
        )
    return " ".join(parts)


def render_nav(current: str) -> str:
    out = ['<nav class="nav" aria-label="Site navigation">']
    for category, items in content.NAV:
        out.append(f'<div class="nav-group"><h3>{esc(category)}</h3><ul>')
        for file, label in items:
            active = ' class="active" aria-current="page"' if file == current else ""
            out.append(f'<li><a href="{esc(file)}"{active}>{esc(label)}</a></li>')
        out.append("</ul></div>")
    out.append("</nav>")
    return "\n".join(out)


PATH_CHOOSER = """
<section class="card chooser" aria-labelledby="chooser-title">
  <h2 id="chooser-title">Choose the best path before implementing anything</h2>
  <p>Select one path. The selection is stored only in this browser (localStorage); it does
     not change the site and does not start any implementation. No path has been chosen by an
     agent — that choice is deliberately left to a reviewer.</p>
  <form id="path-chooser">
    <div class="options">
      <label><input type="radio" name="path" value="A"> <strong>A</strong> — Lock the evidence layer</label>
      <label><input type="radio" name="path" value="B"> <strong>B</strong> — Answer the blocking questions</label>
      <label><input type="radio" name="path" value="C"> <strong>C</strong> — Build injury / depth ingestion</label>
      <label><input type="radio" name="path" value="D"> <strong>D</strong> — License data and run numeric gates</label>
      <label><input type="radio" name="path" value="E"> <strong>E</strong> — Recognition-only leaderboard</label>
    </div>
    <div class="actions">
      <button type="submit" class="btn">Record my choice</button>
      <button type="button" class="btn btn-secondary" id="clear-choice">Clear choice</button>
    </div>
  </form>
  <p id="decision-output" class="decision-output" role="status">No path recorded yet.</p>
  <p class="muted">Blocking questions on the <a href="decisions.html">Questions &amp; answers</a>
     page remain blocking even after a path is chosen.</p>
</section>
"""


def render_table(page_file: str, table: dict) -> str:
    t = normalize_table(table)
    tid = f"{page_file}::{t['key']}"
    out = ['<section class="card">', f'<h2>{esc(t["title"])}</h2>']
    if t.get("intro"):
        out.append(f'<p class="intro">{esc(t["intro"])}</p>')
    out.append('<div class="table-wrap"><table class="data-table" data-sortable>')
    out.append("<thead><tr>" + "".join(f'<th scope="col" tabindex="0">{esc(h)}</th>' for h in t["headers"]) + "</tr></thead>")
    out.append("<tbody>")
    for i, row in enumerate(t["rows"]):
        rid = f"{tid}:{i:03d}"
        src = row["src"]
        cells = [str(c) for c in row["cells"]] + [source_links(src)]
        blank_idx = [j for j, c in enumerate(row["cells"]) if c == ""]
        RECORDS.append({
            "row_id": rid,
            "page": page_file,
            "table": t["key"],
            "headers": t["headers"],
            "cells": cells[:-1],
            "blank_indices": blank_idx,
            "src": src,
            "status": row["status"],
            "flags": row["flags"],
            "note": row.get("note", ""),
        })
        cls = f'row-{esc(row["status"])}'
        flag_attr = esc(" ".join(row["flags"]))
        out.append(f'<tr data-row-id="{esc(rid)}" class="{cls}" data-status="{esc(row["status"])}" data-flags="{flag_attr}">')
        out.append("".join(render_cell(c) if j < len(cells) - 1 else f'<td class="src-cell">{c}</td>'
                           for j, c in enumerate(cells)))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if t.get("analysis"):
        out.append(f'<p class="analysis"><strong>Analysis:</strong> {esc(t["analysis"])}</p>')
    if t.get("note"):
        out.append(f'<p class="muted">{esc(t["note"])}</p>')
    out.append("</section>")
    return "\n".join(out)


def render_page(page: dict) -> str:
    f = page["file"]
    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(page['intro'][:150])}">
<title>{esc(page['title'])} | NFL2</title>
<link rel="stylesheet" href="assets/style.css">
<script src="assets/site.js" defer></script>
</head>
<body data-page="{esc(f)}">
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="brand"><a href="index.html"><span class="brand-mark">NFL2</span><span class="brand-sub">decision dashboard</span></a></div>
  <div class="topbar-meta">
    <span class="chip chip-ok">Verified sources only</span>
    <span class="chip">Captured {esc(content.CAPTURED)}</span>
  </div>
</header>
<div class="layout">
  <aside class="sidebar">{render_nav(f)}</aside>
  <main id="main" class="main">
    <div class="page-head">
      <p class="eyebrow">{esc(page['eyebrow'])}</p>
      <h1>{esc(page['title'])}</h1>
      <p class="lede">{esc(page['intro'])}</p>
    </div>
    <div class="toolbar">
      <label class="filter-label" for="rowFilter">Filter rows
        <input type="search" id="rowFilter" class="filter" placeholder="Type to filter every table on this page…" autocomplete="off">
      </label>
      <span id="rowCount" class="filter-count"></span>
      <span class="legend-inline"><span class="dot dot-verified"></span> verified <span class="dot dot-proposal"></span> proposal <span class="dot dot-unverified"></span> unverified <span class="dot dot-review"></span> needs review</span>
    </div>
"""
    if page.get("hero"):
        head += f"""
    <section class="hero card">
      <h2>What this site is</h2>
      <p>A read-only research and decision dashboard. It does not place wagers, handle money or
         offer betting advice. Numerical results that cannot be confirmed from an official source
         are shown as blank cells with an <span class="badge badge-unverified">UNVERIFIED</span> flag.</p>
      <div class="hero-actions">
        <a class="btn" href="decisions.html">Start with the questions</a>
        <a class="btn btn-secondary" href="suggestions.html">Choose a path</a>
        <a class="btn btn-secondary" href="flagged.html">Flagged for Review</a>
      </div>
    </section>
"""
    if f == "suggestions.html":
        head += PATH_CHOOSER
    body = "\n".join(render_table(f, t) for t in page["sections"])
    footer = f"""
    <footer class="footer">
      <p>NFL2 · Static GitHub Pages dashboard · {esc(content.CAPTURED)} ·
         <a href="methodology.html">Verification methodology</a> ·
         <a href="https://github.com/kanlerxz87-cyber/NFL2" target="_blank" rel="noopener noreferrer">Repository ↗</a></p>
      <p class="muted">Research and validation framework only. No wagering, accounts or payments.
         Legal sports betting is age- and jurisdiction-restricted; help resources:
         <a href="https://www.ncpgambling.org/" target="_blank" rel="noopener noreferrer">National Council on Problem Gambling ↗</a>.
         Not affiliated with or endorsed by the NFL or Kaggle; official pages are cited as references.</p>
    </footer>
  </main>
</div>
</body>
</html>
"""
    return head + body + footer


def main() -> None:
    for page in content.PAGES:
        text = render_page(page)
        (OUT / page["file"]).write_text(text, encoding="utf-8")
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "records.json").write_text(
        json.dumps({"records": RECORDS, "registry_version": content.REGISTRY["registry_version"]},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built {len(content.PAGES)} pages, "
          f"{sum(len(p['sections']) for p in content.PAGES)} tables, {len(RECORDS)} rows.")
    print(f"Wrote {ROOT / 'data' / 'records.json'}")


if __name__ == "__main__":
    main()

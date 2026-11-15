#!/usr/bin/env python3
"""Build and validate the standalone strategy-falsification review page.

Run from any working directory:
    python3 audits/f05c00f2/build.py          # validate and write index.html
    python3 audits/f05c00f2/build.py --check  # validate and compare without writing
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGISTER = ROOT / "data" / "strategies.csv"
RECORDS = HERE / "strategy-falsifiers.json"
OUTPUT = HERE / "index.html"

REQUIRED_FIELDS = {
    "id", "name", "bet_type", "market", "supporting_evidence",
    "what_would_change_our_mind", "missing_information",
    "official_input_url", "official_source_status", "readiness", "source_class",
}
ALLOWED_OFFICIAL_HOSTS = {"www.nfl.com", "operations.nfl.com"}
FORBIDDEN_METRIC_KEYS = {
    "roi", "roi_units_per_100", "win_rate", "hit_rate", "brier_score",
    "log_loss", "clv", "mean_clv", "pnl", "stake", "rank", "performance",
}


def read_register() -> list[dict[str, str]]:
    with REGISTER.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source, delimiter="|"))
    if not rows:
        raise ValueError(f"Strategy register is empty: {REGISTER}")
    ids = [row.get("id", "") for row in rows]
    if len(ids) != len(set(ids)) or any(not item for item in ids):
        raise ValueError("Strategy register must have unique, non-empty IDs")
    return rows


def read_records() -> dict:
    data = json.loads(RECORDS.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("strategies"), list):
        raise ValueError("Falsification JSON must contain a strategies list")
    return data


def validate(register: list[dict[str, str]], data: dict) -> list[dict[str, str]]:
    records = data["strategies"]
    record_ids = [row.get("id", "") for row in records]
    register_ids = [row["id"] for row in register]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("Falsification records contain duplicate strategy IDs")
    if record_ids != register_ids:
        missing = sorted(set(register_ids) - set(record_ids))
        extra = sorted(set(record_ids) - set(register_ids))
        order_changed = not missing and not extra
        raise ValueError(
            "Falsification records must cover each strategy exactly once in register order; "
            f"missing={missing}, extra={extra}, order_changed={order_changed}"
        )

    by_id = {row["id"]: row for row in register}
    for record in records:
        absent = REQUIRED_FIELDS - set(record)
        if absent:
            raise ValueError(f"{record['id']}: missing fields {sorted(absent)}")
        if record.get("source_class") != "project-design":
            raise ValueError(f"{record['id']}: strategy hypotheses must be labelled project-design")
        for field in ("supporting_evidence", "what_would_change_our_mind", "missing_information", "readiness", "official_source_status"):
            if not str(record.get(field, "")).strip():
                raise ValueError(f"{record['id']}: {field} must not be blank")
        for field in ("name", "bet_type", "market"):
            if record[field] != by_id[record["id"]].get(field, ""):
                raise ValueError(
                    f"{record['id']}: {field} differs from the source strategy register; "
                    "update the companion only after review"
                )
        if record["official_input_url"]:
            parsed = urlparse(record["official_input_url"])
            if parsed.scheme != "https" or parsed.hostname not in ALLOWED_OFFICIAL_HOSTS:
                raise ValueError(f"{record['id']}: official input URL must use an approved official host")
            if "only" not in record["official_source_status"].lower() and "pointer" not in record["official_source_status"].lower():
                raise ValueError(
                    f"{record['id']}: official source status must say the link is an input pointer only"
                )
        else:
            status = record["official_source_status"].upper()
            if "UNVERIFIED" not in status and "NOT APPLICABLE" not in status:
                raise ValueError(
                    f"{record['id']}: blank official input URL must be explicitly flagged or not applicable"
                )
        # These records describe prospective tests only. Performance belongs in a separate,
        # eligible forward-scoring pipeline and must not be smuggled into this review page.
        for key in record:
            if key.lower() in FORBIDDEN_METRIC_KEYS:
                raise ValueError(f"{record['id']}: performance field {key!r} is not allowed here")

    return records


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def source_cell(record: dict[str, str]) -> str:
    design = (
        '<a href="../../data/strategies.csv">strategy register</a>'
        ' <span class="tag design">project design</span>'
    )
    url = record["official_input_url"]
    if url:
        official = (
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">official input source</a>'
            ' <span class="tag source">NFL source</span>'
        )
    elif "NOT APPLICABLE" in record["official_source_status"].upper():
        official = '<span class="tag neutral">not applicable</span>'
    else:
        official = '<span class="tag unverified">official input source unverified</span>'
    return (
        f'<div class="source-links">{design}<br>{official}</div>'
        f'<p class="source-note">{esc(record["official_source_status"])}</p>'
    )


def render(register: list[dict[str, str]], records: list[dict[str, str]]) -> str:
    source_hash = hashlib.sha256(REGISTER.read_bytes()).hexdigest()
    body_rows = []
    for record in records:
        source_row = next(row for row in register if row["id"] == record["id"])
        # The registered blocking-gate text is copied as-is; this review does not invent or
        # re-map gates. It is display context, not a claim that any gate has passed.
        registered_gates = source_row.get("gates_blocking", "") or "not registered"
        body_rows.append(
            "<tr>"
            f'<th scope="row"><span class="id">{esc(record["id"])}</span>'
            f'<strong>{esc(record["name"])}</strong>'
            f'<span class="sub">{esc(record["bet_type"])} · {esc(record["market"])}</span></th>'
            f'<td>{esc(record["supporting_evidence"])}</td>'
            f'<td>{esc(record["what_would_change_our_mind"])}</td>'
            f'<td>{esc(record["missing_information"])}</td>'
            f'<td><span class="state">{esc(record["readiness"])}</span>'
            f'<span class="sub">Registered blockers: {esc(registered_gates)}</span></td>'
            f'<td>{source_cell(record)}</td>'
            "</tr>"
        )

    rows = "\n".join(body_rows)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="A review-only, two-sided falsification crosswalk for all NFL2 strategy entries.">
<title>Strategy falsifiers · NFL2 review</title>
<style>
:root {{ color-scheme: light; --ink:#15253b; --muted:#596b82; --line:#d7e0ea; --paper:#f4f7fb; --card:#fff; --navy:#0d2038; --blue:#2253a4; --amber:#9b5d00; --red:#a13434; --green:#126a4b; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }}
a {{ color:var(--blue); }} a:focus-visible, button:focus-visible {{ outline:3px solid #e49c20; outline-offset:2px; }}
header {{ background:var(--navy); color:white; padding:1.2rem max(1rem,calc((100vw - 1440px)/2)); }} header a {{ color:#c5d9ff; }} .crumb {{ font-size:.9rem; color:#b8c7d9; }}
main {{ max-width:1440px; margin:0 auto; padding:1.3rem; }} h1 {{ margin:.4rem 0; line-height:1.15; font-size:clamp(1.8rem,3vw,2.8rem); }} h2 {{ margin:1.6rem 0 .6rem; font-size:1.35rem; }} .lede {{ max-width:100ch; color:#d7e3f2; margin:.4rem 0 .8rem; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:.8rem; margin:1rem 0; }} .card, .note {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:1rem; }} .card b {{ display:block; font-size:1.7rem; line-height:1.2; }} .card span {{ color:var(--muted); font-size:.93rem; }}
.callout {{ border-left:5px solid #d69218; background:#fff7e8; padding:.9rem 1rem; margin:1rem 0; border-radius:6px; }} .callout strong {{ color:#704500; }}
.nav {{ display:flex; flex-wrap:wrap; gap:.55rem 1rem; padding:.5rem 0 0; }} .nav a {{ color:#c5d9ff; }} .table-wrap {{ overflow:auto; background:white; border:1px solid var(--line); border-radius:12px; }} table {{ border-collapse:collapse; width:100%; min-width:1120px; }} caption {{ text-align:left; padding:.85rem 1rem; color:var(--muted); font-size:.94rem; }} th,td {{ text-align:left; vertical-align:top; border-top:1px solid var(--line); padding:.85rem; }} thead th {{ background:#eaf0f7; position:sticky; top:0; z-index:1; }} tbody th {{ min-width:205px; }} td {{ min-width:220px; }} td:nth-child(6) {{ min-width:245px; }} .id {{ display:inline-block; background:#e4edfb; color:#1c477f; font-weight:700; border-radius:5px; padding:.08rem .4rem; margin:0 .35rem .35rem 0; font-size:.84rem; }} tbody th strong {{ display:block; }} .sub {{ display:block; color:var(--muted); font-weight:400; font-size:.9rem; margin-top:.25rem; }} .state {{ display:block; font-weight:700; font-size:.92rem; }} .tag {{ display:inline-block; border-radius:999px; padding:.05rem .45rem; font-size:.76rem; font-weight:700; margin:.15rem .15rem .15rem 0; white-space:nowrap; }} .tag.design {{ background:#e8edf4; color:#35465d; }} .tag.source {{ background:#e6f5ef; color:var(--green); }} .tag.unverified {{ background:#fce8e8; color:var(--red); }} .tag.neutral {{ background:#eef1f4; color:#4d5c6d; }} .source-note {{ margin:.3rem 0 0; color:var(--muted); font-size:.84rem; }} .source-links a {{ white-space:nowrap; }}
footer {{ margin:2rem 0 1rem; padding-top:1rem; border-top:1px solid var(--line); color:var(--muted); font-size:.9rem; }} code {{ overflow-wrap:anywhere; }}
@media(max-width:700px) {{ main {{ padding:.8rem; }} header {{ padding:1rem; }} .card, .note {{ padding:.8rem; }} }}
</style>
</head>
<body>
<header>
  <div class="crumb"><a href="../../index.html">NFL2 Decision Dashboard</a> / Review / Strategy falsifiers</div>
  <h1>Strategy falsifiers</h1>
  <p class="lede">A two-sided review of every current strategy entry: what future evidence could support the hypothesis, what would make us stop, and which source/data gaps prevent a fair test.</p>
  <nav class="nav" aria-label="Related pages">
    <a href="../../strategies.html">Strategy register</a><a href="../../leaderboard.html">Leaderboard</a><a href="../../suggestions.html">Suggestions</a><a href="../../questions.html">Open questions</a><a href="../../flagged-for-review.html">Flagged for Review</a>
  </nav>
</header>
<main>
  <section class="cards" aria-label="Review status">
    <div class="card"><b>{len(records)}</b><span>strategy entries cross-referenced, one-to-one with the current register</span></div>
    <div class="card"><b>0</b><span>performance values or backtest rankings imported into this page</span></div>
    <div class="card"><b>0</b><span>strategies newly validated or approved for staking</span></div>
    <div class="card"><b>{source_hash[:12]}</b><span>SHA-256 prefix of the strategy register used to build this page</span></div>
  </section>
  <div class="callout"><strong>Review-only; no betting signal.</strong> Strategy descriptions and falsification tests are project design, not official NFL findings. An official source link below identifies a possible input source only; it does not support the strategy's thesis. Missing official-source links are intentionally blank and marked unverified/not applicable. No performance statistic is shown here.</div>
  <section class="note">
    <h2>How to use this table</h2>
    <p>For each strategy, freeze the target outcome, comparator, decision cutoff, sample window, uncertainty method and multiplicity family before collecting evaluation results. The “support” and “change our mind” text is a proposed preregistration aid, not a new numeric gate. Apply the existing registered gates without changing their thresholds. Keep forecast skill separate from staking/realized return; never promote a strategy because a lucky stake sequence did well.</p>
    <p>“Missing information” is a discovery checklist. It distinguishes current source links from a complete dataset. No blanks are imputed. The registered blocking-gate text is copied directly from <a href="../../data/strategies.csv">data/strategies.csv</a>; this companion does not reassign gates.</p>
  </section>
  <h2>One record for every registered strategy</h2>
  <div class="table-wrap">
    <table>
      <caption>Project-design hypotheses and future tests only. Official links are input-source pointers, not proof of predictive value. Register fingerprint: <code>SHA-256 {source_hash}</code>.</caption>
      <thead><tr><th scope="col">Entry</th><th scope="col">Evidence that would support it</th><th scope="col">What would change our mind</th><th scope="col">Missing information / discovery needed</th><th scope="col">Current status and registered blockers</th><th scope="col">Sources and source class</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <section class="note">
    <h2>Open integration item</h2>
    <p>The canonical <a href="../../strategies.html">Strategy Registry</a> currently describes the rule to name a falsifier but does not render a per-entry “what would change our mind” field. This standalone crosswalk covers all current IDs without changing the shared strategy register or root navigation while another session's integration PR is open. Change request <strong>CR-F05-01</strong> asks the final integrator to add the two-sided fields to <code>data/strategies.csv</code>, render them on the Strategy Registry page, and enforce exact ID coverage in CI.</p>
    <p>Official pages cited in this review were not re-fetched during this task. They are manual-review pointers drawn from the repository's existing source records. The register's dated captures, verification notes, and irregularity flags remain the evidence for what was actually checked.</p>
  </section>
  <footer>
    <p>Generated deterministically from <code>strategy-falsifiers.json</code> and the registered strategy rows in <code>data/strategies.csv</code>. Source register SHA-256: <code>{source_hash}</code>. No model outputs, picks, probabilities, realized performance, or staking values are produced by this page.</p>
    <p><a href="../../sources.html">Source registry</a> · <a href="../../methodology.html">Verification method</a> · <a href="../../requirements.html">Requirement readiness</a></p>
  </footer>
</main>
</body>
</html>
'''


def check_internal_links(document: str) -> int:
    """Fail on broken local links in the generated standalone page."""
    checked = 0
    for raw in re.findall(r'href=[\"\']([^\"\']+)[\"\']', document):
        parsed = urlparse(raw)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (HERE / unquote(parsed.path)).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ValueError(f"local link escapes repository root: {raw}") from exc
        if not target.exists():
            raise ValueError(f"broken local link: {raw} -> {target.relative_to(ROOT)}")
        checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed HTML is stale")
    args = parser.parse_args()
    register = read_register()
    data = read_records()
    records = validate(register, data)
    output = render(register, records)
    link_count = check_internal_links(output)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != output:
            raise SystemExit("FAIL: index.html does not match the validated JSON/register inputs")
        print(f"PASS: {len(records)} strategy IDs, two-sided criteria, source labels, {link_count} local links and deterministic HTML")
        return 0
    OUTPUT.write_text(output, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(records)} strategy IDs; {link_count} local links checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

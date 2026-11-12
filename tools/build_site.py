#!/usr/bin/env python3
"""NFL2 site builder.

Reads pipe-delimited CSVs from data/ and markdown from content/, emits a static
site at the repository root (GitHub Pages is configured for main / ).

Design rule enforced here: every rendered data row must carry a source that
resolves to an entry in data/sources.csv. If it does not, the build fails.
Blank cells are rendered as "not published" - never as zero, never as a guess.
"""
import csv, hashlib, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CONTENT = os.path.join(ROOT, "content")

OFFICIAL_HOSTS = {"nfl.com", "www.nfl.com", "operations.nfl.com", "static.www.nfl.com"}
PLAYER_URL = "https://www.nfl.com/players/{}/"
BLANKS = {"", "not published", "n/a", "N/A"}
DATA_FETCHED = "2026-11-12 04:45 UTC"

NAV = [
    ("Overview", [("index", "Dashboard"), ("executive-summary", "Executive Summary"),
                  ("requirements", "Requirements"), ("roadmap", "Build Plan & Roadmap")]),
    ("Decisions", [("questions", "Open Questions"), ("suggestions", "Suggestion Register"),
                   ("flagged-for-review", "Flagged for Review")]),
    ("Origination", [("line-origination", "Originate Our Own Lines"), ("signals", "Signal Catalogue"),
                     ("correlation", "Correlation"), ("bet-types", "Bet Types"),
                     ("skill-vs-luck", "Removing Luck")]),
    ("Competition", [("strategies", "Strategy Registry"), ("leaderboard", "Leaderboard & Rewards"),
                     ("validation-gates", "Validation Gates")]),
    ("Data", [("injuries", "Week 10 Injury Report"), ("depth-impact", "Depth & Deficiencies"),
              ("league-data", "Standings & Schedule"), ("data-dictionary", "Data Dictionary")]),
    ("Governance", [("methodology", "Verification Method"), ("sources", "Source Registry")]),
]
PAGES = [slug for _, items in NAV for slug, _ in items]

VALUE_MAP = {
    "practice": {"F": "Full", "L": "Limited", "D": "Did not practice"},
    "status": {"OUT": "Out", "Q": "Questionable", "D": "Doubtful", "": ""},
}


class BuildError(Exception):
    pass


def read_rows(name):
    name = name.split("/")[-1] if name.startswith("data/") else name
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        raise BuildError("missing data file: %s" % name)
    with open(path, encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    header = raw[0]
    bad = [(i + 1, len(r)) for i, r in enumerate(raw[1:], start=1) if len(r) != len(header)]
    if bad:
        raise BuildError("%s: rows with the wrong field count %s" % (name, bad[:8]))
    return [dict(zip(header, r)) for r in raw[1:]]


SOURCES = {r["id"]: r for r in read_rows("sources.csv")}
SCHEDULE = {r["game_id"]: r for r in read_rows("schedule_2026_wk10.csv")}


def blank_cell():
    return '<span class="np" title="Not published by the official source at fetch time; not inferred.">not published</span>'


def expand_metric_refs(text):
    return re.sub(r"\{\{metric (\w+)\}\}", lambda m: metric(m.group(1)), text)


def esc(text):
    return html.escape(str(text), quote=False)


def inline(text):
    out = esc(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                 lambda m: '<a href="%s"%s>%s</a>' % (m.group(2), ' rel="noopener"' if not m.group(2).startswith("/") else "", m.group(1)),
                 out)
    return out


def urlify(cell):
    parts = [p.strip() for p in cell.split("::") if p.strip()]
    out = []
    for p in parts:
        if p.startswith("http://") or p.startswith("https://"):
            host = re.sub(r"^https?://([^/]+).*", r"\1", p)
            mark = "" if host in OFFICIAL_HOSTS else ' <span class="tier src-other">non-official</span>'
            out.append('<a class="src" href="%s" target="_blank" rel="noopener">%s</a>%s' % (p, esc(host), mark))
        else:
            out.append(esc(p))
    return " ".join(out)


def source_link(sid, tier_label=True):
    row = SOURCES.get(sid)
    if not row:
        raise BuildError("row cites unknown source id: %r" % sid)
    tier = row["tier"].strip()
    cls = "src-official" if tier == "A" else "src-other"
    tag = '<span class="tier %s">%s</span>' % (cls, "official" if tier == "A" else row["kind"])
    return '<a class="src" href="%s" target="_blank" rel="noopener">%s</a>%s' % (row["url"], esc(row["name"]), tag if tier_label else "")


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render_md(text, ctx):
    lines = text.split("\n")
    out, buf, mode = [], [], None

    def flush_p():
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
            buf.clear()

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("{{") and stripped.endswith("}}"):
            flush_p(); out.append(directive(stripped[2:-2].strip(), ctx)); mode = None; i += 1; continue
        if not stripped:
            flush_p(); mode = None; i += 1; continue
        if stripped.startswith("```"):
            flush_p(); mode = None
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(code)))
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_p(); lvl = len(m.group(1))
            anchor = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append('<h%d id="%s">%s</h%d>' % (lvl, anchor, inline(m.group(2)), lvl)); mode = None; i += 1; continue
        if stripped in ("---", "***"):
            flush_p(); out.append("<hr>"); i += 1; continue
        if stripped.startswith("> "):
            flush_p(); quote = [stripped[2:]]
            while i + 1 < len(lines) and lines[i + 1].strip().startswith("> "):
                i += 1; quote.append(lines[i].strip()[2:])
            out.append("<blockquote>%s</blockquote>" % inline(" ".join(quote))); i += 1; continue
        stripped = expand_metric_refs(stripped)
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?[\s:|-]+$", lines[i + 1].strip()) and "-" in lines[i + 1]:
            flush_p()
            header = split_row(stripped)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(split_row(expand_metric_refs(lines[i].strip()))); i += 1
            out.append(html_table(header, body)); continue
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if mode != "ul":
                flush_p(); out.append("<ul>"); mode = "ul"
            out.append("<li>%s</li>" % inline(m.group(1))); i += 1; continue
        m = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if m:
            if mode != "ol":
                flush_p(); out.append('<ol>'); mode = "ol"
            out.append("<li>%s</li>" % inline(m.group(1))); i += 1; continue
        if mode:
            out.append("<li>%s</li>" % inline(stripped)); i += 1; continue
        buf.append(stripped); i += 1
    if mode:
        out.append("</%s>" % mode)
    flush_p()
    return "\n".join(out)


def html_table(header, body):
    th = "".join("<th>%s</th>" % inline(h) for h in header)
    trs = []
    for row in body:
        cells = []
        for cell in row:
            cell = cell.strip()
            cells.append("<td>%s</td>" % (blank_cell() if cell in BLANKS and cell != "n/a" else inline(cell)))
        trs.append("<tr>%s</tr>" % "".join(cells))
    return '<div class="tablewrap"><table class="data"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, "".join(trs))


# ---------------------------------------------------------------- metrics ----
OFF_POS = {"QB", "RB", "FB", "WR", "TE", "T", "G", "C", "OT", "OL", "OG"}
DEF_POS = {"DE", "DT", "LB", "CB", "S", "FS", "SS", "Edge", "DB", "DL", "OLB"}
POS_MAP = {
    "F": "Full", "L": "Limited", "D": "Did not practice",
}


def team_availability(injury_rows):
    teams = {}
    for r in injury_rows:
        t = teams.setdefault(r["team"], {"reported": 0, "dnp": 0, "lim": 0, "full": 0, "dnp_off": 0, "dnp_def": 0})
        t["reported"] += 1
        p = r["practice"]
        if p == "D":
            t["dnp"] += 1
        elif p == "L":
            t["lim"] += 1
        elif p == "F":
            t["full"] += 1
        if p == "D":
            if r["pos"] in OFF_POS:
                t["dnp_off"] += 1
            elif r["pos"] in DEF_POS:
                t["dnp_def"] += 1
    return teams


def build_metrics():
    inj = read_rows("injuries_2026_wk10.csv")
    depth = read_rows("depth_changes_2026_wk10.csv")
    st = read_rows("standings_2026.csv")
    agg = team_availability(inj)
    empty = [t for t in ["SEA", "CIN", "LAC", "BAL"]]
    m = {
        "injury_rows": len(inj),
        "injury_teams": len(agg),
        "games": len(read_rows("schedule_2026_wk10.csv")),
        "dnp": sum(1 for r in inj if r["practice"] == "D"),
        "limited": sum(1 for r in inj if r["practice"] == "L"),
        "full": sum(1 for r in inj if r["practice"] == "F"),
        "designations": sum(1 for r in inj if r["status"].strip()),
        "injury_detail_cells": sum(1 for r in inj if r["injury"].strip()),
        "depth_rows": len(depth),
        "dtr_rows": sum(1 for r in depth if r["change"] == "IR-RETURN-DESIG"),
        "ruled_out_rows": sum(1 for r in depth if r["change"] in ("RULED-OUT", "RULED-OUT-WK9")),
        "qb_depth_rows": sum(1 for r in depth if r["change"] == "DEPTH-CHART" and r["pos"] == "QB"),
        "standings_teams": len(st),
        "sources": len(SOURCES),
        "official_sources": sum(1 for r in SOURCES.values() if r["tier"] == "A"),
        "suggestions": len(read_rows("suggestions.csv")),
        "questions": len(read_rows("questions.csv")),
        "requirements": len(read_rows("requirements.csv")),
        "gates": len(read_rows("gates.csv")),
        "signals": len(read_rows("signals.csv")),
        "strategies": len(read_rows("strategies.csv")),
        "correlation": len(read_rows("correlation.csv")),
        "flags": len(read_rows("flags.csv")),
        "empty_clubs": ", ".join(sorted(empty)),
        "empty_club_count": len([t for t in empty if t not in agg]),
    }
    return m, inj, agg


METRICS, INJURY_ROWS, AGG = build_metrics()
BLANK_TALLY = {"count": 0}


def metric(key):
    return str(METRICS.get(key, "?"))


# ------------------------------------------------------------- directives ----
def parse_opts(body):
    opts = {}
    parts = [p.strip() for p in body.split(";;")]
    name = parts[0]
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            opts[k.strip()] = v.strip()
        else:
            opts[p] = True
    return name, opts


def game_label(gid):
    g = SCHEDULE.get(gid)
    if not g:
        return gid
    return "Week %s · %s · %s @ %s · %s ET" % (g["week"], g["date"], g["away"], g["home"], g["kickoff_et"])


def render_csv_table(body):
    name, opts = parse_opts(body)
    rows = read_rows(name)
    cols = [c for c in opts.get("cols", "").split(",") if c]
    if not cols:
        cols = list(rows[0].keys())
    specs = []
    for c in cols:
        parts = [x.strip() for x in c.split(":")]
        key = parts[0]
        label = parts[1] if len(parts) > 1 else key.replace("_", " ").title()
        fn = parts[2] if len(parts) > 2 else ""
        if key not in rows[0]:
            raise BuildError("%s has no column %r (columns: %s)" % (name, key, ", ".join(rows[0].keys())))
        specs.append((key, label, fn))
    src_col = opts.get("source_col", "")
    src_default = opts.get("source", "")
    if not src_col and not src_default:
        raise BuildError("table %s declares no source; every row must cite one" % name)
    if src_col and src_col not in rows[0]:
        raise BuildError("%s has no source column %r" % (name, src_col))
    group = opts.get("group", "")
    link_player = "link_player" in opts
    filters = [f.split("=", 1) for f in opts.get("filter", "").split(",") if "=" in f]
    for k, v in filters:
        neg = v.startswith("!")
        v = v[1:] if neg else v
        if v == "":
            keep = (lambda cell: cell.strip() == "") if neg else (lambda cell: cell.strip() != "")
        else:
            keep = (lambda cell: v.lower() not in cell.lower()) if neg else (lambda cell: v.lower() in cell.lower())
        rows = [r for r in rows if keep(r.get(k, "").strip())]
    head = [lab for _, lab, _ in specs] + (["Source"] if opts.get("show_source", True) else [])
    out = ['<div class="tablewrap"><table class="data"><thead><tr>']
    out += ["<th>%s</th>" % inline(h) for h in head]
    out.append("</tr></thead><tbody>")
    last_group = object()
    for r in rows:
        if group and r.get(group, "") != last_group:
            last_group = r.get(group, "")
            label = game_label(last_group) if group == "game" else inline(last_group.replace("_", " "))
            out.append('<tr class="grp"><td colspan="%d">%s</td></tr>' % (len(head), label))
        out.append("<tr>")
        for key, _lab, fn in specs:
            val = expand_metric_refs(r.get(key, "").strip())
            if key == "player" and link_player and r.get("slug"):
                val = "[%s](%s)" % (val, PLAYER_URL.format(r["slug"]))
            elif fn in VALUE_MAP:
                val = VALUE_MAP[fn].get(val, val)
            if fn == "urls":
                if "http" not in val:
                    raise BuildError("%s row %r: source cell has no URL" % (name, r.get(specs[0][0], "")))
                out.append("<td>%s</td>" % urlify(val))
                continue
            if val in BLANKS and val != "n/a":
                BLANK_TALLY["count"] += 1
                out.append("<td>%s</td>" % blank_cell())
            else:
                out.append("<td>%s</td>" % inline(val))
        if opts.get("show_source", True):
            if src_col:
                out.append("<td>%s</td>" % source_link(r[src_col]))
            else:
                out.append("<td>%s</td>" % source_link(src_default))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    if opts.get("caption"):
        out.append('<p class="caption">%s</p>' % inline(opts["caption"]))
    return "".join(out)


def render_gate_matrix():
    gates = read_rows("gates.csv")
    strats = read_rows("strategies.csv")
    head = "<tr><th>Strategy</th>" + "".join("<th class=\"g\">%s</th>" % g["id"] for g in gates) + "<th>Passed</th></tr>"
    body = []
    for s in strats:
        blocking = set(x.strip() for x in s["gates_blocking"].replace("none", "").split(","))
        cells = []
        passed = 0
        for g in gates:
            gid = g["id"]
            if gid in blocking:
                cells.append('<td class="cell bad">%s</td>' % "blocked" if g["class"] == "hard" else '<td class="cell soft">%s</td>' % "soft")
            elif g["current_status"] in ("not started", "design only", "blocked"):
                cells.append('<td class="cell warn">%s</td>' % "pending")
            else:
                cells.append('<td class="cell ok">ready</td>')
                passed += 1
        body.append("<tr><th scope=\"row\">%s</th>%s<td><strong>%d/%d</strong></td></tr>" % (inline(s["name"]), "".join(cells), passed, len(gates)))
    return ('<div class="tablewrap"><table class="matrix"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '<p class="caption">Legend: <span class="cell inline bad">blocked</span> the gate cannot be evaluated for this strategy yet · '
            '<span class="cell inline warn">pending</span> the gate is defined but nothing has been measured · '
            '<span class="cell inline ok">ready</span> the input to evaluate this gate exists in the repo.</p>' % (head, "".join(body)))


def render_blank_census():
    files = ["injuries_2026_wk10.csv", "depth_changes_2026_wk10.csv", "standings_2026.csv",
             "correlation.csv", "strategies.csv", "leaderboard.csv", "suggestions.csv"]
    rows = []
    for f in files:
        data = read_rows(f)
        cols = list(data[0].keys())
        blanks = {}
        for r in data:
            for c in cols:
                if r.get(c, "").strip() in BLANKS:
                    blanks[c] = blanks.get(c, 0) + 1
        for c in sorted(blanks, key=lambda k: -blanks[k])[:4]:
            rows.append("<tr><td>%s</td><td>%s</td><td class=\"num\">%d</td><td>%d</td><td>%s</td></tr>"
                        % (f, c, blanks[c], len(data), blank_cell()))
    return ('<div class="tablewrap"><table class="data"><thead><tr><th>File</th><th>Column</th><th>Blank cells</th><th>Rows</th><th>Handling</th></tr></thead><tbody>%s</tbody></table></div>'
            % "".join(rows))


def directive(body, ctx):
    if body.startswith("csv "):
        return render_csv_table(body[4:])
    if body == "kpis":
        return kpi_cards()
    if body == "gate_matrix":
        return render_gate_matrix()
    if body == "blank_census":
        return render_blank_census()
    m = re.match(r"^metric (\w+)$", body)
    if m:
        return metric(m.group(1))
    if body == "team_availability":
        agg = AGG
        rows = []
        order = sorted(agg, key=lambda t: (-agg[t]["dnp_def"], -agg[t]["dnp"]))
        for t in order:
            a = agg[t]
            rows.append("<tr><td>%s</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td class=\"num\">%d</td><td>%s</td></tr>"
                        % (t, a["reported"], a["dnp"], a["lim"], a["full"], a["dnp_off"], a["dnp_def"], blank_cell()))
        for t in ["SEA", "CIN", "LAC", "BAL"]:
            if t not in agg:
                rows.append("<tr class=\"flagrow\"><td>%s</td><td colspan=\"6\">%s</td><td>%s</td></tr>"
                            % (t, blank_cell(), source_link("S-INJ")))
        return ('<div class="tablewrap"><table class="data"><thead><tr><th>Club</th><th>Reported</th><th>Did not practice</th><th>Limited</th>'
                '<th>Full</th><th>DNP offence</th><th>DNP defence</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>'
                '<p class="caption">Counts are arithmetic over the official rows only. "Offence"/"defence" use the position mapping in the '
                '<a href="data-dictionary.html">data dictionary</a>. The last four clubs published no rows on the hub page - they are shown as not published, not as zero (<a href="flagged-for-review.html">FL-01</a>).</p>' % "".join(rows))
    if body == "toc":
        items = ctx.get("toc", [])
        return '<nav class="toc">%s</nav>' % "".join('<a href="#%s">%s</a>' % (a, esc(t)) for a, t in items)
    raise BuildError("unknown directive: %r" % body)


# ---------------------------------------------------------------- layout -----
PAGE_KIND = {
    "index": ("program", "Program"), "executive-summary": ("program", "Report"),
    "requirements": ("program", "Traceability"), "roadmap": ("design", "Specification"),
    "questions": ("decision", "Decision needed"), "suggestions": ("decision", "Awaiting owner review"),
    "flagged-for-review": ("decision", "Review queue"),
    "line-origination": ("design", "Specification"), "signals": ("design", "Specification"),
    "correlation": ("design", "Specification"), "bet-types": ("design", "Specification"),
    "skill-vs-luck": ("design", "Specification"), "strategies": ("design", "Specification"),
    "leaderboard": ("design", "Specification"), "validation-gates": ("design", "Specification"),
    "injuries": ("measured", "Measured data"), "depth-impact": ("measured", "Measured data"),
    "league-data": ("measured", "Measured data"), "data-dictionary": ("measured", "Schema"),
    "methodology": ("program", "Policy"), "sources": ("program", "Register"),
}

CSS_HREF = "assets/style.css"


def layout(slug, title, lead, kind_label, kind, body, ctx, toc):
    base = ""
    nav = []
    for group, items in NAV:
        rows = "".join('<a class="%s" href="%s.html">%s</a>' % ("on" if s == slug else "", s, esc(t)) for s, t in items)
        nav.append('<div class="navgroup"><span>%s</span>%s</div>' % (esc(group), rows))
    navhtml = "".join(nav)
    order = PAGES
    idx = order.index(slug) if slug in order else 0
    prevn = '<a class="pager" href="%s.html">&larr; %s</a>' % (order[idx - 1], esc(dict((s, t) for _, it in NAV for s, t in it)[order[idx - 1]])) if idx > 0 else ""
    nxt = order[idx + 1] if idx + 1 < len(order) else None
    nxtt = dict((s, t) for _, it in NAV for s, t in it)[nxt] if nxt else ""
    nextlink = '<a class="pager right" href="%s.html">%s &rarr;</a>' % (nxt, esc(nxtt)) if nxt else ""
    lead_html = '<p class="lead">%s</p>' % inline(lead) if lead else ""
    toc_html = '<nav class="toc"><span>On this page</span>%s</nav>' % "".join(
        '<a href="#%s">%s</a>' % (a, esc(t)) for a, t in toc) if toc else ""
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s · NFL2</title>
<meta name="description" content="%(lead)s">
<link rel="stylesheet" href="%(css)s">
</head>
<body class="kind-%(kind)s">
<header class="top">
  <a class="brand" href="index.html"><span class="mark">NFL</span> <span>Decision dashboard</span></a>
  <div class="asof">Data fetched <strong>%(fetched)s</strong> · official league sources only · <a href="methodology.html">how this is verified</a></div>
</header>
<div class="shell">
  <aside class="side">
    %(nav)s
    <div class="sidefoot"><a href="flagged-for-review.html">%(flags)s open flags</a> · <a href="sources.html">%(sources)s sources</a></div>
  </aside>
  <main>
    <div class="pagehead">
      <span class="badge %(kind)s">%(kind_label)s</span>
      <h1>%(title)s</h1>
      %(lead)s
    </div>
    %(toc)s
    <div class="body">%(body)s</div>
    <footer class="pagefoot">
      %(prev)s
      %(next)s
      <div class="foot-meta">Rendered from <code>data/</code> by <code>tools/build_site.py</code> — the build is byte-deterministic, so this page is exactly what the audited data says · <a href="https://github.com/kanlerxz87-cyber/NFL2">repository</a></div>
    </footer>
  </main>
</div>
</body></html>
""" % dict(title=esc(title), lead=esc(lead) if lead else "", css=CSS_HREF, fetched=DATA_FETCHED, nav=navhtml,
           kind=kind, kind_label=esc(kind_label), toc=toc_html, body=body, prev=prevn, next=nextlink,
           flags=metric("flags"), sources=metric("sources"))


def render_page(slug):
    path = os.path.join(CONTENT, slug + ".md")
    if not os.path.exists(path):
        raise BuildError("missing content page content/%s.md" % slug)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split("\n")
    title = dict((s, t) for _, it in NAV for s, t in it).get(slug, slug)
    lead = ""
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]
    body_md = "\n".join(lines).strip("\n")
    m = re.match(r"^>\s?(.*)\n", body_md)
    if m:
        lead = m.group(1).strip()
        body_md = body_md[m.end():]
    ctx = {"slug": slug}
    body = render_md(body_md, ctx)
    toc = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', body)
    kind, kind_label = PAGE_KIND[slug]
    return layout(slug, title, lead, kind_label, kind, body, ctx, toc)


def main():
    problems = []
    written = []
    for slug in PAGES:
        try:
            htmlout = render_page(slug)
        except BuildError as exc:
            problems.append("%s: %s" % (slug, exc))
            continue
        if "__INJECT_" in htmlout:
            problems.append("%s: unexpanded placeholder" % slug)
        out = os.path.join(ROOT, slug + ".html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(htmlout)
        written.append(os.path.relpath(out, ROOT))
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(render_page("index").replace("<body", '<body', 1))
    digest = hashlib.sha256()
    for d in (DATA, CONTENT):
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and (f.endswith(".csv") or f.endswith(".md")):
                digest.update(f.encode()); digest.update(open(fp, "rb").read())
    manifest = {
        "inputs_sha256": digest.hexdigest(),
        "data_fetched_utc": DATA_FETCHED,
        "pages": written,
        "metrics": METRICS,
        "blank_cells_rendered_as_not_published": BLANK_TALLY["count"],
        "official_host_allowlist": sorted(OFFICIAL_HOSTS),
    }
    with open(os.path.join(DATA, "build_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("built %d pages · %d blank cells rendered as 'not published'" % (len(written), BLANK_TALLY["count"]))
    if problems:
        print("\n".join("ERROR " + p for p in problems))
        return 1
    return 0


import json



KPIS = [
    ("injury_rows", "Injury rows ingested", "injuries",
     lambda m: "28 clubs, %d players, verbatim from the official hub" % m["injury_rows"]),
    ("designations", "Designations published", "injuries",
     lambda m: "%d of %d rows carry a game status; the rest are not published" % (m["designations"], m["injury_rows"])),
    ("depth_rows", "Depth & roster events", "depth-impact",
     lambda m: "%d entries: IR, returns, signings, QB chain changes" % m["depth_rows"]),
    ("standings_teams", "Standings reconciled", "league-data",
     lambda m: "%d clubs; points and winning %s recomputed clean" % (m["standings_teams"], "pct")),
    ("suggestions", "Suggestions to decide", "suggestions",
     lambda m: "%d options scored; none implemented without your pick" % m["suggestions"]),
    ("questions", "Open questions", "questions",
     lambda m: "%d questions, %d marked P0 blocking" % (m["questions"], m.get("p0", "?"))),
    ("flags", "Flags for review", "flagged-for-review",
     lambda m: "%d irregularities published, none blocking" % m["flags"]),
    ("signals", "Signal families specified", "signals",
     lambda m: "%d specified, %d blocked on data we do not have" % (m["signals"], m.get("signals_blocked", "?"))),
]


def kpi_cards():
    METRICS["p0"] = sum(1 for r in read_rows("questions.csv") if r["priority"] == "P0")
    METRICS["signals_blocked"] = sum(1 for r in read_rows("signals.csv") if r["status"] != "specified")
    cards = []
    for key, title, slug, sub in KPIS:
        cards.append('<div class="card"><h3>%s</h3><div class="big"><a href="%s.html">%s</a></div>'
                     '<div class="sub">%s</div></div>' % (esc(title), slug, metric(key), esc(sub(METRICS))))
    return '<div class="cards">%s</div>' % "".join(cards)


if __name__ == "__main__":
    sys.exit(main())

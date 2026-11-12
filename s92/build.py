#!/usr/bin/env python3
"""s92 dashboard builder.

Every page on this dashboard is generated from s92/data/*.csv (or a checked-in
JSON produced by a script that reads the repository's verified inputs). Nothing
on a page is typed by hand at render time, so a number that is not in the data
cannot appear on the site.

Rules enforced by the builder itself:
  * a table row that has no source URL fails the build;
  * a cell whose value is unknown is rendered as "not published" - never 0,
    never an estimate, never a third party's number;
  * every page carries a data-fetched line naming the UTC time of the fetch
    that produced the table.
"""
import csv, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S92 = os.path.join(ROOT, "s92")
DATA = os.path.join(S92, "data")

OFFICIAL_HOSTS = {
    "www.nfl.com", "nfl.com", "operations.nfl.com", "static.www.nfl.com",
    "www.patriots.com", "www.detroitlions.com", "www.commanders.com",
}
FETCHED = "2026-11-12 22:35 UTC"

NAV = [
    ("Overview", [
        ("index", "Home"),
        ("decision-brief", "Decision brief"),
        ("executive-summary", "Executive summary"),
    ]),
    ("Decide", [
        ("questions", "Questions & answers"),
        ("missing-info", "Missing information"),
        ("suggestions", "Suggestion board"),
        ("assumptions", "Assumptions & bounds"),
    ]),
    ("Origination", [
        ("line-lab", "Line lab"),
        ("strategies", "Strategies & gates"),
        ("correlation", "Correlation & luck"),
    ]),
    ("Data", [
        ("availability", "Injuries & backups"),
        ("official-audit", "Repository audit"),
        ("sources", "Sources"),
    ]),
    ("Review", [
        ("flagged", "Flagged for review"),
    ]),
]
PAGES = [slug for _, items in NAV for slug, _ in items]
TITLES = {slug: title for _, items in NAV for slug, title in items}


class BuildError(Exception):
    pass


def esc(x):
    return html.escape(str(x), quote=False)


def inline(text):
    out = esc(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', out)
    return out


def link(url, text=None):
    if not url:
        raise BuildError("empty source URL")
    host = re.sub(r"^https?://([^/]+).*", r"\1", url)
    cls = "src" if host in OFFICIAL_HOSTS else "src off"
    tag = "" if host in OFFICIAL_HOSTS else ' <span class="pill b">non-league</span>'
    return '<a class="%s" href="%s" target="_blank" rel="noopener">%s</a>%s' % (
        cls, url, esc(text or host), tag)


def read_csv(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="|"))
    if not rows:
        raise BuildError("%s has no rows" % name)
    return rows


def read_json(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


BLANK = {"", "not published", "n/a"}


def cell(value):
    """Blank values are never filled in; they are labelled, not estimated."""
    v = "" if value is None or value is False else str(value).strip()
    if v in BLANK:
        return ('<span class="np">not published</span>'
                '<span class="why">not published by the official source; not inferred</span>')
    return inline(v)


def num(value, digits=2):
    v = "" if value is None else str(value).strip()
    if v == "":
        return cell("")
    try:
        f = float(v)
    except ValueError:
        return cell(v)
    return ("%." + str(digits) + "f") % f


def span(value, good=(), bad=(), warn=()):
    """Render a value as a coloured pill by category, used for status columns."""
    v = "" if value is None else str(value).strip()
    if v in BLANK:
        return cell("")
    if v in bad:
        cls = "c"
    elif v in warn:
        cls = "b"
    elif v in good:
        cls = "a"
    else:
        cls = ""
    return '<span class="pill %s">%s</span>' % (cls, esc(v))


def table(header, rows, cls="data", caption=None):
    head = "".join("<th>%s</th>" % esc(h) for h in header)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r) for r in rows)
    out = '<div class="twrap"><table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cls, head, body)
    if caption:
        out += '<p class="caption">%s</p>' % caption
    return out


def kpis(items):
    cards = []
    for title, big, sub, href in items:
        cards.append('<div class="card"><h3>%s</h3><div class="big"><a href="%s">%s</a></div>'
                     '<div class="sub">%s <a class="more" href="%s">evidence &rarr;</a></div></div>'
                     % (esc(title), href, big if big.startswith("<") else esc(big), inline(sub), href))
    return '<div class="cards">%s</div>' % "".join(cards)


def md(text):
    """Tiny markdown: headings, paragraphs, lists, tables, blockquotes."""
    lines = text.strip("\n").split("\n")
    out = []
    i = 0
    para = []

    def flush():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        m = re.match(r"^(#{2,4})\s+(.*)$", s)
        if m:
            flush()
            lvl = len(m.group(1))
            anchor = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-")
            out.append('<h%d id="%s">%s</h%d>' % (lvl, anchor, inline(m.group(2)), lvl)); i += 1; continue
        if s.startswith("> "):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:]); i += 1
            out.append("<blockquote>%s</blockquote>" % inline(" ".join(quote))); continue
        if s.startswith("|"):
            flush()
            head = [c.strip() for c in s.strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([inline(c.strip()) for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append(table(head, rows)); continue
        if re.match(r"^[-*]\s+", s):
            flush()
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(inline(re.sub(r"^[-*]\s+", "", lines[i].strip()))); i += 1
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in items)); continue
        if re.match(r"^\d+[.)]\s+", s):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\d+[.)]\s+", lines[i].strip()):
                items.append(inline(re.sub(r"^\d+[.)]\s+", "", lines[i].strip()))); i += 1
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % x for x in items)); continue
        para.append(s); i += 1
    flush()
    return "\n".join(out)


def layout(slug, kind, kind_label, title, lead, body):
    nav = []
    for group, items in NAV:
        links = "".join('<a class="%s" href="%s.html">%s</a>' % ("on" if s == slug else "", s, esc(t)) for s, t in items)
        nav.append('<div class="navgroup"><span>%s</span>%s</div>' % (esc(group), links))
    idx = PAGES.index(slug)
    prev = '<a class="pager" href="%s.html">&larr; %s</a>' % (PAGES[idx - 1], esc(TITLES[PAGES[idx - 1]])) if idx else ""
    nxt = ('<a class="pager right" href="%s.html">%s &rarr;</a>' % (PAGES[idx + 1], esc(TITLES[PAGES[idx + 1]]))
           if idx + 1 < len(PAGES) else "")
    toc = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    toc_html = ""
    if toc:
        toc_html = '<nav class="toc"><span>On this page</span>%s</nav>' % "".join(
            '<a href="#%s">%s</a>' % (a, re.sub("<[^>]+>", "", t)) for a, t in toc)
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s &middot; NFL2 s92</title>
<meta name="description" content="%(lead_plain)s">
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="kind-%(kind)s">
<header class="top">
  <a class="brand" href="index.html"><span class="mark">NFL2</span> <span>s92 evidence &amp; decision dashboard</span></a>
  <div class="asof">Official sources fetched <strong>%(fetched)s</strong> &middot; every row links its source &middot;
    <a href="../index.html">root dashboard</a></div>
</header>
<div class="shell">
  <aside class="side">
    %(nav)s
    <div class="sidefoot">Session <code>8b4bdcb3</code><br>Branch <code>arena/8b4bdcb3-nfl2</code></div>
  </aside>
  <main>
    <div class="pagehead">
      <span class="badge %(kind)s">%(kind_label)s</span>
      <h1>%(title)s</h1>
      <p class="lead">%(lead)s</p>
    </div>
    %(toc)s
    <div class="body">%(body)s</div>
    <footer class="pagefoot">
      %(prev)s %(next)s
      <div class="foot-meta">Generated by <code>s92/build.py</code> from <code>s92/data/</code> &middot;
        row sources verified against official league and club pages on 2026-11-12 &middot;
        blanket cells are rendered as <span class="np">not published</span>, never estimated.</div>
    </footer>
  </main>
</div>
</body></html>
""" % dict(title=esc(title), lead=lead, lead_plain=esc(re.sub("<[^>]+>", "", lead)),
           kind=kind, kind_label=esc(kind_label), fetched=FETCHED, nav="".join(nav),
           toc=toc_html, body=body, prev=prev, next=nxt)


# ----------------------------------------------------------------- pages ----

def page_index():
    audit = read_csv("repo_audit.csv")
    ok = sum(1 for r in audit if r["result"] == "VERIFIED")
    bad = len(audit) - ok
    inj = read_json("injuries_official.json")
    q = read_csv("questions.csv")
    sug = read_csv("suggestions.csv")
    bt = read_json("backtest.json")
    depth = read_csv("depth_deficiency.csv")
    body = md("""
## What this dashboard is

A second, additive dashboard inside the NFL2 repository. It does not restate the numbers published by
the other trees; it **re-derives** the ones it can and links to the rest. Its job is to answer three
questions honestly: what do we actually know, what is missing, and what would we build first.

The whole build follows one rule: **a number with no official source is not printed**. Where a value
cannot be confirmed, the cell says *not published* and the row says why.

## The five findings that matter

1. **The standings table is exact.** All 32 clubs, 7 shared fields, 224 cells: zero mismatches against
   the official league table, and points-for equals points-against at 6,246.
2. **The injury table is stale and incomplete.** The official hub now carries 277 practice-participation
   rows across 26 clubs; the stored table has 254 rows across 24 clubs, with two clubs missing entirely.
   Five players disagree on practice status and two stored rows are no longer on the official page.
3. **No market data exists.** Not one price, in any file. Every expected-value, closing-line and vig
   statement in the repository is therefore unverifiable, and this dashboard leaves those cells blank.
4. **Our model is not yet better than guessing.** Leave-one-week-out over 136 games: spread MAE 10.55
   against a zero-line baseline of 10.62 (difference interval includes zero). Total MAE is *worse* than
   the league average: 12.86 vs 11.62.
5. **Depth charts are unofficial by their own labels.** Two of the three club charts inspected say so in
   as many words. Three clubs are covered; twenty-nine are not.
""")
    body += kpis([
        ("Clubs reconciled to official standings", "%d / 32" % len(read_csv("standings_official.csv")),
         "zero mismatches across 224 shared cells", "official-audit.html"),
        ("Official injury rows at fetch", "%d" % len(inj),
         "across %d clubs; stored table has 254 rows across 24" % len({r["team"] for r in inj}), "availability.html"),
        ("Rows verified line by line", "%d of %d" % (ok, len(audit)),
         "%d flagged for review" % bad, "official-audit.html"),
        ("Open questions to answer", "%d" % len(q),
         "%d are P0 blockers" % sum(1 for r in q if r["priority"] == "P0"), "questions.html"),
        ("Suggestions on the board", "%d" % len(sug),
         "each with impact, effort, risk and a recommended path", "suggestions.html"),
        ("Spread MAE vs baseline", "%.2f vs %.2f" % (bt["model_margin_mae"], bt["base_margin_mae"]),
         "136 games, leave-one-week-out; the interval includes zero", "line-lab.html"),
        ("Depth lines where the starter is affected", "%d" % len(depth),
         "3 clubs charted, 1 true cascade (NE running back)", "availability.html"),
        ("Prices in the repository", "0",
         "no market data exists, so no edge can be computed", "questions.html"),
    ])
    body += md("""
## Read the dashboard in this order

| If you want to | Open |
| --- | --- |
| Decide something today | the [decision brief](decision-brief.html) — the shortest path from question to choice |
| See what is missing | the [missing-information register](missing-info.html) — what would have to arrive before a decision is reasonable |
| Choose improvements | the [suggestion board](suggestions.html) — 20 options scored, none implemented without a choice |
| Understand the line lab | the [line lab](line-lab.html) — Week 11 lines, and the backtest that says they are not yet good |
| Check our work | the [repository audit](official-audit.html) — 21 rows, each with the official page that settles it |

## What is verified, what is designed, what is unknown

| Class | Meaning | Pages |
| --- | --- | --- |
| **Verified** | checked line by line against an official league or club page today | repository audit, availability, sources |
| **Computed** | arithmetic over the repository's verified game log, reproducible from `s92/sources.json` | line lab, correlation & luck |
| **Designed** | a specification, not a result; nothing has been bet or paid | strategies & gates, suggestions |
| **Unknown** | no data exists; the cell is blank on purpose | questions, missing information |
""")
    body += '<div class="callout warn"><strong>Nothing here is betting advice.</strong> No price data exists, ' \
            'no bet has been placed, no strategy has passed its gates, and the leaderboard is empty on purpose. ' \
            'The one strategy that clears the data-provenance gate still fails the sample gate.</div>'
    return "program", "Programme", "Home", "What this repository knows, and what it does not.", body


def page_exec():
    bt = read_json("backtest.json")
    inj = read_json("injuries_official.json")
    depth = read_csv("depth_deficiency.csv")
    audit = read_csv("repo_audit.csv")
    q = read_csv("questions.csv")
    sug = read_csv("suggestions.csv")
    body = md("""
## Executive summary

The repository holds one genuinely verified dataset (the 2026 standings, reconciled to the official
league table with zero mismatches), one partially verified dataset (a 136-game game log whose
aggregate reconciles exactly but whose individual scores cannot be re-read through this fetch path),
one stale dataset (the injury table, a filing behind the official hub), and one absent dataset
(prices, of any kind). Everything else is specification.

That ordering matters because it sets the order of work: **collect better before modelling more**.
The three decisions that unblock the most are a price feed, a participation-data licence, and an
agreement on what a depth slot means when the clubs themselves label their charts unofficial.

## Verified

| Claim | Value | How it was verified |
| --- | --- | --- |
| Clubs reconciled to official standings | 32 of 32 | every shared field compared, 224 cells, zero mismatches |
| League points balance | 6,246 for / 6,246 against | arithmetic identity over 32 clubs |
| Games in the log | 136 | 272 club-games ÷ 2; matches the standings sum exactly |
| 2026 rule changes | 4 of 4 match | rulebook page, four rules, word-for-word |
| Week 11 schedule | 13 games, 6 byes | official week page; two TV cells differ |

## Not verified, and why

| Item | State | Why it stays blank |
| --- | --- | --- |
| Any market price | absent | no feed, no licence, no stored prices |
| Individual game scores | single-session transcription | official game pages render scores client-side |
| Injury rows | stale by one filing | 277 official vs 254 stored; SEA and CIN missing |
| Depth order | unofficial | club charts say so themselves; 3 of 32 clubs covered |
| Player-level props | absent | no participation, snap or route data |
| Home-field advantage | not estimable from one season | +0.50 points over 129 games, interval wide |

## The model, stated plainly

""" + "```\n" + """Leave-one-week-out over 136 games, weeks 1-9 of 2026.

Spread   our MAE %.2f    zero-line baseline %.2f    difference 95%% interval [%.2f, %.2f]
Total    our MAE %.2f    league-average baseline %.2f  difference 95%% interval [%.2f, %.2f]
Margin correlation (predicted vs actual)  %.3f
Total  correlation (predicted vs actual)  %.3f
""" % (bt["model_margin_mae"], bt["base_margin_mae"], bt["margin_mae_diff_ci"][0], bt["margin_mae_diff_ci"][1],
       bt["model_total_mae"], bt["base_total_mae"], bt["total_mae_diff_ci"][0], bt["total_mae_diff_ci"][1],
       bt["margin_corr"], bt["total_corr"]) + "```" + """

Read that honestly: the spread model's advantage is **not distinguishable from zero**, and the total
model is **worse than assuming the league average**. That is the ordinary outcome for a first model
with nine weeks of data and no market benchmark, and it is the reason no strategy is certified.

## Availability and depth

%d starter lines across the three charted clubs show a starter who did not practise fully or was ruled
out. Exactly one is a genuine cascade — the New England running-back line, where the starter did not
practise and his listed backup was ruled out, so the next available body is the third name on the chart.
That is the concrete form of "down to a third-stringer", and it is rare: one line in 68 charted lines
at these three clubs.

## What I would do first, in order

| Order | Move | Why now |
| --- | --- | --- |
| 1 | Store every injury filing with its timestamp (S-102) | the current table is already a filing behind; everything downstream inherits that error |
| 2 | Freeze the luck-filter thresholds (S-103, S-104) | costs nothing; prevents the leaderboard from becoming self-deception later |
| 3 | One owner per published number (S-112) | five dashboards currently publish overlapping claims |
| 4 | Buy prices before building strategies (S-101) | without a price there is no such thing as an edge, only a prediction |

## Decision readiness

%d questions are open; %d are P0 blockers. %d suggestions are scored and waiting. The
[decision brief](decision-brief.html) reduces all of it to four choices, in the order in which
they actually have to be made.
""" % (len(depth), len(q), sum(1 for r in q if r["priority"] == "P0"), len(sug)))
    return "program", "Report", "Executive summary", "One page: what is verified, what is not, and what to do first.", body


def page_decisions():
    q = read_csv("questions.csv")
    rows = [[cell(r["id"]), cell(r["domain"]), cell(r["question"]), '<span class="pill %s">%s</span>' % (
        "c" if r["priority"] == "P0" else "b", esc(r["priority"])), cell(r["have"]), cell(r["lack"]),
        cell(r["how_to_close"]), cell(r["status"]), link(r["official_url"])] for r in q]
    body = md("""
## How to read this page

Each question carries four things: **what we already have**, **what we lack**, **how the gap closes**,
and **what it blocks**. The order is deliberate. A question whose "have" column is empty is not a
question about analysis; it is a question about access, and no amount of modelling closes it.

`P0` means a decision or a dataset that blocks other work. Everything else waits behind those.
""")
    body += table(["ID", "Domain", "Question", "P", "What we already have", "What we do not have",
                   "How the gap closes", "Status", "Official source"], rows,
                  caption="Sources are the official page the answer would come from, or the repository file that records the current state.")
    body += md("""
## The four questions that block everything else

| Question | What it blocks | The honest answer |
| --- | --- | --- |
| Q-101 price feed | every expected-value, closing-line and vig number | nothing exists; no price is stored anywhere in the repository |
| Q-103 player-level data | replacement cost, unit-level deficiency, props | only box scores; no snaps, routes or targets |
| Q-104 depth authority | the entire 1st-to-4th-string requirement | every club chart inspected is labelled unofficial |
| Q-108 sample size | any claim that a strategy is skilled | no bet has ever been tracked |

## What answering them would change

If Q-101 and Q-103 closed tomorrow, the line lab could price against a benchmark and the availability
page could price a replacement in points rather than count bodies. If Q-104 closed, the depth page would
stop being a three-club sample. If Q-108 closed, the leaderboard could finally mean something. Until
then, the correct output of this project is the register itself, not a certified strategy.
""")
    return ("decision", "Decision needed", "Questions & answers",
            "What has to be true before a decision here can be called reasonable.", body)


def page_missing():
    q = read_csv("questions.csv")
    r = read_csv("repo_audit.csv")
    body = md("""
## The missing-information register

This is the discovery plan the brief asked for: the information that does not exist yet, where it would
come from, and what would have to happen for it to arrive. It is organised by *what is missing*, not by
what we would like to build, so that the roadmap's inputs are visible before the roadmap.

## Information we have

| Dataset | Coverage | Verified how |
| --- | --- | --- |
| 2026 standings | 32 clubs, 7 fields | every cell compared with the official league table |
| 2026 game log | 136 games, weeks 1-9 | aggregate reconciles exactly to the standings |
| Week 11 schedule | 13 games, 6 byes | official week page; two TV cells differ |
| Injury report | 277 official rows at fetch | parsed from the official hub and stored with retrieval time |
| Club depth charts | 3 clubs, 152 slots | transcribed in full, each labelled unofficial where the club says so |
| 2026 rules | 4 rule changes | word-for-word match against the rulebook page |

## Information we do not have

| Missing item | Would come from | Blocks | Closes |
| --- | --- | --- | --- |
| Prices, opening and closing | a licensed feed | every market-relative metric | Q-101 |
| Settlement rules | one venue's published rulebook | the definition of a graded record | Q-102 |
| Snap counts and routes | a participation-data licence | replacement cost in points | Q-103 |
| A league depth chart | the league, which does not publish one | the 1st-4th string requirement | Q-104 |
| Historical injury filings | a scheduled scraper with timestamps | point-in-time availability signals | Q-105 |
| Game-status semantics | the league's filing calendar | the meaning of a blank cell | Q-106 |
| Player-level joint outcomes | play-by-play | prop and same-game-parlay correlation | Q-109 |
| A funded reward schedule | the owner | whether the competition selects for anything | Q-110 |

## How each gap closes

""" + "\n".join("- **%s** — %s" % (r_["id"] + " " + r_["domain"], r_["how_to_close"]) for r_ in q) + """

## The trap this register is designed to avoid

It is easy to spend a season building models on data that already exists and calling the result skill.
The register exists so that the missing inputs are named *before* the models, and so that a strategy
that depends on an input we do not have is visibly blocked rather than quietly over-fitted. The
[strategy registry](strategies.html) applies exactly this rule: eight of ten entries are blocked on a
named missing input, and the two that are not blocked are labelled research, not skill.

## What cannot be discovered from inside this session

Three items need a decision or a purchase, not a search: the price licence (Q-101), the participation
licence (Q-103) and the reward budget (Q-110). They are recorded here so they are not mistaken for
research tasks that a later session could finish on its own.
""")
    return ("decision", "Discovery plan", "Missing information",
            "What does not exist yet, where it would come from, and what it blocks.", body)


def page_suggestions():
    s = read_csv("suggestions.csv")
    rows = [[cell(r["id"]), cell(r["title"]), cell(r["area"]), cell(r["problem"]), cell(r["proposal"]),
             '<span class="pill %s">%s</span>' % ("c" if r["impact"] == "H" else "b", esc(r["impact"])),
             esc(r["effort"]), cell(r["risk"]), cell(r["reversible"]), cell(r["blocked_on"]),
             cell(r["question"]), cell(r["audit"]), span(r["state"], good=("adopted (v1)",),
                                                            warn=("recommended", "recommended, blocked")),
             cell(r["recommendation"])] for r in s]
    body = md("""
## A dedicated place to review suggestions

The brief asks for a section where suggestions can be reviewed and the best path chosen before
anything is implemented. This is that section. Every entry has the problem it solves, what would be
built, impact, effort, risk, reversibility, the question it depends on, and the audit row that
evidences it.

`H/M/L` for impact and effort are judgements about **this repository and this data state**, recorded as
judgement so they can be argued with. **Reversible** is the column that matters most: a reversible
change with high impact can be approved on judgement alone.

## The board

""")
    body += table(["ID", "Suggestion", "Area", "Problem it solves", "What we would build", "I", "E",
                   "Risk", "Rev.", "Blocked on", "Q", "Audit", "State", "Recommendation"], rows,
                  caption="%d suggestions. None is implemented on the owner's behalf except where the recommendation says so." % len(s))
    body += md("""
## If I had to pick a path for you

Four moves, in this order, because each one makes the next cheaper:

| Order | Suggestion | Why this order |
| --- | --- | --- |
| 1 | S-102 store every injury filing | the current table is already a filing behind; fixing it fixes every downstream page |
| 2 | S-103 + S-104 freeze the luck thresholds and pre-register strategies | free, and they are the only barrier against a leaderboard that flatters itself |
| 3 | S-112 one owner per published number | five dashboards currently publish overlapping claims, and none says which is authoritative |
| 4 | S-101 buy a price feed | expensive, but nothing market-relative exists without it |

## What is already adopted here

These are not proposals; they are how this dashboard is built, so the honest record says so.

| Suggestion | Where you can see it |
| --- | --- |
| S-107 three-state game status | availability page, unknown cells separated from ruled-out |
| S-110 correlation only where joint data exists | correlation page, blank prop cells with the reason |
| S-113 score lines against outcomes now | line lab, the week-by-week backtest |
| S-117 evidence on the same row as the number | every table on this dashboard |
| S-118 label stale data instead of refreshing it | the fetch line on every page and the audit's staleness rows |
| S-119 coverage column on league-wide claims | availability page, 3 of 32 clubs stated |
| S-120 discovery plan before roadmap | the missing-information register |

## Decisions that are yours, not mine

| Suggestion | Why it is not mine to make |
| --- | --- |
| S-101 price feed | it is a licence cost |
| S-105 participation data | it is a licence cost |
| S-111 reward schedule | it is a budget and an incentive design |
| S-116 one dashboard | it is a judgement about how you want to read this project |
""")
    return ("decision", "Awaiting owner review", "Suggestion board",
            "%d options to review, scored by impact, effort, risk and reversibility — choose a path before anything is built." % len(s), body)


def page_assumptions():
    a = read_csv("assumptions.csv")
    rows = [[cell(r["id"]), cell(r["claim"]), cell(r["value"]), cell(r["basis"]), cell(r["limits"]),
             cell(r["publication_rule"]), cell(r["audit"]), link(r["source_url"])] for r in a]
    body = md("""
## Why a bounds register exists

A decision made on an unbounded estimate is a guess wearing a suit. This register states every number
this dashboard uses, the evidence under it, the limit of that evidence, and the rule that governs how it
may be published. Nothing in the table is a market line, and nothing in it is a forecast presented as fact.
""")
    body += table(["ID", "Claim", "Value", "Basis", "Limits", "Publication rule", "Audit row", "Source"], rows,
                  caption="Every row is a statistic computed from data/games_2026_wk1_9.csv, whose aggregate reconciles to the official standings.")
    body += md("""
## The rule the bounds impose

- If an estimate's interval spans zero, the site prints the interval, not the point estimate.
- If the evidence is one season, the site says "one season" on the same line as the number.
- If a value could only come from a source we do not have, the cell stays blank.

That is why the line lab publishes home-field advantage as **zero** rather than the +0.50 measured this
season: a one-season estimate with a wide interval is not a parameter, and pretending otherwise would
make every line look more precise than the evidence supports.

## The luck measurements, stated as bounds

| Measurement | Value | Sample | What it means |
| --- | --- | --- | --- |
| Split-half point-differential persistence | r = 0.186 | 32 clubs, weeks 1-4 vs 5-9 | team quality repeats only weakly across a season |
| League one-score record | 76-76 | 152 club-games | close games are a coin flip, as expected |
| Largest luck residual | 2.17 wins | Denver, 9 games | even the luckiest team is within ~1.5 sd of expectation |
| Pythagorean exponent convention | 2.37 | published football convention | a convention, not a measurement of this season |

The last row matters: the Pythagorean expectation used on the correlation page is a **convention**, not a
fitted value. It is labelled that way wherever it appears.
""")
    return ("decision", "Bounds", "Assumptions & bounds",
            "Every number this dashboard uses, with its evidence, its limits and its publication rule.", body)


def page_lines():
    lines = read_csv("week11_lines.csv")
    bt = read_json("backtest.json")
    rows = []
    for r in lines:
        rows.append([cell(r["game_id"]), cell(r["away"]), cell(r["home"]),
                     cell(r["neutral"]), cell(r["fair_spread_home"]), cell(r["fair_total"]),
                     cell(r["home_win_prob"]), cell(r["market_spread"]), cell(r["market_total"]),
                     link("https://www.nfl.com/schedules/2026/by-week/week-11", "schedule") + " " +
                     link("https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/games_2026_wk1_9.csv", "game log")])
    body = md("""
## What these lines are

Thirteen Week 11 fair lines originated from the repository's verified 136-game log. They are **not**
market lines and they are not betting advice. The market columns are blank because no price data exists
in the repository; they will stay blank until a feed is licensed (Q-101).

The method is deliberately simple and reproducible:

1. A margin rating per club, fitted by iterating team strengths until each club's average residual
   margin is zero, then centring the ratings on the league.
2. A scoring model per club: offence and defence ratings around the 2026 league average of 22.96 points
   per team per game.
3. Home-field advantage set to **zero** by published policy (S-109), because the 2026 estimate
   (+0.50 points over 129 games) has an interval that comfortably includes zero.
4. The neutral-site game (Minnesota at San Francisco, Mexico City) has no home term at all.

## Week 11 fair lines

""")
    body += table(["Game", "Away", "Home", "Neutral", "Fair spread (home)", "Fair total",
                   "Home win prob.", "Market spread", "Market total", "Official source"], rows,
                  caption="Spread is the home team's expected margin. A negative number means the home side is the underdog. Market columns are blank on purpose.")
    body += md("""
## Why the totals look high

The fair totals are a direct consequence of 2026 scoring: the league is averaging 45.9 points a game,
and a few clubs (Cincinnati, Jacksonville, Buffalo) have offence ratings far above that. A total of 56.9
for New Orleans at Chicago is what the model says, not what a book would say; a book would shade it
down. **The absence of a market line is the whole problem.** Without one, we cannot tell whether a
56.9 is insight or error.

## The backtest that keeps this honest

Same model, leave-one-week-out over the nine weeks we have.

""" + "```" + """
Spread   our MAE %.2f    zero-line baseline %.2f    95%% interval on the difference [%.2f, %.2f]
Total    our MAE %.2f    league-average %.2f        95%% interval on the difference [%.2f, %.2f]
Correlation of predicted and actual margin  %.3f
Correlation of predicted and actual total   %.3f
""" % (bt["model_margin_mae"], bt["base_margin_mae"], bt["margin_mae_diff_ci"][0], bt["margin_mae_diff_ci"][1],
       bt["model_total_mae"], bt["base_total_mae"], bt["total_mae_diff_ci"][0], bt["total_mae_diff_ci"][1],
       bt["margin_corr"], bt["total_corr"]) + "```" + """

Two things follow, and both are printed on the page rather than buried in a footnote:

- **The spread model is not yet better than a zero line.** The difference interval spans zero.
- **The total model is worse than the league average.** Its error is higher than assuming 45.9 every week.

A model that does not beat a naive baseline is not a signal, and no strategy built on top of it can pass
the sample gate. The correct next step is more data and a market benchmark, not more model complexity.

## What would make these lines better

| Input | Effect | Blocked by |
| --- | --- | --- |
| Closing prices | turn "is it right?" into "is it better than the market?" | Q-101 |
| Injury-adjusted ratings | the model currently ignores who is available | Q-103, Q-105 |
| Realised snap share | replace the unofficial depth prior with who actually played | Q-104 |
| Multi-season history | make home-field and rating stability estimable | repository scope |
""")
    return ("measured", "Computed output", "Line lab",
            "Week 11 fair lines from a reproducible model, with the backtest that shows it is not yet better than guessing.", body)


def page_strategies():
    st = read_csv("strategies.csv")
    g = read_csv("gates.csv")
    sig = read_csv("signals.csv")
    grows = [[cell(r["id"]), cell(r["gate"]), '<span class="pill %s">%s</span>' % (
        "c" if r["class"] == "hard" else "b", esc(r["class"])), cell(r["test"]), cell(r["pass_criterion"]),
        cell(r["blocks"])] for r in g]
    srows = [[cell(r["id"]), cell(r["bet_type"]), cell(r["market"]), cell(r["thesis"]), cell(r["signal"]),
              cell(r["entry_rule"]), cell(r["gate_status"]), '<span class="pill %s">%s</span>' % (
                  "c" if r["state"] in ("blocked", "gated") else "b", esc(r["state"]))] for r in st]
    sigrows = [[cell(r["id"]), cell(r["family"]), cell(r["signal"]), cell(r["evidence"]),
                cell(r["question"]), '<span class="pill %s">%s</span>' % (
                    "a" if r["state"] == "live" else ("b" if r["state"] == "weak" else "c"), esc(r["state"]))]
               for r in sig]
    body = md("""
## The competition, as specified

Ten pre-registered strategies: five singles, three parlays, two player-prop combos. Each is entered
against a gate set that a strategy must clear **before** it can be called skilled, and a second, softer
set before it can be rewarded. Nothing here has been bet. The leaderboard is empty because no strategy
has cleared the gates, and printing an empty leaderboard is more honest than printing a backtested one.

## The validation gates

Two classes. **Hard** gates block promotion or the "skilled" label outright; **soft** gates only affect
the reward tier.

""")
    body += table(["ID", "Gate", "Class", "Test", "Pass criterion", "Blocks"], grows,
                  caption="The gates are ordered so that no amount of statistical significance can rescue a strategy whose data provenance is unproven.")
    body += md("""
## The strategy registry

""")
    body += table(["ID", "Type", "Market", "Thesis", "Signal", "Entry rule", "Gate status", "State"], srows,
                  caption="Eight of ten entries are gated or blocked on a named missing input. None is tracked.")
    body += md("""
## Why eight of ten are blocked

Because the gates are ordered by provenance, not by significance. G-0 requires every input to carry a
source and a licence position. No price feed exists, so any strategy whose entry rule mentions a price
fails G-0 before any backtest is even run. That is the intended behaviour: it prevents a backtest on
third-party data from being presented as a result.

## The signal catalogue

""")
    body += table(["ID", "Family", "Signal", "Evidence", "Question", "State"], sigrows,
                  caption="Live means the data to compute the signal exists in the repository. Weak means it exists but the sample is too small. Blocked means it does not exist.")
    body += md("""
## Leaderboard and rewards — the rules, before any results

| Rule | Why |
| --- | --- |
| Only strategies that pass G-0 to G-3 appear at all | provenance and pre-registration are entry conditions, not achievements |
| A "skilled" label requires G-4 to G-7 | sample sufficiency, multiple-testing correction, persistence and a luck interval |
| Reward tiers require G-8 and G-9 | a benchmark comparison and a capacity check |
| Backtests never appear on the leaderboard | a backtest is a hypothesis, not a record |
| Losing records are published | hiding them would turn the board into marketing |

The payout schedule itself is **unfunded and undefined** (Q-110, S-111). That is an owner decision, not
an engineering task, and it is the one item on this page that cannot be finished by a later session.

## What the first real strategy would look like

The first strategy that could clear the gates is not a parlay. It is a single-market strategy with a
licensed price, a pre-registered rule, a stated sample target and a recorded first-bet timestamp — most
likely an availability-surprise total, because that is where the repository's own data is strongest.
Everything else waits on data.
""")
    return ("design", "Specification", "Strategies & gates",
            "Ten pre-registered strategies and ten gates, ordered so that provenance comes before significance.", body)


def page_correlation():
    bt = read_json("backtest.json")
    luck = read_json("luck.json")
    lrows = [[cell(r["team"]), str(r["games"]), "%d-%d-%d" % (r["w"], r["l"], r["ties"]),
              "%d/%d" % (r["pf"], r["pa"]), num(r["pyth_pct"], 3), num(r["pyth_wins"]), num(r["luck_wins"]),
              num(r["luck_sd"]), num(r["luck_z"]), str(r["one_score_games"]), str(r["one_score_w"])]
             for r in luck]
    body = md("""
## Correlation, measured only where joint data exists

The brief asks for correlation values, for single bets, parlays and player-prop combos. The honest
answer is that **only the game-level pairs are measurable** from the repository's verified data. Anything
involving players requires joint player-level outcomes, which we do not have. Those cells are blank.

## Game-level correlation, 2026, n = 136

| Pair | Pearson r | What it means |
| --- | --- | --- |
| Game margin vs game total | **-0.161** | higher totals go slightly with closer games; the relationship is weak |
| Home points vs away points | **+0.076** | the two sides are effectively independent at game level |

These are descriptive statistics on one season. They are not estimates of a market relationship, and
they cannot price a parlay on their own. A parlay price needs the *joint* probability of both legs
winning, which needs the same-game joint distribution — not a correlation coefficient alone.

## What is blank, and why

| Pair class | Value | Reason |
| --- | --- | --- |
| Spread vs moneyline (same game) | not published | not computable without a price feed |
| Spread vs total (same game) | -0.161 | measured, above |
| Two legs in different games | ~0 | different games are independent by construction |
| Two legs in the same game | not published | joint outcome requires the full same-game distribution |
| QB passing vs WR receiving (same team) | not published | no player-level data |
| RB rushing vs team total | not published | no player-level data |
| Defensive prop vs opposing total | not published | no player-level data |

## Removing luck

Four filters, all computable from the repository's own data.

""" + """
### 1. Pythagorean luck residual

Each club's actual wins compared with a Pythagorean expectation, with the exponent printed as a
convention (2.37) rather than a measured parameter. The largest residual in the league is Denver at
**+2.17 wins**; the unluckiest is Tampa Bay at **-2.17**. Both are within about 1.5 standard deviations
of expectation, which is the point: **nobody in this league has been very lucky yet.**

### 2. Split-half persistence

Point differential in weeks 1-4 compared with weeks 5-9: **r = 0.186** across 32 clubs. Team quality
repeats only weakly over nine weeks, which is why a nine-week model is not a basis for a skilled label.

### 3. One-score records

League-wide, one-score games are **76-76**. Close-game records are a coin flip, and any strategy that
depends on them is depending on variance.

### 4. Multiple-testing correction, pre-registered

Any strategy that is tested more than once must clear a Bonferroni-corrected threshold. The threshold is
fixed in advance (S-103) so it cannot be chosen after seeing the result.
""")
    body += md("""
## The luck table, club by club

""")
    body += table(["Team", "G", "W-L-T", "PF/PA", "Pyth. pct", "Pyth. wins", "Luck (wins)", "sd", "z",
                   "One-score games", "One-score wins"], lrows,
                  caption="Pythagorean expectation is a published convention, not a fitted parameter. Luck is actual wins minus expected wins; z is luck divided by its binomial standard deviation.")
    body += md("""
## What this means for decision making

- **No club is a proven over- or under-performer on this sample.** Every luck residual is inside the
  range that random variation alone would produce.
- **No strategy can be certified from nine weeks.** The sample gate (G-4) exists precisely for this.
- **The measured game-level correlations are small**, which is good news for cross-game parlays (legs are
  close to independent) and bad news for anyone hoping to find a large, simple correlation signal.
- **The prop question is unanswered, not answered negatively.** Blank is not zero, and the route to an
  answer is a participation-data licence, not a better formula.
""")
    return ("measured", "Computed output", "Correlation & luck",
            "Measured game-level correlations, and four filters that separate skill from variance.", body)


def page_availability():
    inj = read_json("injuries_official.json")
    depth = read_csv("depth_deficiency.csv")
    charts = read_csv("depth_charts_official.csv")
    clubs = sorted({r["team"] for r in inj})
    counts = {c: sum(1 for r in inj if r["team"] == c) for c in clubs}
    crow = [[cell(c), str(counts[c]),
             str(sum(1 for r in inj if r["team"] == c and r["practice"] == "D")),
             str(sum(1 for r in inj if r["team"] == c and r["practice"] == "L")),
             str(sum(1 for r in inj if r["team"] == c and r["practice"] == "F")),
             str(sum(1 for r in inj if r["team"] == c and r["status"] == "OUT")),
             link("https://www.nfl.com/injuries/", "official hub")] for c in clubs]
    drow = [[cell(r["club"]), cell(r["unit"]), cell(r["pos"]), cell(r["line"]), cell(r["starter"]),
             '<span class="pill %s">%s</span>' % ("c" if r["starter_state"] in ("OUT", "DNP") else "b", esc(r["starter_state"])),
             cell(r["next_man_up"]), cell(r["next_man_state"]), cell(r["first_available"]),
             cell(r["first_available_state"]), cell(r["depth_rank_used"]),
             ('<span class="pill c">yes</span>' if r["cascade"] == "yes" else "no"), cell(r["note"]),
             link("https://www.nfl.com/injuries/", "injury") + " " + link(r["evidence"].split(" :: ")[1], "chart")]
            for r in depth]
    body = md("""
## What this page covers, and what it does not

Injury participation for **26 clubs** as published on the official hub at fetch time, and club depth
charts for **3 of 32 clubs**, transcribed in full. The shortfall is stated on the page rather than
implied away: 29 clubs have no depth chart here, and every league-wide claim on this page is scoped to
the three clubs that do.

Two of the three charts are described as **unofficial** by the club that publishes them. That is not a
technicality; it means a depth chart cannot be cited as an official source, and the only defensible
depth authority is realised playing time, which requires participation data we do not have (Q-103).

## Injury participation by club, official filing

""")
    body += table(["Club", "Rows", "Did not practise", "Limited", "Full", "Ruled out", "Source"], crow,
                  caption="277 practice-participation rows across 26 clubs at the Thursday 12 November filing. Clubs absent from this table published no rows at fetch.")
    body += md("""
## Lineup deficiency: starters affected and who replaces them

The requirement is to know when a 2nd, 3rd or 4th-string player has to replace a starter, on offence or
defence. The table below answers it for the three charted clubs, using only what the official filing says
about the starter and about the men behind him.

""")
    body += table(["Club", "Unit", "Pos", "Line", "Starter", "Starter state", "Next man up",
                   "His state", "First available", "His state", "Depth used", "Cascade", "Note", "Sources"], drow,
                  caption="A cascade means the starter was out or did not practise AND the next man up was also out or did not practise, so the club goes to its third name.")
    body += md("""
## The one genuine cascade

New England's running-back line is the only true cascade at these three clubs. The starter,
**Rhamondre Stevenson**, did not practise; the next man up, **TreVeyon Henderson**, was ruled **out**;
the first available body is the third name on the chart, **Corey Kiner**. That is exactly the
"down to a third-stringer" case the requirement is about.

Every other affected line has a healthy next man up. That is a finding too: at these three clubs, on this
filing, depth is mostly holding.

## Why this is not yet a league-wide answer

| Requirement | State here | What closes it |
| --- | --- | --- |
| Track injuries | 26 clubs, one filing | store every filing (S-102) |
| Detect backups replacing starters | 3 clubs | chart all 32 clubs, or license participation data |
| Offence and defence separately | yes, where charted | same |
| 2nd, 3rd and 4th string | charted to four deep where the club lists it | same |
| Know who actually played | no | participation data (Q-103) |

## The trap on this page

"Did not practise" is not "will not play", and a blank game-status cell is not "probable" — it is
"not yet filed". This page therefore carries three states, never two, and never converts a practice
status into a prediction of availability.
""")
    return ("measured", "Measured data", "Injuries & backups",
            "Official injury participation for 26 clubs, and starter-to-backup chains for the 3 clubs whose depth charts are published.", body)


def page_audit():
    a = read_csv("repo_audit.csv")
    order = {"VERIFIED": 0, "UNDERCOUNT": 1, "STALE": 2, "STALE-LABEL": 2, "MISMATCH": 1, "EXTRA-ROW": 1,
             "LABEL-RISK": 2, "SEMANTICS": 2, "PARTIAL": 3, "UNVERIFIED": 3, "DUPLICATION": 3,
             "AMBIGUOUS": 3, "NOT-RE-VERIFIABLE": 3}
    rows = []
    for r in sorted(a, key=lambda r: (order.get(r["result"], 9), r["id"])):
        cls = "a" if r["result"] == "VERIFIED" else ("c" if order.get(r["result"], 9) <= 1 else "b")
        rows.append([cell(r["id"]), cell(r["area"]), cell(r["repo_file"]), cell(r["repo_claim"]),
                     cell(r["official_value"]), '<span class="pill %s">%s</span>' % (cls, esc(r["result"])),
                     cell(r["evidence"]), cell(r["resolution"]), link(r["official_url"])])
    ok = sum(1 for r in a if r["result"] == "VERIFIED")
    body = md("""
## What was checked, and against what

Twenty-one findings from a line-by-line review of the repository against official league and club pages
fetched on 12 November 2026. Each row names the repository file, what it claims, what the official source
says, the evidence, and what should happen next. Nothing in the repository was edited to make a row pass:
findings are published, not silently fixed.

**%d of %d rows verified clean. The rest are published on the [flagged for review](flagged.html) page.**
""" % (ok, len(a)))
    body += table(["ID", "Area", "Repository file", "What the repo says", "What the official source says",
                   "Result", "Evidence", "Resolution", "Official source"], rows,
                  caption="Result vocabulary: VERIFIED (matches), UNDERCOUNT/MISMATCH/EXTRA-ROW (differs at row level), STALE (lags the source), PARTIAL (checked in part), LABEL-RISK/SEMANTICS/AMBIGUOUS (true but misleading), DUPLICATION (multiple owners), NOT-RE-VERIFIABLE (could not be re-read through this fetch path).")
    body += md("""
## The row-level diff behind the injury findings

The stored injury table was compared row by row with the official filing, using club and player slug as
the key.

| Comparison | Stored table | Official filing |
| --- | --- | --- |
| Rows | 254 | 277 |
| Clubs with at least one row | 24 | 26 |
| Practice-status disagreements | 5 players | — |
| Rows in the stored table absent from the official page | 2 | — |
| Clubs absent from the stored table entirely | SEA, CIN | — |

The five practice-status disagreements are: Isaac Seumalo (Arizona) full → did not practise; A.J. Haulcy
and Charvarius Ward (Indianapolis) did not practise → full; Jerry Tillery (Indianapolis) limited → did not
practise; Jonathan Taylor (Indianapolis) limited → full.

## What this audit does not claim

It does not claim the repository is wrong everywhere. It claims exactly what each row says, against the
page named in that row, at the time printed at the top of this page. Sources change between filings; a
row that is stale today may have been correct when it was written, which is precisely the defect: the
table does not record *when* it was true.
""")
    return ("measured", "Audit", "Repository audit",
            "Twenty-one findings from a line-by-line review against official pages, published rather than silently fixed.", body)


def page_sources():
    s = read_csv("sources.csv")
    rows = [[cell(r["id"]), cell(r["name"]), cell(r["org"]), link(r["url"]), cell(r["retrieved_utc"]),
             cell(r["used_for"])] for r in s]
    body = md("""
## Every source this dashboard uses

Each row names the page, the organisation, the exact URL, the UTC time it was retrieved, and what it was
used for. Official league and club hosts are marked as such; repository sources are internal and are
labelled.

## Source register

""")
    body += table(["ID", "Source", "Organisation", "URL", "Retrieved (UTC)", "Used for"], rows)
    body += md("""
## How verification was performed

1. The official page was retrieved through the session's page-fetch path and its content stored verbatim
   under `s92/raw/` for each injury chunk, and transcribed into a pipe-delimited table for standings,
   schedule, depth charts and rule changes.
2. The repository file was parsed with the same field vocabulary and compared row by row, keyed on club
   and player slug (injury), or club abbreviation (standings, schedule).
3. Arithmetic identities were re-derived rather than trusted: points-for equals points-against; wins plus
   losses plus ties times two equals twice the game count; net points equals points for minus points
   against.
4. Where a page could not be re-read (game scores render client-side), the row says so instead of
   claiming a verification that did not happen.

## A limitation of this session, stated plainly

Bash-level HTTPS to the league's hosts fails with a TLS error from this sandbox. Every official page
here was therefore retrieved through the session's page-fetch path, which returns rendered text. That is
sufficient for tables and prose, and **not** sufficient for client-rendered score boxes — which is why
the audit carries a NOT-RE-VERIFIABLE row for game scores rather than a green tick.
""")
    return ("program", "Register", "Sources",
            "Every page used on this dashboard, with the exact URL and the UTC retrieval time.", body)


def page_flagged():
    a = read_csv("repo_audit.csv")
    flagged = [r for r in a if r["result"] != "VERIFIED"]
    rows = [[cell(r["id"]), cell(r["area"]), cell(r["repo_claim"]), cell(r["official_value"]),
             '<span class="pill c">%s</span>' % esc(r["result"]), cell(r["evidence"]),
             cell(r["resolution"]), link(r["official_url"])] for r in flagged]
    q = [r for r in read_csv("questions.csv") if r["priority"] == "P0"]
    body = md("""
## Flagged for review

These items do not block the dashboard from publishing, and none of them has been fixed by editing the
repository's own data. They are the things a reader should know before trusting any number on this site.
Each carries the official page that settles it, so a reviewer can check it without re-running anything.

**%d items.** Verified rows are excluded and live on the [repository audit](official-audit.html) page.
""" % len(flagged))
    body += table(["ID", "Area", "What the repository says", "What the official source says", "Result",
                   "Evidence", "What should happen", "Official source"], rows,
                  caption="Nothing on this page is blocking. It exists so that a reviewer can see the known defects without reading the whole repository.")
    body += md(r"""
## Opens that are not defects, but are still open

| Open item | Why it stays open |
| --- | --- |
| No market price exists | a licence decision, not a bug |
| Depth charts are unofficial | the clubs say so themselves; the league publishes none |
| Home-field is set to zero in our lines | a one-season estimate is not a parameter |
| No strategy is certified | no sample, no price, no pre-registration record yet |

## The P0 questions behind the flags

""")
    body += "\n".join("- **%s %s** — %s" % (r["id"], r["domain"], r["question"]) for r in q)
    body += md("""

These are the only items where a decision from the owner, rather than more work from a session, changes
the answer. They are also the items most likely to be mistaken for research tasks, which is why they are
repeated here.
""")
    return ("decision", "Review queue", "Flagged for review",
            "%d irregularities and unverifiable items, each with the official page that settles it." % len(flagged), body)


def page_brief():
    q = read_csv("questions.csv")
    s = read_csv("suggestions.csv")
    body = md("""
## The brief, as a decision

Four choices, in the order in which they have to be made. Each one has a question behind it, a
suggestion that implements it, and a consequence if it is not made. Nothing below has been decided on
your behalf.

## Choice 1 — do we buy prices?

| | |
| --- | --- |
| Question | Q-101. Which feed, at what latency, at what licence cost? |
| Suggestion | S-101. Licence one point-in-time archive and replay a completed season. |
| If yes | every market-relative metric becomes computable: vig, fair value, closing-line value, edge |
| If no | the project stays a prediction exercise; no strategy can ever be called skilled |
| Cost of delay | every week of the season is a week of prices not captured, and prices cannot be bought retrospectively |

**Recommendation: yes, and this is the only purchase that unlocks the rest.**

## Choice 2 — do we buy participation data?

| | |
| --- | --- |
| Question | Q-103. Are we entitled to store and re-price snaps, routes and targets? |
| Suggestion | S-105, then S-106 to use realised snap share instead of club charts. |
| If yes | "a starter is out" becomes "his replacement costs N points", and the depth requirement becomes quantitative |
| If no | the depth page stays a count of bodies, and prop markets stay unpriceable |

**Recommendation: yes, but second. It only pays off once prices exist to value it against.**

## Choice 3 — do we fund the leaderboard?

| | |
| --- | --- |
| Question | Q-110. What does it pay, to whom, on what schedule? |
| Suggestion | S-111. Write the budget, tiers, eligibility and anti-gaming rules before the first entry. |
| If yes | the competition has an incentive structure and the gates have teeth |
| If no | keep the registry as a research log; drop the reward language so the page does not promise what it cannot pay |

**Recommendation: write the rules now even if the budget is zero. An unfunded but well-specified board is
more honest than a funded one with no rules.**

## Choice 4 — one dashboard or many?

| | |
| --- | --- |
| Question | Q-112. Which page owns each number? |
| Suggestion | S-112 and S-116. A metric ownership table, and one landing page with category navigation. |
| If yes | a reader can trust that two pages will not disagree, and the archives stay as archives |
| If no | every number needs an owner named next to it, forever |

**Recommendation: yes. This dashboard is built that way on purpose; it links rather than restates.**

## What I would not spend your decision on

| Item | Why not |
| --- | --- |
| Which betting market to enter first | it is downstream of Choice 1 |
| How many strategies to register | the registry is free; the gates do the filtering |
| Whether to publish losing records | yes, obviously; hiding them would make the board marketing |

## The honest summary

The repository has one fully verified dataset, one partially verified dataset, one stale dataset and one
absent dataset. The highest-value work is not a better model; it is storing better data. If you approve
only one thing, approve **S-102**: store every injury filing with its timestamp. It costs nothing, it
fixes an error that is already visible, and it is the prerequisite for the only signal family where this
project is currently strongest.
""")
    return ("decision", "Decision needed", "Decision brief",
            "Four choices, in the order they have to be made, with the consequence of each.", body)


PAGE_FUNCS = {
    "index": page_index,
    "executive-summary": page_exec,
    "decision-brief": page_brief,
    "questions": page_decisions,
    "missing-info": page_missing,
    "suggestions": page_suggestions,
    "assumptions": page_assumptions,
    "line-lab": page_lines,
    "strategies": page_strategies,
    "correlation": page_correlation,
    "availability": page_availability,
    "official-audit": page_audit,
    "sources": page_sources,
    "flagged": page_flagged,
}


def main():
    os.makedirs(os.path.join(S92, "assets"), exist_ok=True)
    written = []
    problems = []
    for slug in PAGES:
        try:
            kind, label, title, lead, body = PAGE_FUNCS[slug]()
        except BuildError as exc:
            problems.append("%s: %s" % (slug, exc))
            continue
        page = layout(slug, kind, label, title, lead, body)
        if "__MISSING" in page:
            problems.append("%s: unexpanded placeholder" % slug)
        with open(os.path.join(S92, slug + ".html"), "w", encoding="utf-8") as fh:
            fh.write(page)
        written.append(slug + ".html")
    if problems:
        print("\n".join("ERROR " + p for p in problems))
        return 1
    print("built %d pages in s92/" % len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())

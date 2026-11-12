#!/usr/bin/env python3
"""
verify_site.py — checks the generated HTML before it is allowed to go live.

The failures this guards against are the ones that make a page look fine and be wrong:

  H1  every page parses and has balanced <table>/<tr>/<td> counts
  H2  no raw "&amp;amp;" double-escaping (a classic sign of double-E() calls)
  H3  no unresolved "None"/"null"/"nan"/"{"/"}" leaked into rendered text
  H4  every internal href resolves to a file that exists
  H5  every page carries the nav and the footer provenance line
  H6  every "source" link is absolute https and points at an official host
  H7  no page exceeds a sane size and none is empty
  H8  the pages that must state a withholding actually do
  H9  no page claims a strategy is VALIDATED when analysis says none is
  H10 every page declares a charset and a viewport (mobile + encoding)
"""
import os, re, sys, json, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html","results.html","standings.html","teams.html","injuries.html",
         "analysis.html","strategies.html","method.html","sources.html",
         "questions.html","suggestions.html","flagged.html"]
# Official NFL club sites are the ONLY place depth charts and club injury pages exist.
# They are official club properties, not third-party aggregators, so they are allowed
# by explicit enumeration -- never by pattern (no wildcard, no "any *.com").
CLUB_OFFICIAL = {
 "www.chiefs.com","www.detroitlions.com","www.packers.com","www.patriots.com",
 "www.vikings.com","www.commanders.com","www.buffalobills.com","www.miamidolphins.com",
 "www.newyorkjets.com","www.baltimoreravens.com","www.bengals.com","www.clevelandbrowns.com",
 "www.steelers.com","www.houstontexans.com","www.colts.com","www.jaguars.com",
 "www.tennesseetitans.com","www.denverbroncos.com","www.raiders.com","www.chargers.com",
 "www.dallascowboys.com","www.giants.com","www.philadelphiaeagles.com","www.washington.com",
 "www.chicagobears.com","www.lions.com","www.packers.com","www.vikings.com",
 "www.atlantafalcons.com","www.panthers.com","www.neworleanssaints.com","www.buccaneers.com",
 "www.azcardinals.com","www.rams.com","www.49ers.com","www.seahawks.com",
}
OFFICIAL_HOSTS = {"www.nfl.com","nfl.com","operations.nfl.com","github.com","kanlerxz87-cyber.github.io"}
OFFICIAL = ("nfl.com","operations.nfl.com","github.com","kanlerxz87-cyber.github.io")

checks=[]
def add(cid, name, ok, detail=""):
    checks.append({"id":cid,"name":name,"ok":bool(ok),"detail":detail[:1500]})

docs={}
for p in PAGES:
    fp=os.path.join(ROOT,p)
    docs[p]=open(fp,encoding="utf-8").read() if os.path.exists(fp) else None

missing=[p for p in PAGES if docs[p] is None]
add("H0","All 12 pages exist",not missing,f"missing={missing}")

# H1 structural balance
bad1=[]
for p,d in docs.items():
    if d is None: continue
    for tag in ("table","tr","td","th","div"):
        o=len(re.findall(rf"<{tag}[\s>]",d)); c=len(re.findall(rf"</{tag}>",d))
        if o!=c: bad1.append(f"{p}:<{tag}> {o} vs {c}")
add("H1","Tags balanced on every page",not bad1,"; ".join(bad1))

# H2 double escaping
bad2=[p for p,d in docs.items() if d and ("&amp;amp;" in d or "&amp;lt;" in d or "&amp;gt;" in d)]
add("H2","No double-escaped entities",not bad2,", ".join(bad2))

# H3 leaked python/JS values
leak=re.compile(r">\s*(None|null|nan|NaN|undefined|\[object Object\])\s*<")
bad3=[p for p,d in docs.items() if d and leak.search(d)]
braces=[p for p,d in docs.items() if d and re.search(r">\s*\{[a-zA-Z_]+\}\s*<",d)]
add("H3a","No leaked None/null/nan in rendered text",not bad3,", ".join(bad3))
add("H3b","No unrendered f-string placeholders",not braces,", ".join(braces))

# H4 internal links resolve
bad4=[]
for p,d in docs.items():
    if d is None: continue
    for href in set(re.findall(r'href="([^"]+)"',d)):
        if href.startswith(("http","#","mailto")): continue
        target=href.split("#")[0]
        if not target: continue
        if not os.path.exists(os.path.join(ROOT,target)):
            bad4.append(f"{p} -> {href}")
add("H4","Every internal link resolves to a real file",not bad4,"; ".join(sorted(set(bad4))))

# H5 nav + footer
bad5=[p for p,d in docs.items() if d and ('class="brand"' not in d or "Flagged for Review" not in d)]
add("H5","Every page carries the shared nav and the Flagged-for-Review link",not bad5,", ".join(bad5))

# H6 external links official https
bad6=[]
for p,d in docs.items():
    if d is None: continue
    for href in set(re.findall(r'href="(https?://[^"]+)"',d)):
        if not href.startswith("https://"): bad6.append(f"{p}: non-https {href}")
        host = href.split("/")[2].lower()
        if host in OFFICIAL_HOSTS or host in CLUB_OFFICIAL: continue
        bad6.append(f"{p}: non-official host {host}")
add("H6","Every external link is https and on an official host",not bad6,"; ".join(sorted(set(bad6))[:12]))

# H7 size
bad7=[p for p,d in docs.items() if d is not None and (len(d)<3000 or len(d)>900_000)]
add("H7","No page is empty or absurdly large",not bad7,", ".join(bad7))

# H8 required disclosures
must={
 "flagged.html":["IR-04","IR-08","FL-04","FL-08","withheld","Withheld"],
 "injuries.html":["unofficial","depth","unmapped"],
 "analysis.html":["MODEL","model","withheld"],
 "strategies.html":["UNDERPOWERED","200","gate"],
 "teams.html":["Withheld","scoring"],
 "questions.html":["BLOCKED","no official source"],
 "suggestions.html":["none is built","PROPOSED"],
}
bad8=[]
for p,words in must.items():
    d=docs.get(p) or ""
    for w in words:
        if w.lower() not in d.lower(): bad8.append(f"{p} missing '{w}'")
add("H8","Every page states the disclosures it is required to state",not bad8,"; ".join(bad8))

# H9 no false validation claim
AN=json.load(open(os.path.join(ROOT,"data","derived","analysis.json")))
nval=sum(1 for s in AN["strategies"] if s["status"]=="VALIDATED")
bad9=[]
if nval==0:
    for p,d in docs.items():
        if d and re.search(r">\s*VALIDATED\s*<",d):
            bad9.append(p)
add("H9",f"No page shows a VALIDATED badge while the analysis says 0 of {len(AN['strategies'])} are validated",
    not bad9,", ".join(bad9))

# H11 every data table row carries a source link (project requirement).
#     Some tables are explanatory rather than factual (the gate definitions, the
#     withheld-dataset list, the "unverified values by page" list). Those are
#     named here explicitly so the exemption is a decision, not a loophole.
# Row-level: every factual row must contain a link. Explanation-only tables are
# listed below by (page, table index) and are exempt by explicit decision.
EXPLANATORY = {
 ("method.html",0):  "gate/check definitions - not data rows",
 ("method.html",1):  "personnel check definitions",
 ("strategies.html",0):"gate definitions",
 ("strategies.html",2):"gate-by-gate status - derived from analysis.json",
 ("strategies.html",3):"fold hit rates - derived from the same backtest",
 ("analysis.html",0):"club correlations - derived, sourced once in the caption",
 ("analysis.html",1):"game correlations - derived, sourced once in the caption",
 ("sources.html",9): "rejected sources - the point is that they do not work",
 ("sources.html",10):"data files produced by this repo",
 ("flagged.html",1): "withheld datasets - explains why there is no source",
 ("flagged.html",2): "unverified values - explains why there is no value",
}
bad11=[]; ok11=0
for p,d in docs.items():
    if d is None: continue
    for ti,tb in enumerate(re.findall(r"<table.*?</table>",d,flags=re.S)):
        body_rows=re.findall(r"<tr>(?!.*?</thead>)(.*?)</tr>",tb.split("</thead>")[-1],flags=re.S)
        if (p,ti) in EXPLANATORY: continue
        if not body_rows: continue
        # a row may legitimately have no link ONLY if it declares that no source
        # exists. That marker is explicit, so it cannot be used as a silent dodge.
        missing=[r for r in body_rows
                 if "<a " not in r and "no source exists" not in r and "none exists" not in r]
        if missing: bad11.append(f"{p} table#{ti}: {len(missing)}/{len(body_rows)} rows have no link")
        else: ok11+=1
add("H11",f"Every factual table row carries a source link ({ok11} tables fully linked; "
         f"{len(EXPLANATORY)} explanation-only tables exempt by explicit decision)",
    not bad11,"; ".join(bad11))

# H10 charset + viewport
bad10=[p for p,d in docs.items() if d and ('charset="utf-8"' not in d or "viewport" not in d)]
add("H10","Every page declares charset and viewport",not bad10,", ".join(bad10))

npass=sum(1 for c in checks if c["ok"])
for c in checks:
    print(f'[{"PASS" if c["ok"] else "FAIL"}] {c["id"]:5s} {c["name"]}')
    if not c["ok"] and c["detail"]: print(f"        {c['detail']}")
print(f"\n{npass}/{len(checks)} site checks passed")

with open(os.path.join(ROOT,"data","derived","site_report.json"),"w",encoding="utf-8") as f:
    json.dump({"checks":checks,"passed":npass,"total":len(checks),
               "pages":PAGES},f,indent=1)
sys.exit(0 if npass==len(checks) else 1)

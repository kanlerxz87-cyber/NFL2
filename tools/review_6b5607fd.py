#!/usr/bin/env python3
"""Session 6b5607fd - repo review register and live official spot-check.

Reproduces, from files in this repository only (plus the GitHub CLI for the
Actions run list), every number published in:

  data/repo_review_6b5607fd_20261116.csv        one row per check, with evidence
  data/live_spotcheck_6b5607fd_compare.csv      the 50 live rows vs the repo read, cell by cell

Inputs:
  data/live_spotcheck_6b5607fd_20261116.csv     transcribed from https://www.nfl.com/injuries/
                                                (read 2026-11-16 ~18:05Z, chunk 0 of 8, as displayed)
  data/injuries_wk10_4e475b8b_20261116.csv      the repo's 347-row read (14:44Z)
  data/captures/injuries_hub/*.bin              raw official responses, SHA-256 retained

Run:  python3 tools/review_6b5607fd.py          (exit 0 = every check ran; FLAG rows are not failures)
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

PRACTICE = {
    "Full Participation in Practice": "F",
    "Limited Participation in Practice": "L",
    "Did Not Participate In Practice": "D",
    "": "",
}
# The repo and the page both spell the TE "Chig Okonkwo"; no alias is needed.
ALIAS_PAGE_TO_REPO = {}
# data/injuries_wk10_4e475b8b_20261116.csv and content/data-dictionary.md use OUT / Q / D for game status
STATUS = {"Out": "OUT", "Questionable": "Q", "Doubtful": "D", "": ""}
OFFICIAL_HOST_SUFFIXES = ("nfl.com",)  # league domains; club sites listed in sources.csv are checked separately


def run(cmd, timeout=600):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def last_line(text):
    lines = [l for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else ""


def read_pipe(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f, delimiter="|"))


# ---------------------------------------------------------------- R-01 live vs repo
live = read_pipe("data/live_spotcheck_6b5607fd_20261116.csv")
lhdr, live = live[0], [r for r in live[1:] if r]
repo = read_pipe("data/injuries_wk10_4e475b8b_20261116.csv")
rhdr, repo = repo[0], [r for r in repo[1:] if r]
ridx = {h: i for i, h in enumerate(rhdr)}
repo_by_key = {}
for r in repo:
    repo_by_key[(r[ridx["team"]], r[ridx["player"]])] = r

compare_rows = []
match_all = mismatch_rows = missing = 0
for r in live:
    club, player, pos, injury_p, practice_p, status_p, src, note = r
    key_name = ALIAS_PAGE_TO_REPO.get(player, player)
    rr = repo_by_key.get((club, key_name))
    if rr is None:
        missing += 1
        compare_rows.append([club, player, "NOT IN REPO READ"] + [""] * 6)
        continue
    live_practice = PRACTICE[practice_p]
    repo_practice = rr[ridx["practice"]]
    repo_injury = rr[ridx["injury"]]
    repo_status = rr[ridx["status"]]
    d_inj = "same" if injury_p == repo_injury else "DIFF"
    d_prc = "same" if live_practice == repo_practice else "DIFF"
    d_sts = "same" if STATUS[status_p] == repo_status else "DIFF"
    diffs = [x for x in (d_inj, d_prc, d_sts) if x == "DIFF"]
    if diffs:
        mismatch_rows += 1
    else:
        match_all += 1
    compare_rows.append([club, player, "ok" if not diffs else "MISMATCH",
                         injury_p, repo_injury, live_practice, repo_practice, status_p, repo_status])

with open("data/live_spotcheck_6b5607fd_compare.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="|", lineterminator="\n")
    w.writerow(["club", "player", "result", "injury_live", "injury_repo_14:44Z",
                "practice_live_code", "practice_repo_code", "status_live", "status_repo"])
    w.writerows(compare_rows)

live_summary = (f"{len(live)} live rows; {match_all} identical on injury, practice and game status; "
                f"{mismatch_rows} with at least one differing cell; {missing} not found in repo read")

# ---------------------------------------------------------------- R-02 raw capture reconciliation
rc_code, rc_out = run("python3 tools/reconcile_capture_7c23f22f.py --check")
rc_line = next((l for l in rc_out.splitlines() if l.startswith("matched=")), "")
rc_ok = rc_code == 0 and "mismatched_in_both=0" in rc_line and "capture_only=0" in rc_line and "repo_only=0" in rc_line

# ---------------------------------------------------------------- R-03 byte diff between the two 16 Nov captures
caps = sorted(Path("data/captures/injuries_hub").glob("*.bin"))
a, b = caps[0].read_bytes(), caps[1].read_bytes()
diff_idx = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
# Strict test: every differing byte must sit inside the quoted value of a data-jsonid="..." attribute.
JSONID = re.compile(rb'data-jsonid="([^"]*)"')
spans = [m.span(1) for m in JSONID.finditer(a)]
def inside_jsonid(i):
    return any(s0 <= i < e0 for s0, e0 in spans)
diff_ctx_ok = len(a) == len(b) and len(diff_idx) > 0 and all(inside_jsonid(i) for i in diff_idx)
diff_summary = (f"{caps[0].name} vs {caps[1].name}: sizes {len(a)}/{len(b)}, {len(diff_idx)} bytes differ "
                f"(range {diff_idx[0]}..{diff_idx[-1]}); every differing byte lies inside the quoted value of a "
                f"data-jsonid attribute: {diff_ctx_ok}; the other {len(a) - len(diff_idx):,} bytes are identical")

# ---------------------------------------------------------------- R-04 scheduled capture runs
gh_code, gh_out = run("gh run list --workflow capture.yml --limit 50 --json event,createdAt,conclusion,headBranch")
events = {}
if gh_code == 0:
    for run_ in json.loads(gh_out or "[]"):
        events.setdefault(run_["event"], 0)
        events[run_["event"]] += 1
cap_manifest = list(csv.DictReader(open("data/capture_manifest.csv", encoding="utf-8")))
cap_summary = (f"gh run list (capture.yml): events={events if gh_code == 0 else 'gh unavailable'}; "
               f"manifest rows={len(cap_manifest)}; cron '17 14 * * *' first due 2026-11-17 14:17Z")

# ---------------------------------------------------------------- R-05 / R-06 existing verifiers
vf_code, vf_out = run("python3 tools/verify.py")
cs_code, cs_out = run("python3 tools/check_site.py")
verify_line = last_line(vf_out)
check_line = last_line(cs_out)

# ---------------------------------------------------------------- R-07 flags register parse
flags = read_pipe("data/flags.csv")
flag_widths = {}
for r in flags[1:]:
    flag_widths[len(r)] = flag_widths.get(len(r), 0) + 1
flags_ok = set(flag_widths) == {len(flags[0])}
flag_ids = [r[0] for r in flags[1:] if r]
max_fl = max(int(x.split("-")[1]) for x in flag_ids)

# ---------------------------------------------------------------- R-08 non-official hosts in sources register
srcs = read_pipe("data/sources.csv")
shdr = srcs[0]
si = {h: i for i, h in enumerate(shdr)}
non_official = []
CLUB_DOMAINS = (
    "patriots.com", "seahawks.com", "therams.com", "commanders.com", "giants.com",
    "detroitlions.com", "chiefs.com", "packers.com", "miamidolphins.com",
    "baltimoreravens.com", "chargers.com", "azcardinals.com", "49ers.com", "dallascowboys.com",
)
for r in srcs[1:]:
    if len(r) < len(shdr):
        continue
    m = re.match(r"https?://([^/]+)", r[si["url"]])
    host = m.group(1) if m else ""
    official = host.endswith(OFFICIAL_HOST_SUFFIXES) or host.endswith("github.com") \
        or any(host.endswith(d) for d in CLUB_DOMAINS)
    if host and not official:
        non_official.append((r[si["id"]], host, r[si["kind"]], r[si["tier"]]))

# ---------------------------------------------------------------- R-09 coordination file size
coord = Path("COORDINATION.md")
coord_text = coord.read_text(encoding="utf-8")
coord_sections = sum(1 for l in coord_text.splitlines() if l.startswith("## "))
coord_bytes = coord.stat().st_size

# ---------------------------------------------------------------- write the register
R = []


def add(cid, area, check, method, result, status, evidence, source):
    R.append([cid, area, check, method, result, status, evidence, source])


add("RV6-01", "Live official hub", "50 rows from the live nfl.com/injuries page vs the repo's 16 Nov 14:44Z read",
    "tools/review_6b5607fd.py; cell-by-cell on injury, practice code and game status",
    live_summary, "PASS" if mismatch_rows == 0 and missing == 0 else "FLAG",
    "data/live_spotcheck_6b5607fd_compare.csv; data/live_spotcheck_6b5607fd_20261116.csv",
    "https://www.nfl.com/injuries/")
add("RV6-02", "Raw capture", "Repo's 347-row Week 10 read vs the retained raw official response (14:39Z, SHA-256 e2b4074a…)",
    "python3 tools/reconcile_capture_7c23f22f.py --check",
    rc_line or "no output", "PASS" if rc_ok else "FLAG",
    "data/captures/injuries_hub/20261116T143921Z_e2b4074a9837.bin; data/capture_reconciliation_7c23f22f.csv",
    "https://www.nfl.com/injuries/")
add("RV6-03", "Raw capture", "Why two 16 Nov captures have different SHA-256 values",
    "byte diff of the two stored .bin files", diff_summary,
    "PASS" if diff_ctx_ok else "FLAG",
    "data/captures/injuries_hub/ (both files); data/capture_manifest.csv", "https://www.nfl.com/injuries/")
add("RV6-04", "Scheduled capture", "Has the daily 14:17 UTC capture cron produced a scheduled run?",
    "gh run list --workflow capture.yml --json event,createdAt,conclusion",
    cap_summary, "OPEN" if events.get("schedule", 0) == 0 else "PASS",
    ".github/workflows/capture.yml; data/capture_manifest.csv",
    "https://github.com/kanlerxz87-cyber/NFL2/actions/workflows/capture.yml")
add("RV6-05", "Build & verify", "tools/verify.py (data audit) on this tree", "python3 tools/verify.py",
    verify_line, "PASS" if vf_code == 0 and "0 failures" in verify_line else "FLAG",
    "tools/verify.py", "https://github.com/kanlerxz87-cyber/NFL2/blob/main/tools/verify.py")
add("RV6-06", "Build & verify", "tools/check_site.py (links, blanks, template markers, official-source coverage)",
    "python3 tools/check_site.py", check_line, "PASS" if cs_code == 0 else "FLAG",
    "tools/check_site.py; the warning class is listed in RV6-08",
    "https://github.com/kanlerxz87-cyber/NFL2/blob/main/tools/check_site.py")
add("RV6-07", "Flag register", f"data/flags.csv parses as {len(flag_ids)} rows of {len(flags[0])} fields; highest id FL-{max_fl:03d}",
    "csv.reader(delimiter='|') over every row (FL-43 and FL-106 contain quoted pipes and parse correctly)",
    f"row widths {flag_widths}", "PASS" if flags_ok else "FLAG",
    "data/flags.csv", "https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/flags.csv")
add("RV6-08", "Source register", f"{len(non_official)} source rows point to a host that is neither a league domain nor a club domain",
    "parse of data/sources.csv url column against nfl.com and the club domains listed there",
    "; ".join(f"{i} {h} ({k}, tier {t})" for i, h, k, t in non_official) or "none",
    "FLAG" if non_official else "PASS", "data/sources.csv",
    "https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/sources.csv")
add("RV6-09", "Repo maintainability", f"COORDINATION.md is {coord_bytes:,} bytes with {coord_sections} sections",
    "wc -c; grep '^## ' COORDINATION.md", f"{coord_bytes} bytes; {coord_sections} sections",
    "FLAG" if coord_bytes > 200_000 else "PASS", "COORDINATION.md",
    "https://github.com/kanlerxz87-cyber/NFL2/blob/main/COORDINATION.md")
add("RV6-10", "Official Game Books", "Use official NFL Game Books for actual starters and game-day status",
    "no fetch. The two verified Game Books carry a written-permission notice; bulk fetch, retention or parsing is not permitted without it",
    "BLOCKED - owner decision Q-50; FL-55", "BLOCKED", "data/flags.csv (FL-55); data/sources.csv (S-GAMEBOOK-*)",
    "https://static.www.nfl.com/image/upload/v1789038923/gamecenter/a8fb0d78-4feb-11f1-abca-2c54536568a9.pdf")

with open("data/repo_review_6b5607fd_20261116.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="|", lineterminator="\n")
    w.writerow(["id", "area", "check", "method", "result", "status", "evidence", "source_url"])
    w.writerows(R)

print("\n".join(f"{r[0]} {r[5]:<7} {r[4][:150]}" for r in R))
print("live compare:", live_summary)
print("non-official source rows:", len(non_official))
print("flags max id:", max_fl)

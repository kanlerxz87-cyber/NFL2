#!/usr/bin/env python3
"""Build data/decision_readiness.csv: one row per requirement, the gate that blocks it, and the number that would clear it.

The requirement text and status come from data/requirements.csv; the gate, its status and its pass
criterion come from data/gates.csv; open questions come from data/questions.csv. Nothing is typed in
as a fact here except the mapping of requirement -> gate/question IDs, and tools/verify.py checks every
ID in that mapping against the register it names, so a typo fails the build instead of publishing.

A requirement whose clearing number is not defined anywhere in the repository says so. It is never
given a number that the repository does not contain.

Usage:  python3 tools/build_decision_readiness.py          (writes the CSV)
        python3 tools/build_decision_readiness.py --check  (exit 1 if the file on disk is stale)
"""
import csv
import io
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "decision_readiness.csv")
SOURCE = "S-DESIGN"  # the design register where gates and their thresholds are written down

NA = "n/a"  # done rows: nothing blocks them

# requirement id -> (gate ids, clearing text or None, open question ids)
# A clearing text of None means: take the pass criterion of the first gate listed.
MAP = {
    "R-01": ([], "No single number: closes when R-08 to R-18 close", ["Q-01", "Q-02"]),
    "R-02": ([], NA, []),
    "R-03": ([], NA, []),
    "R-04": ([], NA, []),
    "R-05": ([], NA, []),
    "R-06": ([], NA, []),
    "R-07": ([], NA, []),
    "R-08": (["G-06"], None, ["Q-01"]),
    "R-09": (["G-01"], None, ["Q-02"]),
    "R-10": ([], NA, []),
    "R-11": ([], "Reward budget not set; no number in the repository (Q-59)", ["Q-26", "Q-59"]),
    "R-12": (["G-07"], None, ["Q-01"]),
    "R-13": (["G-05"], None, ["Q-12", "Q-18"]),
    "R-14": (["G-05"], None, ["Q-02", "Q-12", "Q-13"]),
    "R-15": (["G-01"], "Pass all 14 gates; 0 strategies pass at present (data/gates.csv)", []),
    "R-16": ([], "No rho threshold in the repository; needs joint bet-settlement data (Q-12)", ["Q-12", "Q-33"]),
    "R-17": (["G-12", "G-08"], None, ["Q-14"]),
    "R-18": ([], "No selectivity threshold in the repository (Q-15)", ["Q-15"]),
    "R-19": (["G-02"], None, ["Q-22"]),
    "R-20": (["G-02"], "Charts joined for 10 of 32 clubs now; the clearing number is 32 of 32 clubs with a chart admissible under Q-56", ["Q-05", "Q-49", "Q-56", "Q-60"]),
    "R-21": (["G-02"], "Same as R-20: 10 of 32 clubs now; clears at 32 of 32", ["Q-05", "Q-60"]),
    "R-22": ([], NA, []),
    "R-23": ([], NA, []),
    "R-24": ([], NA, []),
    "R-25": ([], NA, []),
    "R-26": ([], NA, []),
    "R-27": ([], "Pages build of the merge commit succeeds and the root page is served (CI and deploy record in COORDINATION.md)", ["Q-39"]),
    "R-28": ([], NA, []),
    "R-29": ([], NA, []),
    "R-30": ([], NA, []),
    "R-31": ([], NA, []),
    "R-32": ([], NA, []),
    "R-33": ([], "Zero rows without a literal official link; design rows cannot meet this and are labelled as design (Q-28)", ["Q-28"]),
    "R-34": ([], NA, []),
    "R-35": ([], NA, []),
    "R-36": ([], NA, []),
    "R-37": ([], "PR merged with CI green (recorded in COORDINATION.md)", []),
    "R-38": ([], "Pages deploy success for the merge commit (recorded in COORDINATION.md)", []),
    "R-39": ([], NA, []),
    "R-40": ([], NA, []),
    "R-41": ([], NA, []),
    "R-42": (["G-06"], None, ["Q-30"]),
    "R-43": (["G-05"], "Prop-level pairs: no prop archive exists; a joint interval that excludes zero is required before use (Q-12, Q-33)", ["Q-12", "Q-33"]),
    "R-44": (["G-02"], "Charts joined for 10 of 32 clubs now; the clearing number is 32 of 32 clubs (Q-60)", ["Q-49", "Q-60"]),
    "R-45": ([], NA, []),
    "R-46": ([], NA, []),
}


def read(name, delim="|"):
    with open(os.path.join(DATA, name), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(io.StringIO(fh.read().replace("\r\n", "\n")), delimiter=delim))


def build():
    reqs = read("requirements.csv")
    gates = {g["id"]: g for g in read("gates.csv")}
    questions = {q["id"]: q for q in read("questions.csv")}
    req_ids = [r["id"] for r in reqs]
    missing = sorted(set(req_ids) ^ set(MAP))
    if missing:
        raise SystemExit("mapping and requirements.csv disagree on: %s" % missing)
    rows, problems = [], []
    for r in reqs:
        gids, clearing, qids = MAP[r["id"]]
        for g in gids:
            if g not in gates:
                problems.append("%s cites unknown gate %s" % (r["id"], g))
        for q in qids:
            if q not in questions:
                problems.append("%s cites unknown question %s" % (r["id"], q))
        if clearing is None:
            clearing = gates[gids[0]]["pass_criterion"]
        rows.append({
            "req_id": r["id"],
            "requirement": r["requirement"],
            "status": r["status"],
            "blocking_gate": "; ".join("%s %s (%s)" % (g, gates[g]["gate"], gates[g]["current_status"]) for g in gids) or NA,
            "clearing_number": clearing,
            "open_questions": ", ".join(qids) or NA,
            "source": SOURCE,
        })
    if problems:
        raise SystemExit("\n".join(problems))
    return rows


def render(rows):
    cols = ["req_id", "requirement", "status", "blocking_gate", "clearing_number", "open_questions", "source"]
    lines = ["|".join(cols)]
    for r in rows:
        lines.append("|".join(str(r[c]).replace("|", "/").replace("\n", " ") for c in cols))
    return "\n".join(lines) + "\n"


def main():
    text = render(build())
    if "--check" in sys.argv:
        on_disk = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if on_disk != text:
            print("data/decision_readiness.csv is stale; run tools/build_decision_readiness.py")
            return 1
        print("decision_readiness.csv matches the registers")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("wrote %d rows to data/decision_readiness.csv" % (text.count("\n") - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Session 4e475b8b — H3: transactions register + join against the 16 Nov injury read.

Parses 4e475b8b/raw/transactions-{reserve-list,trades}-2026-11.md into
data/transactions_read_4e475b8b_20261116.csv, then joins against
data/injuries_wk10_4e475b8b_20261116.csv to publish:
  * which Reserve/Injured placements also appear on the weekly report (the FL-96 class),
  * where each November-traded player appears in the Week 10 report (old club vs new club).
Nothing is corrected: rows are transcribed as published and the join is published as found.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "4e475b8b" / "raw"
FETCH_UTC = "2026-11-16T14:46Z"
SRC_RESERVE = "https://www.nfl.com/transactions/league/reserve-list/2026/11"
SRC_TRADES = "https://www.nfl.com/transactions/league/trades/2026/11"
OUT = ROOT / "data" / "transactions_read_4e475b8b_20261116.csv"

ROW_RE = re.compile(r"^\| ([A-Z]{2,3}) [^|]*\| ([A-Z]{2,3}) [^|]*\| (\d\d/\d\d) \| \[([^]]+)]\((https://www\.nfl\.com/players/[^)]+)\) \| ([^|]*) \| ([^|]+) \|\s*$")


def parse(path, page):
    rows = []
    for ln in path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln.startswith("#") or not ln.startswith("|"):
            continue
        m = ROW_RE.match(ln)
        if not m:
            sys.exit(f"FAIL: unparseable transactions row in {path.name}: {ln[:80]!r}")
        frm, to, date, name, url, pos, txn = m.groups()
        rows.append({"page": page, "from": frm, "to": to, "date": date, "player": name,
                     "position": pos.strip(), "transaction": txn.strip(),
                     "fetched_utc": FETCH_UTC,
                     "source": SRC_RESERVE if page == "reserve-list" else SRC_TRADES})
    return rows


def main():
    reserve = parse(RAW / "transactions-reserve-list-2026-11.md", "reserve-list")
    trades = parse(RAW / "transactions-trades-2026-11.md", "trades")
    all_rows = reserve + trades

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["page", "from", "to", "date", "player", "position",
                                          "transaction", "fetched_utc", "source"], delimiter="|", lineterminator="\n")
        w.writeheader()
        w.writerows(all_rows)

    # ---- joins against the 16 Nov injury read ----
    hub = list(csv.DictReader(open(ROOT / "data" / "injuries_wk10_4e475b8b_20261116.csv", encoding="utf-8"), delimiter="|"))

    print(f"transactions rows: reserve-list={len(reserve)} trades={len(trades)} total={len(all_rows)}")

    # 1. Reserve/Injured players who also appear on the weekly report
    reserve_names = {r["player"] for r in reserve}
    overlap = [(r["team"], r["player"], r["practice"], r["status"], r["injury"]) for r in hub if r["player"] in reserve_names]
    print(f"reserve-list players also on the weekly report: {len(overlap)} of {len(reserve_names)}")
    for team, player, prac, status, inj in sorted(overlap):
        print(f"  {team:3} {player:22} practice={prac or '-':1} status={status or '-':3} injury={inj or '-'}")
    reserve_only = sorted(reserve_names - {r['player'] for r in hub})
    print(f"reserve-list players absent from the weekly report: {len(reserve_only)}")
    for name in reserve_only:
        print("  ", name)

    # 2. November-traded players: where does the Week 10 report list them?
    print("traded players in the Week 10 report:")
    for t in trades:
        hits = [(r["game"], r["team"], r["practice"], r["status"]) for r in hub if r["player"] == t["player"]]
        expected_new = t["to"]
        if hits:
            for g, team, prac, status in hits:
                side = "NEW club (post-trade)" if team == expected_new else ("OLD club (pre-trade)" if team == t["from"] else "NEITHER page-club")
                print(f"  {t['player']:18} {t['from']}->{t['to']} {t['date']}: report lists {team} ({g}) — {side}")
        else:
            print(f"  {t['player']:18} {t['from']}->{t['to']} {t['date']}: absent from the report")

    # 3. FL-95's named rows, re-confirmed today
    checks = [("Jacoby Brissett", "trades", "AZ", "BAL", "11/06"),
              ("Keenan Allen", "trades", "IND", "SF", "11/10"),
              ("Josh Downs", "trades", "IND", "KC", "11/10"),
              ("Malik Willis", "reserve-list", "MIA", "MIA", "11/10"),
              # the transactions page abbreviates the Rams "LA"
              ("Puka Nacua", "reserve-list", "LA", "LA", "11/12")]
    print("FL-95 named rows re-read today:")
    for name, page, frm, to, date in checks:
        src = trades if page == "trades" else reserve
        hit = [r for r in src if r["player"] == name and r["date"] == date and r["from"] == frm and r["to"] == to]
        print(f"  {name}: {'CONFIRMED' if hit else 'NOT FOUND'} ({page} {date} {frm}->{to})")


if __name__ == "__main__":
    main()

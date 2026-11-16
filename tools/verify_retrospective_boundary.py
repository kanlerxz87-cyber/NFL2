#!/usr/bin/env python3
"""Guard the S2268 retrospective-score page from leaderboard/reward framing."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "s2268" / "competition.html"


class PageReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text: list[str] = []
        self.headers: list[str] = []
        self._in_th = False
        self._in_h1 = False
        self.h1 = ""

    def handle_starttag(self, tag, attrs):
        if tag == "th":
            self._in_th = True
        elif tag == "h1":
            self._in_h1 = True

    def handle_endtag(self, tag):
        if tag == "th":
            self._in_th = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        self.text.append(text)
        if self._in_th:
            self.headers.append(text.lower())
        if self._in_h1:
            self.h1 += text


def main() -> int:
    if not PAGE.exists():
        print(f"FAIL missing generated page: {PAGE.relative_to(ROOT)}")
        return 1
    source = PAGE.read_text(encoding="utf-8")
    page = PageReader()
    page.feed(source)
    title = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
    title_text = re.sub(r"<[^>]+>", "", title.group(1)).replace("&amp;", "&") if title else ""
    text = " ".join(page.text).lower()
    checks = []
    checks.append(("title and h1 clearly classify this as retrospective research",
                   "retrospective strategy audit (research)" in title_text.lower()
                   and "retrospective strategy audit (research)" in page.h1.lower()))
    checks.append(("page explicitly labels the results retrospective and research-only",
                   "retrospective research only" in text and "historical holdout" in text))
    forbidden_words = re.compile(r"\b(?:leaderboard|rewards?|stake|rank(?:ed|ing)?|roi|clv|max_drawdown)\b", re.I)
    checks.append(("no leaderboard, rank, reward, stake, or betting-return framing", not forbidden_words.search(text)))
    forbidden_columns = {"rank", "tier", "reward earned", "stake multiplier", "roi units per 100",
                         "closing line value", "max drawdown"}
    checks.append(("historical table excludes ranking, reward, stake and return columns",
                   not forbidden_columns.intersection(page.headers)
                   and {"hit rate", "log loss", "binomial p"}.issubset(set(page.headers))))
    for label, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'} {label}")
    if not all(ok for _, ok in checks):
        return 1
    print(f"retrospective boundary: {len(checks)} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

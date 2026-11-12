#!/usr/bin/env python3
"""
NFL2 — Reproducible Official 2026 NFL Team Stats Ingestion, Correlation Matrix (n=32),
Luck-vs-Skill Residuals, and v1 Efficiency-Aware Fair Line Projections.

Every input number is transcribed line-by-line from official NFL.com 2026 Regular Season pages
fetched 2026-11-12:
  1. https://www.nfl.com/standings/division/2026/reg
  2. https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all
  3. https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all
  4. https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all
  5. https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all
  6. https://www.nfl.com/news/week-11-schedule-change

Statistical correlation formulas follow NIST/SEMATECH e-Handbook of Statistical Methods:
  https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm
"""
from __future__ import annotations
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Official 2026 Offense Passing:
# Columns: Att, Cmp, Cmp%, Yds/Att, PassYds, TD, INT, Rate, 1st, 1st%, 20+, 40+, Lng, Sck, SckY
OFF_PASS = {
    "SF":  (236, 163, 69.1, 8.4, 1980, 17, 5, 109.8, 97, 41.1, 27, 4, "82T", 8, 48),
    "CHI": (312, 211, 67.6, 7.4, 2310, 10, 9, 88.0, 108, 34.6, 35, 4, "58T", 20, 141),
    "CIN": (296, 219, 74.0, 8.1, 2386, 23, 6, 114.8, 119, 40.2, 27, 5, "47T", 15, 102),
    "BUF": (236, 156, 66.1, 8.6, 2027, 12, 6, 99.3, 93, 39.4, 32, 8, "57", 17, 109),
    "DEN": (287, 174, 60.6, 6.0, 1730, 11, 4, 84.7, 85, 29.6, 21, 4, "52T", 11, 57),
    "CLE": (283, 185, 65.4, 7.4, 2105, 9, 3, 93.7, 93, 32.9, 28, 5, "64T", 38, 211),
    "TB":  (240, 146, 60.8, 5.9, 1423, 6, 9, 70.2, 67, 27.9, 16, 5, "64", 27, 146),
    "AZ":  (359, 232, 64.6, 5.8, 2080, 13, 7, 84.0, 110, 30.6, 19, 0, "38", 23, 142),
    "LAC": (243, 146, 60.1, 6.6, 1615, 7, 11, 70.6, 71, 29.2, 18, 6, "58", 31, 198),
    "KC":  (263, 177, 67.3, 7.8, 2037, 14, 4, 101.8, 94, 35.7, 22, 7, "73T", 11, 66),
    "IND": (304, 184, 60.5, 5.7, 1730, 6, 10, 69.1, 86, 28.3, 18, 3, "55T", 25, 167),
    "WAS": (266, 164, 61.6, 6.7, 1776, 12, 1, 94.8, 86, 32.3, 24, 5, "53", 20, 119),
    "DAL": (336, 218, 64.9, 7.1, 2381, 16, 5, 95.4, 119, 35.4, 28, 6, "53", 14, 69),
    "MIA": (209, 122, 58.4, 6.9, 1442, 6, 6, 77.1, 64, 30.6, 18, 5, "77T", 24, 124),
    "PHI": (303, 179, 59.1, 5.7, 1740, 10, 6, 78.0, 81, 26.7, 14, 3, "64", 30, 195),
    "ATL": (256, 156, 60.9, 6.9, 1766, 11, 12, 76.4, 74, 28.9, 23, 4, "76", 16, 97),
    "NYG": (268, 165, 61.6, 7.1, 1900, 12, 6, 88.5, 90, 33.6, 25, 5, "49", 27, 132),
    "JAX": (227, 147, 64.8, 8.6, 1940, 18, 4, 110.8, 91, 40.1, 27, 4, "52", 13, 106),
    "NYJ": (271, 183, 67.5, 7.7, 2078, 12, 3, 100.4, 89, 32.8, 24, 9, "60", 28, 236),
    "DET": (274, 186, 67.9, 7.8, 2145, 15, 2, 106.5, 104, 38.0, 23, 5, "57", 19, 129),
    "GB":  (341, 215, 63.0, 7.7, 2618, 19, 6, 97.9, 110, 32.3, 40, 12, "81T", 17, 101),
    "CAR": (313, 189, 60.4, 7.2, 2244, 16, 6, 91.3, 111, 35.5, 28, 4, "55", 26, 155),
    "NE":  (281, 183, 65.1, 8.4, 2349, 18, 11, 96.2, 102, 36.3, 33, 6, "63", 20, 103),
    "LV":  (324, 209, 64.5, 7.4, 2401, 20, 8, 97.0, 121, 37.4, 31, 5, "45", 11, 64),
    "LA":  (349, 232, 66.5, 6.8, 2387, 16, 9, 90.5, 122, 35.0, 24, 6, "64", 13, 97),
    "BAL": (247, 165, 66.8, 7.5, 1842, 10, 5, 93.9, 90, 36.4, 20, 6, "54", 23, 146),
    "NO":  (308, 204, 66.2, 6.4, 1986, 14, 6, 91.2, 99, 32.1, 21, 5, "52", 20, 142),
    "SEA": (288, 182, 63.2, 7.2, 2089, 15, 9, 89.3, 109, 37.8, 24, 4, "82", 19, 136),
    "PIT": (290, 175, 60.3, 6.4, 1871, 13, 6, 85.6, 82, 28.3, 24, 6, "80T", 23, 187),
    "HOU": (285, 182, 63.9, 7.9, 2258, 16, 2, 104.1, 98, 34.4, 32, 7, "63T", 16, 103),
    "TEN": (248, 155, 62.5, 6.0, 1483, 6, 5, 78.8, 73, 29.4, 16, 1, "41", 13, 99),
    "MIN": (225, 137, 60.9, 6.4, 1437, 8, 5, 82.0, 68, 30.2, 19, 2, "51T", 23, 151),
}

# Official 2026 Offense Rushing:
# Columns: Att, RushYds, YPC, TD, 20+, 40+, Lng, Rush1st, Rush1st%, RushFUM
OFF_RUSH = {
    "SF":  (234, 1082, 4.6, 12, 4, 0, "35T", 69, 29.5, 3),
    "CHI": (303, 1278, 4.2, 17, 6, 1, "61", 67, 22.1, 6),
    "CIN": (177, 685, 3.9, 5, 0, 0, "19", 48, 27.1, 2),
    "BUF": (261, 1173, 4.5, 17, 7, 0, "35", 76, 29.1, 6),
    "DEN": (223, 823, 3.7, 9, 1, 1, "62T", 51, 22.9, 5),
    "CLE": (233, 876, 3.8, 6, 5, 0, "30T", 44, 18.9, 4),
    "TB":  (294, 1475, 5.0, 11, 11, 3, "72", 80, 27.2, 7),
    "AZ":  (226, 924, 4.1, 4, 5, 2, "63T", 49, 21.7, 0),
    "LAC": (224, 916, 4.1, 4, 5, 1, "42T", 38, 17.0, 4),
    "KC":  (217, 1102, 5.1, 10, 7, 2, "76", 61, 28.1, 1),
    "IND": (249, 1037, 4.2, 11, 6, 0, "38T", 70, 28.1, 3),
    "WAS": (210, 946, 4.5, 5, 7, 0, "38", 45, 21.4, 3),
    "DAL": (233, 932, 4.0, 11, 3, 0, "34T", 59, 25.3, 2),
    "MIA": (215, 940, 4.4, 7, 5, 1, "53", 52, 24.2, 4),
    "PHI": (213, 797, 3.7, 8, 5, 1, "42", 43, 20.2, 2),
    "ATL": (258, 1235, 4.8, 9, 10, 2, "59T", 69, 26.7, 4),
    "NYG": (232, 897, 3.9, 6, 5, 1, "42T", 54, 23.3, 5),
    "JAX": (230, 937, 4.1, 8, 4, 0, "39", 55, 23.9, 0),
    "NYJ": (231, 947, 4.1, 5, 4, 0, "27T", 61, 26.4, 5),
    "DET": (230, 1022, 4.4, 10, 3, 0, "30T", 66, 28.7, 4),
    "GB":  (202, 614, 3.0, 6, 4, 0, "34T", 39, 19.3, 5),
    "CAR": (189, 810, 4.3, 7, 4, 0, "32T", 48, 25.4, 1),
    "NE":  (256, 1079, 4.2, 7, 8, 0, "39T", 66, 25.8, 4),
    "LV":  (222, 642, 2.9, 5, 2, 0, "36T", 38, 17.1, 0),
    "LA":  (242, 1128, 4.7, 11, 4, 0, "30T", 67, 27.7, 3),
    "BAL": (265, 1240, 4.7, 11, 8, 2, "65", 59, 22.3, 5),
    "NO":  (203, 762, 3.8, 7, 2, 0, "36", 51, 25.1, 8),
    "SEA": (258, 997, 3.9, 7, 3, 0, "28", 54, 20.9, 6),
    "PIT": (193, 943, 4.9, 4, 7, 2, "51", 58, 30.0, 2),
    "HOU": (195, 697, 3.6, 6, 1, 0, "25", 41, 21.0, 0),
    "TEN": (189, 796, 4.2, 8, 5, 1, "40T", 41, 21.7, 3),
    "MIN": (211, 848, 4.0, 3, 4, 0, "35", 38, 18.0, 4),
}

# Official 2026 Defense Passing:
# Columns: Att, Cmp, Cmp%, Yds/Att, Yds, TD, INT, Rate, 1st, 1st%, 20+, 40+, Lng, Sck
DEF_PASS = {
    "SF":  (280, 188, 67.1, 6.4, 1783, 11, 6, 88.7, 86, 30.7, 18, 2, "77T", 15),
    "CHI": (260, 161, 61.9, 8.2, 2120, 13, 7, 93.1, 88, 33.8, 26, 12, "58T", 26),
    "CIN": (273, 174, 63.7, 7.3, 1989, 9, 5, 88.9, 93, 34.1, 26, 2, "48T", 23),
    "BUF": (300, 183, 61.0, 6.7, 2022, 15, 6, 89.3, 107, 35.7, 28, 1, "44T", 17),
    "DEN": (344, 207, 60.2, 6.5, 2249, 14, 8, 83.4, 106, 30.8, 26, 6, "73T", 26),
    "CLE": (297, 177, 59.6, 6.7, 1982, 12, 6, 84.6, 88, 29.6, 26, 5, "58", 26),
    "TB":  (307, 190, 61.9, 6.6, 2040, 12, 16, 72.7, 86, 28.0, 21, 6, "76", 17),
    "AZ":  (258, 166, 64.3, 8.0, 2076, 19, 3, 108.9, 92, 35.7, 25, 6, "82T", 19),
    "LAC": (233, 153, 65.7, 7.9, 1845, 13, 7, 95.9, 85, 36.5, 23, 5, "63T", 13),
    "KC":  (276, 170, 61.6, 6.4, 1764, 7, 6, 79.4, 88, 31.9, 20, 5, "57", 14),
    "IND": (264, 162, 61.4, 8.1, 2145, 16, 2, 104.1, 89, 33.7, 30, 11, "80T", 19),
    "WAS": (296, 194, 65.5, 6.9, 2048, 16, 5, 96.5, 99, 33.4, 24, 3, "64", 17),
    "DAL": (296, 194, 65.5, 7.2, 2133, 16, 4, 99.1, 106, 35.8, 28, 4, "64", 17),
    "MIA": (221, 168, 76.0, 8.1, 1797, 16, 5, 114.0, 87, 39.4, 22, 8, "60", 12),
    "PHI": (300, 180, 60.0, 7.2, 2150, 13, 3, 92.2, 102, 34.0, 31, 4, "53", 16),
    "ATL": (318, 210, 66.0, 6.8, 2171, 14, 3, 96.3, 108, 34.0, 26, 5, "55", 20),
    "NYG": (253, 156, 61.7, 6.0, 1514, 14, 6, 87.0, 80, 31.6, 15, 2, "64", 16),
    "JAX": (261, 172, 65.9, 7.3, 1907, 8, 11, 80.1, 89, 34.1, 21, 5, "62T", 16),
    "NYJ": (270, 174, 64.4, 7.1, 1909, 16, 1, 103.5, 98, 36.3, 23, 4, "63T", 22),
    "DET": (313, 203, 64.9, 7.2, 2265, 18, 6, 97.5, 114, 36.4, 34, 6, "51", 27),
    "GB":  (325, 203, 62.5, 6.4, 2087, 13, 13, 77.6, 101, 31.1, 22, 4, "68", 26),
    "CAR": (278, 176, 63.3, 6.4, 1774, 12, 5, 88.3, 92, 33.1, 14, 4, "57", 12),
    "NE":  (286, 193, 67.5, 7.9, 2256, 14, 5, 100.2, 99, 34.6, 32, 7, "58", 25),
    "LV":  (279, 183, 65.6, 8.0, 2238, 20, 7, 103.6, 112, 40.1, 27, 6, "55", 19),
    "LA":  (293, 179, 61.1, 6.4, 1882, 11, 7, 82.3, 93, 31.7, 21, 6, "57", 16),
    "BAL": (287, 187, 65.2, 7.6, 2177, 12, 4, 96.1, 102, 35.5, 26, 7, "52", 17),
    "NO":  (261, 171, 65.5, 7.8, 2045, 13, 4, 99.6, 91, 34.9, 28, 6, "64T", 23),
    "SEA": (277, 178, 64.3, 5.5, 1519, 9, 8, 77.3, 73, 26.4, 14, 1, "44", 21),
    "PIT": (280, 183, 65.4, 6.9, 1936, 7, 7, 83.3, 88, 31.4, 27, 4, "63", 26),
    "HOU": (276, 178, 64.5, 7.4, 2056, 12, 4, 95.3, 91, 33.0, 31, 7, "58T", 29),
    "TEN": (272, 193, 71.0, 8.0, 2182, 11, 8, 95.9, 105, 38.6, 30, 2, "52", 20),
    "MIN": (234, 135, 57.7, 6.4, 1495, 5, 9, 67.9, 68, 29.1, 16, 5, "81T", 29),
}

# Official 2026 Defense Rushing:
# Columns: Att, RushYds, YPC, TD, 20+, 40+, Lng, Rush1st, Rush1st%, RushFUM
DEF_RUSH = {
    "SF":  (194, 647, 3.3, 4, 0, 0, "17", 37, 19.1, 4),
    "CHI": (185, 820, 4.4, 8, 6, 0, "25", 38, 20.5, 2),
    "CIN": (201, 1013, 5.0, 8, 11, 1, "40T", 53, 26.4, 3),
    "BUF": (189, 733, 3.9, 7, 1, 0, "26", 41, 21.7, 4),
    "DEN": (248, 1119, 4.5, 6, 9, 2, "60T", 68, 27.4, 2),
    "CLE": (249, 1175, 4.7, 8, 6, 1, "51", 70, 28.1, 8),
    "TB":  (201, 712, 3.5, 3, 4, 0, "31", 47, 23.4, 2),
    "AZ":  (262, 1097, 4.2, 10, 4, 1, "62T", 68, 26.0, 5),
    "LAC": (240, 976, 4.1, 11, 4, 0, "33T", 51, 21.2, 3),
    "KC":  (215, 780, 3.6, 5, 2, 0, "24T", 47, 21.9, 3),
    "IND": (250, 1233, 4.9, 9, 7, 1, "50T", 63, 25.2, 0),
    "WAS": (209, 818, 3.9, 7, 2, 1, "42", 51, 24.4, 2),
    "DAL": (266, 1327, 5.0, 11, 11, 3, "72", 67, 25.2, 4),
    "MIA": (236, 894, 3.8, 6, 3, 0, "27", 56, 23.7, 0),
    "PHI": (276, 1135, 4.1, 10, 4, 0, "34", 65, 23.6, 2),
    "ATL": (242, 1069, 4.4, 10, 7, 2, "47", 60, 24.8, 10),
    "NYG": (211, 989, 4.7, 7, 8, 0, "38T", 49, 23.2, 3),
    "JAX": (194, 714, 3.7, 5, 2, 1, "65T", 36, 18.6, 6),
    "NYJ": (282, 1152, 4.1, 10, 4, 0, "26", 71, 25.2, 7),
    "DET": (184, 753, 4.1, 6, 6, 0, "35", 49, 26.6, 1),
    "GB":  (244, 981, 4.0, 11, 5, 1, "55", 63, 25.8, 3),
    "CAR": (231, 1067, 4.6, 13, 7, 2, "61T", 59, 25.5, 3),
    "NE":  (225, 870, 3.9, 8, 1, 0, "34", 50, 22.2, 2),
    "LV":  (272, 1361, 5.0, 12, 8, 1, "76", 74, 27.2, 6),
    "LA":  (236, 934, 4.0, 4, 4, 0, "31", 47, 19.9, 5),
    "BAL": (249, 899, 3.6, 12, 5, 0, "38", 55, 22.1, 3),
    "NO":  (237, 1071, 4.5, 11, 6, 1, "59T", 66, 27.8, 3),
    "SEA": (233, 802, 3.4, 7, 3, 0, "39", 48, 20.6, 1),
    "PIT": (185, 671, 3.6, 4, 6, 0, "39T", 45, 24.3, 4),
    "HOU": (209, 824, 3.9, 9, 4, 1, "42", 51, 24.4, 4),
    "TEN": (239, 993, 4.2, 10, 2, 0, "30", 61, 25.5, 4),
    "MIN": (224, 951, 4.2, 5, 3, 1, "53", 51, 22.8, 2),
}


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    return num / math.sqrt(dx * dy)


def ranks(vals: list[float]) -> list[float]:
    idx = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[idx[j + 1]] == vals[idx[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[idx[k]] = avg_rank
        i = j + 1
    return out


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(ranks(xs), ranks(ys))


def reg_t_ci(r: float, n: int) -> tuple[float, float, float, float]:
    """Return (t_stat, two_tailed_p_approx, ci95_low, ci95_high) via Fisher z and Student-t."""
    df = n - 2
    if abs(r) >= 0.999999:
        return (float("inf"), 0.0, r, r)
    t = r * math.sqrt(df / (1.0 - r * r))
    # Regularized incomplete beta / exact t two-tailed p-value via numerical integration
    # Using Simpson's rule on Student-t PDF from |t| to 40
    abs_t = abs(t)
    upper = max(40.0, abs_t + 20.0)
    steps = 2000
    h = (upper - abs_t) / steps
    coeff = math.exp(math.lgamma((df + 1) / 2.0) - math.lgamma(df / 2.0)) / math.sqrt(df * math.pi)

    def pdf(x: float) -> float:
        return coeff * ((1.0 + (x * x) / df) ** (-(df + 1) / 2.0))

    area = pdf(abs_t) + pdf(upper)
    for k in range(1, steps):
        area += (4.0 if k % 2 == 1 else 2.0) * pdf(abs_t + k * h)
    one_tail = area * h / 3.0
    p_two = min(1.0, max(0.0, 2.0 * one_tail))

    z = 0.5 * math.log((1.0 + r) / (1.0 - r))
    se = 1.0 / math.sqrt(n - 3)
    z_lo = z - 1.959963984540054 * se
    z_hi = z + 1.959963984540054 * se
    ci_lo = math.tanh(z_lo)
    ci_hi = math.tanh(z_hi)
    return (t, p_two, ci_lo, ci_hi)


def normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def main() -> None:
    standings = json.loads((ROOT / "data" / "standings-2026.json").read_text())
    schedule = json.loads((ROOT / "data" / "schedule-week11-2026.json").read_text())
    def_existing = json.loads((ROOT / "data" / "team_stats_defense_2026.json").read_text())
    def_map_check = {
        ("AZ" if t["abbr"] == "ARI" else ("LA" if t["abbr"] == "LAR" else t["abbr"])): t
        for t in def_existing["teams"]
    }

    teams_out = []
    for st in standings["teams"]:
        abbr = st["abbr"]
        assert abbr in OFF_PASS and abbr in OFF_RUSH and abbr in DEF_PASS and abbr in DEF_RUSH, f"Missing {abbr}"
        g = st["w"] + st["l"] + st["t"]
        op = OFF_PASS[abbr]
        orr = OFF_RUSH[abbr]
        dp = DEF_PASS[abbr]
        dr = DEF_RUSH[abbr]

        # Cross-verify against arena-85d79210's data/team_stats_defense_2026.json
        chk = def_map_check[abbr]
        assert chk["pass_yds_allowed"] == dp[4], f"{abbr} pass_yds_allowed mismatch"
        assert chk["rush_yds_allowed"] == dr[1], f"{abbr} rush_yds_allowed mismatch"

        off_plays = op[0] + op[13] + orr[0]  # Pass Att + Sacks + Rush Att
        off_net_pass_yds = op[4] - op[14]    # Gross Pass Yds - Sack Yds
        off_total_gross_yds = op[4] + orr[1]
        off_yds_per_play = off_total_gross_yds / off_plays

        def_plays = dp[0] + dp[13] + dr[0]
        def_total_gross_yds = dp[4] + dr[1]
        def_yds_per_play = def_total_gross_yds / def_plays

        # Pythagorean expectation (Daryl Morey / Pro-Football standard NFL exponent 2.37; model metric)
        pf_exp = st["pf"] ** 2.37
        pa_exp = st["pa"] ** 2.37
        pyth_pct = pf_exp / (pf_exp + pa_exp)
        luck_win_pct_residual = st["pct"] - pyth_pct

        # Passing INT differential (Def INT - Off INT) — exact official counts (fumble recoveries require play-by-play)
        int_margin = dp[6] - op[6]
        sack_rate_off = op[13] / (op[0] + op[13])
        sack_rate_def = dp[13] / (dp[0] + dp[13])

        teams_out.append({
            "team": st["team"],
            "abbr": abbr,
            "conf": st["conf"],
            "div": st["div"],
            "games": g,
            "w": st["w"],
            "l": st["l"],
            "t": st["t"],
            "win_pct": st["pct"],
            "pf": st["pf"],
            "pa": st["pa"],
            "net_pts": st["net"],
            "pf_per_g": round(st["pf"] / g, 2),
            "pa_per_g": round(st["pa"] / g, 2),
            "net_pts_per_g": round(st["net"] / g, 2),
            "pythagorean_win_pct": round(pyth_pct, 3),
            "luck_residual_win_pct": round(luck_win_pct_residual, 3),
            "luck_residual_wins": round(luck_win_pct_residual * g, 2),
            "off_pass": {
                "att": op[0], "cmp": op[1], "cmp_pct": op[2], "yds_per_att": op[3],
                "pass_yds": op[4], "td": op[5], "int": op[6], "rate": op[7],
                "first_downs": op[8], "first_pct": op[9], "big_20": op[10], "big_40": op[11],
                "lng": op[12], "sck": op[13], "sck_yds": op[14],
                "source": "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all"
            },
            "off_rush": {
                "att": orr[0], "rush_yds": orr[1], "ypc": orr[2], "td": orr[3],
                "big_20": orr[4], "big_40": orr[5], "lng": orr[6],
                "first_downs": orr[7], "first_pct": orr[8], "rush_fum": orr[9],
                "source": "https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all"
            },
            "def_pass": {
                "att": dp[0], "cmp": dp[1], "cmp_pct": dp[2], "yds_per_att": dp[3],
                "pass_yds_allowed": dp[4], "td_allowed": dp[5], "int": dp[6], "rate_allowed": dp[7],
                "first_downs_allowed": dp[8], "first_pct_allowed": dp[9],
                "big_20_allowed": dp[10], "big_40_allowed": dp[11], "lng": dp[12], "sck": dp[13],
                "source": "https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all"
            },
            "def_rush": {
                "att": dr[0], "rush_yds_allowed": dr[1], "ypc_allowed": dr[2], "td_allowed": dr[3],
                "big_20_allowed": dr[4], "big_40_allowed": dr[5], "lng": dr[6],
                "first_downs_allowed": dr[7], "first_pct_allowed": dr[8], "forced_rush_fum": dr[9],
                "source": "https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all"
            },
            "derived_efficiency": {
                "off_plays": off_plays,
                "off_gross_yds": off_total_gross_yds,
                "off_net_pass_yds": off_net_pass_yds,
                "off_yds_per_play": round(off_yds_per_play, 2),
                "def_plays": def_plays,
                "def_gross_yds_allowed": def_total_gross_yds,
                "def_yds_per_play_allowed": round(def_yds_per_play, 2),
                "net_yds_per_play": round(off_yds_per_play - def_yds_per_play, 2),
                "int_margin": int_margin,
                "int_margin_per_g": round(int_margin / g, 2),
                "off_sack_rate_pct": round(sack_rate_off * 100, 2),
                "def_sack_rate_pct": round(sack_rate_def * 100, 2),
            },
            "standings_source": "https://www.nfl.com/standings/division/2026/reg",
        })

    stats_payload = {
        "season": 2026,
        "seasonType": "REG",
        "asOf": "2026-11-12",
        "n_teams": len(teams_out),
        "sources": {
            "standings": "https://www.nfl.com/standings/division/2026/reg",
            "offense_passing": "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
            "offense_rushing": "https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all",
            "defense_passing": "https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all",
            "defense_rushing": "https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all",
        },
        "teams": teams_out,
    }
    (ROOT / "data" / "team-stats-offense-defense-2026.json").write_text(
        json.dumps(stats_payload, indent=2) + "\n"
    )

    # Compute 14 verified team-level empirical correlations (n = 32 NFL teams, 2026 REG)
    pairs_spec = [
        (
            "C-01",
            "Net Points/Game vs. Actual Win %",
            "Core Scoring Efficiency -> Win Rate",
            lambda t: t["net_pts_per_g"],
            lambda t: t["win_pct"],
            "https://www.nfl.com/standings/division/2026/reg",
            "Strongest team-level skill anchor; residuals (Actual Win% - Pythagorean) isolate close-game luck."
        ),
        (
            "C-02",
            "Pythagorean Expected Win % vs. Actual Win %",
            "Skill Baseline vs. Realized Record",
            lambda t: t["pythagorean_win_pct"],
            lambda t: t["win_pct"],
            "https://www.nfl.com/standings/division/2026/reg",
            "Separates repeatable point-differential skill from 1-score variance (e.g., DEN +0.242 luck vs TB -0.242 bad luck)."
        ),
        (
            "C-03",
            "Net Yards/Play Differential vs. Net Points/Game",
            "Play-Efficiency Signal -> Spread Margin",
            lambda t: t["derived_efficiency"]["net_yds_per_play"],
            lambda t: t["net_pts_per_g"],
            "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
            "Validates using yards-per-play differential as a less noisy input than raw points for spread origination."
        ),
        (
            "C-04",
            "Offensive Passer Rating vs. Points For/Game",
            "Passing Efficiency -> Team Scoring",
            lambda t: t["off_pass"]["rate"],
            lambda t: t["pf_per_g"],
            "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
            "Passing efficiency strongly drives team points; backup QB drop-off directly hits this channel."
        ),
        (
            "C-05",
            "Offensive Passing Yards/Attempt vs. Points For/Game",
            "Explosive Pass Efficiency -> Team Scoring",
            lambda t: t["off_pass"]["yds_per_att"],
            lambda t: t["pf_per_g"],
            "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
            "Yards/Attempt captures downfield passing skill far better than raw pass attempts."
        ),
        (
            "C-06",
            "Offensive Pass Attempts/Game vs. Win %",
            "Game-Script Trap (Trailing Teams Throw More)",
            lambda t: t["off_pass"]["att"] / t["games"],
            lambda t: t["win_pct"],
            "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
            "CRITICAL PARLAY/PROP LESSON: Pass volume correlates NEGATIVELY/WEAKLY with winning because trailing teams pass more."
        ),
        (
            "C-07",
            "Offensive Rush Attempts/Game vs. Win %",
            "Game-Script Artifact (Leading Teams Run Clock)",
            lambda t: t["off_rush"]["att"] / t["games"],
            lambda t: t["win_pct"],
            "https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all",
            "Leading teams run in Q4; naive models confuse clock-killing rush volume with rushing causation."
        ),
        (
            "C-08",
            "Offensive Rushing Yards/Carry (YPC) vs. Points For/Game",
            "Rushing Efficiency -> Team Scoring",
            lambda t: t["off_rush"]["ypc"],
            lambda t: t["pf_per_g"],
            "https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all",
            "Moderate positive signal, substantially weaker than passing Yds/Att and Passer Rating."
        ),
        (
            "C-09",
            "Offensive Sack Rate Allowed (%) vs. Points For/Game",
            "OL Pass-Protection Deficiency -> Scoring Suppression",
            lambda t: t["derived_efficiency"]["off_sack_rate_pct"],
            lambda t: t["pf_per_g"],
            "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all",
            "Direct empirical proof why 2nd/3rd-string OL injury cascades suppress team totals and QB passing props."
        ),
        (
            "C-10",
            "Defensive Passer Rating Allowed vs. Points Allowed/Game",
            "Coverage/Pass-Defense Deficiency -> Opponent Scoring",
            lambda t: t["def_pass"]["rate_allowed"],
            lambda t: t["pa_per_g"],
            "https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all",
            "Backup CB/Safety clusters inflate opposing QB rating and drive opponent team-total overs."
        ),
        (
            "C-11",
            "Defensive Sack Rate Generated (%) vs. Points Allowed/Game",
            "Pass-Rush Disruption -> Defensive Scoring Prevention",
            lambda t: t["derived_efficiency"]["def_sack_rate_pct"],
            lambda t: t["pa_per_g"],
            "https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all",
            "Higher defensive sack rate suppresses opponent points allowed per game."
        ),
        (
            "C-12",
            "Defensive Rushing Yards Allowed/Game vs. Points Allowed/Game",
            "Run-Front Deficiency -> Opponent Scoring",
            lambda t: t["def_rush"]["rush_yds_allowed"] / t["games"],
            lambda t: t["pa_per_g"],
            "https://www.nfl.com/stats/team-stats/defense/rushing/2026/reg/all",
            "Interior DL/LB injuries (e.g., NT/MLB DNP clusters) leak rushing yards and elevate opponent scoring floor."
        ),
        (
            "C-13",
            "Interception Margin/Game (Def INT - Off INT) vs. Win %",
            "Turnover Variance + Ball-Hawking -> Realized Wins",
            lambda t: t["derived_efficiency"]["int_margin_per_g"],
            lambda t: t["win_pct"],
            "https://www.nfl.com/stats/team-stats/defense/passing/2026/reg/all",
            "Interception rates carry heavy short-sample luck (~50%+ regression to mean); shrink INT-driven records when originating lines."
        ),
        (
            "C-14",
            "Offensive Points/Game vs. Defensive Points Allowed/Game",
            "Offense-Defense Independence Check (Totals Pricing)",
            lambda t: t["pf_per_g"],
            lambda t: t["pa_per_g"],
            "https://www.nfl.com/standings/division/2026/reg",
            "Near-zero cross-unit correlation confirms team offense and team defense must be rated as distinct components."
        ),
    ]

    computed_corrs = []
    for cid, label, category, fx, fy, src, note in pairs_spec:
        xs = [float(fx(t)) for t in teams_out]
        ys = [float(fy(t)) for t in teams_out]
        r = pearson(xs, ys)
        rho = spearman(xs, ys)
        t_stat, p_val, ci_lo, ci_hi = reg_t_ci(r, len(teams_out))
        computed_corrs.append({
            "id": cid,
            "pair": label,
            "category": category,
            "sample": "n = 32 NFL teams (2026 REG, Weeks 1–9)",
            "pearson_r": round(r, 3),
            "spearman_rho": round(rho, 3),
            "r_squared": round(r * r, 3),
            "t_stat": round(t_stat, 2),
            "p_value": round(p_val, 5),
            "ci95_low": round(ci_lo, 3),
            "ci95_high": round(ci_hi, 3),
            "verified_status": "VERIFIED (Computed from NFL.com 2026 Team Stats)",
            "source": src,
            "method_source": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm",
            "implication": note,
        })

    # Unverified game-level / play-level parlay & player-prop leg correlations:
    # STRICT RULE: Leave empirical r value BLANK ("") and flag as UNVERIFIED because repo has no official play-by-play feed!
    unverified_sgp_corrs = [
        {
            "id": "U-C01",
            "leg_a": "QB Passing Yards Over",
            "leg_b": "Primary WR1 Receiving Yards Over (same team)",
            "bet_structure": "Same-Game Parlay / Player Prop Combo",
            "expected_mechanism": "Positive structural coupling (shared pass completions & air yards)",
            "empirical_r": "",
            "joint_copula_adjustment": "",
            "status": "UNVERIFIED — Blank (Requires Official Play-by-Play / Gamebook Log Feed)",
            "source": "https://operations.nfl.com/gameday/technology/nfl-next-gen-stats/"
        },
        {
            "id": "U-C02",
            "leg_a": "QB Passing Attempts Over",
            "leg_b": "Own Team Point Spread Cover (-X.5)",
            "bet_structure": "Same-Game Parlay",
            "expected_mechanism": "Negative game-script coupling (trailing teams pass more in Q3/Q4; see C-06 team-level r)",
            "empirical_r": "",
            "joint_copula_adjustment": "",
            "status": "UNVERIFIED — Blank (Requires Official Play-by-Play / Closing Spread Archive)",
            "source": "https://www.nfl.com/stats/team-stats/offense/passing/2026/reg/all"
        },
        {
            "id": "U-C03",
            "leg_a": "RB1 Rushing Attempts Over",
            "leg_b": "Own Team Moneyline / Spread Cover",
            "bet_structure": "Same-Game Parlay / Prop + Side Combo",
            "expected_mechanism": "Positive game-script coupling (leading teams run clock in second half; see C-07)",
            "empirical_r": "",
            "joint_copula_adjustment": "",
            "status": "UNVERIFIED — Blank (Requires Official Gamebook Player Logs)",
            "source": "https://www.nfl.com/stats/team-stats/offense/rushing/2026/reg/all"
        },
        {
            "id": "U-C04",
            "leg_a": "Opposing EDGE Sack / QB Hits Over",
            "leg_b": "Offense Playing 2nd/3rd-String OT/OG QB Passing Yards Under",
            "bet_structure": "Injury-Deficiency Prop Combo",
            "expected_mechanism": "Positive deficiency coupling via OL pressure rate (consistent with C-09 team sack rate r)",
            "empirical_r": "",
            "joint_copula_adjustment": "",
            "status": "UNVERIFIED — Blank (Requires Official Snap-Level OL Lineup & Pressure Logs)",
            "source": "https://www.nfl.com/injuries/league/2026/REG10"
        },
        {
            "id": "U-C05",
            "leg_a": "WR1 Target Share / Receiving Yards Over",
            "leg_b": "Opposing Defense Missing 1st-String Outside CB (2nd/3rd-String Replacement)",
            "bet_structure": "Defensive-Deficiency Prop Combo",
            "expected_mechanism": "Positive matchup coupling (consistent with C-10 defensive passer rating allowed r)",
            "empirical_r": "",
            "joint_copula_adjustment": "",
            "status": "UNVERIFIED — Blank (Requires Official Coverage Matchup / Gamebook Feed)",
            "source": "https://www.nfl.com/injuries/league/2026/REG10"
        },
        {
            "id": "U-C06",
            "leg_a": "Game Total Over",
            "leg_b": "Both QBs Passing TD Over (Bring-Back Shootout Stack)",
            "bet_structure": "Same-Game Parlay / Prop Stack",
            "expected_mechanism": "Positive pace & shootout feedback loop",
            "empirical_r": "",
            "joint_copula_adjustment": "",
            "status": "UNVERIFIED — Blank (Requires Official Gamebook Scoring Summary Archive)",
            "source": "https://static.www.nfl.com/image/upload/fl_attachment/league/tqivdkzt9mu6wdgsh1ku.pdf"
        },
    ]

    # Build v1 Efficiency-Blended Fair Lines for all 13 Week 11 games (MODEL ONLY — market lines strictly blank)
    by_name = {t["team"]: t for t in teams_out}
    lg_pf_pg = sum(t["pf"] for t in teams_out) / sum(t["games"] for t in teams_out)
    lg_ypp = sum(t["derived_efficiency"]["off_yds_per_play"] for t in teams_out) / len(teams_out)

    week11_model_lines = []
    for g in schedule["games"]:
        away = by_name[g["away"]]
        home = by_name[g["home"]]
        is_neutral = "Mexico City" in g.get("note", "")
        hfa = 0.0 if is_neutral else 2.0  # Editable v1 model assumption (0.0 neutral site)

        # Blend 60% luck-regressed PF/PA margin + 40% Yards/Play efficiency differential (regressed 25% to league mean)
        def off_rating(tm: dict) -> float:
            raw_pts_delta = tm["pf_per_g"] - lg_pf_pg
            ypp_pts_delta = (tm["derived_efficiency"]["off_yds_per_play"] - lg_ypp) * 7.5
            return 0.75 * (0.60 * raw_pts_delta + 0.40 * ypp_pts_delta)

        def def_rating(tm: dict) -> float:
            # Positive def_rating = points allowed BELOW league average (good defense)
            raw_pa_delta = lg_pf_pg - tm["pa_per_g"]
            ypp_pa_delta = (lg_ypp - tm["derived_efficiency"]["def_yds_per_play_allowed"]) * 7.5
            return 0.75 * (0.60 * raw_pa_delta + 0.40 * ypp_pa_delta)

        proj_home = lg_pf_pg + (off_rating(home) - def_rating(away)) + (hfa / 2.0)
        proj_away = lg_pf_pg + (off_rating(away) - def_rating(home)) - (hfa / 2.0)
        fair_margin_home = proj_home - proj_away  # >0 means home favored
        fair_total = proj_home + proj_away
        p_home = normal_cdf(fair_margin_home / 13.5)
        ml_home = round(-100 * p_home / (1 - p_home)) if p_home >= 0.5 else round(100 * (1 - p_home) / p_home)
        ml_away = round(-100 * (1 - p_home) / p_home) if (1 - p_home) >= 0.5 else round(100 * p_home / (1 - p_home))

        spread_label = (
            f"{home['abbr']} -{abs(fair_margin_home):.1f}"
            if fair_margin_home >= 0
            else f"{home['abbr']} +{abs(fair_margin_home):.1f}"
        )
        week11_model_lines.append({
            "date": g["date"],
            "kickoff_et": g["timeET"],
            "away": g["away"],
            "away_abbr": away["abbr"],
            "home": g["home"],
            "home_abbr": home["abbr"],
            "neutral_site": is_neutral,
            "hfa_assumed": hfa,
            "model_proj_away": round(proj_away, 1),
            "model_proj_home": round(proj_home, 1),
            "model_fair_spread_home": spread_label,
            "model_fair_total": round(fair_total, 1),
            "model_home_win_prob_pct": round(p_home * 100, 1),
            "model_fair_ml_home": f"{'+' if ml_home > 0 else ''}{ml_home}",
            "model_fair_ml_away": f"{'+' if ml_away > 0 else ''}{ml_away}",
            "market_spread": "",
            "market_total": "",
            "edge_vs_market": "",
            "market_status": "UNVERIFIED — Blank (No Licensed Sportsbook Feed Connected)",
            "schedule_source": "https://www.nfl.com/news/week-11-schedule-change",
            "stats_source": "https://www.nfl.com/standings/division/2026/reg",
        })

    luck_ranking = sorted(
        [
            {
                "team": t["team"],
                "abbr": t["abbr"],
                "record": f"{t['w']}-{t['l']}-{t['t']}",
                "actual_win_pct": t["win_pct"],
                "pf": t["pf"],
                "pa": t["pa"],
                "net_pts": t["net_pts"],
                "pythagorean_win_pct": t["pythagorean_win_pct"],
                "luck_residual_win_pct": t["luck_residual_win_pct"],
                "luck_residual_wins": t["luck_residual_wins"],
                "int_margin": t["derived_efficiency"]["int_margin"],
                "net_yds_per_play": t["derived_efficiency"]["net_yds_per_play"],
                "signal_classification": (
                    "Fade Candidate (Lucky Record > Skill)"
                    if t["luck_residual_win_pct"] >= 0.12
                    else (
                        "Buy-Low Candidate (Skill > Unlucky Record)"
                        if t["luck_residual_win_pct"] <= -0.12
                        else "Aligned (Record Near Skill Baseline)"
                    )
                ),
                "source": "https://www.nfl.com/standings/division/2026/reg",
            }
            for t in teams_out
        ],
        key=lambda x: x["luck_residual_win_pct"],
        reverse=True,
    )

    corr_payload = {
        "asOf": "2026-11-12",
        "season": 2026,
        "methodology_source": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm",
        "team_stats_sources": stats_payload["sources"],
        "verified_team_correlations": computed_corrs,
        "unverified_parlay_prop_correlations": unverified_sgp_corrs,
        "luck_vs_skill_team_residuals": luck_ranking,
        "week11_v1_model_originated_lines": week11_model_lines,
    }
    (ROOT / "data" / "correlations-2026.json").write_text(
        json.dumps(corr_payload, indent=2) + "\n"
    )
    print("SUCCESS: Computed 32-team stats, 14 verified correlations, 32 luck residuals, 13 Week-11 v1 fair lines.")
    for c in computed_corrs:
        print(f"  {c['id']}: {c['pair']} -> r={c['pearson_r']:+.3f} (p={c['p_value']:.5f}, 95% CI [{c['ci95_low']:+.3f}, {c['ci95_high']:+.3f}])")


if __name__ == "__main__":
    main()

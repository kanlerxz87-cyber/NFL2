(function () {
  "use strict";

  // 1. Live table text search & category filtering
  document.querySelectorAll("[data-table-filter]").forEach(function (input) {
    var targetId = input.getAttribute("data-table-filter");
    var table = document.getElementById(targetId);
    if (!table) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      table.querySelectorAll("tbody tr").forEach(function (tr) {
        var text = tr.textContent.toLowerCase();
        tr.style.display = !q || text.indexOf(q) !== -1 ? "" : "none";
      });
    });
  });

  // 2. Click-to-sort table headers
  document.querySelectorAll("table[data-sortable] thead th").forEach(function (th, colIdx) {
    th.title = "Click to sort column";
    th.addEventListener("click", function () {
      var table = th.closest("table");
      var tbody = table.querySelector("tbody");
      var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
      var asc = th.getAttribute("data-sort-dir") !== "asc";
      table.querySelectorAll("thead th").forEach(function (h) {
        h.removeAttribute("data-sort-dir");
      });
      th.setAttribute("data-sort-dir", asc ? "asc" : "desc");
      rows.sort(function (a, b) {
        var ca = (a.children[colIdx] ? a.children[colIdx].textContent : "").trim();
        var cb = (b.children[colIdx] ? b.children[colIdx].textContent : "").trim();
        var na = parseFloat(ca.replace(/[^0-9.\-+]/g, ""));
        var nb = parseFloat(cb.replace(/[^0-9.\-+]/g, ""));
        if (!isNaN(na) && !isNaN(nb) && ca !== "" && cb !== "") {
          return asc ? na - nb : nb - na;
        }
        return asc ? ca.localeCompare(cb) : cb.localeCompare(ca);
      });
      rows.forEach(function (r) {
        tbody.appendChild(r);
      });
    });
  });

  // Normal CDF (Abramowitz & Stegun 7.1.26)
  function normCdf(x) {
    var sign = x < 0 ? -1 : 1;
    var z = Math.abs(x) / Math.sqrt(2);
    var t = 1 / (1 + 0.3275911 * z);
    var erf = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z);
    return 0.5 * (1 + sign * erf);
  }

  function toAmerican(p) {
    p = Math.max(0.01, Math.min(0.99, p));
    if (Math.abs(p - 0.5) < 1e-6) return "+100";
    return p > 0.5 ? String(-Math.round((100 * p) / (1 - p))) : "+" + String(Math.round((100 * (1 - p)) / p));
  }

  // 3. Interactive Line Origination & No-Vig Edge Calculator
  var lineForm = document.getElementById("portal-line-calc");
  var lineOut = document.getElementById("portal-line-out");
  if (lineForm && lineOut) {
    var runLineCalc = function (ev) {
      if (ev) ev.preventDefault();
      var lgMean = parseFloat(document.getElementById("lc-lg").value) || 22.963;
      var homeOff = parseFloat(document.getElementById("lc-hoff").value) || 0;
      var homeDef = parseFloat(document.getElementById("lc-hdef").value) || 0;
      var awayOff = parseFloat(document.getElementById("lc-aoff").value) || 0;
      var awayDef = parseFloat(document.getElementById("lc-adef").value) || 0;
      var hfa = parseFloat(document.getElementById("lc-hfa").value) || 0;
      var injDelta = parseFloat(document.getElementById("lc-inj").value) || 0;
      var sd = parseFloat(document.getElementById("lc-sd").value) || 13.45;

      var projHome = lgMean + homeOff + awayDef + 0.5 * hfa + 0.5 * injDelta;
      var projAway = lgMean + awayOff + homeDef - 0.5 * hfa - 0.5 * injDelta;
      var marginHome = projHome - projAway;
      var spreadLine = -Math.round(marginHome * 2) / 2;
      var totalLine = Math.round((projHome + projAway) * 2) / 2;
      var pHome = normCdf(marginHome / sd);
      var keyNote = "None";
      var absM = Math.abs(marginHome);
      if (absM >= 2.6 && absM <= 3.4) keyNote = "ALERT: Crossing NFL Key Number 3 (Field Goal)";
      else if (absM >= 6.6 && absM <= 7.4) keyNote = "ALERT: Crossing NFL Key Number 7 (TD + XP)";

      lineOut.textContent =
        "MODEL-ONLY ORIGINATED LINE (Not a sportsbook quote):\n" +
        "  Projected Score : Away " + projAway.toFixed(1) + "  —  Home " + projHome.toFixed(1) + "\n" +
        "  Fair Home Spread: " + (spreadLine > 0 ? "+" + spreadLine.toFixed(1) : spreadLine.toFixed(1)) +
        "   (Exact margin: " + (marginHome >= 0 ? "+" : "") + marginHome.toFixed(2) + " pts)\n" +
        "  Fair Game Total : " + totalLine.toFixed(1) + " pts\n" +
        "  Fair Win Prob   : Home " + (100 * pHome).toFixed(1) + "% (" + toAmerican(pHome) + ")  |  Away " +
        (100 * (1 - pHome)).toFixed(1) + "% (" + toAmerican(1 - pHome) + ")\n" +
        "  Key-Number Check: " + keyNote;
    };
    lineForm.addEventListener("submit", runLineCalc);
    runLineCalc();
  }

  // 4. Interactive SGP / Parlay Correlation & Vig Auditor
  var sgpForm = document.getElementById("portal-sgp-calc");
  var sgpOut = document.getElementById("portal-sgp-out");
  if (sgpForm && sgpOut) {
    var runSgpCalc = function (ev) {
      if (ev) ev.preventDefault();
      var pA = (parseFloat(document.getElementById("sgp-pa").value) || 50) / 100;
      var pB = (parseFloat(document.getElementById("sgp-pb").value) || 50) / 100;
      var r = parseFloat(document.getElementById("sgp-r").value) || 0;
      var bookAmerican = parseFloat(document.getElementById("sgp-book").value) || 264;
      pA = Math.max(0.05, Math.min(0.95, pA));
      pB = Math.max(0.05, Math.min(0.95, pB));
      r = Math.max(-0.85, Math.min(0.85, r));

      var indepP = pA * pB;
      // First-order Bahadur / tetrachoric approximation around marginals
      var jointP = Math.max(0.01, Math.min(Math.min(pA, pB), indepP + r * Math.sqrt(pA * (1 - pA) * pB * (1 - pB))));
      var decOdds = bookAmerican > 0 ? 1 + bookAmerican / 100 : 1 + 100 / Math.abs(bookAmerican);
      var evPct = (jointP * decOdds - 1) * 100;
      var gatePass = evPct >= 3.0 ? "PASSES Gate G6 Threshold (EV >= +3.0%)" : "REJECTED by Gate G6 (Insufficient edge over SGP vig)";

      sgpOut.textContent =
        "JOINT PROBABILITY & SGP VIG AUDIT (MODEL ONLY):\n" +
        "  Independent P(A)*P(B)     : " + (100 * indepP).toFixed(2) + "%  (Fair " + toAmerican(indepP) + ")\n" +
        "  Correlated Joint P(A & B) : " + (100 * jointP).toFixed(2) + "%  (Fair " + toAmerican(jointP) + " at r=" + r.toFixed(2) + ")\n" +
        "  Quoted Payout Tested      : " + (bookAmerican > 0 ? "+" : "") + bookAmerican + " (" + decOdds.toFixed(3) + "x decimal)\n" +
        "  Expected Value (EV)       : " + (evPct >= 0 ? "+" : "") + evPct.toFixed(2) + "%  -->  " + gatePass;
    };
    sgpForm.addEventListener("submit", runSgpCalc);
    runSgpCalc();
  }
})();

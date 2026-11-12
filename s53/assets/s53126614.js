(function () {
  "use strict";

  // Instant text filter for any input[data-filter-input="<table-id>"]
  document.querySelectorAll("[data-filter-input]").forEach(function (input) {
    var tableId = input.getAttribute("data-filter-input");
    var table = document.getElementById(tableId);
    if (!table || !table.tBodies[0]) return;
    var rows = Array.prototype.slice.call(table.tBodies[0].rows);
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      rows.forEach(function (tr) {
        if (!q) {
          tr.style.display = "";
          return;
        }
        tr.style.display = tr.textContent.toLowerCase().indexOf(q) !== -1 ? "" : "none";
      });
    });
  });

  // Expose pure math helpers for originated-lines & gate calculators
  window.NFL2S53 = {
    erf: function (x) {
      var sign = x < 0 ? -1 : 1;
      var ax = Math.abs(x);
      var t = 1 / (1 + 0.3275911 * ax);
      var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-ax * ax);
      return sign * y;
    },
    normCdf: function (z) {
      return 0.5 * (1 + window.NFL2S53.erf(z / Math.SQRT2));
    },
    probToAmerican: function (p) {
      if (!(p > 0 && p < 1)) return "N/A";
      if (Math.abs(p - 0.5) < 1e-6) return "+100";
      if (p > 0.5) return String(Math.round(-100 * p / (1 - p)));
      return "+" + String(Math.round(100 * (1 - p) / p));
    },
    americanToImplied: function (odds) {
      if (!isFinite(odds) || odds === 0) return null;
      if (odds < 0) return (-odds) / ((-odds) + 100);
      return 100 / (odds + 100);
    }
  };
})();

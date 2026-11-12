/* NFL2 dashboard behaviour: filter, sort, path chooser. No external dependencies. */
(function () {
  "use strict";

  var filter = document.getElementById("rowFilter");
  var count = document.getElementById("rowCount");
  var rows = Array.prototype.slice.call(document.querySelectorAll("table.data-table tbody tr"));

  function updateCount() {
    if (!count) return;
    var shown = rows.filter(function (r) { return !r.classList.contains("hidden"); }).length;
    count.textContent = shown + " of " + rows.length + " rows shown";
  }

  function applyFilter() {
    var q = (filter && filter.value ? filter.value : "").trim().toLowerCase();
    rows.forEach(function (r) {
      var text = (r.textContent || "").toLowerCase();
      r.classList.toggle("hidden", q !== "" && text.indexOf(q) === -1);
    });
    updateCount();
  }

  if (filter) {
    filter.addEventListener("input", applyFilter);
    filter.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { filter.value = ""; applyFilter(); }
    });
  }
  updateCount();

  /* Sortable headers: click or Enter/Space on a focused <th>. */
  document.querySelectorAll("table.data-table").forEach(function (table) {
    var body = table.querySelector("tbody");
    if (!body) return;
    var heads = Array.prototype.slice.call(table.querySelectorAll("thead th"));
    heads.forEach(function (th, index) {
      function sort() {
        var trs = Array.prototype.slice.call(body.querySelectorAll("tr"));
        var dir = th.dataset.dir === "asc" ? "desc" : "asc";
        heads.forEach(function (h) { delete h.dataset.dir; });
        th.dataset.dir = dir;
        trs.sort(function (a, b) {
          var x = (a.children[index] ? a.children[index].textContent : "").trim();
          var y = (b.children[index] ? b.children[index].textContent : "").trim();
          var nx = parseFloat(x.replace(/[^0-9.\-+]/g, ""));
          var ny = parseFloat(y.replace(/[^0-9.\-+]/g, ""));
          var cmp;
          if (!isNaN(nx) && !isNaN(ny) && x !== "" && y !== "") { cmp = nx - ny; }
          else { cmp = x.localeCompare(y, undefined, { numeric: true, sensitivity: "base" }); }
          return dir === "asc" ? cmp : -cmp;
        });
        trs.forEach(function (tr) { body.appendChild(tr); });
      }
      th.addEventListener("click", sort);
      th.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); sort(); }
      });
    });
  });

  /* Suggestions path chooser — local only, never changes the site. */
  var form = document.getElementById("path-chooser");
  if (form) {
    var output = document.getElementById("decision-output");
    var clear = document.getElementById("clear-choice");
    var KEY = "nfl2-chosen-path";
    var names = {
      A: "Lock the evidence layer",
      B: "Answer the blocking questions",
      C: "Build injury / depth ingestion",
      D: "License data and run numeric gates",
      E: "Recognition-only leaderboard"
    };
    function show(v) {
      if (v && names[v]) {
        output.textContent = "Recorded choice: Path " + v + " — " + names[v] +
          ". Stored in this browser only. No implementation has started.";
        var radio = form.querySelector('input[value="' + v + '"]');
        if (radio) radio.checked = true;
      } else {
        output.textContent = "No path recorded yet.";
      }
    }
    try { show(window.localStorage.getItem(KEY)); } catch (e) { /* storage unavailable */ }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var picked = form.querySelector("input[name=path]:checked");
      if (!picked) { output.textContent = "Please select a path first."; return; }
      try { window.localStorage.setItem(KEY, picked.value); } catch (e) { /* ignore */ }
      show(picked.value);
    });
    if (clear) {
      clear.addEventListener("click", function () {
        try { window.localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
        form.querySelectorAll("input[name=path]").forEach(function (r) { r.checked = false; });
        show(null);
      });
    }
  }
})();

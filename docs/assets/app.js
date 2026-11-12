// NFL2 dashboard helpers — no external dependencies.
(function(){
  "use strict";
  // Table search/filter: input[data-filter-target="tableId"]
  document.querySelectorAll("input[data-filter-target]").forEach(function(inp){
    inp.addEventListener("input", function(){
      var table = document.getElementById(inp.getAttribute("data-filter-target"));
      if(!table) return;
      var q = inp.value.trim().toLowerCase();
      table.querySelectorAll("tbody tr").forEach(function(tr){
        tr.style.display = tr.textContent.toLowerCase().indexOf(q) === -1 ? "none" : "";
      });
    });
  });
  // Odds helpers
  function implied(odds){
    odds = parseFloat(odds);
    if(isNaN(odds) || odds === 0) return null;
    if(odds < 0) return Math.abs(odds) / (Math.abs(odds) + 100);
    return 100 / (odds + 100);
  }
  function probToAmerican(p){
    if(p <= 0 || p >= 1) return "—";
    if(p >= 0.5) return Math.round(-100 * p / (1 - p));
    return Math.round(100 * (1 - p) / p);
  }
  function fmtPct(p){ return p === null ? "—" : (p*100).toFixed(2) + "%"; }
  function fmtOdds(o){ if(o === null || isNaN(o)) return "—"; return (o > 0 ? "+" : "") + Math.round(o); }

  // No-vig calculator (lines.html): inputs #nv-a, #nv-b
  var nvA = document.getElementById("nv-a"), nvB = document.getElementById("nv-b"), nvOut = document.getElementById("nv-result");
  function runNoVig(){
    if(!nvOut) return;
    var a = implied(nvA.value), b = implied(nvB.value);
    if(a === null || b === null){ nvOut.innerHTML = "<p class='muted'>Enter both American odds (e.g. -110 and -110).</p>"; return; }
    var total = a + b, vig = total - 1;
    var fa = a / total, fb = b / total;
    nvOut.innerHTML =
      "<p><strong>Side A implied:</strong> " + fmtPct(a) + " &nbsp;|&nbsp; <strong>Side B implied:</strong> " + fmtPct(b) + "</p>" +
      "<p><strong>Overround:</strong> " + fmtPct(total) + " &nbsp;|&nbsp; <strong>Overround:</strong> " + fmtPct(vig) + "</p>" +
      "<p><strong>Fair (no-vig) A:</strong> " + fmtPct(fa) + " ≈ " + fmtOdds(probToAmerican(fa)) + " &nbsp;|&nbsp; <strong>Fair B:</strong> " + fmtPct(fb) + " ≈ " + fmtOdds(probToAmerican(fb)) + "</p>" +
      "<p class='small muted'>Formulas: negative odds → |odds|/(|odds|+100); positive → 100/(odds+100). Fair = implied / overround. See lines.html methodology.</p>";
  }
  if(nvA){ nvA.addEventListener("input", runNoVig); nvB.addEventListener("input", runNoVig); runNoVig(); }

  // Fair-lines calculator (lines.html): inputs #fl-home-pts, #fl-away-pts, #fl-home-allow, #fl-away-allow, #fl-hfa, #fl-total-avg
  var fl = ["fl-home-pts","fl-away-pts","fl-home-allow","fl-away-allow","fl-hfa","fl-total-avg"].map(function(id){ return document.getElementById(id); });
  var flOut = document.getElementById("fl-result");
  function num(id, def){ var el = document.getElementById(id); var v = parseFloat(el ? el.value : ""); return isNaN(v) ? def : v; }
  function runFair(){
    if(!flOut) return;
    var hp = num("fl-home-pts", 0), ap = num("fl-away-pts", 0), ha = num("fl-home-allow", 0), aa = num("fl-away-allow", 0);
    var hfa = num("fl-hfa", 2.5), tavg = num("fl-total-avg", 44);
    // Simple power-rating style estimate (ILLUSTRATIVE, uncalibrated):
    // Home expected = (hp + aa)/2 + hfa/2 ; Away expected = (ap + ha)/2 - hfa/2 ; then blend toward league total avg 50/50.
    var homeRaw = (hp + aa) / 2 + hfa / 2;
    var awayRaw = (ap + ha) / 2 - hfa / 2;
    var homeExp = homeRaw * 0.5 + (tavg / 2) * 0.5;
    var awayExp = awayRaw * 0.5 + (tavg / 2) * 0.5;
    var spread = homeExp - awayExp; // positive = home favoured by this many
    var total = homeExp + awayExp;
    // Moneyline from spread via normal approx (sd ~ 13.5 for NFL margin — placeholder, labelled uncalibrated)
    var sd = 13.5;
    var z = spread / sd;
    var Phi = function(x){ return 0.5 * (1 + erf(x / Math.sqrt(2))); };
    var pHome = Phi(z);
    var mlHome = probToAmerican(pHome), mlAway = probToAmerican(1 - pHome);
    flOut.innerHTML =
      "<p><strong>Home expected points:</strong> " + homeExp.toFixed(1) + " &nbsp;|&nbsp; <strong>Away expected:</strong> " + awayExp.toFixed(1) + "</p>" +
      "<p><strong>Fair spread (home):</strong> " + (spread >= 0 ? "−" : "+") + Math.abs(spread).toFixed(1) + " &nbsp;|&nbsp; <strong>Fair total:</strong> " + total.toFixed(1) + "</p>" +
      "<p><strong>Fair moneyline — Home:</strong> " + fmtOdds(mlHome) + " (" + fmtPct(pHome) + ") &nbsp;|&nbsp; <strong>Away:</strong> " + fmtOdds(mlAway) + " (" + fmtPct(1-pHome) + ")</p>" +
      "<p class='small muted'>⚠️ ILLUSTRATIVE ONLY — uncalibrated toy model (50% blend to league average, placeholder HFA + margin SD 13.5). NOT a prediction. Do not bet on this. See lines.html §2–3 and QIA Q-04/Q-15.</p>";
  }
  function erf(x){ var s = x < 0 ? -1 : 1; x = Math.abs(x); var t = 1 / (1 + 0.3275911 * x); var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return s * y; }
  if(fl[0]){ fl.forEach(function(el){ el.addEventListener("input", runFair); }); runFair(); }

  // Kelly calculator (strategies.html): #k-p, #k-odds
  var kP = document.getElementById("k-p"), kO = document.getElementById("k-odds"), kOut = document.getElementById("k-result");
  function runKelly(){
    if(!kOut) return;
    var p = parseFloat(kP.value) / 100, odds = parseFloat(kO.value);
    var imp = implied(odds);
    if(isNaN(p) || p <= 0 || p >= 1 || imp === null){ kOut.innerHTML = "<p class='muted'>Enter win probability % and American odds.</p>"; return; }
    var b = odds > 0 ? odds / 100 : 100 / Math.abs(odds); // net odds per unit staked
    var f = (b * p - (1 - p)) / b;
    var ev = p * b - (1 - p); // per unit staked
    kOut.innerHTML =
      "<p><strong>Break-even (implied):</strong> " + fmtPct(imp) + " &nbsp;|&nbsp; <strong>Your edge:</strong> " + ((p - imp) * 100).toFixed(2) + " pp</p>" +
      "<p><strong>Expected value per $100 staked:</strong> $" + (ev * 100).toFixed(2) + "</p>" +
      "<p><strong>Full Kelly f*:</strong> " + (f > 0 ? (f * 100).toFixed(2) + "% of bankroll" : "≤ 0 — no bet (negative EV)") + " &nbsp;|&nbsp; <strong>Quarter-Kelly:</strong> " + (f > 0 ? (f * 25).toFixed(2) + "%" : "—") + "</p>" +
      "<p class='small muted'>f* = (bp − q)/b. Full Kelly assumes perfect probability knowledge — never use it directly. Site policy (S-12): cap 1% until 500 graded bets.</p>";
  }
  if(kP){ kP.addEventListener("input", runKelly); kO.addEventListener("input", runKelly); runKelly(); }
})();

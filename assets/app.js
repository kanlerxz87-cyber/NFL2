/* NFL2 — small client helpers. No network calls. All math is transparent and shown. */
(function(){
  "use strict";
  function $(s, r){ return (r||document).querySelector(s); }
  function $$(s, r){ return Array.from((r||document).querySelectorAll(s)); }

  // ---- Table filter (used on standings / injuries / teams) ----
  $$("[data-filter-input]").forEach(function(inp){
    var target = document.querySelector(inp.getAttribute("data-filter-input"));
    if(!target) return;
    inp.addEventListener("input", function(){
      var q = inp.value.trim().toLowerCase();
      $$("tbody tr", target).forEach(function(tr){
        tr.style.display = (!q || tr.textContent.toLowerCase().indexOf(q) !== -1) ? "" : "none";
      });
    });
  });

  // ---- Originated-lines calculator (MODEL ONLY) ----
  // Inputs: home PF, home PA, away PF, away PA, games played (same for both assumed), home-field points (default 2.5, editable).
  // Method (documented on lines-lab.html):
  //   avgPtsFor = PF/games, avgPtsAgainst = PA/games
  //   projHome = (homePF/g + awayPA/g)/2 + HFA
  //   projAway = (awayPF/g + homePA/g)/2
  //   fairSpread (home perspective) = projHome - projAway  (positive = home favoured)
  //   fairTotal = projHome + projAway
  //   winProb via normal approx: P(home win) = Phi(spread / 13.5)  [13.5 = typical NFL margin SD, editable]
  // This is a deliberately simple baseline. It is NOT a sportsbook line and NOT betting advice.
  var form = $("#lines-calc");
  if(form){
    var out = $("#lines-out");
    function phi(z){ // standard normal CDF approximation (Abramowitz-Stegun 26.2.17)
      var t = 1/(1+0.2316419*Math.abs(z));
      var d = 0.3989422804014327*Math.exp(-z*z/2);
      var p = d*t*(0.319381530 + t*(-0.356563782 + t*(1.781477937 + t*(-1.821255978 + t*1.330274429))));
      return z>0 ? 1-p : p;
    }
    function num(id, def){ var el = $(id); var v = parseFloat(el && el.value); return isNaN(v) ? def : v; }
    function run(){
      var g = Math.max(1, num("#g", 8));
      var hPF = num("#hPF", 0), hPA = num("#hPA", 0), aPF = num("#aPF", 0), aPA = num("#aPA", 0);
      var hfa = num("#hfa", 2.5), sd = Math.max(1, num("#sd", 13.5));
      var projHome = (hPF/g + aPA/g)/2 + hfa;
      var projAway = (aPF/g + hPA/g)/2;
      var spread = projHome - projAway;
      var total = projHome + projAway;
      var pHome = phi(spread/sd);
      var mlHome = pHome>=0.5 ? -100*pHome/(1-pHome) : 100*(1-pHome)/pHome;
      var mlAway = (1-pHome)>=0.5 ? -100*(1-pHome)/pHome : 100*pHome/(1-pHome);
      function fmtML(v){ return (v>0?"+":"") + Math.round(v); }
      out.textContent =
        "MODEL ONLY — baseline from points for/against (not a market line, not betting advice)\n" +
        "Games assumed: " + g + " each\n" +
        "Home proj: " + projHome.toFixed(1) + " pts  |  Away proj: " + projAway.toFixed(1) + " pts\n" +
        "Fair spread (home): " + (spread>=0? "home -" : "home +") + Math.abs(spread).toFixed(1) + "\n" +
        "Fair total: " + total.toFixed(1) + "\n" +
        "P(home win) ≈ " + (pHome*100).toFixed(1) + "%  →  fair ML home " + fmtML(mlHome) + " / away " + fmtML(mlAway) + "\n" +
        "Assumptions: HFA=" + hfa + " pts, margin SD=" + sd + ". Replace with opponent-adjusted ratings before any use.";
    }
    form.addEventListener("submit", function(e){ e.preventDefault(); run(); });
    run();
  }

  // ---- Correlation helper (Pearson r) ----
  var corrForm = $("#corr-calc");
  if(corrForm){
    var corrOut = $("#corr-out");
    corrForm.addEventListener("submit", function(e){
      e.preventDefault();
      function parse(id){
        var v = $(id).value.trim();
        if(!v) return [];
        return v.split(/[\s,;]+/).map(Number).filter(function(n){ return !isNaN(n); });
      }
      var x = parse("#corr-x"), y = parse("#corr-y");
      if(x.length !== y.length || x.length < 3){
        corrOut.textContent = "Enter two equal-length lists with at least 3 paired numbers (e.g. one per game).";
        return;
      }
      var n = x.length, mx = x.reduce(function(a,b){return a+b;},0)/n, my = y.reduce(function(a,b){return a+b;},0)/n;
      var numSum=0, dx=0, dy=0;
      for(var i=0;i<n;i++){ var a=x[i]-mx, b=y[i]-my; numSum+=a*b; dx+=a*a; dy+=b*b; }
      var r = (dx===0||dy===0) ? NaN : numSum/Math.sqrt(dx*dy);
      corrOut.textContent = "n=" + n + "  Pearson r = " + (isNaN(r)? "undefined (zero variance)" : r.toFixed(3)) +
        "\nInterpretation: |r|<0.10 negligible, 0.10–0.30 weak, 0.30–0.50 moderate, >0.50 strong. Correlation ≠ causation; check sample size and out-of-sample stability before trusting any signal.";
    });
  }
})();

/* Shaw Local – County board partisan makeup widget.
   Embed: <div class="slm-board-makeup" data-county="kane"></div>
          <script src="URL/board-makeup.js"></script>
   Optional data-county (or ?county= in the page URL) presets the county; default is DuPage. */
(function () {
  var DATA = [{"id": "bureau", "name": "Bureau County", "note": "District 15 was vacant as of March 2026 and is shown in gray. Figures for 2022 and 2024 are based on Shaw Local reporting.", "rows": [{"y": "2022", "t": 18, "d": 6, "r": 11, "o": 1, "u": false}, {"y": "2024", "t": 18, "d": 6, "r": 11, "o": 1, "u": false}, {"y": "2026", "t": 18, "d": 6, "r": 11, "o": 1, "u": true}], "close": []}, {"id": "carroll", "name": "Carroll County", "note": "Party affiliations are from the Carroll County Republican Central Committee and Shaw Local reporting.", "rows": [{"y": "2024", "t": 9, "d": 1, "r": 8, "o": 0, "u": false}, {"y": "2026", "t": 9, "d": 0, "r": 9, "o": 0, "u": true}], "close": []}, {"id": "cook", "name": "Cook County, including Chicago", "note": "The Cook County Board includes commissioners from Chicago and suburban Cook County. All 17 seats are elected every four years.", "rows": [{"y": "2010", "t": 17, "d": 13, "r": 4, "o": 0, "u": false}, {"y": "2014", "t": 17, "d": 13, "r": 4, "o": 0, "u": false}, {"y": "2018", "t": 17, "d": 15, "r": 2, "o": 0, "u": false}, {"y": "2022", "t": 17, "d": 16, "r": 1, "o": 0, "u": false}, {"y": "2026", "t": 17, "d": 17, "r": 0, "o": 0, "u": true}], "close": []}, {"id": "dekalb", "name": "DeKalb County", "note": "Board makeup before 2022 is not available online.", "rows": [{"y": "2022", "t": 24, "d": 13, "r": 11, "o": 0, "u": false}, {"y": "2024", "t": 24, "d": 11, "r": 13, "o": 0, "u": false}, {"y": "2026", "t": 24, "d": 13, "r": 11, "o": 0, "u": true}], "close": ["District 3: Republican Marc R. Doty leads Democrat Joanne Pickering by 36 votes."]}, {"id": "dupage", "name": "DuPage County", "note": "", "rows": [{"y": "2012", "t": 18, "d": 3, "r": 15, "o": 0, "u": false}, {"y": "2014", "t": 18, "d": 2, "r": 16, "o": 0, "u": false}, {"y": "2016", "t": 18, "d": 1, "r": 17, "o": 0, "u": false}, {"y": "2018", "t": 18, "d": 7, "r": 11, "o": 0, "u": false}, {"y": "2020", "t": 18, "d": 11, "r": 7, "o": 0, "u": false}, {"y": "2022", "t": 18, "d": 11, "r": 7, "o": 0, "u": false}, {"y": "2024", "t": 18, "d": 12, "r": 6, "o": 0, "u": false}, {"y": "2026", "t": 18, "d": 17, "r": 1, "o": 0, "u": true}], "close": []}, {"id": "grundy", "name": "Grundy County", "note": "In 2016, a District 3 tie was decided by lot. Democrat Jim Ryan won the seat.", "rows": [{"y": "2012", "t": 18, "d": 5, "r": 13, "o": 0, "u": false}, {"y": "2014", "t": 18, "d": 5, "r": 13, "o": 0, "u": false}, {"y": "2016", "t": 18, "d": 6, "r": 12, "o": 0, "u": false}, {"y": "2018", "t": 18, "d": 6, "r": 12, "o": 0, "u": false}, {"y": "2020", "t": 18, "d": 4, "r": 14, "o": 0, "u": false}, {"y": "2022", "t": 18, "d": 1, "r": 17, "o": 0, "u": false}, {"y": "2024", "t": 18, "d": 1, "r": 17, "o": 0, "u": false}, {"y": "2026", "t": 18, "d": 0, "r": 18, "o": 0, "u": true}], "close": []}, {"id": "kane", "name": "Kane County", "note": "", "rows": [{"y": "2012", "t": 24, "d": 10, "r": 14, "o": 0, "u": false}, {"y": "2014", "t": 24, "d": 10, "r": 14, "o": 0, "u": false}, {"y": "2016", "t": 24, "d": 10, "r": 14, "o": 0, "u": false}, {"y": "2018", "t": 24, "d": 12, "r": 12, "o": 0, "u": false}, {"y": "2020", "t": 24, "d": 13, "r": 11, "o": 0, "u": false}, {"y": "2022", "t": 24, "d": 16, "r": 8, "o": 0, "u": false}, {"y": "2024", "t": 24, "d": 17, "r": 7, "o": 0, "u": false}, {"y": "2026", "t": 24, "d": 21, "r": 3, "o": 0, "u": true}], "close": ["District 5: Democrat Philip Silagi leads Republican Bill Lenert by 11 votes.", "District 15: Democrat Kate Monteleone leads Republican David Young by 113 votes.", "District 9: Democrat Marc A. Guttke leads Republican Jennifer Abbatacola by 132 votes."]}, {"id": "kankakee", "name": "Kankakee County", "note": "Gray seats are one Libertarian (2020) and two members elected in 2014 whose party was not listed on official results (2016).", "rows": [{"y": "2016", "t": 28, "d": 6, "r": 20, "o": 2, "u": false}, {"y": "2018", "t": 28, "d": 6, "r": 22, "o": 0, "u": false}, {"y": "2020", "t": 28, "d": 7, "r": 20, "o": 1, "u": false}, {"y": "2022", "t": 28, "d": 6, "r": 22, "o": 0, "u": false}, {"y": "2024", "t": 28, "d": 6, "r": 22, "o": 0, "u": false}, {"y": "2026", "t": 28, "d": 9, "r": 19, "o": 0, "u": true}], "close": ["District 21: Democrat Marta Perales leads Republican Steven Taden by 11 votes."]}, {"id": "kendall", "name": "Kendall County", "note": "The first bar shows the board before the 2026 election.", "rows": [{"y": "Before 2026", "t": 10, "d": 3, "r": 7, "o": 0, "u": false}, {"y": "2026", "t": 10, "d": 5, "r": 5, "o": 0, "u": true}], "close": []}, {"id": "lasalle", "name": "La Salle County", "note": "", "rows": [{"y": "2012", "t": 29, "d": 14, "r": 15, "o": 0, "u": false}, {"y": "2014", "t": 29, "d": 12, "r": 17, "o": 0, "u": false}, {"y": "2016", "t": 29, "d": 11, "r": 18, "o": 0, "u": false}, {"y": "2018", "t": 29, "d": 12, "r": 17, "o": 0, "u": false}, {"y": "2020", "t": 29, "d": 12, "r": 17, "o": 0, "u": false}, {"y": "2022", "t": 29, "d": 11, "r": 18, "o": 0, "u": false}, {"y": "2024", "t": 29, "d": 9, "r": 20, "o": 0, "u": false}, {"y": "2026", "t": 29, "d": 9, "r": 20, "o": 0, "u": true}], "close": []}, {"id": "lake", "name": "Lake County", "note": "The board shrank from 21 to 19 seats after 2022 redistricting.", "rows": [{"y": "2012", "t": 21, "d": 8, "r": 13, "o": 0, "u": false}, {"y": "2014", "t": 21, "d": 7, "r": 14, "o": 0, "u": false}, {"y": "2016", "t": 21, "d": 7, "r": 14, "o": 0, "u": false}, {"y": "2018", "t": 21, "d": 12, "r": 9, "o": 0, "u": false}, {"y": "2020", "t": 21, "d": 15, "r": 6, "o": 0, "u": false}, {"y": "2022", "t": 19, "d": 14, "r": 5, "o": 0, "u": false}, {"y": "2024", "t": 19, "d": 14, "r": 5, "o": 0, "u": false}, {"y": "2026", "t": 19, "d": 17, "r": 2, "o": 0, "u": true}], "close": []}, {"id": "lee", "name": "Lee County", "note": "The board shrank from 24 to 20 seats after 2022 redistricting. One seat was vacant after the 2024 election and is shown in gray.", "rows": [{"y": "2012", "t": 24, "d": 4, "r": 20, "o": 0, "u": false}, {"y": "2016", "t": 24, "d": 3, "r": 21, "o": 0, "u": false}, {"y": "2018", "t": 24, "d": 3, "r": 21, "o": 0, "u": false}, {"y": "2020", "t": 24, "d": 3, "r": 21, "o": 0, "u": false}, {"y": "2022", "t": 20, "d": 0, "r": 20, "o": 0, "u": false}, {"y": "2024", "t": 20, "d": 0, "r": 19, "o": 1, "u": false}, {"y": "2026", "t": 20, "d": 1, "r": 19, "o": 0, "u": true}], "close": ["District 3, second seat: Democrat David J. Bally leads Republican Jason Todd Anderson by 71 votes."]}, {"id": "mchenry", "name": "McHenry County", "note": "The board shrank from 24 to 18 seats after 2022 redistricting.", "rows": [{"y": "2020", "t": 24, "d": 8, "r": 16, "o": 0, "u": false}, {"y": "2022", "t": 18, "d": 5, "r": 13, "o": 0, "u": false}, {"y": "2024", "t": 18, "d": 3, "r": 15, "o": 0, "u": false}, {"y": "2026", "t": 18, "d": 8, "r": 10, "o": 0, "u": true}], "close": ["District 9: Democrat Christine B. Hamm leads Republican Niko Kanakaris by 262 votes."]}, {"id": "ogle", "name": "Ogle County", "note": "", "rows": [{"y": "2018", "t": 24, "d": 1, "r": 23, "o": 0, "u": false}, {"y": "2020", "t": 24, "d": 1, "r": 23, "o": 0, "u": false}, {"y": "2022", "t": 24, "d": 0, "r": 24, "o": 0, "u": false}, {"y": "2024", "t": 24, "d": 0, "r": 24, "o": 0, "u": false}, {"y": "2026", "t": 24, "d": 0, "r": 24, "o": 0, "u": true}], "close": []}, {"id": "putnam", "name": "Putnam County", "note": "All five board members are elected at large.", "rows": [{"y": "2024", "t": 5, "d": 5, "r": 0, "o": 0, "u": false}, {"y": "2026", "t": 5, "d": 5, "r": 0, "o": 0, "u": true}], "close": []}, {"id": "whiteside", "name": "Whiteside County", "note": "The 2016 bar shows the board as of February 2018.", "rows": [{"y": "2016", "t": 27, "d": 16, "r": 11, "o": 0, "u": false}, {"y": "2018", "t": 27, "d": 16, "r": 11, "o": 0, "u": false}, {"y": "2020", "t": 27, "d": 15, "r": 12, "o": 0, "u": false}, {"y": "2022", "t": 27, "d": 10, "r": 17, "o": 0, "u": false}, {"y": "2024", "t": 27, "d": 10, "r": 17, "o": 0, "u": false}, {"y": "2026", "t": 27, "d": 12, "r": 15, "o": 0, "u": true}], "close": ["District 1, fifth seat: Democrat Vincent Joseph Vaughn leads Republican Kurt Glazier by 32 votes."]}, {"id": "will", "name": "Will County", "note": "The board shrank from 27 to 26 seats after 2012 redistricting and to 22 seats after 2022 redistricting.", "rows": [{"y": "2010", "t": 27, "d": 11, "r": 16, "o": 0, "u": false}, {"y": "2012", "t": 26, "d": 12, "r": 14, "o": 0, "u": false}, {"y": "2014", "t": 26, "d": 11, "r": 15, "o": 0, "u": false}, {"y": "2016", "t": 26, "d": 10, "r": 16, "o": 0, "u": false}, {"y": "2018", "t": 26, "d": 14, "r": 12, "o": 0, "u": false}, {"y": "2020", "t": 26, "d": 14, "r": 12, "o": 0, "u": false}, {"y": "2022", "t": 22, "d": 11, "r": 11, "o": 0, "u": false}, {"y": "2024", "t": 22, "d": 11, "r": 11, "o": 0, "u": false}, {"y": "2026", "t": 22, "d": 13, "r": 9, "o": 0, "u": true}], "close": []}];
  var SOURCE = "Source: Illinois State Board of Elections; county clerks; Shaw Local reporting.";
  var C = { d: "#2a78d6", r: "#e34948", o: "#86857f" };

  var CSS = [
    ":host{all:initial;display:block;}",
    ".w{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.4;color:#1a1a1a;background:#fff;max-width:720px;margin:0 auto;padding:16px 0;box-sizing:border-box;}",
    ".w *{box-sizing:border-box;}",
    "h2{font-size:24px;line-height:1.25;margin:0 0 6px;font-weight:700;}",
    ".dek{font-size:17px;margin:0 0 14px;color:#333;}",
    ".ctl{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 14px;}",
    "label.lab{font-size:16px;font-weight:600;}",
    "select{font:inherit;font-size:16px;padding:8px 36px 8px 12px;border:1px solid #8a8a8a;border-radius:6px;background:#fff url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%23333' stroke-width='2'/%3E%3C/svg%3E\") no-repeat right 12px center;-webkit-appearance:none;appearance:none;color:#1a1a1a;min-width:240px;max-width:100%;}",
    "button{font:inherit;font-size:16px;font-weight:600;background:#162b75;color:#fff;border:0;border-radius:6px;padding:9px 16px;cursor:pointer;}",
    "button:hover{background:#0f1f57;}",
    "button:focus-visible,select:focus-visible,.seg:focus-visible{outline:3px solid #f2b705;outline-offset:2px;}",
    ".sum{font-size:18px;margin:0 0 14px;}",
    ".sum b{font-weight:700;}",
    ".leg{display:flex;flex-wrap:wrap;gap:16px;margin:0 0 12px;font-size:16px;}",
    ".leg span{display:inline-flex;align-items:center;gap:6px;}",
    ".sw{width:14px;height:14px;border-radius:3px;display:inline-block;}",
    ".rows{position:relative;}",
    ".row{display:grid;grid-template-columns:96px 1fr;gap:10px;align-items:center;margin:0 0 10px;}",
    ".yr{font-size:16px;font-weight:600;line-height:1.2;}",
    ".yr small{display:block;font-size:16px;font-weight:400;font-style:italic;color:#555;}",
    ".bw{display:flex;flex-direction:column;gap:3px;}",
    ".bar{display:flex;gap:2px;height:30px;}",
    ".seg{height:30px;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;font-weight:700;cursor:default;min-width:0;}",
    ".seg.lo{color:#1a1a1a;}",
    ".meta{font-size:16px;color:#444;}",
    ".note{font-size:16px;color:#333;margin:12px 0 0;}",
    ".close{margin:14px 0 0;padding:10px 12px;border-left:4px solid #eda100;background:#fdf6e6;}",
    ".close p{margin:0 0 6px;font-size:16px;font-weight:700;}",
    ".close ul{margin:0;padding:0 0 0 20px;}",
    ".close li{font-size:16px;margin:0 0 4px;}",
    ".flag{display:inline-block;font-size:16px;font-weight:700;color:#7a4f00;}",
    ".src{font-size:16px;font-style:italic;color:#555;margin:12px 0 0;}",
    ".cred{font-size:16px;color:#555;margin:4px 0 0;}",
    ".tip{position:absolute;pointer-events:none;background:#1a1a1a;color:#fff;font-size:16px;padding:8px 10px;border-radius:6px;white-space:nowrap;z-index:5;display:none;}",
    "table{border-collapse:collapse;width:100%;font-size:16px;margin:4px 0 0;font-variant-numeric:tabular-nums;}",
    "th,td{text-align:right;padding:6px 8px;border-bottom:1px solid #ddd;}",
    "th:first-child,td:first-child{text-align:left;}",
    "thead th{font-weight:700;border-bottom:2px solid #999;}","tbody th{font-weight:600;}",
    ".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;}"
  ].join("");

  function fmt(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
  function plural(n, one, many) { return fmt(n) + " " + (n === 1 ? one : many); }
  function majority(r) {
    var need = Math.floor(r.t / 2) + 1;
    if (r.d >= need) return "Democratic majority";
    if (r.r >= need) return "Republican majority";
    if (r.d === r.r) return "Tied";
    return "No majority";
  }
  function yearLabel(r) { return r.y === "Before 2026" ? "Before the 2026 election" : "After the " + r.y + " election"; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function init(host) {
    if (host.shadowRoot) return;
    var root = host.attachShadow({ mode: "open" });
    var st = document.createElement("style"); st.textContent = CSS; root.appendChild(st);
    var w = el("div", "w"); root.appendChild(w);

    w.appendChild(el("h2", null, "Blue Wave: Who controls the county board?"));
    w.appendChild(el("p", "dek", "Seats held by each party on county boards across northern Illinois after each general election. Results for 2026 are unofficial until counties certify them."));

    var ctl = el("div", "ctl");
    var uid = "c" + Math.random().toString(36).slice(2, 8);
    var lab = el("label", "lab", "County"); lab.htmlFor = uid;
    var sel = el("select"); sel.id = uid;
    DATA.forEach(function (c, i) { var o = el("option", null, c.name); o.value = c.id; sel.appendChild(o); });
    var btn = el("button", null, "View as table"); btn.type = "button"; btn.setAttribute("aria-pressed", "false");
    ctl.appendChild(lab); ctl.appendChild(sel); ctl.appendChild(btn);
    w.appendChild(ctl);

    var sum = el("p", "sum"); sum.setAttribute("aria-live", "polite"); w.appendChild(sum);
    var leg = el("div", "leg");
    [["d", "Democrat"], ["r", "Republican"], ["o", "Other or vacant"]].forEach(function (p) {
      var s = el("span"); var sw = el("span", "sw"); sw.style.background = C[p[0]]; s.appendChild(sw); s.appendChild(document.createTextNode(p[1])); leg.appendChild(s);
    });
    w.appendChild(leg);
    var body = el("div", "rows"); w.appendChild(body);
    var tip = el("div", "tip"); body.appendChild(tip);
    var close = el("div", "close"); w.appendChild(close);
    var note = el("p", "note"); w.appendChild(note);
    w.appendChild(el("p", "src", SOURCE));
    w.appendChild(el("p", "cred", "Created by Emily K. Coleman"));

    var asTable = false;
    var pre = (host.getAttribute("data-county") || "").toLowerCase();
    try { var q = new URLSearchParams(location.search).get("county"); if (q) pre = q.toLowerCase(); } catch (e) {}
    if (pre && DATA.some(function (c) { return c.id === pre; })) sel.value = pre;
    else sel.value = "dupage";

    function showTip(e, text) {
      tip.textContent = text; tip.style.display = "block";
      var b = body.getBoundingClientRect(), t = e.target.getBoundingClientRect();
      var x = t.left - b.left + t.width / 2 - tip.offsetWidth / 2;
      x = Math.max(0, Math.min(x, b.width - tip.offsetWidth));
      tip.style.left = x + "px"; tip.style.top = (t.top - b.top - tip.offsetHeight - 6) + "px";
    }
    function hideTip() { tip.style.display = "none"; }

    function fitLabels() {
      body.querySelectorAll(".seg").forEach(function (s) {
        var n = s.getAttribute("data-n");
        s.textContent = (s.getBoundingClientRect().width >= (n.length * 10 + 12)) ? n : "";
      });
    }

    function render() {
      var c = DATA.filter(function (x) { return x.id === sel.value; })[0];
      Array.prototype.slice.call(body.childNodes).forEach(function (n) { if (n !== tip) body.removeChild(n); });
      var last = c.rows[c.rows.length - 1];
      sum.innerHTML = "";
      sum.appendChild(document.createTextNode(yearLabel(last) + (last.u ? " (unofficial)" : "") + ": "));
      sum.appendChild(el("b", null, "Democrats hold " + fmt(last.d) + " of " + fmt(last.t) + " seats"));
      sum.appendChild(document.createTextNode("; Republicans hold " + fmt(last.r) + (last.o ? "; " + plural(last.o, "seat is", "seats are") + " vacant or held by another party." : ".")));
      note.textContent = c.note; note.style.display = c.note ? "block" : "none";
      close.innerHTML = "";
      if (c.close && c.close.length) {
        close.appendChild(el("p", null, (c.close.length === 1 ? "Close race" : "Close races") + " to watch: Mail ballots postmarked by Election Day can arrive through Nov. 17 and could change " + (c.close.length === 1 ? "this result." : "these results.")));
        var ul = el("ul"); c.close.forEach(function (s) { ul.appendChild(el("li", null, s)); }); close.appendChild(ul);
        close.style.display = "block";
      } else close.style.display = "none";
      leg.style.display = asTable ? "none" : "flex";

      if (asTable) {
        var tb = el("table"); var cap = el("caption", "sr", c.name + " board seats by party"); tb.appendChild(cap);
        var hr = el("tr"); ["Election", "Democrats", "Republicans", "Other or vacant", "Total seats", "Control"].forEach(function (h) { var th = el("th", null, h); th.scope = "col"; hr.appendChild(th); });
        var th0 = el("thead"); th0.appendChild(hr); tb.appendChild(th0);
        var tbd = el("tbody");
        c.rows.forEach(function (r) {
          var tr = el("tr");
          [r.y + (r.u ? " (unofficial)" : ""), fmt(r.d), fmt(r.r), fmt(r.o), fmt(r.t), majority(r)].forEach(function (v, i) { var td = el(i ? "td" : "th", null, v); if (!i) td.scope = "row"; tr.appendChild(td); });
          tbd.appendChild(tr);
        });
        tb.appendChild(tbd); body.appendChild(tb);
        return;
      }
      var maxT = Math.max.apply(null, c.rows.map(function (r) { return r.t; }));
      c.rows.forEach(function (r) {
        var row = el("div", "row");
        var yr = el("div", "yr", r.y); if (r.u) yr.appendChild(el("small", null, "Unofficial"));
        var bw = el("div", "bw");
        var bar = el("div", "bar"); bar.style.width = (100 * r.t / maxT) + "%";
        bar.setAttribute("role", "img");
        bar.setAttribute("aria-label", r.y + (r.u ? " unofficial" : "") + ": " + plural(r.d, "Democrat", "Democrats") + ", " + plural(r.r, "Republican", "Republicans") + (r.o ? ", " + fmt(r.o) + " other or vacant" : "") + " of " + fmt(r.t) + " seats. " + majority(r) + ".");
        [["d", r.d, "Democrats"], ["o", r.o, "Other or vacant"], ["r", r.r, "Republicans"]].forEach(function (p) {
          if (!p[1]) return;
          var s = el("div", "seg" + (p[0] === "o" ? " lo" : ""));
          s.style.background = C[p[0]]; s.style.flex = p[1] + " 1 0"; s.setAttribute("data-n", fmt(p[1]));
          s.tabIndex = 0;
          var label = p[2] + ": " + fmt(p[1]) + " of " + fmt(r.t) + " seats (" + r.y + (r.u ? ", unofficial" : "") + ")";
          s.setAttribute("aria-label", label);
          s.addEventListener("mouseenter", function (e) { showTip(e, label); });
          s.addEventListener("focus", function (e) { showTip(e, label); });
          s.addEventListener("mouseleave", hideTip); s.addEventListener("blur", hideTip);
          bar.appendChild(s);
        });
        bw.appendChild(bar);
        var meta = el("div", "meta", majority(r) + " · " + fmt(r.t) + " seats");
        if (r.u && c.close && c.close.length) { meta.appendChild(document.createTextNode(" · ")); meta.appendChild(el("span", "flag", "⚑ " + c.close.length + (c.close.length === 1 ? " close race" : " close races"))); }
        bw.appendChild(meta);
        row.appendChild(yr); row.appendChild(bw); body.appendChild(row);
      });
      fitLabels();
    }
    sel.addEventListener("change", render);
    btn.addEventListener("click", function () { asTable = !asTable; btn.textContent = asTable ? "View as chart" : "View as table"; btn.setAttribute("aria-pressed", String(asTable)); render(); });
    if (window.ResizeObserver) new ResizeObserver(function () { if (!asTable) fitLabels(); }).observe(w);
    render();
  }
  function boot() { document.querySelectorAll(".slm-board-makeup").forEach(init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();

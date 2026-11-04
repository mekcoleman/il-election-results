/* Shaw Local – Voter turnout widget.
   Embed: <div class="slm-turnout" data-county="kane"></div>
          <script src="URL/turnout.js"></script>
   Optional data-county (or ?county= in the page URL) presets the place; default is Kane. */
(function () {
  var DATA = {"places": [{"id": "bureau", "name": "Bureau County", "rows": [{"y": 2010, "reg": 23782, "b": 12969, "u": false}, {"y": 2012, "reg": 23588, "b": 16786, "u": false}, {"y": 2014, "reg": 24311, "b": 12956, "u": false}, {"y": 2016, "reg": 24087, "b": 16771, "u": false}, {"y": 2018, "reg": 23847, "b": 13840, "u": false}, {"y": 2020, "reg": 23651, "b": 17609, "u": false}, {"y": 2022, "reg": 23600, "b": 12873, "u": false}, {"y": 2024, "reg": 22738, "b": 16197, "u": false}, {"y": 2026, "reg": 20675, "b": 12195, "u": true}]}, {"id": "carroll", "name": "Carroll County", "rows": [{"y": 2010, "reg": 11895, "b": 5242, "u": false}, {"y": 2012, "reg": 11182, "b": 7429, "u": false}, {"y": 2014, "reg": 11440, "b": 5681, "u": false}, {"y": 2016, "reg": 11008, "b": 7566, "u": false}, {"y": 2018, "reg": 10682, "b": 6039, "u": false}, {"y": 2020, "reg": 10424, "b": 8096, "u": false}, {"y": 2022, "reg": 10357, "b": 6070, "u": false}, {"y": 2024, "reg": 10405, "b": 7922, "u": false}, {"y": 2026, "reg": 10791, "b": 6198, "u": true}]}, {"id": "cook", "name": "Cook County, including Chicago", "rows": [{"y": 2010, "reg": 2704993, "b": 1424959, "u": false}, {"y": 2012, "reg": 2781182, "b": 2030563, "u": false}, {"y": 2014, "reg": 2767432, "b": 1364436, "u": false}, {"y": 2016, "reg": 3082719, "b": 2205504, "u": false}, {"y": 2018, "reg": 3090800, "b": 1795518, "u": false}, {"y": 2020, "reg": 3253333, "b": 2349010, "u": false}, {"y": 2022, "reg": 3189527, "b": 1458690, "u": false}, {"y": 2024, "reg": 3138913, "b": 2108301, "u": false}, {"y": 2026, "reg": 3287333, "b": 1402300, "u": true}]}, {"id": "suburban-cook", "name": "Suburban Cook County", "rows": [{"y": 2010, "reg": 1370186, "b": 719090, "u": false}, {"y": 2012, "reg": null, "b": 1001693, "u": false}, {"y": 2014, "reg": 1398724, "b": 696403, "u": false}, {"y": 2016, "reg": 1512190, "b": 1089840, "u": false}, {"y": 2018, "reg": 1587447, "b": 883457, "u": false}, {"y": 2020, "reg": 1669040, "b": 1188017, "u": false}, {"y": 2022, "reg": 1648709, "b": 743892, "u": false}, {"y": 2024, "reg": 1640040, "b": 1089942, "u": false}, {"y": 2026, "reg": 1750625, "b": 742305, "u": true}]}, {"id": "chicago", "name": "Chicago", "rows": [{"y": 2010, "reg": 1334807, "b": 705869, "u": false}, {"y": 2012, "reg": null, "b": 1028870, "u": false}, {"y": 2014, "reg": 1368708, "b": 668033, "u": false}, {"y": 2016, "reg": 1570529, "b": 1115664, "u": false}, {"y": 2018, "reg": 1503353, "b": 912061, "u": false}, {"y": 2020, "reg": 1584293, "b": 1160993, "u": false}, {"y": 2022, "reg": 1540821, "b": 714798, "u": false}, {"y": 2024, "reg": 1498873, "b": 1018359, "u": false}, {"y": 2026, "reg": 1536708, "b": 659995, "u": true}]}, {"id": "dekalb", "name": "DeKalb County", "rows": [{"y": 2010, "reg": 57102, "b": 29197, "u": false}, {"y": 2012, "reg": 57915, "b": 41428, "u": false}, {"y": 2014, "reg": 58482, "b": 28438, "u": false}, {"y": 2016, "reg": 62119, "b": 43978, "u": false}, {"y": 2018, "reg": 60754, "b": 36610, "u": false}, {"y": 2020, "reg": 65009, "b": 48258, "u": false}, {"y": 2022, "reg": 61517, "b": 34705, "u": false}, {"y": 2024, "reg": 65694, "b": 47842, "u": false}, {"y": 2026, "reg": 69061, "b": 36449, "u": true}]}, {"id": "dupage", "name": "DuPage County", "rows": [{"y": 2010, "reg": 558929, "b": 288680, "u": false}, {"y": 2012, "reg": 560718, "b": 403312, "u": false}, {"y": 2014, "reg": 587216, "b": 288692, "u": false}, {"y": 2016, "reg": 614752, "b": 435143, "u": false}, {"y": 2018, "reg": 639752, "b": 370249, "u": false}, {"y": 2020, "reg": 641503, "b": 491067, "u": false}, {"y": 2022, "reg": 616283, "b": 343734, "u": false}, {"y": 2024, "reg": 627899, "b": 464364, "u": false}, {"y": 2026, "reg": 634871, "b": 334647, "u": true}]}, {"id": "grundy", "name": "Grundy County", "rows": [{"y": 2010, "reg": 29708, "b": 16973, "u": false}, {"y": 2012, "reg": 30820, "b": 21419, "u": false}, {"y": 2014, "reg": 30095, "b": 16780, "u": false}, {"y": 2016, "reg": 32626, "b": 23474, "u": false}, {"y": 2018, "reg": 33041, "b": 19646, "u": false}, {"y": 2020, "reg": 33656, "b": 26895, "u": false}, {"y": 2022, "reg": 34048, "b": 19587, "u": false}, {"y": 2024, "reg": 35637, "b": 26788, "u": false}, {"y": 2026, "reg": 36127, "b": 18638, "u": true}]}, {"id": "kane", "name": "Kane County", "rows": [{"y": 2010, "reg": 260429, "b": 129050, "u": false}, {"y": 2012, "reg": 272843, "b": 182747, "u": false}, {"y": 2014, "reg": 275885, "b": 126912, "u": false}, {"y": 2016, "reg": 300293, "b": 204393, "u": false}, {"y": 2018, "reg": 314170, "b": 172056, "u": false}, {"y": 2020, "reg": 318506, "b": 234751, "u": false}, {"y": 2022, "reg": 301004, "b": 159613, "u": false}, {"y": 2024, "reg": 304232, "b": 225945, "u": false}, {"y": 2026, "reg": 292309, "b": 167714, "u": true}]}, {"id": "kankakee", "name": "Kankakee County", "rows": [{"y": 2010, "reg": 64306, "b": 32999, "u": false}, {"y": 2012, "reg": 64366, "b": 45864, "u": false}, {"y": 2014, "reg": 61292, "b": 34576, "u": false}, {"y": 2016, "reg": 64829, "b": 47785, "u": false}, {"y": 2018, "reg": 68513, "b": 37012, "u": false}, {"y": 2020, "reg": 67051, "b": 50303, "u": false}, {"y": 2022, "reg": 65500, "b": 35687, "u": false}, {"y": 2024, "reg": 66302, "b": 48173, "u": false}, {"y": 2026, "reg": 68874, "b": 34685, "u": true}]}, {"id": "kendall", "name": "Kendall County", "rows": [{"y": 2010, "reg": 65153, "b": 31538, "u": false}, {"y": 2012, "reg": 68453, "b": 47565, "u": false}, {"y": 2014, "reg": 67829, "b": 32586, "u": false}, {"y": 2016, "reg": 75755, "b": 54495, "u": false}, {"y": 2018, "reg": 78788, "b": 45534, "u": false}, {"y": 2020, "reg": 84165, "b": 64552, "u": false}, {"y": 2022, "reg": 84619, "b": 45532, "u": false}, {"y": 2024, "reg": 92076, "b": 66808, "u": false}, {"y": 2026, "reg": 96942, "b": 49422, "u": true}]}, {"id": "lasalle", "name": "La Salle County", "rows": [{"y": 2010, "reg": 73051, "b": 34423, "u": false}, {"y": 2012, "reg": 71565, "b": 47748, "u": false}, {"y": 2014, "reg": 67532, "b": 35823, "u": false}, {"y": 2016, "reg": 70850, "b": 50401, "u": false}, {"y": 2018, "reg": 71111, "b": 40691, "u": false}, {"y": 2020, "reg": 73034, "b": 54087, "u": false}, {"y": 2022, "reg": 70871, "b": 39919, "u": false}, {"y": 2024, "reg": 73745, "b": 53072, "u": false}, {"y": 2026, "reg": 76032, "b": 38577, "u": true}]}, {"id": "lake", "name": "Lake County", "rows": [{"y": 2010, "reg": 404637, "b": 207499, "u": false}, {"y": 2012, "reg": 406567, "b": 289385, "u": false}, {"y": 2014, "reg": 404004, "b": 202532, "u": false}, {"y": 2016, "reg": 430436, "b": 306829, "u": false}, {"y": 2018, "reg": 448295, "b": 254217, "u": false}, {"y": 2020, "reg": 487186, "b": 337976, "u": false}, {"y": 2022, "reg": 459794, "b": 230574, "u": false}, {"y": 2024, "reg": 448174, "b": 315616, "u": false}, {"y": 2026, "reg": 470713, "b": 222492, "u": true}]}, {"id": "lee", "name": "Lee County", "rows": [{"y": 2010, "reg": 25723, "b": 11075, "u": false}, {"y": 2012, "reg": 21843, "b": 15439, "u": false}, {"y": 2014, "reg": 23335, "b": 11455, "u": false}, {"y": 2016, "reg": 22919, "b": 15707, "u": false}, {"y": 2018, "reg": 22496, "b": 12742, "u": false}, {"y": 2020, "reg": 22291, "b": 16547, "u": false}, {"y": 2022, "reg": 21557, "b": 12318, "u": false}, {"y": 2024, "reg": 22023, "b": 16290, "u": false}, {"y": 2026, "reg": 22398, "b": 12270, "u": true}]}, {"id": "mchenry", "name": "McHenry County", "rows": [{"y": 2010, "reg": 202033, "b": 95339, "u": false}, {"y": 2012, "reg": 203225, "b": 134550, "u": false}, {"y": 2014, "reg": 206197, "b": 94609, "u": false}, {"y": 2016, "reg": 218178, "b": 145254, "u": false}, {"y": 2018, "reg": 235593, "b": 117838, "u": false}, {"y": 2020, "reg": 237640, "b": 165515, "u": false}, {"y": 2022, "reg": 226709, "b": 117032, "u": false}, {"y": 2024, "reg": 204366, "b": 163996, "u": false}, {"y": 2026, "reg": 220335, "b": 115305, "u": true}]}, {"id": "ogle", "name": "Ogle County", "rows": [{"y": 2010, "reg": 40973, "b": 17461, "u": false}, {"y": 2012, "reg": 34994, "b": 23533, "u": false}, {"y": 2014, "reg": 33852, "b": 17279, "u": false}, {"y": 2016, "reg": 33627, "b": 24460, "u": false}, {"y": 2018, "reg": 32316, "b": 19267, "u": false}, {"y": 2020, "reg": 31786, "b": 26535, "u": false}, {"y": 2022, "reg": 32022, "b": 19647, "u": false}, {"y": 2024, "reg": 33870, "b": 26096, "u": false}, {"y": 2026, "reg": 35426, "b": 19641, "u": true}]}, {"id": "putnam", "name": "Putnam County", "rows": [{"y": 2010, "reg": 4296, "b": 2371, "u": false}, {"y": 2012, "reg": 4248, "b": 3178, "u": false}, {"y": 2014, "reg": 4241, "b": 2636, "u": false}, {"y": 2016, "reg": 4260, "b": 3183, "u": false}, {"y": 2018, "reg": 4289, "b": 2645, "u": false}, {"y": 2020, "reg": 4191, "b": 3419, "u": false}, {"y": 2022, "reg": 4104, "b": 2847, "u": false}, {"y": 2024, "reg": 4116, "b": 3389, "u": false}, {"y": 2026, "reg": 4019, "b": 2482, "u": true}]}, {"id": "whiteside", "name": "Whiteside County", "rows": [{"y": 2010, "reg": 38300, "b": 19240, "u": false}, {"y": 2012, "reg": 38166, "b": 25994, "u": false}, {"y": 2014, "reg": 37510, "b": 17860, "u": false}, {"y": 2016, "reg": 37759, "b": 25875, "u": false}, {"y": 2018, "reg": 37945, "b": 21723, "u": false}, {"y": 2020, "reg": 38436, "b": 27623, "u": false}, {"y": 2022, "reg": 36976, "b": 20271, "u": false}, {"y": 2024, "reg": 37430, "b": 26742, "u": false}, {"y": 2026, "reg": 37781, "b": 19434, "u": true}]}, {"id": "will", "name": "Will County", "rows": [{"y": 2010, "reg": 371079, "b": 196857, "u": false}, {"y": 2012, "reg": 386172, "b": 279352, "u": false}, {"y": 2014, "reg": 393738, "b": 197970, "u": false}, {"y": 2016, "reg": 417813, "b": 310937, "u": false}, {"y": 2018, "reg": 429647, "b": 249682, "u": false}, {"y": 2020, "reg": 463465, "b": 348071, "u": false}, {"y": 2022, "reg": 462483, "b": 234851, "u": false}, {"y": 2024, "reg": 441483, "b": 331367, "u": false}, {"y": 2026, "reg": 466424, "b": 231160, "u": true}]}], "state": [{"y": 2010, "reg": 7506073, "b": 3792770, "u": false}, {"y": 2012, "reg": 7520722, "b": 5279752, "u": false}, {"y": 2014, "reg": 7483031, "b": 3680417, "u": false}, {"y": 2016, "reg": 8029847, "b": 5666118, "u": false}, {"y": 2018, "reg": 8099372, "b": 4635541, "u": false}, {"y": 2020, "reg": 8364099, "b": 6098729, "u": false}, {"y": 2022, "reg": 8115751, "b": 4144125, "u": false}, {"y": 2024, "reg": 8101424, "b": 5705246, "u": false}]};
  var SOURCE = "Source: Illinois State Board of Elections; county clerks; Chicago Board of Election Commissioners.";
  var MID = "#6250d6", PRES = "#c4c3bd", STATE = "#1a1a1a", GRID = "#e4e3df", INK = "#1a1a1a", INK2 = "#555";
  var NOTES = {
    "chicago": "Chicago’s 2026 figures reflect 1,241 of 1,291 precincts reporting.",
    "cook": "Chicago’s 2026 figures reflect 1,241 of 1,291 precincts reporting."
  };
  var SPLIT = "Separate registration figures for Chicago and suburban Cook County are not available for 2012. Use “Show ballots cast” to see every year. Suburban registration for 2014 through 2020 is the Cook County total minus Chicago.";

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
    "button:focus-visible,select:focus-visible,.hit:focus-visible{outline:3px solid #f2b705;outline-offset:2px;}",
    ".sum{font-size:18px;margin:0 0 12px;}",
    ".leg{display:flex;flex-wrap:wrap;gap:16px;margin:0 0 8px;font-size:16px;}",
    ".leg span{display:inline-flex;align-items:center;gap:6px;}",
    ".sw{width:14px;height:14px;border-radius:3px;display:inline-block;}",
    ".dot{width:12px;height:12px;border-radius:50%;display:inline-block;background:" + STATE + ";border:2px solid #fff;box-shadow:0 0 0 1px " + STATE + ";}",
    ".plot{position:relative;}",
    "svg{display:block;overflow:visible;}",
    "svg text{font-family:inherit;font-size:16px;fill:" + INK2 + ";}",
    "svg text.v{fill:" + INK + ";font-weight:700;}",
    ".hit{cursor:default;}",
    ".note{font-size:16px;color:#333;margin:10px 0 0;}",
    ".src{font-size:16px;font-style:italic;color:#555;margin:12px 0 0;}",
    ".cred{font-size:16px;color:#555;margin:4px 0 0;}",
    ".tip{position:absolute;pointer-events:none;background:#1a1a1a;color:#fff;font-size:16px;padding:8px 10px;border-radius:6px;z-index:5;display:none;max-width:280px;}",
    "table{border-collapse:collapse;width:100%;font-size:16px;margin:4px 0 0;font-variant-numeric:tabular-nums;}",
    "th,td{text-align:right;padding:6px 8px;border-bottom:1px solid #ddd;}",
    "th:first-child,td:first-child{text-align:left;}",
    "thead th{font-weight:700;border-bottom:2px solid #999;}",
    "tbody th{font-weight:600;}",
    ".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;}"
  ].join("");

  var NS = "http://www.w3.org/2000/svg";
  function fmt(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
  function pct(r) { return r.reg ? 100 * r.b / r.reg : null; }
  function p1(v) { return v.toFixed(1) + "%"; }
  function isMid(y) { return y % 4 === 2; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function sv(tag, attrs, text) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; return e; }
  function compact(n) { return n >= 1e6 ? (n / 1e6).toFixed(n % 1e6 ? 1 : 0) + "M" : n >= 1e3 ? Math.round(n / 1e3) + "K" : String(n); }
  function nice(max) { var e = Math.pow(10, Math.floor(Math.log10(max))), f = max / e; var s = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10; return s * e; }

  function init(host) {
    if (host.shadowRoot) return;
    var root = host.attachShadow({ mode: "open" });
    var st = document.createElement("style"); st.textContent = CSS; root.appendChild(st);
    var w = el("div", "w"); root.appendChild(w);
    w.appendChild(el("h2", null, "Blue Wave: Did more voters turn out?"));
    w.appendChild(el("p", "dek", "Share of registered voters who cast a ballot in each general election. Midterm years, when there is no presidential race, are highlighted. Results for 2026 are unofficial."));

    var ctl = el("div", "ctl");
    var uid = "t" + Math.random().toString(36).slice(2, 8);
    var lab = el("label", "lab", "Place"); lab.htmlFor = uid;
    var sel = el("select"); sel.id = uid;
    DATA.places.forEach(function (c) { var o = el("option", null, c.name); o.value = c.id; sel.appendChild(o); });
    var bMode = el("button", null, "Show ballots cast"); bMode.type = "button"; bMode.setAttribute("aria-pressed", "false");
    var bTab = el("button", null, "View as table"); bTab.type = "button"; bTab.setAttribute("aria-pressed", "false");
    ctl.appendChild(lab); ctl.appendChild(sel); ctl.appendChild(bMode); ctl.appendChild(bTab);
    w.appendChild(ctl);
    var sum = el("p", "sum"); sum.setAttribute("aria-live", "polite"); w.appendChild(sum);
    var leg = el("div", "leg"); w.appendChild(leg);
    var plot = el("div", "plot"); w.appendChild(plot);
    var tip = el("div", "tip");
    var note = el("p", "note"); w.appendChild(note);
    var note2 = el("p", "note", "Figures for 2026 are election-night counts. Mail ballots postmarked by Election Day can still arrive through Nov. 17, so 2026 turnout will rise."); w.appendChild(note2);
    w.appendChild(el("p", "src", SOURCE));
    w.appendChild(el("p", "cred", "Created by Emily K. Coleman"));

    var mode = "pct", asTable = false;
    var pre = (host.getAttribute("data-county") || "").toLowerCase();
    try { var q = new URLSearchParams(location.search).get("county"); if (q) pre = q.toLowerCase(); } catch (e) {}
    sel.value = DATA.places.some(function (c) { return c.id === pre; }) ? pre : "kane";
    var stateBy = {}; DATA.state.forEach(function (r) { stateBy[r.y] = r; });

    function setLegend() {
      leg.innerHTML = "";
      function item(sw, text) { var s = el("span"); s.appendChild(sw); s.appendChild(document.createTextNode(text)); leg.appendChild(s); }
      var a = el("span", "sw"); a.style.background = MID; item(a, "Midterm election");
      var b = el("span", "sw"); b.style.background = PRES; item(b, "Presidential election");
      if (mode === "pct") item(el("span", "dot"), "Illinois statewide");
      leg.style.display = asTable ? "none" : "flex";
    }

    function render() {
      var c = DATA.places.filter(function (x) { return x.id === sel.value; })[0];
      var rows = c.rows;
      var last = rows[rows.length - 1], prevMid = rows.filter(function (r) { return r.y === last.y - 4; })[0];
      sum.innerHTML = "";
      if (pct(last) != null) {
        sum.appendChild(document.createTextNode("2026 turnout (unofficial): "));
        sum.appendChild(el("b", null, p1(pct(last))));
        if (prevMid && pct(prevMid) != null) sum.appendChild(document.createTextNode(", compared with " + p1(pct(prevMid)) + " in 2022."));
        else sum.appendChild(document.createTextNode("."));
      } else {
        sum.appendChild(document.createTextNode("Ballots cast in 2026 (unofficial): "));
        sum.appendChild(el("b", null, fmt(last.b)));
        sum.appendChild(document.createTextNode("."));
      }
      var n = NOTES[c.id] || "";
      if (c.id === "suburban-cook" || c.id === "chicago") n = (n ? n + " " : "") + SPLIT;
      note.textContent = n; note.style.display = n ? "block" : "none";
      setLegend();
      plot.innerHTML = ""; plot.appendChild(tip); tip.style.display = "none";

      if (asTable) {
        var tb = el("table"); tb.appendChild(el("caption", "sr", c.name + " voter turnout by year"));
        var hr = el("tr"); ["Election", "Registered voters", "Ballots cast", "Turnout", "Illinois turnout"].forEach(function (h) { var th = el("th", null, h); th.scope = "col"; hr.appendChild(th); });
        var th0 = el("thead"); th0.appendChild(hr); tb.appendChild(th0);
        var tbd = el("tbody");
        rows.forEach(function (r) {
          var s = stateBy[r.y], tr = el("tr");
          [r.y + (r.u ? " (unofficial)" : ""), r.reg ? fmt(r.reg) : "Not available", fmt(r.b), pct(r) != null ? p1(pct(r)) : "Not available", s ? p1(pct(s)) : "Not yet available"].forEach(function (v, i) { var td = el(i ? "td" : "th", null, v); if (!i) td.scope = "row"; tr.appendChild(td); });
          tbd.appendChild(tr);
        });
        tb.appendChild(tbd); plot.appendChild(tb); return;
      }

      var W = Math.max(280, plot.clientWidth || w.clientWidth), narrow = W < 520;
      var H = narrow ? 280 : 320, m = { t: 30, r: 8, b: 30, l: mode === "pct" ? 50 : 58 };
      var iw = W - m.l - m.r, ih = H - m.t - m.b;
      var vals = rows.map(function (r) { return mode === "pct" ? pct(r) : r.b; });
      var smax = mode === "pct" ? Math.max.apply(null, rows.map(function (r) { var s = stateBy[r.y]; return s ? pct(s) : 0; })) : 0;
      var top = mode === "pct" ? 100 : nice(Math.max.apply(null, vals.filter(function (v) { return v != null; })) * 1.12);
      var ticks = mode === "pct" ? [0, 25, 50, 75, 100] : [0, top / 4, top / 2, 3 * top / 4, top];
      var svg = sv("svg", { width: W, height: H, role: "img", "aria-label": c.name + " " + (mode === "pct" ? "turnout" : "ballots cast") + " by election year. Use View as table for exact figures." });
      var g = sv("g", { transform: "translate(" + m.l + "," + m.t + ")" }); svg.appendChild(g);
      function y(v) { return ih - ih * v / top; }
      ticks.forEach(function (t) {
        g.appendChild(sv("line", { x1: 0, x2: iw, y1: y(t), y2: y(t), stroke: GRID, "stroke-width": 1 }));
        g.appendChild(sv("text", { x: -8, y: y(t) + 5, "text-anchor": "end" }, mode === "pct" ? t + "%" : compact(t)));
      });
      var slot = iw / rows.length, bw = Math.min(24, slot * 0.6);
      rows.forEach(function (r, i) {
        var cx = slot * i + slot / 2, v = vals[i], mid = isMid(r.y);
        var lbl = narrow ? "’" + String(r.y).slice(2) : String(r.y);
        g.appendChild(sv("text", { x: cx, y: ih + 22, "text-anchor": "middle" }, lbl));
        var s = stateBy[r.y];
        var tipText = r.y + (r.u ? " (unofficial)" : "") + ": " + (v == null ? "registration not available; " + fmt(r.b) + " ballots cast" : mode === "pct" ? p1(v) + " turnout (" + fmt(r.b) + " of " + fmt(r.reg) + " registered voters)" : fmt(r.b) + " ballots cast") + (mode === "pct" && s ? ". Illinois: " + p1(pct(s)) + "." : ".");
        if (v != null) {
          var h = ih - y(v), x0 = cx - bw / 2, rr = Math.min(4, h);
          var d = "M" + x0 + "," + ih + "V" + (ih - h + rr) + "Q" + x0 + "," + (ih - h) + " " + (x0 + rr) + "," + (ih - h) + "H" + (x0 + bw - rr) + "Q" + (x0 + bw) + "," + (ih - h) + " " + (x0 + bw) + "," + (ih - h + rr) + "V" + ih + "Z";
          var bar = sv("path", { d: d, fill: mid ? MID : PRES });
          if (r.u) { bar.setAttribute("fill", "url(#" + uid + "h)"); }
          g.appendChild(bar);
          var showLbl = mid && (!narrow || r.y >= 2022);
          var topY = y(v); if (mode === "pct" && s) topY = Math.min(topY, y(pct(s)) - 6);
          if (showLbl) g.appendChild(sv("text", { x: cx, y: topY - 9, "text-anchor": "middle", "class": "v" }, mode === "pct" ? p1(v) : compact(v)));
        }
        if (mode === "pct" && s) {
          g.appendChild(sv("circle", { cx: cx, cy: y(pct(s)), r: 5, fill: STATE, stroke: "#fff", "stroke-width": 2 }));
        }
        var hit = sv("rect", { x: cx - slot / 2, y: 0, width: slot, height: ih, fill: "transparent", "class": "hit", tabindex: 0, "aria-label": tipText });
        function show() {
          tip.textContent = tipText; tip.style.display = "block";
          var left = m.l + cx - tip.offsetWidth / 2; left = Math.max(0, Math.min(left, W - tip.offsetWidth));
          tip.style.left = left + "px"; tip.style.top = Math.max(0, m.t + (v != null ? y(v) : ih) - tip.offsetHeight - 14) + "px";
        }
        hit.addEventListener("mouseenter", show); hit.addEventListener("focus", show);
        hit.addEventListener("mouseleave", function () { tip.style.display = "none"; }); hit.addEventListener("blur", function () { tip.style.display = "none"; });
        g.appendChild(hit);
      });
      // hatch pattern for unofficial 2026 bar
      var defs = sv("defs"), pat = sv("pattern", { id: uid + "h", width: 8, height: 8, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" });
      pat.appendChild(sv("rect", { width: 8, height: 8, fill: MID }));
      pat.appendChild(sv("line", { x1: 0, y1: 0, x2: 0, y2: 8, stroke: "#fff", "stroke-width": 3, "stroke-opacity": 0.45 }));
      defs.appendChild(pat); svg.insertBefore(defs, svg.firstChild);
      g.appendChild(sv("line", { x1: 0, x2: iw, y1: ih, y2: ih, stroke: "#9a9a96", "stroke-width": 1 }));
      plot.insertBefore(svg, tip);
    }
    sel.addEventListener("change", render);
    bMode.addEventListener("click", function () { mode = mode === "pct" ? "b" : "pct"; bMode.textContent = mode === "pct" ? "Show ballots cast" : "Show turnout rate"; bMode.setAttribute("aria-pressed", String(mode === "b")); render(); });
    bTab.addEventListener("click", function () { asTable = !asTable; bTab.textContent = asTable ? "View as chart" : "View as table"; bTab.setAttribute("aria-pressed", String(asTable)); bMode.style.display = asTable ? "none" : ""; render(); });
    var lastW = 0;
    if (window.ResizeObserver) new ResizeObserver(function () { var cw = plot.clientWidth; if (!asTable && Math.abs(cw - lastW) > 4) { lastW = cw; render(); } }).observe(plot);
    render();
  }
  function boot() { document.querySelectorAll(".slm-turnout").forEach(init); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();

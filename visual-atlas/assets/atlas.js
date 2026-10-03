(function () {
  "use strict";

  var THEME_KEY = "atlas-theme";

  function applyTheme(theme) {
    if (theme === "dark") document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = theme === "dark" ? "Light theme" : "Dark theme";
  }

  function initTheme() {
    var q = new URLSearchParams(location.search).get("theme");
    var stored = null;
    try { stored = localStorage.getItem(THEME_KEY); } catch (e) { stored = null; }
    var theme = q === "dark" || q === "light" ? q : (stored || "light");
    applyTheme(theme);
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
        applyTheme(next);
      });
    }
  }

  function renderLadder(svg, flow, visibleCount) {
    var parties = flow.parties;
    var steps = flow.steps;
    var w = 760;
    var colW = (w - 80) / parties.length;
    var top = 48;
    var rowH = 46;
    var h = top + 28 + steps.length * rowH + 24;
    var ns = "http://www.w3.org/2000/svg";
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", flow.title);

    var title = document.createElementNS(ns, "title");
    title.textContent = flow.title;
    svg.appendChild(title);

    parties.forEach(function (name, i) {
      var x = 40 + i * colW + colW / 2;
      var label = document.createElementNS(ns, "text");
      label.setAttribute("x", x);
      label.setAttribute("y", 22);
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("font-size", "13");
      label.setAttribute("font-weight", "700");
      label.setAttribute("fill", "currentColor");
      label.textContent = name;
      svg.appendChild(label);
      var line = document.createElementNS(ns, "line");
      line.setAttribute("x1", x);
      line.setAttribute("x2", x);
      line.setAttribute("y1", top);
      line.setAttribute("y2", h - 16);
      line.setAttribute("stroke", "currentColor");
      line.setAttribute("stroke-opacity", "0.35");
      line.setAttribute("stroke-dasharray", "4 4");
      svg.appendChild(line);
    });

    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    steps.forEach(function (step, idx) {
      var y = top + 18 + idx * rowH;
      var x1 = 40 + step.from * colW + colW / 2;
      var x2 = 40 + step.to * colW + colW / 2;
      var g = document.createElementNS(ns, "g");
      g.setAttribute("class", idx < visibleCount ? "step-on" : "step-hidden");
      if (idx >= visibleCount) g.setAttribute("opacity", "0");
      var path = document.createElementNS(ns, "line");
      path.setAttribute("x1", x1);
      path.setAttribute("y1", y);
      path.setAttribute("x2", x2);
      path.setAttribute("y2", y);
      path.setAttribute("stroke", step.color || "#2563eb");
      path.setAttribute("stroke-width", "2.5");
      if (step.dashed) path.setAttribute("stroke-dasharray", "6 4");
      g.appendChild(path);
      var dir = x2 >= x1 ? 1 : -1;
      var ah = document.createElementNS(ns, "polygon");
      var ax = x2;
      var pts = [
        ax + "," + y,
        (ax - dir * 10) + "," + (y - 5),
        (ax - dir * 10) + "," + (y + 5)
      ].join(" ");
      ah.setAttribute("points", pts);
      ah.setAttribute("fill", step.color || "#2563eb");
      g.appendChild(ah);
      var t = document.createElementNS(ns, "text");
      t.setAttribute("x", (x1 + x2) / 2);
      t.setAttribute("y", y - 6);
      t.setAttribute("text-anchor", "middle");
      t.setAttribute("font-family", "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace");
      t.setAttribute("font-size", "12");
      t.setAttribute("fill", "currentColor");
      t.textContent = step.label;
      g.appendChild(t);
      if (!reduce && idx === visibleCount - 1) {
        var packet = document.createElementNS(ns, "circle");
        packet.setAttribute("class", "packet");
        packet.setAttribute("r", "5");
        packet.setAttribute("cy", y);
        packet.setAttribute("fill", step.color || "#2563eb");
        var anim = document.createElementNS(ns, "animate");
        anim.setAttribute("attributeName", "cx");
        anim.setAttribute("from", x1);
        anim.setAttribute("to", x2);
        anim.setAttribute("dur", "0.7s");
        anim.setAttribute("fill", "freeze");
        packet.appendChild(anim);
        g.appendChild(packet);
      }
      svg.appendChild(g);
    });
  }

  function mountFlow(root) {
    var flow = root._flow;
    if (!flow) {
      var dataNode = root.querySelector("script.flow-data");
      if (!dataNode) return;
      flow = JSON.parse(dataNode.textContent);
    }
    var svg = root.querySelector("svg.ladder-svg");
    var caption = root.querySelector(".step-caption");
    var status = root.querySelector(".flow-status");
    var transcript = root.querySelector(".transcript ol");
    var i = 0;

    function show(n) {
      i = Math.max(0, Math.min(n, flow.steps.length));
      renderLadder(svg, flow, i);
      if (i === 0) {
        caption.textContent = "Press Next or Play. " + flow.steps.length + " steps.";
      } else {
        var step = flow.steps[i - 1];
        caption.textContent = "Step " + i + " of " + flow.steps.length + ": " + step.label + " — " + (step.caption || "");
      }
      if (status) status.textContent = i + " / " + flow.steps.length;
      var prev = root.querySelector("[data-act=prev]");
      var next = root.querySelector("[data-act=next]");
      if (prev) prev.disabled = i === 0;
      if (next) next.disabled = i === flow.steps.length;
    }

    if (transcript) {
      flow.steps.forEach(function (step, idx) {
        var li = document.createElement("li");
        li.textContent = step.label + " — " + (step.caption || "");
        transcript.appendChild(li);
      });
    }

    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-act]");
      if (!btn || !root.contains(btn)) return;
      var act = btn.getAttribute("data-act");
      if (act === "prev") show(i - 1);
      if (act === "next") show(i + 1);
      if (act === "reset") { stop(); show(0); }
      if (act === "play") play();
    });

    var timer = null;
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
      var play = root.querySelector("[data-act=play]");
      if (play) play.textContent = "Play";
    }
    function play() {
      if (timer) { stop(); return; }
      if (i >= flow.steps.length) show(0);
      var playBtn = root.querySelector("[data-act=play]");
      if (playBtn) playBtn.textContent = "Pause";
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (reduce) { show(flow.steps.length); stop(); return; }
      timer = setInterval(function () {
        if (i >= flow.steps.length) { stop(); return; }
        show(i + 1);
      }, 900);
    }

    root.tabIndex = 0;
    root.addEventListener("keydown", function (ev) {
      if (ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA") return;
      if (ev.key === "ArrowRight") { ev.preventDefault(); show(i + 1); }
      if (ev.key === "ArrowLeft") { ev.preventDefault(); show(i - 1); }
      if (ev.key === " " || ev.key === "Spacebar") { ev.preventDefault(); play(); }
      if (ev.key === "Home") { ev.preventDefault(); stop(); show(0); }
    });

    show(0);
    root._flowApi = { show: show, play: play, stop: stop };
  }

  function initFlows() {
    document.querySelectorAll(".flow-panel").forEach(mountFlow);
  }

  function markDrill(btn) {
    var id = btn.getAttribute("data-drill");
    if (!id) return;
    var store = {};
    try { store = JSON.parse(localStorage.getItem("atlas-drill-progress") || "{}"); } catch (e) { store = {}; }
    if (btn.classList.contains("is-flipped")) store[id] = 1;
    else delete store[id];
    try { localStorage.setItem("atlas-drill-progress", JSON.stringify(store)); } catch (e) {}
    var el = document.getElementById("drill-progress");
    if (el) {
      var n = Object.keys(store).length;
      var total = document.querySelectorAll("[data-drill]").length;
      el.textContent = n + " of " + total + " marked known (this browser only).";
    }
  }

  function initFlips() {
    document.querySelectorAll("button.flip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        btn.classList.toggle("is-flipped");
        var on = btn.classList.contains("is-flipped");
        btn.setAttribute("aria-pressed", on ? "true" : "false");
        markDrill(btn);
      });
    });
  }

  function initSearch() {
    var input = document.getElementById("atlas-search");
    var list = document.getElementById("search-results");
    if (!input || !list || !window.ATLAS_INDEX) return;
    var items = window.ATLAS_INDEX;
    function run() {
      var q = input.value.trim().toLowerCase();
      list.innerHTML = "";
      if (!q) return;
      var hits = items.filter(function (item) {
        return (item.title + " " + item.blurb + " " + (item.tags || "")).toLowerCase().indexOf(q) !== -1;
      }).slice(0, 20);
      hits.forEach(function (item) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = item.href;
        a.textContent = item.title;
        li.appendChild(a);
        var span = document.createElement("span");
        span.textContent = " — " + item.blurb;
        li.appendChild(span);
        list.appendChild(li);
      });
      if (!hits.length) {
        var empty = document.createElement("li");
        empty.textContent = "No matches.";
        list.appendChild(empty);
      }
    }
    input.addEventListener("input", run);
  }

  function initFilter() {
    var input = document.getElementById("term-filter");
    if (!input) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      document.querySelectorAll(".term").forEach(function (el) {
        var text = el.textContent.toLowerCase();
        el.hidden = q && text.indexOf(q) === -1;
      });
    });
  }

  function initHub() {
    var blurb = document.getElementById("island-blurb");
    document.querySelectorAll(".island").forEach(function (node) {
      function show() {
        if (blurb) blurb.textContent = node.getAttribute("data-blurb") || "";
      }
      node.addEventListener("mouseenter", show);
      node.addEventListener("focus", show);
    });
  }

  function initDrills() {
    var store = {};
    try { store = JSON.parse(localStorage.getItem("atlas-drill-progress") || "{}"); } catch (e) { store = {}; }
    document.querySelectorAll("[data-drill]").forEach(function (card) {
      var id = card.getAttribute("data-drill");
      if (store[id]) {
        card.classList.add("is-flipped");
        card.setAttribute("aria-pressed", "true");
      }
    });
    var el = document.getElementById("drill-progress");
    if (!el) return;
    var total = document.querySelectorAll("[data-drill]").length;
    el.textContent = Object.keys(store).length + " of " + total + " marked known (this browser only).";
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initFlows();
    initFlips();
    initSearch();
    initFilter();
    initHub();
    initDrills();
  });
})();

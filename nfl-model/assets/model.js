/* Table controls for the nfl-model section: text filter, status filter, paging.
   Deliberately dependency-free so every page stays inspectable in the HTML source. */
(function () {
  "use strict";

  function statusBucket(value) {
    var v = (value || "").toLowerCase();
    if (v.indexOf("verified") >= 0 && v.indexOf("unverified") < 0) return "verified";
    if (v.indexOf("partial") >= 0 || v.indexOf("review") >= 0 || v.indexOf("derived") >= 0) return "partial";
    if (v.indexOf("open") >= 0 || v.indexOf("blocked") >= 0 || v.indexOf("unverified") >= 0 || v.indexOf("not-") >= 0 || v.indexOf("awaiting") >= 0) return "open";
    return "other";
  }

  function init(wrap) {
    var size = parseInt(wrap.getAttribute("data-page-size") || "25", 10);
    var rows = Array.prototype.slice.call(wrap.querySelectorAll("tbody tr"));
    var search = wrap.querySelector('input[type="search"]');
    var prev = wrap.querySelector("[data-page-prev]");
    var next = wrap.querySelector("[data-page-next]");
    var label = wrap.querySelector(".pager-label");
    var statusBtns = Array.prototype.slice.call(wrap.querySelectorAll("[data-status-filter]"));
    var state = { q: "", status: null, page: 0 };

    function visible() {
      return rows.filter(function (tr) {
        var okQ = !state.q || (tr.textContent || "").toLowerCase().indexOf(state.q) >= 0;
        var okS = !state.status || statusBucket(tr.getAttribute("data-row-status")) === state.status;
        return okQ && okS;
      });
    }

    function render() {
      var list = visible();
      var pages = Math.max(1, Math.ceil(list.length / size));
      if (state.page >= pages) state.page = pages - 1;
      var start = state.page * size;
      var shown = list.slice(start, start + size);
      rows.forEach(function (tr) { tr.hidden = true; });
      shown.forEach(function (tr) { tr.hidden = false; });
      if (label) label.textContent = list.length ? (start + 1) + "-" + (start + shown.length) + " of " + list.length : "0 rows";
      if (prev) prev.disabled = state.page === 0;
      if (next) next.disabled = state.page >= pages - 1;
    }

    if (search) search.addEventListener("input", function () { state.q = search.value.trim().toLowerCase(); state.page = 0; render(); });
    statusBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var want = btn.getAttribute("data-status-filter");
        state.status = state.status === want ? null : want;
        statusBtns.forEach(function (b) { b.classList.toggle("is-on", b.getAttribute("data-status-filter") === state.status); });
        state.page = 0;
        render();
      });
    });
    if (prev) prev.addEventListener("click", function () { state.page -= 1; render(); });
    if (next) next.addEventListener("click", function () { state.page += 1; render(); });
    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    Array.prototype.forEach.call(document.querySelectorAll(".table-wrap[data-table]"), init);
  });
})();

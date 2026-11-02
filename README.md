# Free Time Vacation

A static, source-linked Bay Area sports planning dashboard. Open `index.html` via a web server or deploy the repository root to GitHub Pages. The browser queries MLB's official schedule feed for the selected date; all other entries are a partial manually reviewed snapshot as of 2026-11-02.

**No date or vacation window is certified free.** The project does not contain complete NFL, college football, other sports, postseason or local AM/FM broadcast data. Official future schedules and local carriage can be unannounced; see [Flagged for Review](review.html). All end times are estimates or assumptions, and TBD starts are left blank.

Test with `node tests/test.mjs` and `node tests/ui.mjs`. Serve locally with `python3 -m http.server 8000` and visit `http://localhost:8000/`. The live MLB query needs a working connection and browser cross-origin support; an error is shown if unavailable. A successful empty response does not establish schedule completeness.

# capture status — why `raw/` is empty here

This directory is where `scripts/fetch_nfl_model_sources.py` writes one gzip per captured
official response, and where `../manifest.json` records the URL, HTTP status, retrieval
timestamp, byte count and SHA-256 of each.

**No captures exist yet.** The sandbox that authored this section has no outbound route to
`nfl.com`, `49ers.com`, `nj.gov`, `sbg.colorado.gov`, `the-odds-api.com` or `arxiv.org` — only
`github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org` and `files.pythonhosted.org` are
reachable. Retrieval happened through the agent's page-fetch tool instead, which returns rendered
text but no byte artifact to hash.

Consequences, all disclosed on the site rather than hidden:

1. Every value row in `nfl-model/data/*.json` cites a source with `method: "page-fetched"` or
   `"pdf-fetched"`, meaning the page was read in full, but the reader cannot yet diff it against
   a stored copy. Section flag **IR-025** says so on the sources page.
2. Documents whose *later content* was never retrieved stay blank in the data — New Jersey's
   handle/parlay table (`M-07`) is the example.
3. Sources read only through a search-result snippet are registered as `PARTIAL` and the verifier
   refuses them as the basis of a `VERIFIED` row.

## To close the gap

Run the collector where outbound access exists (CI, via `workflow_dispatch`):

```bash
python3 scripts/fetch_nfl_model_sources.py --season 2026 --week 10
```

It writes `raw/*.gz` + `manifest.json`, asserts the render-integrity rules before accepting a
capture, and exits non-zero on any failed assertion so a truncated page never becomes "no
injuries". After the first successful run, `nfl-model/data/injuries.json` and `depth.json` should
be re-derived from the manifest and the retrieval method upgraded to `repo-snapshot`.

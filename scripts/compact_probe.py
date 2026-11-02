#!/usr/bin/env python3
"""Package official-source probe responses into tracked, compressed research files.

Artifact downloads are not available to the Arena sandbox, so the GitHub Actions
probe publishes its raw responses (gzip-compressed) plus a manifest and the
JSON summary to `research/probe/` on the same fixed branch.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

SRC = Path("probe_out")
DST = Path("research/probe")
RAW = DST / "raw"
RAW.mkdir(parents=True, exist_ok=True)

summary = json.loads((SRC / "summary.json").read_text(encoding="utf-8"))
shutil.copyfile(SRC / "summary.json", DST / "summary.json")

manifest_files = []
raw_total = 0
compressed_total = 0
for path in sorted(SRC.iterdir()):
    if not path.is_file() or path.name == "summary.json":
        continue
    data = path.read_bytes()
    packed = gzip.compress(data, compresslevel=9, mtime=0)
    out = RAW / f"{path.name}.gz"
    out.write_bytes(packed)
    raw_total += len(data)
    compressed_total += len(packed)
    manifest_files.append({
        "file": str(out),
        "source": path.name,
        "raw_bytes": len(data),
        "compressed_bytes": len(packed),
        "sha256_raw": hashlib.sha256(data).hexdigest(),
    })

manifest = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
    "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
    "github_sha": os.environ.get("GITHUB_SHA", ""),
    "source_count": len(manifest_files),
    "raw_bytes": raw_total,
    "compressed_bytes": compressed_total,
    "files": manifest_files,
    "sources": summary,
}
(DST / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
(DST / "README.md").write_text(
    "# Official-source probe snapshot\n\n"
    "These are raw responses fetched by `.github/workflows/probe-sources.yml` on a GitHub-hosted runner. "
    "Each file in `raw/` is gzip-compressed; `summary.json` and `manifest.json` record HTTP status, "
    "URL, byte counts and SHA-256. The capture is for offline verification and is not a claim that "
    "unreleased future schedules exist.\n",
    encoding="utf-8",
)
print(f"Packaged {len(manifest_files)} raw responses: {raw_total:,} raw bytes -> {compressed_total:,} compressed bytes")

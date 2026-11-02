#!/usr/bin/env python3
"""No-op compatibility shim.

PR #10's redirect generator is preserved verbatim in
`research/legacy/generate_legacy_redirects_9d83abee.py`. The final integration
publishes the root dashboard and keeps legacy trees linked directly, so the old
permalink overrides are intentionally not regenerated.
"""
print('Final integration keeps legacy trees linked; PR #10 redirect generator preserved in research/legacy/.')

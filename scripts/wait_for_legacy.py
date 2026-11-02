#!/usr/bin/env python3
"""Keep the legacy Pages publisher from overwriting a freshly updated artifact.

The repository currently has Pages set to build from main:/ as well as this
repository's custom workflow. On a main push, wait *outside* the Pages
environment for that commit's legacy deployment to finish, then publish the
newly refreshed artifact. A scheduled custom deployment has no legacy build.
"""
import json
import os
import subprocess
import sys
import time


def api(path):
    result = subprocess.run(['gh', 'api', path], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def latest_legacy(runs, sha):
    matches = [r for r in runs if r.get('event') == 'dynamic'
               and r.get('name') == 'pages build and deployment'
               and r.get('head_sha') == sha]
    return max(matches, key=lambda r: (r.get('created_at', ''), r.get('id', 0)), default=None)


def wait(repo, sha, attempts=48, interval=5):
    path = f'repos/{repo}/actions/runs?head_sha={sha}&per_page=100'
    for attempt in range(attempts):
        legacy = latest_legacy(api(path).get('workflow_runs', []), sha)
        if legacy:
            print(f"Legacy Pages run {legacy['id']}: {legacy['status']} / {legacy.get('conclusion')}", flush=True)
            if legacy['status'] == 'completed':
                if legacy.get('conclusion') != 'success':
                    raise RuntimeError('Legacy Pages build/deploy failed; do not silently race it')
                return
        elif attempt >= 5 or attempt == attempts - 1:
            # If the owner changes Pages to the workflow source, no automatic
            # legacy run is expected. The API must affirm that configuration.
            if api(f'repos/{repo}/pages').get('build_type') == 'workflow':
                print('Pages now uses a workflow source; no legacy run to await.', flush=True)
                return
        if attempt + 1 < attempts:
            time.sleep(interval)
    raise RuntimeError('Legacy Pages run did not complete in time for this commit')


if __name__ == '__main__':
    try:
        wait(os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_SHA'])
    except (KeyError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'::error::{exc}', file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""Keep the freshest available group from the committed and cached snapshots.

A cache created before a newly added feed must never erase that feed's committed
baseline. The refresh subsequently replaces groups whose official fetch works.
"""
import json
import sys
from pathlib import Path


def reconcile(committed, cached):
    result = dict(cached)
    events = list(cached.get('events', []))
    states = dict(cached.get('sources', {}))
    for group, baseline in committed.get('sources', {}).items():
        stored = states.get(group, {})
        if not stored.get('lastSuccess') or (baseline.get('lastSuccess') or '') > (stored.get('lastSuccess') or ''):
            if baseline.get('lastSuccess'):
                events = [e for e in events if e.get('group') != group]
                events.extend(e for e in committed.get('events', []) if e.get('group') == group)
                states[group] = baseline
    result['events'], result['sources'] = events, states
    return result


def main():
    if len(sys.argv) != 3:
        sys.exit('Usage: reconcile_snapshot.py COMMITTED CACHED')
    committed_path, cached_path = map(Path, sys.argv[1:])
    committed = json.loads(committed_path.read_text())
    cached = json.loads(cached_path.read_text())
    cached_path.write_text(json.dumps(reconcile(committed, cached), separators=(',', ':'), ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main()

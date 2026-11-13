#!/usr/bin/env python3
"""Hash NFL Lines artifacts and record provenance/verification limits."""
import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'nfl'
FILES={
 'schedule_2026.json':('DERIVED_FROM_OFFICIAL_SNAPSHOTS','Official NFL weekly schedule snapshots; source snapshots and hashes in research/official/manifest.json.'),
 'standings.csv':('PROVISIONAL_VALUE_AUDIT','Official NFL season standings; known corrections applied, complete row-by-row audit remains open.'),
 'injuries_w10_2026.csv':('PROVISIONAL_VALUE_AUDIT','Official NFL Week 10 injury report; independent value-by-value transcription audit remains open.'),
 'depth.csv':('PROVISIONAL_VALUE_AUDIT','Official 49ers, Dolphins and Ravens depth charts only; remaining 29 clubs not captured.'),
 'teams.csv':('PARTIAL','Official NFL team pages and candidate official club depth-chart URLs; depth verification state is explicit.'),
 'gates.json':('PROGRAM_RULES','Program-defined validation gates; not an official NFL record.'),
 'strategies.json':('PROGRAM_RULES','Program-defined strategy hypotheses and states; not official NFL values.'),
 'leaderboard_rules.json':('PROGRAM_RULES','Program-defined scoring/settlement rules; rewards are not awarded.'),
 'suggestions.json':('PROGRAM_DECISIONS','Review proposals; none is automatically approved.'),
 'decisions.json':('PROGRAM_DECISIONS','Open information/decision register; owner-specific answers remain blank.'),
}
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def source_urls(path):
    if path.suffix=='.csv':
        with path.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
        return sorted({v for row in rows for k,v in row.items() if k.endswith('url') and v.startswith('https://')})
    data=json.loads(path.read_text(encoding='utf-8'))
    found=set()
    def walk(x):
        if isinstance(x,dict):
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
        elif isinstance(x,str) and x.startswith('https://'):
            found.add(x)
    walk(data); return sorted(found)
entries=[]
for name,(status,note) in FILES.items():
    p=DATA/name
    entries.append({'path':f'data/nfl/{name}','sha256':digest(p),'bytes':p.stat().st_size,'status':status,'source_urls':source_urls(p),'audit_note':note})
out={'program':'NFL Lines','generated_utc':datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
     'method':'SHA-256 over current local artifacts; source URL list extracted from each artifact where present.',
     'raw_capture_limit':'Official schedule snapshots are preserved in research/official/raw and its manifest. The Week 10 injury report and three team depth pages were read through the Arena page-fetch facility, but their full response bodies are not stored locally in this branch; their row-level fidelity remains flagged rather than certified.',
     'datasets':entries}
(DATA/'manifest.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'datasets':len(entries),'sha256_files':len(entries),'output':'data/nfl/manifest.json'}))

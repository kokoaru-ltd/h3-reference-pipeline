from __future__ import annotations
from copy import deepcopy
from typing import Any

FALLBACK = {'shot':'medium_closeup','camera':'locked','actor_action':'stable chest-up performance with hands below frame; hold a clear facial reaction','purpose':'safe_fallback'}

def patch_failed_shots(plan: dict[str, Any], qc: dict[str, Any], attempt: int, max_attempts: int = 2) -> dict[str, Any]:
    """Patch only failed shot IDs. After the retry budget, switch those shots to a safe fallback."""
    out = deepcopy(plan)
    failed = set(qc.get('failed_shots') or [])
    reasons = set(qc.get('reasons') or [])
    if not failed:
        failed = {s['id'] for s in out.get('shots', []) if s.get('status') == 'FAIL'}
    for s in out.get('shots', []):
        if s['id'] not in failed: continue
        if attempt >= max_attempts:
            keep = {k:s[k] for k in ('id','start','end','dialogue') if k in s}
            keep.update(FALLBACK); s.clear(); s.update(keep); continue
        if 'BAD_HANDS' in reasons or 'LIP_SYNC_BAD' in reasons:
            s['shot'] = 'medium_closeup'; s['camera'] = 'locked'
            s['actor_action'] = s.get('actor_action','') + '; keep hands below chest line and maintain stable mouth timing'
        elif 'CAMERA_MISMATCH' in reasons:
            s['camera'] = 'locked'
        elif 'WRONG_ACTION' in reasons:
            s['actor_action'] = s.get('actor_action','') + '; make the stated action unmistakable with one continuous gesture'
    return out

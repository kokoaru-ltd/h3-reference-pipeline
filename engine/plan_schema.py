from __future__ import annotations
from dataclasses import dataclass
from typing import Any

REQUIRED_SHOT_KEYS = {'id', 'start', 'end', 'shot', 'camera', 'actor_action', 'purpose'}
ALLOWED_SHOTS = {'wide', 'medium', 'medium_closeup', 'closeup', 'macro', 'pov'}
ALLOWED_CAMERAS = {'locked', 'slow_push_in', 'push_in', 'pull_out', 'pan_left', 'pan_right', 'dolly_left', 'dolly_right', 'handheld', 'eye_level', 'low_angle', 'high_angle'}

def validate_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for k in ('recipe_id', 'offer_id', 'duration', 'shots'):
        if k not in plan: errors.append(f'missing:{k}')
    if not isinstance(plan.get('shots'), list) or not plan.get('shots'):
        return errors + ['shots:non_empty_list']
    duration = float(plan.get('duration', 0) or 0)
    if duration <= 0 or duration > 60: errors.append('duration:1..60')
    last = 0.0
    ids = set()
    for i, shot in enumerate(plan['shots']):
        missing = REQUIRED_SHOT_KEYS - set(shot)
        errors.extend(f'shots[{i}]:missing:{x}' for x in sorted(missing))
        sid = shot.get('id')
        if sid in ids: errors.append(f'shots[{i}]:duplicate_id')
        ids.add(sid)
        try: start, end = float(shot['start']), float(shot['end'])
        except Exception: errors.append(f'shots[{i}]:invalid_time'); continue
        if start < 0 or end <= start or end > duration: errors.append(f'shots[{i}]:invalid_range')
        if start < last - 1e-6: errors.append(f'shots[{i}]:not_sorted')
        last = end
        if shot.get('shot') not in ALLOWED_SHOTS: errors.append(f"shots[{i}]:shot_not_allowed")
        camera = shot.get('camera')
        if camera not in ALLOWED_CAMERAS: errors.append(f"shots[{i}]:camera_not_allowed")
        if not isinstance(shot.get('actor_action'), str) or not shot['actor_action'].strip(): errors.append(f'shots[{i}]:actor_action_required')
        if shot.get('dialogue') is not None and not isinstance(shot.get('dialogue'), str): errors.append(f'shots[{i}]:dialogue_invalid')
    if abs(last - duration) > 0.05: errors.append('shots:must_cover_duration')
    return errors

def assert_valid(plan: dict[str, Any]) -> None:
    errors = validate_plan(plan)
    if errors: raise ValueError('INVALID_CREATIVE_PLAN\n' + '\n'.join(errors))

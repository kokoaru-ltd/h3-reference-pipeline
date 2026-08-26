from __future__ import annotations
from typing import Any
from .plan_schema import validate_plan

def preflight(plan: dict[str, Any], offer: dict[str, Any] | None = None) -> dict[str, Any]:
    errors = validate_plan(plan)
    offer = offer or {}
    if plan.get('locale', 'ja-JP') != 'ja-JP': errors.append('locale_must_be_ja-JP_for_JP_campaign')
    if plan.get('aspect_ratio', '9:16') != '9:16': errors.append('aspect_ratio_must_be_9:16')
    if not offer.get('offer_id') and not plan.get('offer_id'): errors.append('offer_id_required')
    for i, shot in enumerate(plan.get('shots', [])):
        if len(shot.get('actor_action', '')) > 240: errors.append(f'shots[{i}]:actor_action_too_long')
        if 'prompt' in shot or 'negative_prompt' in shot: errors.append(f'shots[{i}]:freeform_prompt_forbidden')
    return {'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'checked': ['schema','locale','aspect_ratio','offer_binding','no_freeform_prompt']}

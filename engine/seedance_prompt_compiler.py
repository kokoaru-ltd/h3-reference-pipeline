from __future__ import annotations
from typing import Any
from .plan_schema import assert_valid

SHOT_WORDS = {'wide':'wide shot','medium':'medium shot','medium_closeup':'medium close-up','closeup':'close-up','macro':'macro detail','pov':'first-person POV'}
CAMERA_WORDS = {'locked':'locked camera','slow_push_in':'slow push-in','push_in':'push-in','pull_out':'pull-out','pan_left':'pan left','pan_right':'pan right','dolly_left':'dolly left','dolly_right':'dolly right','handheld':'handheld camera','eye_level':'eye-level angle','low_angle':'low-angle view','high_angle':'high-angle view'}

def compile_prompt(plan: dict[str, Any], offer: dict[str, Any] | None = None) -> dict[str, Any]:
    assert_valid(plan)
    offer = offer or {}
    shots = []
    for s in plan['shots']:
        line = f"{s['start']:.2f}-{s['end']:.2f}s | {SHOT_WORDS[s['shot']]} | {CAMERA_WORDS[s['camera']]} | {s['actor_action']}"
        if s.get('dialogue'): line += f" | spoken Japanese: {s['dialogue']}"
        shots.append(line)
    product = offer.get('product') or offer.get('service') or offer.get('offer_id') or plan['offer_id']
    return {
        'prompt_version': 'seedance_compiler.v1',
        'prompt': f"Vertical 9:16 Japanese TikTok ad for {product}. Follow the timed shot list exactly. Preserve identity, product shape, wardrobe and location across shots.\n" + '\n'.join(shots),
        'negative_prompt': 'no extra actors, no product substitution, no text rendered in video, no logo invention, no camera movement outside shot list, no gore, no deformed hands',
        'shot_instructions': shots,
        'audio_reference': plan.get('audio_reference'),
    }

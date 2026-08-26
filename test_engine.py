import json
from pathlib import Path
from engine.plan_schema import validate_plan
from engine.preflight_validator import preflight
from engine.seedance_prompt_compiler import compile_prompt
from engine.retry_controller import patch_failed_shots

ROOT = Path(__file__).parent

def test_plan_and_compiler():
    plan = json.loads((ROOT / 'creative_plan_example.json').read_text(encoding='utf-8'))
    assert validate_plan(plan) == []
    assert preflight(plan, {'offer_id': plan['offer_id']})['status'] == 'PASS'
    result = compile_prompt(plan, {'product': '外国人材採用サポート'})
    assert result['prompt_version'] == 'seedance_compiler.v1'
    assert len(result['shot_instructions']) == 4

def test_partial_retry_and_fallback():
    plan = json.loads((ROOT / 'creative_plan_example.json').read_text(encoding='utf-8'))
    patched = patch_failed_shots(plan, {'failed_shots':['s2'], 'reasons':['BAD_HANDS']}, attempt=1)
    assert patched['shots'][1]['camera'] == 'locked'
    assert patched['shots'][0] == plan['shots'][0]
    fallback = patch_failed_shots(plan, {'failed_shots':['s2']}, attempt=2)
    assert fallback['shots'][1]['purpose'] == 'safe_fallback'

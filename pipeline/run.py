from __future__ import annotations
import argparse, json
from pathlib import Path
from engine.campaign_runner import run as run_campaign
from image.reference_builder import ReferenceBuilder
from image.comfyui_provider import ComfyUIProvider

ROOT=Path(__file__).resolve().parents[1]

def load_persona(persona_id: str) -> dict:
    p=ROOT/'personas'/persona_id/'persona.json'
    if not p.exists(): raise SystemExit(f'PERSONA_NOT_FOUND:{persona_id}')
    return json.loads(p.read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--idea',required=True); ap.add_argument('--persona',required=True); ap.add_argument('--count',type=int,default=1); ap.add_argument('--mode',choices=['dry-run','seedance'],default='dry-run'); ap.add_argument('--reference-mode',choices=['dry-run','comfyui'],default='dry-run'); ap.add_argument('--out',default=None); ap.add_argument('--publish',action='store_true'); a=ap.parse_args()
    persona=load_persona(a.persona)
    offer={'offer_id':f'idea_{a.persona}','product':persona.get('content_theme','UGC'),'character_id':a.persona,'idea':a.idea,'recipe_hint':('pattern_interrupt' if any(x in a.idea for x in ('破','捨','落ち','フリーズ')) else 'story_vlog'),'default_dialogue':'仕事探し、まだ難しいです。','persona':persona}
    out=Path(a.out) if a.out else ROOT/'outputs'/f'{a.persona}_idea'
    ref_provider=ComfyUIProvider() if a.reference_mode=='comfyui' else None
    # Build references from the first deterministic plan without invoking an LLM.
    from engine.creative_planner import CreativePlanner
    reference_plan=CreativePlanner().next_plan(offer,[],0)
    ReferenceBuilder(ROOT,ref_provider).build(reference_plan,a.persona,out/'references',dry_run=(a.reference_mode=='dry-run'))
    summary=run_campaign(offer,a.count,out,a.mode)
    summary['publish_requested']=a.publish; summary['publish_status']='NEEDS_HUMAN_VERIFICATION' if a.publish else 'NOT_REQUESTED'
    (out/'pipeline_result.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

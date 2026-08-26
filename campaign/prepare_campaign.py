from __future__ import annotations
import argparse, json
from pathlib import Path
from research_success_ads.engine.creative_planner import CreativePlanner
from research_success_ads.browser_ai.client import GatewayClient
from research_success_ads.browser_ai.image_generator import generate_shot_image
from research_success_ads.qc.image_qc import check

ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--theme',required=True); ap.add_argument('--persona',required=True); ap.add_argument('--count',type=int,default=30); ap.add_argument('--out',default=None); ap.add_argument('--gateway-url',default=None); ap.add_argument('--dry-run',action='store_true'); a=ap.parse_args()
    persona=json.loads((ROOT/'personas'/a.persona/'persona.json').read_text(encoding='utf-8')); out=Path(a.out or ROOT/'outputs'/f'{a.persona}_launch_{a.count}'); out.mkdir(parents=True,exist_ok=True); planner=CreativePlanner(); gateway=GatewayClient(a.gateway_url); plans=[]
    for i in range(a.count):
        plan=planner.next_plan({'offer_id':a.persona,'product':a.theme,'character_id':a.persona,'recipe_hint':planner.recipes[i%len(planner.recipes)]},plans,i); plan['idea']=a.theme; pdir=out/f'{i+1:03d}'; pdir.mkdir(exist_ok=True); (pdir/'creative_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8'); refs=[]
        for shot in plan['shots'][:3]:
            target=pdir/f'{shot["id"]}_start.png'; prompt=f"Vertical 9:16 start frame for {a.theme}. Same fictional persona {a.persona}. {shot['actor_action']}. {shot['shot']} {shot['camera']}. No readable text, no logo, no subtitles."
            if a.dry_run:
                from PIL import Image; Image.new('RGB',(720,1280),'#d8d8d8').save(target)
            else: generate_shot_image(prompt,refs,target,gateway)
            qc=check(target); refs.append(str(target)); (pdir/f'{shot["id"]}_image_qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf-8')
        plans.append(plan)
    (out/'plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({'status':'PREPARED','count':len(plans),'out':str(out),'gateway':gateway.base_url,'dry_run':a.dry_run},ensure_ascii=False,indent=2))
if __name__=='__main__': main()

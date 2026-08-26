from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from browser_ai.client import GatewayClient
from browser_ai.image_generator import generate_shot_image
from browser_ai.prompt_templates import VIDEO001, SHOT_START, IDENTITY_MASTER_SHEET
from qc.image_qc import check

ROOT=Path(__file__).resolve().parents[1]
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser(); ap.add_argument('--persona',default='linh_01'); ap.add_argument('--out',default=None); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--gateway-url'); a=ap.parse_args()
    out=Path(a.out or ROOT/'outputs'/'linh_video001'); out.mkdir(parents=True,exist_ok=True); p=ROOT/'personas'/a.persona/'persona.json'; persona=json.loads(p.read_text(encoding='utf-8')); client=GatewayClient(a.gateway_url); shots=[]
    # Generate the persona anchor once and reuse it for every Shot. This prevents
    # each image request from inventing a new face. It is never overwritten.
    # Dry-run placeholders stay inside the run directory and can never be
    # mistaken for a production identity cache.
    identity=(out/'identity_master.png') if a.dry_run else (ROOT/'personas'/a.persona/'identity_master.png')
    if not identity.exists():
        existing_qc=check(target) if target.exists() else {'status':'FAIL'}
        if existing_qc.get('status')=='PASS':
            shots.append({'shot_id':s['id'],'duration':s['duration'],'dialogue_vi':s['dialogue_vi'],'image':str(target),'identity_reference':str(identity),'qc':existing_qc,'reused':True})
            continue
        if a.dry_run:
            from PIL import Image,ImageDraw
            identity.parent.mkdir(parents=True,exist_ok=True)
            im=Image.new('RGB',(720,1280),'#c8d0d8'); ImageDraw.Draw(im).text((40,80),f'IDENTITY MASTER\n{persona.get("display_name",a.persona)}',fill='black'); im.save(identity)
        else:
            generate_shot_image(IDENTITY_MASTER_SHEET,(),identity,client)
    identity_qc=check(identity)
    for s in VIDEO001:
        target=out/f'{s["id"]}_start.png'; prompt=SHOT_START.format(location=s['location'],camera=s['camera'],action=s['action'],wardrobe='simple casual clothes or fixed recruitment wardrobe',prop='black A4 work/interview bag; no readable text')
        if a.dry_run:
            from PIL import Image,ImageDraw
            im=Image.new('RGB',(720,1280),'#d8d8d8'); ImageDraw.Draw(im).text((40,80),f"{s['id']}\n{s['action']}",fill='black'); im.save(target)
        else: generate_shot_image(prompt, (identity,), target, client)
        shots.append({'shot_id':s['id'],'duration':s['duration'],'dialogue_vi':s['dialogue_vi'],'image':str(target),'identity_reference':str(identity),'qc':check(target)})
    result={'campaign':'linh_video001','persona':persona,'identity_master':str(identity),'identity_qc':identity_qc,'shots':shots,'video_generation_started':False,'status':'IMAGE_QC_READY' if identity_qc['status']=='PASS' and all(x['qc']['status']=='PASS' for x in shots) else 'IMAGE_QC_FAIL'}; (out/'creative_plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

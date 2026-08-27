from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from PIL import Image
from browser_ai.client import GatewayClient
from browser_ai.image_generator import generate_shot_image
from browser_ai.prompt_templates import VIDEO001, STORYBOARD_GRID, CAMERA_PRESETS
from qc.image_qc import check

ROOT=Path(__file__).resolve().parents[1]

def crop_grid(grid: Path, out_dir: Path) -> list[Path]:
    im=Image.open(grid).convert('RGB')
    # 2x2 cells. The bottom-right cell is intentionally unused.
    w,h=im.size; cw,ch=w//2,h//2
    paths=[]
    for idx, shot in enumerate(VIDEO001[:3]):
        x=(idx%2)*cw; y=(idx//2)*ch
        cell=im.crop((x,y,x+cw,y+ch))
        target=out_dir/f'{shot["id"]}_start.png'; cell.save(target); paths.append(target)
    return paths

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser(); ap.add_argument('--persona',default='linh_01'); ap.add_argument('--out',default=None); ap.add_argument('--dry-run',action='store_true'); ap.add_argument('--gateway-url'); a=ap.parse_args()
    out=Path(a.out or ROOT/'outputs'/'linh_video001_grid'); out.mkdir(parents=True,exist_ok=True)
    persona=json.loads((ROOT/'personas'/a.persona/'persona.json').read_text(encoding='utf-8'))
    identity=ROOT/'personas'/a.persona/'identity_master.png'
    if not identity.exists(): raise SystemExit('IDENTITY_MASTER_REQUIRED: run prepare_video001 first')
    grid=out/'storyboard_grid.png'
    prompt=STORYBOARD_GRID.format(
        s1=f'{VIDEO001[0]["location"]}; camera {CAMERA_PRESETS["propped_static"]}; {VIDEO001[0]["action"]}',
        s2=f'{VIDEO001[1]["location"]}; camera {CAMERA_PRESETS["selfie_front"]}; {VIDEO001[1]["action"]}',
        s3=f'{VIDEO001[2]["location"]}; camera {CAMERA_PRESETS["phone_raw"]}; {VIDEO001[2]["action"]}')
    if a.dry_run:
        from PIL import ImageDraw
        im=Image.new('RGB',(720,1280),'#d8d8d8'); d=ImageDraw.Draw(im); d.rectangle((0,0,360,640),outline='blue',width=4); d.rectangle((360,0,720,640),outline='red',width=4); d.rectangle((0,640,360,1280),outline='green',width=4); im.save(grid)
    else: generate_shot_image(prompt,(identity,),grid,GatewayClient(a.gateway_url))
    frames=crop_grid(grid,out)
    result={'campaign':'linh_video001','mode':'storyboard_grid','identity_reference':str(identity),'grid':str(grid),'shots':[{'shot_id':s['id'],'image':str(p),'qc':check(p)} for s,p in zip(VIDEO001,frames)]}
    result['status']='IMAGE_QC_READY' if all(x['qc']['status']=='PASS' for x in result['shots']) else 'IMAGE_QC_FAIL'
    (out/'creative_plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

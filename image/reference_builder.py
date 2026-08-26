from __future__ import annotations
import json, os
from pathlib import Path
from PIL import Image, ImageDraw
from .reference_selector import ReferenceSelector
from .image_cache import ImageCache

class ReferenceBuilder:
    def __init__(self, project_root: str | Path, provider=None):
        self.root=Path(project_root); self.provider=provider; self.selector=ReferenceSelector(self.root); self.cache=ImageCache(self.root/'outputs'/'image_cache')
    def build(self, plan: dict, persona_id: str, out_dir: str | Path, dry_run=True) -> dict:
        out=Path(out_dir); out.mkdir(parents=True,exist_ok=True); records=[]
        for shot in plan.get('shots',[]):
            refs=self.selector.select(shot,persona_id); key=self.cache.key(persona_id,'recruitment_suit','japanese_apartment',shot.get('purpose'),shot.get('camera'),shot.get('actor_action'))
            files={}
            for kind in ('start','end'):
                p=out/f'{shot["id"]}_{kind}.png'
                if dry_run:
                    im=Image.new('RGB',(720,1280),'#d8d8d8'); ImageDraw.Draw(im).text((40,80),f'{shot["id"]} {kind}\n{shot.get("actor_action","")}',fill='black'); im.save(p)
                elif self.provider: self.provider.generate_start_frame(shot,{},refs,p) if kind=='start' else self.provider.generate_end_frame(shot,{},refs,p)
                files[kind]=str(p)
            records.append({'shot_id':shot['id'],'cache_key':key,'references':refs,'generated':files})
        manifest={'persona_id':persona_id,'count':len(records),'shots':records,'provider':'dry-run' if dry_run else 'comfyui'}; (out/'reference_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); return manifest

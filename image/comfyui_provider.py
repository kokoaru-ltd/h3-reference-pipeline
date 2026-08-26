from __future__ import annotations
import json, os, urllib.request, urllib.parse, uuid, time
from pathlib import Path
from .image_cache import ImageCache

class ComfyUIProvider:
    def __init__(self, base_url=None, workflow_path=None, cache=None):
        self.base_url=(base_url or os.getenv('COMFYUI_URL','http://127.0.0.1:8188')).rstrip('/')
        self.workflow_path=workflow_path or os.getenv('COMFYUI_WORKFLOW_PATH')
        self.cache=cache
    def _submit(self, prompt):
        if not self.workflow_path: raise RuntimeError('COMFYUI_WORKFLOW_PATH_REQUIRED')
        workflow=json.loads(Path(self.workflow_path).read_text(encoding='utf-8'))
        # Existing workflow JSON is passed through unchanged; users can use its own prompt nodes.
        body=json.dumps({'prompt':workflow,'client_id':str(uuid.uuid4())}).encode()
        req=urllib.request.Request(self.base_url+'/prompt',data=body,headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=60) as r: return json.load(r)['prompt_id']
    def generate_start_frame(self, shot, persona, references, out): return self._generate('start',shot,persona,references,out)
    def generate_end_frame(self, shot, persona, references, out): return self._generate('end',shot,persona,references,out)
    def _generate(self, kind, shot, persona, references, out):
        prompt=f"{kind} frame; preserve persona identity and wardrobe; shot={shot.get('id')} action={shot.get('actor_action')}"
        pid=self._submit(prompt)
        deadline=time.time()+float(os.getenv('COMFYUI_TIMEOUT_SEC','300'))
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(self.base_url+'/history/'+pid,timeout=30) as r: hist=json.load(r)
                outputs=(hist.get(pid) or {}).get('outputs') or {}
                for node in outputs.values():
                    for image in node.get('images',[]):
                        q=urllib.parse.urlencode({'filename':image['filename'],'subfolder':image.get('subfolder',''),'type':image.get('type','output')})
                        with urllib.request.urlopen(self.base_url+'/view?'+q,timeout=60) as r: Path(out).write_bytes(r.read())
                        return Path(out)
            except Exception: pass
            time.sleep(2)
        raise RuntimeError(f'COMFYUI_TIMEOUT:{pid}')

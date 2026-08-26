from __future__ import annotations
import hashlib, json
from pathlib import Path

class ImageCache:
    def __init__(self, root: str | Path): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def key(self, persona_id, wardrobe_id, location_id, pose, camera, prop_state):
        raw='|'.join(map(str,(persona_id,wardrobe_id,location_id,pose,camera,prop_state)))
        return hashlib.sha256(raw.encode()).hexdigest()[:20]
    def path(self, key, kind): return self.root/f'{key}_{kind}.png'
    def get(self, key, kind):
        p=self.path(key,kind); return p if p.exists() else None
    def put(self, key, kind, source):
        p=self.path(key,kind); Path(source).replace(p) if Path(source).resolve()!=p.resolve() else None; return p

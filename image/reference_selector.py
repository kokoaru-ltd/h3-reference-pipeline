from __future__ import annotations
from pathlib import Path

class ReferenceSelector:
    def __init__(self, root: str | Path): self.root=Path(root)
    def select(self, shot: dict, persona_id: str) -> dict:
        base=self.root/'personas'/persona_id
        refs={'identity':str(base/'identity'/'base_face.png'),'face':str(base/'identity'/'face_closeup.png'),'wardrobe':str(base/'wardrobe'/'recruitment_suit.png'),'props':[],'location':str(base/'locations'/'japanese_apartment.png')}
        action=(shot.get('actor_action') or '').lower()
        if any(k in action for k in ('resume','履歴書','tear','破')): refs['props'].append(str(base/'props'/'resume.png'))
        if any(k in action for k in ('phone','スマホ','smartphone')): refs['props'].append(str(base/'props'/'smartphone.png'))
        return {k:v for k,v in refs.items() if (not isinstance(v,str) or Path(v).exists()) and v not in ([],)}

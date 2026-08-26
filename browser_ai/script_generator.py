from __future__ import annotations
import json
from .client import GatewayClient

def generate_script(idea: str, persona: dict, gateway: GatewayClient | None = None) -> dict:
    gateway=gateway or GatewayClient()
    prompt='Return JSON only with keys dialogue_segments and caption. Create short simple lines matching this persona and idea. No extra keys. Persona='+json.dumps(persona,ensure_ascii=False)+' Idea='+idea
    raw=gateway.chat([{'role':'user','content':prompt}])
    return json.loads(raw)

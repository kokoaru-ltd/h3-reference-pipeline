from __future__ import annotations
import base64, json, hashlib
from pathlib import Path
from .client import GatewayClient

def save_gateway_image(response: dict, out: str | Path, exclude=()) -> Path:
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    items=response.get('data') or [{}]
    excluded={hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in exclude if Path(p).exists()}
    chosen=None
    for item in items:
        if item.get('b64_json'):
            raw=base64.b64decode(item['b64_json'])
            if hashlib.sha256(raw).hexdigest() not in excluded:
                chosen=raw; break
    if chosen is not None: out.write_bytes(chosen)
    elif items[0].get('b64_json'): out.write_bytes(base64.b64decode(items[0]['b64_json']))
    elif item.get('url'):
        import urllib.request; urllib.request.urlretrieve(item['url'],str(out))
    else: raise RuntimeError('GATEWAY_IMAGE_RESPONSE_HAS_NO_IMAGE')
    return out

def generate_shot_image(prompt: str, references=(), out='shot.png', gateway=None) -> Path:
    return save_gateway_image((gateway or GatewayClient()).image(prompt,references),out,exclude=references)

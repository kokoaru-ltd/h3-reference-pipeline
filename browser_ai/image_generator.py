from __future__ import annotations
import base64, json
from pathlib import Path
from .client import GatewayClient

def save_gateway_image(response: dict, out: str | Path) -> Path:
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    # Gateways may echo uploaded reference thumbnails before the newly
    # generated image. The final item is the generation result.
    item=(response.get('data') or [{}])[-1]
    if item.get('b64_json'): out.write_bytes(base64.b64decode(item['b64_json']))
    elif item.get('url'):
        import urllib.request; urllib.request.urlretrieve(item['url'],str(out))
    else: raise RuntimeError('GATEWAY_IMAGE_RESPONSE_HAS_NO_IMAGE')
    return out

def generate_shot_image(prompt: str, references=(), out='shot.png', gateway=None) -> Path:
    return save_gateway_image((gateway or GatewayClient()).image(prompt,references),out)

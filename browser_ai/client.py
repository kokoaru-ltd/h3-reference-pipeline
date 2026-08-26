from __future__ import annotations
import base64, json, os, urllib.request, urllib.error
from pathlib import Path

class GatewayClient:
    def __init__(self, base_url=None): self.base_url=(base_url or os.getenv('CHATGPT_GATEWAY_URL','http://127.0.0.1:8000')).rstrip('/')
    def _post(self,path,body):
        req=urllib.request.Request(self.base_url+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=600) as r: return json.load(r)
        except urllib.error.URLError as e:
            raise RuntimeError(f'GATEWAY_UNAVAILABLE:{self.base_url} ({e.reason})') from e
    def chat(self, messages, model=None):
        data=self._post('/v1/chat/completions',{'model':model or os.getenv('CHATGPT_GATEWAY_MODEL','chatgpt-web'),'messages':messages,'temperature':0})
        return data['choices'][0]['message']['content']
    def image(self, prompt, references=(), model=None):
        # The browser gateway exposes the image-2 lane; keep the model configurable
        # because gateways may use a different public model alias.
        body={'model':model or os.getenv('CHATGPT_GATEWAY_IMAGE_MODEL','image-2'),'prompt':prompt,'n':1,'size':'1024x1536'}
        if references: body['reference_images']=[self._data_url(p) for p in references]
        return self._post('/v1/images/generations',body)
    @staticmethod
    def _data_url(path):
        p=Path(path); mime='image/png' if p.suffix.lower()=='.png' else 'image/jpeg'; return f'data:{mime};base64,'+base64.b64encode(p.read_bytes()).decode()

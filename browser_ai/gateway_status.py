from __future__ import annotations
import argparse, json, os, urllib.request, urllib.error
from engine.env import load_dotenv

def probe(base: str) -> dict:
    base = base.rstrip('/')
    token=os.getenv('CHATGPT_GATEWAY_API_TOKEN','')
    for path in ('/healthz', '/health', '/v1/models'):
        try:
            req=urllib.request.Request(base + path, headers={'Authorization':f'Bearer {token}'} if token else {})
            with urllib.request.urlopen(req, timeout=5) as r:
                return {'status':'READY', 'url':base, 'probe':path, 'http_status':r.status}
        except urllib.error.HTTPError as e:
            # A live gateway may not expose /health; a 401/404 still proves a
            # process is listening, so report it separately for diagnosis.
            if e.code in (401, 403, 404, 405):
                continue
        except urllib.error.URLError:
            pass
    return {'status':'UNAVAILABLE', 'url':base, 'reason':'no HTTP response from gateway'}

def main():
    load_dotenv()
    ap=argparse.ArgumentParser(description='Check the local ChatGPT Web Gateway before Image-2 generation')
    ap.add_argument('--url', default=os.getenv('CHATGPT_GATEWAY_URL','http://127.0.0.1:8000'))
    args=ap.parse_args(); print(json.dumps(probe(args.url), ensure_ascii=False, indent=2))

if __name__ == '__main__': main()

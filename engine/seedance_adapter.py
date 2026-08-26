from __future__ import annotations
import json, os, subprocess, time, urllib.request
from .env import load_dotenv, required
from pathlib import Path

class SeedanceAdapter:
    def __init__(self, mode='dry-run'):
        load_dotenv(); self.mode=mode
    def generate(self, prompt: dict, shot: dict, out: str | Path) -> Path:
        if self.mode != 'dry-run':
            return self._generate_remote(prompt, shot, out)
        out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
        duration=float(shot['end'])-float(shot['start'])
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f"color=c=gray:s=320x568:r=24:d={duration}",'-c:v','libx264','-pix_fmt','yuv420p',str(out)],check=True)
        return out

    def _generate_remote(self, prompt, shot, out):
        provider=os.getenv('VIDEO_PROVIDER','seedance').lower()
        requested=float(shot['end'])-float(shot['start'])
        if provider == 'byteplus':
            url=os.getenv('BYTEPLUS_API_URL','https://operator.las.ap-southeast-1.bytepluses.com/api/v1/contents/generations/tasks')
            key=required('BYTEPLUS_API_KEY'); model=os.getenv('BYTEPLUS_SEEDANCE_MODEL','dreamina-seedance-2-5-260628')
            content=[{'type':'text','text':prompt['prompt']}]
            for ref in filter(None, (os.getenv('BYTEPLUS_REFERENCE_CONTENT','').split(','))):
                ref=ref.strip(); content.append({'type':'image_url','image_url':{'url':ref},'role':'reference_image'})
            body={'model':model,'content':content,'ratio':'9:16','duration':max(4,int(round(requested))),'resolution':os.getenv('BYTEPLUS_RESOLUTION','720p'),'generate_audio':os.getenv('BYTEPLUS_GENERATE_AUDIO','true').lower()=='true','watermark':False}
            callback=os.getenv('BYTEPLUS_CALLBACK_URL')
            if callback: body['callback_url']=callback
            poll=os.getenv('BYTEPLUS_POLL_URL_TEMPLATE',url.rstrip('/')+'/{id}')
        else:
            url=required('SEEDANCE_API_URL'); key=required('SEEDANCE_API_KEY'); model=os.getenv('SEEDANCE_MODEL','seedance-2.5')
            body={'model':model,'prompt':prompt['prompt'],'duration':requested,'aspect_ratio':'9:16','resolution':os.getenv('SEEDANCE_RESOLUTION','720p'),'generate_audio':False}; poll=os.getenv('SEEDANCE_POLL_URL_TEMPLATE')
        req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=120) as resp: data=json.load(resp)
        result_url=data.get('video_url') or data.get('url') or (data.get('data') or {}).get('video_url') or (data.get('content') or {}).get('video_url')
        task_id=data.get('id') or data.get('task_id') or (data.get('data') or {}).get('id')
        for _ in range(int(os.getenv('SEEDANCE_MAX_POLLS','60'))):
            if result_url: break
            if not (poll and task_id): break
            time.sleep(float(os.getenv('SEEDANCE_POLL_SECONDS','5')))
            purl=poll.format(id=task_id, task_id=task_id); preq=urllib.request.Request(purl,headers={'Authorization':f'Bearer {key}'})
            with urllib.request.urlopen(preq,timeout=120) as resp: data=json.load(resp)
            status=data.get('status') or (data.get('data') or {}).get('status')
            if status in ('failed','expired','cancelled'): raise RuntimeError(f'SEEDANCE_TASK_{status}')
            result_url=data.get('video_url') or data.get('url') or (data.get('data') or {}).get('video_url') or (data.get('content') or {}).get('video_url')
        if not result_url: raise RuntimeError('SEEDANCE_RESULT_URL_NOT_FOUND')
        temp=Path(out).with_suffix('.raw.mp4'); urllib.request.urlretrieve(result_url,str(temp))
        if provider == 'byteplus' and requested < 4:
            subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(temp),'-t',str(requested),'-c','copy',str(out)],check=True); temp.unlink(missing_ok=True)
        else: temp.replace(out)
        return Path(out)

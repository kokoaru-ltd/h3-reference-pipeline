from __future__ import annotations
import base64, json, os, urllib.request, wave
from pathlib import Path
from .env import load_dotenv, required

class ElevenLabsTTS:
    def __init__(self, mode='dry-run'):
        load_dotenv(); self.mode=mode
    def generate(self, text: str, out: str | Path, duration_sec: float = 15.0, speaker: str = 'narrator', language_code: str | None = 'ja') -> dict:
        if self.mode != 'dry-run':
            key=required('ELEVENLABS_API_KEY'); voice=required('ELEVENLABS_VOICE_ID')
            try: voice = json.loads(os.getenv('ELEVENLABS_VOICE_MAP_JSON','{}')).get(speaker, voice)
            except json.JSONDecodeError: pass
            model=os.getenv('ELEVENLABS_MODEL_ID','eleven_multilingual_v2')
            url=f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format={os.getenv('ELEVENLABS_OUTPUT_FORMAT','mp3_44100_128')}"
            body={'text':text or '','model_id':model}
            if language_code: body['language_code']=language_code
            req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=120) as resp: data=json.load(resp)
            Path(out).write_bytes(base64.b64decode(data['audio_base64']))
            return {'audio_path':str(out),'alignment':data.get('alignment') or data.get('normalized_alignment'),'status':'generated','paid_api_called':True}
        out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
        with wave.open(str(out),'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b'\0'*int(16000*2*duration_sec))
        alignment={'characters':list(text or ''),'character_start_times_seconds':[],'character_end_times_seconds':[]}
        return {'audio_path':str(out),'alignment':alignment,'status':'dry_run','paid_api_called':False}

    def generate_script(self, segments: list[dict], out: str | Path, total_duration: float) -> dict:
        """Generate a multi-speaker script. Each segment has speaker,text,start,end."""
        segments = [s for s in segments if s.get('text')]
        if not segments:
            return self.generate('', out, total_duration, 'narrator')
        if self.mode == 'dry-run':
            return self.generate(' '.join(s['text'] for s in segments), out, total_duration, 'narrator')
        from tempfile import TemporaryDirectory
        import subprocess
        with TemporaryDirectory() as td:
            files=[]; align=[]
            for i,s in enumerate(segments):
                p=Path(td)/f's{i}.mp3'; r=self.generate(s['text'],p,max(0.1,float(s.get('end',s.get('start',0)+1))-float(s.get('start',0))),s.get('speaker','narrator'),s.get('language_code','ja')); files.append((p,float(s.get('start',0)))); align.append({'speaker':s.get('speaker','narrator'),'text':s['text'],'start':s.get('start',0),'end':s.get('end'),'language_code':s.get('language_code','ja')})
            inputs=[]; filters=[]
            for i,(p,start) in enumerate(files): inputs += ['-i',str(p)]; filters.append(f'[{i}:a]adelay={int(start*1000)}|{int(start*1000)}[a{i}]')
            labels=''.join(f'[a{i}]' for i in range(len(files))); filters.append(f'{labels}amix=inputs={len(files)}:duration=longest,apad,atrim=duration={total_duration}[aout]')
            subprocess.run(['ffmpeg','-y','-loglevel','error',*inputs,'-filter_complex',';'.join(filters),'-map','[aout]','-c:a','mp3',str(out)],check=True)
        return {'audio_path':str(out),'alignment':align,'status':'generated','paid_api_called':True}

import json, os, subprocess, re

ROOT = os.path.dirname(__file__)
DATA = json.load(open(os.path.join(ROOT, 'success_ads_10.json'), encoding='utf-8'))
out = []
for idx, item in enumerate(DATA, 1):
    vdir = os.path.join(ROOT, 'videos', f'{idx:02d}')
    files = [os.path.join(vdir, f) for f in os.listdir(vdir)] if os.path.isdir(vdir) else []
    video = next((f for f in files if f.lower().endswith('.mp4')), None)
    rec = {'id': item['id'], 'index': idx, 'video_url': item['video_url'], 'downloaded': bool(video), 'frames': [], 'scene_cuts_sec': [], 'error': None}
    if not video:
        rec['error'] = 'video_not_downloaded_or_access_denied'
        out.append(rec); continue
    try:
        probe = subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',video], text=True)
        p = json.loads(probe); stream = next(s for s in p['streams'] if s.get('codec_type')=='video')
        dur = float(p['format'].get('duration') or stream.get('duration') or 0)
        fps = eval(stream.get('r_frame_rate','0/1')) if '/' in stream.get('r_frame_rate','0/1') else float(stream.get('r_frame_rate',0))
        rec.update({'duration_sec': dur, 'fps': fps, 'width': stream.get('width'), 'height': stream.get('height')})
        frame_dir = os.path.join(vdir, 'keyframes'); os.makedirs(frame_dir, exist_ok=True)
        for t in [0,2,5,8,10,12,15]:
            if t <= max(dur-0.05, 0):
                path = os.path.join(frame_dir, f'{t:02d}s.jpg')
                subprocess.run(['ffmpeg','-y','-ss',str(t),'-i',video,'-frames:v','1','-q:v','3',path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                rec['frames'].append({'time_sec': t, 'path': os.path.relpath(path, ROOT).replace('\\','/')})
        scene = subprocess.run(['ffmpeg','-hide_banner','-i',video,'-filter:v',"select='gt(scene,0.35)',showinfo",'-f','null','-'],capture_output=True,text=True).stderr
        rec['scene_cuts_sec'] = [round(float(x),3) for x in re.findall(r'pts_time:([0-9.]+)', scene)]
    except Exception as e:
        rec['error'] = str(e)
    out.append(rec)
json.dump(out, open(os.path.join(ROOT,'video_analysis.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))

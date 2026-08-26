from __future__ import annotations
import json, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageStat

def _duration(video: Path) -> float:
    raw = subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(video)], text=True)
    return float(raw.strip())

def _frame(video: Path, t: float, path: Path) -> None:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(max(t,0)), '-i',str(video), '-frames:v','1',str(path)], check=True)

def evaluate_clip(video: str | Path, plan: dict) -> dict:
    video = Path(video)
    reasons, evidence = [], {'file_exists': video.exists()}
    if not video.exists(): return {'status':'FAIL','score':0,'reasons':['MISSING_VIDEO'],'failed_shots':[],'evidence':evidence}
    with tempfile.TemporaryDirectory() as td:
        try:
            dur = _duration(video); evidence['duration_sec'] = round(dur, 3)
            expected = float(plan['duration']); evidence['duration_delta_sec'] = round(abs(dur-expected),3)
            if abs(dur-expected) > 0.25: reasons.append('DURATION_INVALID')
            mids = []
            for s in plan.get('shots', []):
                p = Path(td) / f"{s['id']}.jpg"; _frame(video, (float(s['start'])+float(s['end']))/2, p)
                mids.append((s['id'], p))
            evidence['shot_frames_extracted'] = len(mids)
            # A blank/near-black frame is a concrete artifact signal, not a semantic claim.
            failed = []
            for sid, p in mids:
                mean = sum(ImageStat.Stat(Image.open(p).convert('RGB')).mean)/3
                if mean < 3: failed.append(sid)
            if failed: reasons.append('VISUAL_ARTIFACT')
            evidence['dark_shot_ids'] = failed
        except Exception as exc:
            reasons.append('VIDEO_ANALYSIS_ERROR'); evidence['error'] = str(exc); failed = []
    score = max(0, 100 - len(reasons)*30)
    return {'status':'PASS' if not reasons else 'FAIL','score':score,'reasons':reasons,'failed_shots':failed,'evidence':evidence}

from __future__ import annotations
import subprocess
from pathlib import Path

class FinalAssembler:
    def render(self, shots: list[str | Path], audio: dict, out: str | Path) -> Path:
        out=Path(out); out.parent.mkdir(parents=True,exist_ok=True); concat=out.with_suffix('.concat.txt')
        concat.write_text(''.join(f"file '{Path(s).resolve().as_posix()}'\n" for s in shots),encoding='utf-8')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-i',str(audio['audio_path']),'-map','0:v:0','-map','1:a:0','-shortest','-vf','scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(out)],check=True)
        return out

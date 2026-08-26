from __future__ import annotations
import os
from pathlib import Path

def load_dotenv(path: str | Path | None = None) -> None:
    path = Path(path or Path(__file__).resolve().parents[1] / '.env')
    if not path.exists(): return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k, v = line.split('=', 1); k=k.strip(); v=v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)

def required(name: str) -> str:
    value = os.getenv(name)
    if not value: raise RuntimeError(f'MISSING_ENV:{name}')
    return value

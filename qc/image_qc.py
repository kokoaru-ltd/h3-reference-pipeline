from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageStat

def check(path: str | Path) -> dict:
    p=Path(path); evidence={'exists':p.exists()}
    if not p.exists(): return {'status':'FAIL','reasons':['MISSING_IMAGE'],'evidence':evidence}
    try:
        im=Image.open(p).convert('RGB'); evidence.update({'size':im.size,'mean_luma':round(sum(ImageStat.Stat(im).mean)/3,2)})
        reasons=[]
        if im.width/im.height < .5 or im.width/im.height > .8: reasons.append('ASPECT_RATIO_NOT_VERTICAL')
        if evidence['mean_luma'] < 3: reasons.append('IMAGE_NEAR_BLACK')
        return {'status':'PASS' if not reasons else 'FAIL','reasons':reasons,'evidence':evidence}
    except Exception as e: return {'status':'FAIL','reasons':['IMAGE_READ_ERROR'],'evidence':{'error':str(e)}}

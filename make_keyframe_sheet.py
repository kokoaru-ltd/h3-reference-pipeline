from PIL import Image, ImageDraw
import os, json

root = os.path.dirname(__file__)
data = json.load(open(os.path.join(root, 'success_ads_10.json'), encoding='utf-8'))
times = [0, 2, 5, 8, 10, 12, 15]
rows = []
for i, d in enumerate(data, 1):
    p = os.path.join(root, 'videos', f'{i:02d}', 'keyframes')
    fs = [os.path.join(p, f'{t:02d}s.jpg') for t in times]
    if any(os.path.exists(x) for x in fs):
        rows.append((d, fs))

cw, ch = 170, 145
sheet = Image.new('RGB', (cw * 7, ch * len(rows)), 'white')
draw = ImageDraw.Draw(sheet)
for r, (d, fs) in enumerate(rows):
    for c, f in enumerate(fs):
        x, y = c * cw, r * ch
        if os.path.exists(f):
            im = Image.open(f).convert('RGB')
            im.thumbnail((cw, 120))
            sheet.paste(im, (x + (cw - im.width) // 2, y))
        draw.text((x + 4, y + 122), f"{d['brand'][:18]} {times[c]}s", fill='black')
sheet.save(os.path.join(root, 'keyframe_sheet.jpg'), quality=90)
print(len(rows))

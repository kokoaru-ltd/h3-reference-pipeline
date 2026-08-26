from PIL import Image, ImageDraw
import json, math, os
from urllib.parse import urlparse, parse_qs

root = os.path.dirname(__file__)
data = json.load(open(os.path.join(root, 'success_ads_10.json'), encoding='utf-8'))
items = []
for d in data:
    u = urlparse(d['video_url'])
    vid = parse_qs(u.query).get('v', [None])[0] or u.path.rstrip('/').split('/')[-1]
    p = os.path.join(root, 'thumbnails', vid + '.jpg')
    items.append((d, p if os.path.exists(p) else None))

W, H, cols = 360, 260, 2
sheet = Image.new('RGB', (W * cols, H * math.ceil(len(items) / cols)), 'white')
draw = ImageDraw.Draw(sheet)
for n, (d, p) in enumerate(items):
    if p:
        im = Image.open(p).convert('RGB')
        im.thumbnail((W, 200))
    else:
        im = Image.new('RGB', (W, 200), '#d9d9d9')
        ImageDraw.Draw(im).text((24, 88), 'thumbnail unavailable', fill='#555555')
    x, y = (n % cols) * W, (n // cols) * H
    sheet.paste(im, (x + (W - im.width) // 2, y))
    draw.text((x + 8, y + 204), f"{n+1:02d} {d['brand']}", fill='black')
    draw.text((x + 8, y + 222), d['industry'], fill='gray')
sheet.save(os.path.join(root, 'thumbnail_sheet.jpg'), quality=92)
print(f'saved {len(items)} thumbnails')

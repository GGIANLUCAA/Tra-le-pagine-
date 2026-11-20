from PIL import Image
import os

im = Image.open('/workspace/wheat-cypresses.jpg')
IW, IH = im.size  # 4000 x 3184
print('source', IW, IH)

OUT_W, OUT_H = 1080, 1920  # 9:16
# max crop width that fits 9:16 in the source
max_crop_w = int(IH * OUT_W / OUT_H)  # 1791

scenes = [
    # (cx, cy, zoom, duration, motion)
    (1800, 2600, 1.25, 6.0, 'in'),    # 1 campo grano
    (3200, 1700, 1.20, 6.0, 'in'),    # 2 cipressi
    (3350, 1850, 1.70, 6.0, 'hold'),  # 3 cipressi dettaglio
    (2000,  600, 1.20, 6.0, 'in'),    # 4 cielo
    (1400,  550, 1.85, 6.0, 'hold'),  # 5 pennellate cielo
    (2600, 2000, 0.95, 6.0, 'out'),   # 6 campo+cipressi
    (1000, 2400, 1.70, 6.0, 'hold'),  # 7 dettaglio pennellate
    (2000, 1592, 0.90, 6.0, 'out'),   # 8 tutta opera
    (1200, 2700, 1.50, 6.0, 'in'),    # 9 campo dettaglio
    (2000, 1592, 0.85, 4.0, 'hold'),  # 10 tutta opera ferma
]

os.makedirs('/workspace/scenes', exist_ok=True)
for i, (cx, cy, zoom, dur, motion) in enumerate(scenes, 1):
    cw = int(max_crop_w / zoom)
    ch = int(cw * OUT_H / OUT_W)
    left = cx - cw // 2
    top = cy - ch // 2
    left = max(0, min(left, IW - cw))
    top = max(0, min(top, IH - ch))
    crop = im.crop((left, top, left + cw, top + ch))
    crop = crop.resize((OUT_W, OUT_H), Image.LANCZOS)
    crop.save(f'/workspace/scenes/scene_{i:02d}.jpg', quality=92)
    print(f'scene {i}: crop {cw}x{ch} @ ({left},{top}) dur {dur} {motion}')
print('done')

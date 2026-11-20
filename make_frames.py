from PIL import Image, ImageDraw, ImageFont
import numpy as np, os

im = Image.open('/workspace/wheat-cypresses.jpg')
IW, IH = im.size
OUT_W, OUT_H = 1080, 1920
FPS = 30
max_crop_w = int(IH * OUT_W / OUT_H)  # 1791

scenes = [
    (1800, 2600, 1.0, 1.10, 6.0),   # in
    (3200, 1700, 1.0, 1.10, 6.0),   # in
    (3350, 1850, 1.0, 1.0, 6.0),    # hold
    (2000,  600, 1.0, 1.10, 6.0),   # in
    (1400,  550, 1.0, 1.0, 6.0),    # hold
    (2600, 2000, 1.10, 1.0, 6.0),   # out
    (1000, 2400, 1.0, 1.0, 6.0),    # hold
    (2000, 1592, 1.10, 1.0, 6.0),   # out
    (1200, 2700, 1.0, 1.10, 6.0),   # in
    (2000, 1592, 1.0, 1.0, 4.0),    # hold
]

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f_title = ImageFont.truetype(FONT_BOLD, 52)
f_sub = ImageFont.truetype(FONT_BOLD, 30)
f_c1 = ImageFont.truetype(FONT_BOLD, 38)
f_c2 = ImageFont.truetype(FONT_BOLD, 26)
f_c3 = ImageFont.truetype(FONT_BOLD, 20)

GOLD = (255, 201, 77)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_shadow(draw, text, font, x, y, fill, ox=3, oy=3):
    draw.text((x+ox, y+oy), text, font=font, fill=(0,0,0,200))
    draw.text((x, y), text, font=font, fill=fill)

def centered(draw, text, font, y, fill):
    bbox = draw.textbbox((0,0), text, font=font)
    w = bbox[2]-bbox[0]
    x = (OUT_W - w)//2
    draw_shadow(draw, text, font, x, y, fill)

os.makedirs('/workspace/frames', exist_ok=True)
# clean
for f in os.listdir('/workspace/frames'):
    os.remove(f'/workspace/frames/{f}')

fade_frames = int(0.15 * FPS)  # 4-5 frames
frame_idx = 0
total_duration = sum(s[4] for s in scenes)
total_frames = int(total_duration * FPS)
print(f'total {total_frames} frames, {total_duration}s')

for si, (cx, cy, zs, ze, dur) in enumerate(scenes):
    N = int(dur * FPS)
    for i in range(N):
        t = i / max(N-1, 1)
        zoom = zs + (ze - zs) * t
        cw = int(max_crop_w / zoom)
        ch = int(cw * OUT_H / OUT_W)
        left = cx - cw // 2
        top = cy - ch // 2
        left = max(0, min(left, IW - cw))
        top = max(0, min(top, IH - ch))
        crop = im.crop((left, top, left+cw, top+ch)).resize((OUT_W, OUT_H), Image.LANCZOS)
        # fade
        if i < fade_frames:
            a = i / fade_frames
        elif i > N - fade_frames - 1:
            a = (N - 1 - i) / fade_frames
        else:
            a = 1.0
        if a < 1.0:
            arr = np.array(crop).astype(np.float32)
            arr = arr * a
            crop = Image.fromarray(arr.astype(np.uint8))
        # title (first 4s = 120 frames of whole video)
        if frame_idx < 120:
            d = ImageDraw.Draw(crop)
            centered(d, 'WHEAT FIELD WITH CYPRESSES', f_title, int(OUT_H*0.38), WHITE)
            centered(d, 'Vincent van Gogh  |  1889', f_sub, int(OUT_H*0.46), GOLD)
        # credit (last 3.5s = 105 frames)
        if frame_idx > total_frames - 105:
            d = ImageDraw.Draw(crop)
            centered(d, 'Wheat Field with Cypresses', f_c1, int(OUT_H*0.40), WHITE)
            centered(d, 'Vincent van Gogh, 1889', f_c2, int(OUT_H*0.47), GOLD)
            centered(d, 'The Metropolitan Museum of Art, New York', f_c3, int(OUT_H*0.52), WHITE)
        crop.save(f'/workspace/frames/f_{frame_idx:05d}.jpg', quality=90)
        frame_idx += 1

print(f'generated {frame_idx} frames')

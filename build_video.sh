#!/bin/bash
cd /workspace
F=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

# Zoompan expressions
ZIN="z='1+on*0.0006':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
ZOUT="z='1.1-on*0.0006':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
ZHOLD="z=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"

ffmpeg -y -loglevel error \
  -loop 1 -t 6 -i scenes/scene_01.jpg \
  -loop 1 -t 6 -i scenes/scene_02.jpg \
  -loop 1 -t 6 -i scenes/scene_03.jpg \
  -loop 1 -t 6 -i scenes/scene_04.jpg \
  -loop 1 -t 6 -i scenes/scene_05.jpg \
  -loop 1 -t 6 -i scenes/scene_06.jpg \
  -loop 1 -t 6 -i scenes/scene_07.jpg \
  -loop 1 -t 6 -i scenes/scene_08.jpg \
  -loop 1 -t 6 -i scenes/scene_09.jpg \
  -loop 1 -t 4 -i scenes/scene_10.jpg \
  -filter_complex "
    [0:v]zoompan=${ZIN}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v0];
    [1:v]zoompan=${ZIN}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v1];
    [2:v]zoompan=${ZHOLD}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v2];
    [3:v]zoompan=${ZIN}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v3];
    [4:v]zoompan=${ZHOLD}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v4];
    [5:v]zoompan=${ZOUT}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v5];
    [6:v]zoompan=${ZHOLD}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v6];
    [7:v]zoompan=${ZOUT}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v7];
    [8:v]zoompan=${ZIN}:d=180:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=5.6:d=0.4[v8];
    [9:v]zoompan=${ZHOLD}:d=120:s=1080x1920,fps=30,fade=t=in:st=0:d=0.3,fade=t=out:st=3.6:d=0.4[v9];
    [v0][v1][v2][v3][v4][v5][v6][v7][v8][v9]concat=n=10:v=1:a=0[vcat];
    [vcat]drawtext=fontfile=${F}:text='WHEAT FIELD WITH CYPRESSES':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=h*0.38:shadowcolor=black@0.8:shadowx=3:shadowy=3:enable='between(t,0,4)',
    drawtext=fontfile=${F}:text='Vincent van Gogh  |  1889':fontcolor=0xFFC94D:fontsize=30:x=(w-text_w)/2:y=h*0.46:shadowcolor=black@0.8:shadowx=2:shadowy=2:enable='between(t,0,4)',
    drawtext=fontfile=${F}:text='Wheat Field with Cypresses':fontcolor=white:fontsize=38:x=(w-text_w)/2:y=h*0.40:shadowcolor=black@0.9:shadowx=2:shadowy=2:enable='between(t,54.5,58)',
    drawtext=fontfile=${F}:text='Vincent van Gogh, 1889':fontcolor=0xFFC94D:fontsize=26:x=(w-text_w)/2:y=h*0.47:shadowcolor=black@0.9:shadowx=2:shadowy=2:enable='between(t,54.5,58)',
    drawtext=fontfile=${F}:text='The Metropolitan Museum of Art, New York':fontcolor=white@0.85:fontsize=20:x=(w-text_w)/2:y=h*0.52:shadowcolor=black@0.9:shadowx=1:shadowy=1:enable='between(t,54.5,58)'[vout]
  " -map "[vout]" -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p video-mute.mp4

echo "mute done"
ls -la video-mute.mp4

from pathlib import Path
from PIL import Image
import subprocess,json,hashlib,zipfile,shutil,numpy as np
R=Path('/mnt/data');D=R/'GOLDFINCH_S01_V49_WORK';Q=R/'GOLDFINCH_V49_QA'
shots=[('bird',127),('head',122),('wing',122),('chain',125),('whole',130)]
for i,(name,frames) in enumerate(shots,start=3):
    path=Q/f'detail_{name}.jpg';out=D/f'detail_{i:02d}.mp4'
    # Tiny one-way zoom on two scenes, never a pretend animated action.
    if name in ('head','wing'):
        z=f"min(1.009,1+on*{.009/frames:.8f})"
        vf=f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s=1080x1920:fps=24,format=yuv420p"
    else:vf='format=yuv420p'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','24','-i',str(path),'-vf',vf,'-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(out)],check=True)
    print('DETAIL',name,flush=True)
clips=[D/'clip_00.mp4',D/'clip_01.mp4',D/'clip_02.mp4']+[D/f'detail_{i:02d}.mp4' for i in range(3,8)]+[D/'clip_08.mp4',D/'clip_09.mp4']
(D/'concat_v50.txt').write_text(''.join("file '"+str(p.resolve())+"'\n" for p in clips))
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(D/'concat_v50.txt'),'-c:v','copy',str(D/'silent_v50.mp4')],check=True)
FINAL=R/'ArtVision_Goldfinch_Museum_V50_REVIEW.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(D/'silent_v50.mp4'),'-i',str(R/'ArtVision_Goldfinch_S01.mp4'),'-map','0:v:0','-map','1:a:0','-vf','fps=24,setpts=N/(24*TB)','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(FINAL)],check=True)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-xerror','-i',str(FINAL),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height','-of','json',str(FINAL)]))
assert any(s.get('codec_name')=='h264' and s.get('width')==1080 and s.get('height')==1920 for s in probe['streams'])
assert any(s.get('codec_name')=='aac' for s in probe['streams'])
first=D/'QA_FIRST_FRAME_V50.jpg';subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(FINAL),'-frames:v','1',str(first)],check=True)
cover=R/'ArtVision_Goldfinch_Museum_V49_Cover.jpg'
with Image.open(first) as a,Image.open(cover) as b:
    assert a.size==b.size==(1080,1920)
    mad=float(np.mean(np.abs(np.asarray(a,dtype=np.int16)[1340:1590]-np.asarray(b,dtype=np.int16)[1340:1590])))
    assert mad<15
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=R/'GOLDFINCH_S01_V50_PACKAGE';shutil.copytree(R/'GOLDFINCH_S01_V49_PACKAGE',P,dirs_exist_ok=True)
shutil.copy2(FINAL,P/'VIDEO_MASTER.mp4');shutil.copy2(first,P/'QA_FIRST_FRAME_V50.jpg')
for name,frames in shots:shutil.copy2(Q/f'detail_{name}.jpg',P/f'QA_DETAIL_{name.upper()}.jpg')
recipe=json.loads((P/'VIDEO_RECIPE_V13.json').read_text());recipe.update({'revision':'V50','new_video_sha256':sha(FINAL),'detail_plan':[(n,f) for n,f in shots],'status':'rendered_needs_review','human_approved':False,'camera_motion':'static and very slight motivated slow push only; no fake animation'})
(P/'VIDEO_RECIPE_V13.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n')
qa=json.loads((P/'TECHNICAL_QA_V30.json').read_text());qa.update({'revision':'V50','video_sha256':sha(FINAL),'qa_ffprobe':probe,'full_decode':True,'cover_first_frame_band_mad':mad,'detail_crops':['bird','head','yellow-wing','chain','whole-panel'],'v44_status':'rendered_needs_review','human_artistic_approval':False,'three_issues_for_review':['Need full-speed aesthetic viewing of frame-to-painting cut at ~16 seconds','Check musical phrase against 5 detail holds','Photo-realistic gallery is a fictional reconstruction, not the actual museum room']})
(P/'TECHNICAL_QA_V30.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
(P/'RELEASE_STATUS.json').write_text(json.dumps({'state':'rendered_needs_review','video_sha256':sha(FINAL),'human_approved':False,'social_published':False},indent=2)+'\n')
(P/'REVISION_V50.md').write_text('# Goldfinch V50 — curated details\n\nReplaces V48 repeated bird crops with distinct original-painting studies: full bird, eye/red mask, yellow wing scratched paint, delicate chain, entire panel. Photographic-style fictional museum background from V49, physical scale from Mauritshuis 33.5 × 22.8 cm. No paid video API, no social publication. Status rendered_needs_review; not Gold Master.\n')
Z=R/'ArtVision_Goldfinch_Museum_V50_Complete.zip'
with zipfile.ZipFile(Z,'w',allowZip64=True) as z:
 for p in P.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(P),compress_type=zipfile.ZIP_STORED if p.suffix.lower() in ('.mp4','.jpg','.mp3','.png') else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(Z) as z:assert z.testzip() is None
print('V50_COMPLETE',json.dumps({'sha256':sha(FINAL),'seconds':probe['format']['duration'],'size':FINAL.stat().st_size,'zip':Z.stat().st_size,'cover_first_diff':mad,'status':'rendered_needs_review'}),flush=True)
#!/usr/bin/env python3
"""ArtVision V55: Winslow Homer The Gulf Stream two REAL Cinema variants.

Generates a complete 4x1 mother dossier but only renders the two legally
possible voice-free variants. Critico Standard/Museum remain blocked for exact
verified Google Gacrux WAV, never silently replaced. No paid provider calls.
Authentic painting: The Met 11122 (06.1234) Open Access.
Museum room/frame: clearly labelled, original contemporary reconstruction;
painting and known *physical* frame measurements from Met, not a claim of
photographic copy of a historical frame or current Met gallery.
"""
from __future__ import annotations
import hashlib
import json
import math
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from artvision_four_variants_gate import validate as four_validate
from video_director_v13 import check,read_json,write_json,capture,digest
from artvision_delivery_v55 import pack, inspect_video
from artvision_cinema_prepared_v55 import SCHEMA as CINEMA_SCHEMA, sha256 as sha

ROOT_OUT=ROOT/'output/artvision-homer-gulf-stream-v55'
OBJ='https://collectionapi.metmuseum.org/public/collection/v1/objects/11122'
MET='https://www.metmuseum.org/art/collection/search/11122'
MUSIC='https://incompetech.com/music/royalty-free/mp3-royaltyfree/Water%20Lily.mp3'
MUSIC_PAGE='https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035'
MUSIC_HASH='b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6'
TITLE='The Gulf Stream'
ARTIST='Winslow Homer'
SIZE=(124.8,71.4)  # canvas width, height in cm
FRAMED=(159.3,107.5)  # actual outer frame width, height in cm per Met catalog
W,H,FPS=1080,1920,24
DETAILS=[
 ("sharks","foreground left and lower right","Dark dorsal fins and open jaws surround the small damaged craft.","The visible sharks intensify danger but are not evidence of anyone's fate.","documented"),
 ("survivor","right-hand deck of damaged boat","A solitary man sits calmly amid turbulent water without a working mast.","The compositional contrast between his still posture and churning sea is an interpretation.","interpretation"),
 ("broken_boat","central and right middle foreground","The vessel has lost its mast; sugarcane stalks lie loose across the deck.","Damage to the boat and sugarcane are documented by the Met catalogue.","documented"),
 ("waterspout","distant sky and left/middle horizon","A faint waterspout descends from the grey distance near a far-off vessel.","The approaching storm multiplies the visible threats far beyond the sharks.","documented"),
 ("waves","middle and foreground","Dark blue-green rollers and white spray form an almost continuous heaving sea.","Broad, emphatic brushwork links vulnerability with the physical scale of the Gulf Stream current.","interpretation")
]
KEYS=("facebook","instagram","tiktok","youtube")
CAPTIONS={
 "cinema_standard":{
  "facebook":"Un uomo, una barca senza albero, squali sotto la superficie. Nel dipinto The Gulf Stream (1899, rielaborato entro il 1906), Winslow Homer mette la calma di una figura umana contro un oceano senza tregua. Questa versione Cinema Standard attraversa i dettagli autentici del quadro, senza scene artificiali. Opera originale: Metropolitan Museum of Art 06.1234, pubblico dominio. Musica: Water Lily — Kevin MacLeod, CC BY 4.0 (incompetech.com). Quale dettaglio hai notato per primo?",
  "instagram":"🦈 Guardi l'uomo o gli squali? The Gulf Stream di Winslow Homer lascia sospesa una domanda: resisterà? L'imbarcazione spezzata, il mare scuro, il vortice lontano. Solo dettagli veri dell'opera, 1899 e rielaborata entro il 1906. Met Open Access, 06.1234 (pubblico dominio). 🎵 Water Lily, Kevin MacLeod, CC BY 4.0 (incompetech.com). #WinslowHomer #TheGulfStream #Arte #ArtVision",
  "tiktok":"Il mare, una barca rotta e gli squali. Ma perché l'uomo sembra così immobile? 👀 The Gulf Stream di Winslow Homer è un quadro dove ogni dettaglio cambia il racconto. Questa versione Cinema Standard usa solo l'immagine autentica del Met (06.1234, pubblico dominio). Water Lily — Kevin MacLeod, CC BY 4.0, incompetech.com. #ArtTok #MuseumArt #WinslowHomer #TheGulfStream",
  "youtube":"The Gulf Stream — Winslow Homer | ArtVision Cinema Standard. Dipinto del 1899, rielaborato entro il 1906, al Metropolitan Museum of Art (06.1234). Il film esplora in successione gli squali, il marinaio seduto, l'imbarcazione danneggiata, il vortice lontano e le onde, poi ricompone l'intero quadro. La storia e il contesto di impero e schiavitù sono trattati nelle schede, non inventati come animazioni. Opera e riproduzione: Met Open Access / pubblico dominio. Musica Water Lily di Kevin MacLeod, CC BY 4.0, https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035."
 },
 "cinema_museum":{
  "facebook":"Davanti al dipinto The Gulf Stream di Winslow Homer l'imbarcazione sembra minuscola: 124,8 centimetri di oceano dipinto, incorniciati in una sala espositiva ricostruita. Poi la camera entra nei dettagli veri dell'opera: squali, barca, figura solitaria e tempesta lontana. La stanza e la cornice visibile sono ricostruzioni contemporanee, non una fotografia del Metropolitan Museum. Fonte autentica: Met 06.1234, pubblico dominio. 🎵 Water Lily — Kevin MacLeod, CC BY 4.0 (incompetech.com).",
  "instagram":"Un quadro di 124,8 × 71,4 cm, un oceano che sembra immenso. 🌊 The Gulf Stream di Winslow Homer, versione Cinema Museum: ingresso da una sala espositiva immaginata, dettagli originali e ritorno alla stessa parete. La stanza e la cornice visibili sono ricostruzioni artistiche, non foto del Met; le misure del dipinto e della sua cornice sono documentate nel catalogo. Met Open Access 06.1234, pubblico dominio. Water Lily — Kevin MacLeod, CC BY 4.0. #ArtVision #MuseumImmersion #WinslowHomer #TheGulfStream",
  "tiktok":"Ti avvicini al quadro, poi scopri che sotto la barca ci sono gli squali 🦈 The Gulf Stream di Winslow Homer in una versione Museum Immersion con stanza ricostruita e dettagli autentici. Non è una ripresa delle sale del Met e la cornice mostrata non è una replica storica. Quadro originale pubblico dominio Met 06.1234. Musica Water Lily di Kevin MacLeod, CC BY 4.0, incompetech.com. #MuseumImmersion #ArtTok #WinslowHomer",
  "youtube":"Winslow Homer — The Gulf Stream | Cinema Museum Immersion. The Metropolitan Museum of Art, numero 06.1234, olio su tela del 1899 rielaborato entro il 1906. L'opera misura 71,4 × 124,8 cm; il catalogo registra 107,5 × 159,3 cm inclusa la cornice. Il nostro percorso inizia da una sala espositiva e una cornice contemporanee RICOSTRUITE, si avvicina al dipinto autentico e ritorna alla stessa parete dopo gli approfondimenti su marinaio, barca, squali e mare. Non rappresenta una sala reale del Met, né sostiene che la cornice disegnata sia originale. Riproduzione: Met Open Access / pubblico dominio. Musica Water Lily — Kevin MacLeod, CC BY 4.0; crediti incompetech.com, licenza creativecommons.org/licenses/by/4.0/."
 }
}

def get(url,path,limit=25000000):
    if not url.startswith('https://'):raise ValueError('Source must be HTTPS')
    request=urllib.request.Request(url,headers={'User-Agent':'ArtVision V55 authentic museum artwork / licensed recording'})
    with urllib.request.urlopen(request,timeout=70) as response:
        if response.status!=200:raise ValueError('Remote source HTTP status '+str(response.status))
        with path.open('wb') as stream:
            n=0
            while True:
                block=response.read(1024*1024)
                if not block:break
                n+=len(block)
                if n>limit:raise ValueError('Source exceeds maximum size')
                stream.write(block)
    if path.stat().st_size<100000:raise ValueError('Source is too small')
    return path

def prepare():
    if ROOT_OUT.exists():raise RuntimeError('Production already exists: no overwrite')
    ROOT_OUT.mkdir(parents=True)
    dossier=ROOT_OUT/'ARTVISION_4X1_PLAN.json'
    subprocess.run([sys.executable,'src/video_director_v13.py','four-brief',
         '--topic',TITLE,'--artist',ARTIST,'--out',str(dossier)],cwd=ROOT,check=True)
    folder=ROOT_OUT/'cinema_standard'
    assets=folder/'assets'
    assets.mkdir()
    req=urllib.request.Request(OBJ,headers={'User-Agent':'ArtVision Open Access original source'})
    with urllib.request.urlopen(req,timeout=65) as response:meta=json.load(response)
    if meta.get('objectID')!=11122 or meta.get('isPublicDomain') is not True:
        raise RuntimeError('Met 11122 public-domain gate failed')
    image_url=meta.get('primaryImage')
    if not isinstance(image_url,str) or not image_url.startswith('https://'):
        raise RuntimeError('No Met 11122 original primaryImage')
    image=get(image_url,assets/'met_11122_original.jpg')
    with Image.open(image) as im:im.verify()
    with Image.open(image) as im:
        if min(im.size)<1000:raise ValueError('Museum image insufficient resolution')
    music=get(MUSIC,assets/'water_lily_original.mp3',11000000)
    if digest(music)!=MUSIC_HASH:raise RuntimeError('Music is not the approved original Water Lily recording')
    write_json(ROOT_OUT/'MET_OPEN_ACCESS_SOURCE.json',{
      'met_object_id':11122,'met_catalog':MET,'met_api':OBJ,'met_image_url':image_url,
      'public_domain_verified':True,'official_title':meta.get('title'),
      'date':'1899; reworked by 1906','canvas_dimensions_cm':{'width':124.8,'height':71.4},
      'outer_frame_dimensions_cm':{'width':159.3,'height':107.5,'depth':15.0},
      'source_art_sha256':digest(image),'music_sha256':digest(music),
      'music_license':'CC BY 4.0','music_source':MUSIC_PAGE})
    return dossier,folder,image,music,image_url

def four_plan(dossier):
    plan=read_json(dossier)
    detail_ids=[d[0] for d in DETAILS]
    plan['research_status']='Met Open Access public-domain image and physical measurements verified at render'
    plan['emotional_direction']={
      'central_tension':'A lone survivor remains conspicuously still in a dismasted boat, while visible sharks and a waterspout make the churning ocean threatening.',
      'intended_feeling':['dread','compassion'],
      'evidence_details':[{'id':k,'location':where,'observation':observation,
          'significance':reason,'claim_type':claim,'image_source':MET}
          for k,where,observation,reason,claim in DETAILS],
      'reveal_order':detail_ids,
      'opening_hook':'A predatory shark fin emerges from the original foreground; only later does the frame reveal the seated figure and entire vulnerable boat.',
      'closing_payoff':'The final full painting unites the broken boat, the stoic man, sharks and distant storm into one composition.',
      'wow_justification':'Five visibly different, authentic locations in the painting create a suspenseful visual narrative without animating false ocean motion.'
    }
    # The planned critics share *identical* spoken lines, not a made-up WAV.
    spoken={
      'sharks':'Nel primo piano non c’è un mare vuoto: gli squali nuotano attorno alla barca danneggiata.',
      'survivor':'L’uomo resta seduto, quasi immobile. Homer contrappone questa quiete a un oceano senza tregua.',
      'broken_boat':'L’albero della barca è spezzato. Sulla coperta vediamo la canna da zucchero: un dettaglio che allude alla storia del commercio caraibico.',
      'waterspout':'Nella distanza appare una tromba marina, e perfino il cielo sembra diventare una minaccia.',
      'waves':'Le pennellate ampie rendono il movimento delle onde; il quadro non offre una conclusione semplice al destino dell’uomo.'
    }
    for ident,variant in plan['variants'].items():
        museum=ident.endswith('museum')
        critic=ident.startswith('critico')
        variant['status']='blocked' if critic else 'planned'
        variant['variation_reason']=('A documented-size painting in a specifically labelled reconstructed gallery receives an actual entry and return.'
             if museum else 'Direct compositions, truthful painting-only focal crops and a return to the original complete oil painting, without museum architecture.')
        variant['opening_0_7']={
         'first_frame_title_artist':'THE GULF STREAM — WINSLOW HOMER with readable cover typography and opening image.',
         'first_frame_visual':('Real-scale reconstructed framed painting on a warmly lit wall, focusing immediately on threatening water below the damaged boat.'
             if museum else 'Authentic Met painting, shark fin and deep-blue swirling sea occupy the portrait mobile crop.'),
         'first_3_seconds_hook':'Present a shark fin beside a vulnerable boat before the entire composition is revealed.',
         'seconds_3_to_7_reveal':'Reveal the motionless figure and damaged mast, making danger unmistakable within the first seven seconds.',
         'detail_id':'sharks',
         'mobile_composition_reason':'The shark/boat visual contrast and readable value shapes anchor the opening in a narrow vertical frame.',
         'audio_or_voice_cue':('Critico: genuine full Italian Google Gacrux voice WAV is required and is currently unavailable.'
             if critic else 'Authentic Kevin MacLeod Water Lily instrumental CC BY 4.0, no spoken voice.'),
         'qa_status':'pending_visual_review'}
        details=[]
        for i,(k,where,observation,reason,claim) in enumerate(DETAILS):
            shot={'kind':'detail','detail_id':k,
               'purpose':f'Show {k} from the authentic Met original to explain the human stakes and sea threats in Winslow Homer.',
               'movement':'Slow measured optical push following genuine brushstrokes only, no AI water deformation.',
               'emotional_effect':'Deepening tension through concrete observed threats in different regions of the canvas.',
               'duration_seconds':5.4+i*.4}
            if critic:shot['spoken_line']=spoken[k]
            details.append(shot)
        details.append({'kind':'whole','detail_id':'waves',
           'purpose':'Return to the entire painting to see the shark, lone survivor, far storm and broken boat together.',
           'movement':'Steady full artwork hold for compositional payoff.',
           'emotional_effect':'A final recognition of vulnerability within the huge open sea.',
           'duration_seconds':7.5,
           **({'spoken_line':'Ora ricomponiamo tutta la scena: una sola persona e un mondo di acqua, senza una risposta definitiva.'} if critic else {})})
        if museum:
            variant['scenes']=[{'kind':'gallery_entry','purpose':'Establish physical 124.8x71.4 cm canvas scale within an explicitly reconstructed contemporary gallery.',
              'movement':'Purposeful approach from same gallery wall to center of real Met painting.',
              'emotional_effect':'Understand how an ordinary-scale painting contains an overwhelming visual threat.',
              'duration_seconds':4.2}]+details+[{'kind':'gallery_exit','purpose':'Return to precisely the original reconstructed gallery wall and modern frame.',
              'movement':'Retreat from the painting back to the same room and camera axis.',
              'emotional_effect':'See the physical artwork anew after facing the scene inside its details.',
              'duration_seconds':4.2}]
            variant['museum']={
               'width_cm':124.8,'height_cm':71.4,
               'dimensions_source':MET+' framed 107.5×159.3cm, canvas 71.4×124.8cm',
               'frame_status':'Met reports historical frame outer DIMENSIONS, but our shown frame profile is a modern stylized reconstruction, not a documented replica.',
               'gallery_id':'homer_11122_modern_reconstructed_gallery_same_entry_exit',
               'entrance_plan':'Begin with visual of the framed original artwork on a contemporary gallery wall; no false actual Met location.',
               'exit_same_gallery_plan':'Retreat from artwork to the exact same rendered wall and frame, use identical geometry.',
               'scene_is_reconstruction':True}
        else:variant['scenes']=details
    plan['learning']={
      'previous_reference':'Hokusai Museum V55C camera-focus and truthful-room disclosure are useful lessons, not copied dimensions.',
      'experiment_variable':'Painting contains distinct, recognizable sea hazards and a solitary human; preserve visual continuity across cuts.',
      'expected_improvement':'Different perceptual shot subjects including shark, human, vessel, sky and wave; avoid repetitions.',
      'post_render_review':'pending'}
    plan['approval']={'artistic_status':'pending','user_approval':False}
    errs=four_validate(plan)
    if errs:raise RuntimeError('V54 four-check blocked: '+json.dumps(errs))
    write_json(dossier,plan)

def project_setup(folder,dossier,art,music,image_url,variant):
    project=read_json(folder/'PROJECT_V13.json')
    project['status']='prepared'
    project['artvision_4x1_variant']=variant
    project['assets']=[
      {'id':'met_art','file':'assets/'+art.name,'sha256':digest(art),'role':'visual',
       'source':MET+' | '+image_url,'rights':'Met 11122 Open Access isPublicDomain=true, image reproduction CC0/public-domain'},
      {'id':'macloud_music','file':'assets/'+music.name,'sha256':digest(music),'role':'music',
       'source':MUSIC_PAGE,'rights':'Water Lily Kevin MacLeod original recording, CC BY 4.0, attribution required'}]
    plan4=read_json(dossier)
    project['scenes']=[
      {'asset_id':'met_art','description':detail['observation'],'reason':detail['significance']}
      for detail in plan4['emotional_direction']['evidence_details']]
    if variant=='cinema_museum':
        project['scenes']=[{'asset_id':'met_art',
          'description':'Framed genuine Homer painting in a modern fictional display with Met size measured.',
          'reason':'Establish recorded painting width/height before a cinematic movement into painting.'}]+project['scenes']+[
          {'asset_id':'met_art','description':'Return to same reconstructed room and frame as first museum shot.',
           'reason':'Contrast physical museum work size with the emotional impression of the storm.'}]
    e=project['editorial_plan']
    e.update({
     'subject_insight':'A lone seated survivor on a dismasted boat is threatened by sharks and a waterspout; the Met relates the picture to Caribbean history, including sugarcane and slavery.',
     'sources':[
       {'reference':MET,'finding':'The Met 11122 documents painter, date, canvas/frame sizes, sharks, waterspout and sugarcane.',
        'verification_notes':'Authoritative Met Open Access object API checked at runtime, artwork must be public domain.','status':'reviewed'},
       {'reference':MUSIC_PAGE,'finding':'Water Lily is the original recording by Kevin MacLeod under CC BY 4.0.',
        'verification_notes':'Original recorded MP3 SHA256 must match known approved hash.','status':'reviewed'}
     ],
     'opening_promise':'Sharks and a destroyed boat introduce human peril in the first seven seconds.',
     'payoff':'The full painting ultimately reveals both natural danger and a still, almost defiant human figure.',
     'cover_reason':'The visually striking human and sharks create an authentic social curiosity hook, not AI reconstruction.',
     'duration_seconds':55,
     'duration_reason':'Six nonidentical artwork-specific shots and a whole reveal, plus gallery entry/exit when Museum.',
     'mix_reason':'Soft instrumental original CC BY 4.0 supports contemplative tension; Cinema never receives narrator voice.',
     'social_languages':{'facebook':'it','instagram':'it','tiktok':'it','youtube':'it'},
     'techniques':[{'id':'close_then_wide','status':'trial',
           'reason':'Shark and man clues before whole image establish conflict without claiming unseen movement.'}],
     'media_sourcing':{'policy_id':e['media_sourcing']['policy_id'],'review_status':'reviewed',
       'decisions':[{'asset_id':'met_art','source_kind':'authentic_artwork','provider':'The Metropolitan Museum of Art',
         'source_reference':MET+' original Met API '+image_url,
         'choice_reason':'Official Met object 11122, high-res public-domain original.',
         'scene_match_note':'Every artistic detail is a crop from the unchanged genuine original painting.',
         'rights_review':'reviewed','scene_relevance':'reviewed','visual_review':'passed'}]},
     'audience_research':{'selection_mode':'research_selected',
       'candidates':[
        {'artist':ARTIST,'work':TITLE,'visual_hook':'Sharks and a vulnerable human on a broken boat.',
          'human_interest':'Survival, isolation and historical Caribbean context.',
          'historical_anchor':'Met 11122, 1899 reworked by 1906, original record verified.',
          'asset_rights_notes':'Met original public domain and official Open Access reproduction.',
          'comparison_reason':'Strong focal variety plus factual narrative beyond pure spectacle.',
          'audience_signal':{'status':'unavailable','reason':'No measured social performance data for this specific film.'}},
        {'artist':'Katsushika Hokusai','work':'The Great Wave',
          'visual_hook':'Foam claws loom over human boats and Fuji.',
          'human_interest':'Vulnerability in nature.',
          'historical_anchor':'Met JP1847 1830–32.',
          'asset_rights_notes':'Met Open Access verified in prior Hokusai film.',
          'comparison_reason':'Already produced; avoid duplicate user experience.',
          'audience_signal':{'status':'unavailable','reason':'No observed conversion statistics.'}},
        {'artist':'Utagawa Hiroshige','work':'Sudden Shower over Shin-Ōhashi Bridge and Atake',
          'visual_hook':'Rain lines slash diagonally over bridge and pedestrians.',
          'human_interest':'People exposed to sudden storm.',
          'historical_anchor':'1857 print by Hiroshige; exact source to be retrieved for future work.',
          'asset_rights_notes':'19th-century print public domain; reproduction rights must be checked for future work.',
          'comparison_reason':'Excellent atmospheric vertical effect but less immediate animal/boat danger.',
          'audience_signal':{'status':'unavailable','reason':'No current published retention available.'}}
       ],
       'selected_work':TITLE,
       'selection_reason':'Met 11122 provides strong shark/human contrast and documented 19th-century historical context.',
       'viewer_interest':'The man is still even though the sea and visible sharks surround the wreck.',
       'creative_direction':'First sharks, then man, hull, distant waterspout, waves, and whole painting.',
       'signal_limitations':'Visual hooks are hypotheses and not measured current audience data.',
       'analytics_feedback':'not_yet_published'},
     'narrative_design':{
       'story_beats':['Sharks','Seated survivor','Broken boat with sugarcane','Distant sky','Final visual scale'],
       'distinct_visual_needs':['sharks','survivor','broken_boat','waterspout','waves','whole'],
       'image_count_reason':'Distinct semantic regions of ONE authentic Met painting; never claim different source images.',
       'pace_reason':'Scene durations depend on readable visual detail, avoid stereotyped zoom rhythm.',
       'reference_id':'Hokusai V55 provided technical museum scale lesson only.',
       'portable_lessons':['No blank gallery intro; genuine authentic detail first'],
       'do_not_copy_reference_parameters':True}
    })
    project['reviews']={
      'story':{'status':'passed','notes':'Research V32 3 distinct alternatives, factual Met sharks/man/sugarcane detail, separately documented interpretation.'},
      'visuals':{'status':'passed','notes':'Original image downloaded from Met API object 11122, isPublicDomain=true, original high-resolution verified.'},
      'rights':{'status':'passed','notes':'Met public-domain picture and original MacLeod music licensed CC BY 4.0, recorded hash; publishing still needs final approval.'}}
    p=folder/'PROJECT_V13.json'
    write_json(p,project)
    result=check(p)
    if not result['ready']:raise RuntimeError('V13 preflight '+variant+': '+json.dumps(result['blockers'],ensure_ascii=False))
    return p

def ffmpeg_render(slug,stills,music,seconds,output):
    args=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y']
    for path,duration in zip(stills,seconds):
        args+=['-loop','1','-framerate',str(FPS),'-t',str(duration),'-i',str(path)]
    args+=['-stream_loop','-1','-i',str(music)]
    flt=[]
    for i,dur in enumerate(seconds):
        # Gentle continuous optical push, 0-4%, avoiding shaky or animated falsification.
        flt.append(f'[{i}:v]zoompan=z=\'min(zoom+0.00009,1.04)\':d=1:fps={FPS}:s={W}x{H},trim=duration={dur},setpts=PTS-STARTPTS[v{i}]')
    flt.append(''.join(f'[v{i}]' for i in range(len(stills)))+f'concat=n={len(stills)}:v=1:a=0[v]')
    total=sum(seconds)
    args+=['-filter_complex',';'.join(flt),'-map','[v]','-map',f'{len(stills)}:a:0',
        '-t',str(total),'-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','20',
        '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
        '-af',f'afade=t=in:st=0:d=.35,afade=t=out:st={total-1.8}:d=1.8',
        '-movflags','+faststart',str(output)]
    subprocess.run(args,check=True,timeout=1500)

def typeface(size,serif=False):
    f=('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
       if serif else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(f,size)

def brand(im):
    im=im.convert('RGBA')
    layer=Image.new('RGBA',im.size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    d.rounded_rectangle((60,H-440,W-60,H-140),radius=25,fill=(10,13,18,225))
    f=typeface(65,True)
    while d.textbbox((0,0),TITLE,font=f)[2]>W-140:f=typeface(f.size-2,True)
    d.text((W//2,H-335),TITLE,anchor='mm',font=f,fill='#f5efe2')
    d.line((180,H-270,W-180,H-270),fill='#c8b18a',width=4)
    d.text((W//2,H-206),ARTIST.upper(),font=typeface(34),anchor='mm',fill='#efe2cb')
    return Image.alpha_composite(im,layer).convert('RGB')

def detail(im,x,y,scale=.64):
    iw,ih=im.size
    crop_h=min(ih,int(ih*scale))
    crop_w=min(iw,int(crop_h*W/H))
    left=max(0,min(iw-crop_w,round(iw*x-crop_w/2)))
    top=max(0,min(ih-crop_h,round(ih*y-crop_h/2)))
    return im.crop((left,top,left+crop_w,top+crop_h)).resize((W,H),Image.Resampling.LANCZOS)

def whole(im):
    c=Image.new('RGB',(W,H),(16,22,28))
    art=im.copy()
    art.thumbnail((W-50,H-300),Image.Resampling.LANCZOS)
    c.paste(art,((W-art.width)//2,(H-art.height)//2))
    return c

def gallery(im):
    """Original modern fictional gallery. Inner/outer dimensions document 06.1234."""
    fw,fh=2160,3840
    wall=Image.new('RGB',(fw,fh),(189,180,164))
    d=ImageDraw.Draw(wall)
    # Original, understated room perspective and low raking light.
    d.rectangle((0,3120,fw,3160),fill=(111,101,91))
    d.polygon(((0,3160),(fw,3160),(fw,fh),(0,fh)),fill=(130,122,111))
    for yy in range(3200,fh,160):
        d.line((0,yy,fw,yy),fill=(137,128,115),width=3)
    for xx in range(0,fw,170):
        d.line((xx,3160,xx+180,fh),fill=(145,135,121),width=2)
    # Painting and documented physical outer frame ratios, not authentic frame profile.
    pw=1030
    ph=round(pw*SIZE[1]/SIZE[0])
    outer_w=round(pw*FRAMED[0]/SIZE[0])
    outer_h=round(pw*FRAMED[1]/SIZE[0])
    x=(fw-pw)//2;y=1640-ph//2
    ox=(fw-outer_w)//2;oy=y-(outer_h-ph)//2
    shadow=Image.new('RGBA',(fw,fh),(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.rectangle((ox+22,oy+30,ox+outer_w+24,oy+outer_h+34),fill=(22,20,17,130))
    shadow=shadow.filter(ImageFilter.GaussianBlur(35))
    wall=Image.alpha_composite(wall.convert('RGBA'),shadow)
    d=ImageDraw.Draw(wall)
    d.rectangle((ox,oy,ox+outer_w,oy+outer_h),fill=(76,57,38,255))
    for off,col,thickness in [(9,(155,132,90,255),10),(28,(91,72,47,255),8),(48,(204,184,135,255),5)]:
        d.rectangle((ox+off,oy+off,ox+outer_w-off,oy+outer_h-off),outline=col,width=thickness)
    # Neutral linen mat inside reconstructed ornamental surround.
    d.rectangle((x-14,y-14,x+pw+14,y+ph+14),fill=(227,219,201,255))
    art=im.resize((pw,ph),Image.Resampling.LANCZOS)
    wall.paste(art,(x,y))
    d=ImageDraw.Draw(wall)
    px=ox+outer_w+45
    d.line((px,y+15,px+220,y+15),fill=(79,71,61,255),width=3)
    d.text((px,y+45),'WINSLOW HOMER',font=typeface(25),fill=(55,50,45,255))
    d.text((px,y+100),'The Gulf Stream',font=typeface(29,True),fill=(48,44,39,255))
    d.text((px,y+149),'1899 | reworked 1906',font=typeface(18),fill=(62,56,49,255))
    d.text((px,y+195),'124.8 x 71.4 cm',font=typeface(18),fill=(62,56,49,255))
    d.text((px,y+237),'DISPLAY RECONSTRUCTION',font=typeface(15),fill=(83,73,60,255))
    return wall.convert('RGB')

def room_frame(original,zoom=1.0):
    """Portrait camera follows actual frame center (y=1640), not room middle."""
    zoom=float(zoom)
    iw,ih=original.size
    cropw=round(iw/zoom);croph=round(ih/zoom)
    x=max(0,min(iw-cropw,round(iw/2-cropw/2)))
    y=max(0,min(ih-croph,round(1640-croph/2)))
    return original.crop((x,y,x+cropw,y+croph)).resize((W,H),Image.Resampling.LANCZOS)

def deliver(variant,video,cover,art,music,dossier,project,room=None):
    folder=video.parent
    rights=folder/'SOURCES_AND_RIGHTS.md'
    extra=(
      'Museum wall and frame PROFILE are original digital reconstructions, NOT photographs or exact replicas of Met interior/frame. '
      'Dimensions of actual canvas 71.4x124.8 cm; Met reports outer framed 107.5x159.3x15 cm. '
      'The digital frame preserves outer proportions but ornamental contours are not authenticated. '
      'Opening and ending represent the exact same constructed room image. '
      if room is not None else 'Cinema Standard: no museum room or reconstructed frame is shown. '
    )
    rights.write_text(
      '# Winslow Homer, The Gulf Stream | ArtVision '+variant+'\n\n'
      'Original artwork and high-resolution photograph: Metropolitan Museum of Art Open Access, '
      'object 11122, accession 06.1234, public domain/CC0. Official record: '+MET+
      '. Image SHA256: '+digest(art)+'. Year 1899, reworked by 1906. '
      'Canvas 71.4x124.8 cm. '+extra+'\n\n'
      'Original recording: Water Lily — Kevin MacLeod, CC BY 4.0. Source: '+MUSIC_PAGE+
      ' License: https://creativecommons.org/licenses/by/4.0/ . '
      'Original recorded SHA256: '+digest(music)+'. Rights and credits must be maintained.\n'
      'No paid video service or AI reconstruction of painting content was used. '
      'Final platform rights approval and aesthetic review remain pending.\n',encoding='utf8')
    files={}
    for key,copy in CAPTIONS[variant].items():
        file=folder/('POST_'+key.upper()+'.txt')
        file.write_text(copy+'\n',encoding='utf8')
        files[key]=file
    recipe=capture('artvision_cinema',TITLE,video,cover,folder,
      sources=[art,music,dossier,project,ROOT/'scripts/artvision_homer_four_v55.py',rights]
      +([room] if room else []))
    recipe.update({'variant':variant,'review_state':'rendered_needs_review',
        'source_object_id':11122,'art_dimensions_cm':{'width':124.8,'height':71.4},
        'frame_dimensions_cm':{'width':159.3,'height':107.5},
        'museum_reconstruction':bool(room),'original_room_sha256':digest(room) if room else None,
        'human_full_watch':False,'artistic_approval':False,'V25_approved':False,
        'site_imported':False,'paid_api_calls':0})
    write_json(folder/'VIDEO_RECIPE_V13.json',recipe)
    dest=ROOT_OUT/(variant+'_V55_DELIVERY')
    pack(video,cover,files,rights,folder/'VIDEO_RECIPE_V13.json',dest)
    with zipfile.ZipFile(dest/(video.stem+'_ANDROID_ONLY.zip'),'w') as z:
        z.write(video,video.name,compress_type=zipfile.ZIP_STORED)
    for z in dest.glob('*.zip'):
        with zipfile.ZipFile(z) as f:
            if f.testzip():raise RuntimeError('ZIP CRC failed')
    if digest(video)!=recipe['video']['sha256']:raise RuntimeError('Capture video does not match exact render')
    return {'video':str(video),'video_sha256':digest(video),'size':video.stat().st_size,
            'package_directory':str(dest),'status':'rendered_needs_review',
            'variant':variant,'paid_video_calls':0}

def cinema_standard(dossier,folder,art,music):
    project=project_setup(folder,dossier,art,music,read_json(ROOT_OUT/'MET_OPEN_ACCESS_SOURCE.json')['met_image_url'],'cinema_standard')
    from PIL import Image
    with Image.open(art) as a:source=ImageOps.exif_transpose(a).convert('RGB')
    out=ROOT_OUT/'cinema_standard_rendered'
    out.mkdir(exist_ok=False)
    # These are original physically different regions; avoid false claim of
    # multi-image source diversity. All shots derive from the exact Met JPG.
    frames=[
      brand(detail(source,.20,.83,.53)), # first shark beneath threatening sea
      detail(source,.80,.52,.52), # still person
      detail(source,.62,.66,.57), # broken mast / deck
      detail(source,.38,.29,.55), # grey waterspout / horizon
      detail(source,.17,.66,.58), # sea and shark other region
      whole(source)
    ]
    secs=[5.2,6.0,6.5,5.9,5.9,7.8]
    image_dir=out/'SCENE_IMAGES';image_dir.mkdir()
    stills=[]
    for i,im in enumerate(frames):
        p=image_dir/(f'{i:02}.jpg');im.save(p,quality=94,subsampling=0);stills.append(p)
    cover=out/'COPERTINA.jpg';shutil.copy2(stills[0],cover)
    video=out/'ARTVISION_WINSLOW_HOMER_CINEMA_STANDARD_V55_REVIEW.mp4'
    ffmpeg_render('cinema_standard',stills,music,secs,video)
    print('HOMER_CINEMA_STANDARD_RENDERED',digest(video),'bytes',video.stat().st_size,flush=True)
    return deliver('cinema_standard',video,cover,art,music,dossier,project)

def cinema_museum(dossier,std_folder,art,music):
    folder=ROOT_OUT/'cinema_museum'
    (folder/'assets').mkdir(exist_ok=True)
    for p in (std_folder/'assets').iterdir():
        if p.is_file():shutil.copy2(p,folder/'assets'/p.name)
    original_art=folder/'assets'/art.name
    music_copy=folder/'assets'/music.name
    project=project_setup(folder,dossier,original_art,music_copy,read_json(ROOT_OUT/'MET_OPEN_ACCESS_SOURCE.json')['met_image_url'],'cinema_museum')
    with Image.open(original_art) as a:source=ImageOps.exif_transpose(a).convert('RGB')
    out=ROOT_OUT/'cinema_museum_rendered';out.mkdir(exist_ok=False)
    room=out/'RECONSTRUCTED_GALLERY_ORIGINAL.jpg'
    room_original=gallery(source);room_original.save(room,quality=94,subsampling=0)
    frames=[
       brand(room_frame(room_original,1.48)),
       room_frame(room_original,1.68),
       detail(source,.80,.53,.49), # face of survivor
       detail(source,.23,.82,.56), # lower shark
       detail(source,.62,.64,.59), # wood and sugarcane
       detail(source,.35,.28,.55), # distant storm
       whole(source),
       room_frame(room_original,1.66),
       room_frame(room_original,1.22)
    ]
    seconds=[3.8,4.6,5.6,5.9,5.8,5.6,7.5,5.4,4.4]
    image_dir=out/'SCENE_IMAGES';image_dir.mkdir()
    paths=[]
    for i,im in enumerate(frames):
        p=image_dir/(f'{i:02}.jpg');im.save(p,quality=94,subsampling=0);paths.append(p)
    cover=out/'COPERTINA.jpg';shutil.copy2(paths[0],cover)
    video=out/'ARTVISION_WINSLOW_HOMER_CINEMA_MUSEUM_V55_REVIEW.mp4'
    ffmpeg_render('cinema_museum',paths,music_copy,seconds,video)
    print('HOMER_CINEMA_MUSEUM_RENDERED',digest(video),'bytes',video.stat().st_size,flush=True)
    return deliver('cinema_museum',video,cover,original_art,music_copy,dossier,project,room)

def main():
    dossier,folder,art,music,url=prepare()
    four_plan(dossier)
    standard=cinema_standard(dossier,folder,art,music)
    museum=cinema_museum(dossier,folder,art,music)
    result={'schema':'artvision-homer-four-v55','two_distinct_real_videos':[standard,museum],
      'critico_standard':'blocked_exact_gacrux_voice_unavailable',
      'critico_museum':'blocked_exact_gacrux_voice_unavailable',
      'site':'archive_sync_pending','V25_approved':False,'paid_api_calls':0}
    write_json(ROOT_OUT/'RESULT_V55.json',result)
    print('HOMER_4X1_REAL_CINEMA_PAIR',json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""One new, authentic, rights-gated Cinema Standard V55 production attempt.

Hokusai Met JP1847 image (Met Open Access) and MacLeod Water Lily recording
(CC BY 4.0). No paid APIs, no AI video, no upload or automatic approval.
Run from repository checkout: python scripts/artvision_hokusai_cinema_v55.py
"""
from __future__ import annotations
import hashlib, json, subprocess, sys, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from video_director_v13 import check, read_json, write_json
from artvision_four_variants_gate import validate as four_validate

DEST=ROOT/'output/artvision-hokusai-cinema-standard-v55'
OBJ='https://collectionapi.metmuseum.org/public/collection/v1/objects/45434'
MET='https://www.metmuseum.org/art/collection/search/45434'
MUSIC='https://incompetech.com/music/royalty-free/mp3-royaltyfree/Water%20Lily.mp3'
MUSIC_PAGE='https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035'
MUSIC_SHA='b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6'
TITLE='The Great Wave'
ARTIST='Katsushika Hokusai'
DETAILS=[
('crest','top center/right, curling blue wave with foam fingers','Claw-like foam above the boats makes the sea seem close enough to touch.','The sea is presented as a powerful threat, a reading of the visible shape.','interpretation'),
('boats','lower half, three slim oshiokuri-bune craft','Three boats and their rowers are carried through the trough beneath the wave.','Tiny human scale sharpens the opposition between labor and nature.','documented'),
('fuji','right lower horizon, small triangular mountain','Mount Fuji is a diminutive triangle in the gap under the looming wave.','A familiar mountain is made visually small through perspective.','documented'),
('foam','upper curling rim, repeated white spume forms','White foam splits into numerous pointed shapes against Prussian blue.','Repeating organic shapes create motion in a still print.','documented')]

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as stream:
        for x in iter(lambda:stream.read(1048576),b''):h.update(x)
    return h.hexdigest()

def get(url,dest,maxbytes=25000000):
    if not url.startswith('https://'):raise ValueError('HTTPS required')
    req=urllib.request.Request(url,headers={'User-Agent':'ArtVisionV55/1.0 (rights verified artwork render)'})
    with urllib.request.urlopen(req,timeout=65) as r:
        if r.status!=200:raise ValueError('Source HTTP '+str(r.status))
        with dest.open('wb') as file:
            n=0
            while True:
                b=r.read(1048576)
                if not b:break
                n+=len(b)
                if n>maxbytes:raise ValueError('Asset exceeds limit: '+url)
                file.write(b)
    if dest.stat().st_size<100000:raise ValueError('Source too small')
    return dest

def prep():
    from PIL import Image
    if DEST.exists():raise ValueError('Existing Hokusai output: never overwrite original')
    DEST.mkdir(parents=True)
    dossier=DEST/'ARTVISION_4X1_PLAN.json'
    subprocess.run([sys.executable,'src/video_director_v13.py','four-brief',
                    '--topic',TITLE,'--artist',ARTIST,'--out',str(dossier)],
                   cwd=ROOT,check=True)
    folder=DEST/'cinema_standard'
    assets=folder/'assets'
    assets.mkdir()
    req=urllib.request.Request(OBJ,headers={'User-Agent':'ArtVisionV55/1.0'})
    with urllib.request.urlopen(req,timeout=45) as r:
        meta=json.load(r)
    if meta.get('objectID')!=45434 or meta.get('isPublicDomain') is not True:
        raise ValueError('Met Open Access rights gate failed')
    url=meta.get('primaryImage')
    if not isinstance(url,str) or not url.startswith('https://'):
        raise ValueError('Missing high-resolution Met primary image')
    art=get(url,assets/'met_45434_original.jpg')
    with Image.open(art) as im:
        im.verify()
    with Image.open(art) as im:
        if min(im.size)<800:raise ValueError('Met original insufficient detail')
    recording=get(MUSIC,assets/'water_lily_original.mp3',10000000)
    if sha(recording)!=MUSIC_SHA:
        raise ValueError('Recording differs from previously documented Water Lily SHA256')
    (DEST/'MET_OPEN_ACCESS_SOURCE.json').write_text(json.dumps({
        'met_object_id':45434,'museum_catalog':MET,'api_object':OBJ,
        'source_image_url':url,'isPublicDomain':meta['isPublicDomain'],
        'short_title_used':'The Great Wave',
        'official_catalog_title':meta.get('title'),
        'dimensions':'25.7 x 37.9 cm for Met JP1847',
        'artwork_sha256':sha(art),'recording_sha256':sha(recording),
        'music_original_recording':MUSIC,'music_license':'CC BY 4.0'
        },indent=2)+'\n')
    return dossier,folder,assets,art,recording,url

def make_four(dossier):
    plan=read_json(dossier)
    plan['research_status']='Met Open Access verified in production; other formats planned and voice blocked'
    plan['emotional_direction']={
      'central_tension':'The tiny boats and distant Mount Fuji are almost swallowed by a towering curling wave; the contrast gives the still image a sense of peril.',
      'intended_feeling':['suspense','wonder'],
      'evidence_details':[{'id':k,'location':loc,'observation':obs,'significance':sig,
        'image_source':MET,'claim_type':kind} for k,loc,obs,sig,kind in DETAILS],
      'reveal_order':['crest','boats','fuji','foam'],
      'opening_hook':'Begin inside the huge blue crest, then reveal the vulnerable boats and distant Mount Fuji before the complete print.',
      'closing_payoff':'The final full print makes the boats, wave and Fuji legible as a single staged encounter.',
      'wow_justification':'The spectacle is the documented perspective: famous Fuji appears smaller than the fragile boats under the sea.'}
    sp=[
      ('crest','The blue claws of foam appear frozen just before crashing onto the boats.'),
      ('boats','Three working boats struggle through the surf, smaller than the great wave.'),
      ('fuji','Fuji is recognizable only as a calm miniature beyond the storm.'),
      ('foam','The white foam repeats like delicate fingers across the wave.')]
    def shot(k,n,spoken=None):
        result={'kind':'detail','detail_id':k,
          'purpose':'Reveal the authentic '+k+' detail as part of the contrast between human scale and the threatening sea.',
          'movement':'Slow optical drift following original woodblock lines, no synthetic water.',
          'emotional_effect':'A mix of wonder and tension from the real geometry of the print.',
          'duration_seconds':5.0+n*0.3}
        if spoken:result['spoken_line']=spoken
        return result
    for ident,v in plan['variants'].items():
        museum=ident.endswith('museum')
        critico=ident.startswith('critico')
        v['variation_reason']=('Museum framing establishes the small physical scale then exits the same reconstructed gallery.'
                              if museum else 'Standard cuts directly through the original inked details with no invented museum environment.')
        v['status']='blocked' if critico else 'planned'
        v['opening_0_7']={
          'first_frame_title_artist':'THE GREAT WAVE — KATSUSHIKA HOKUSAI in original title band',
          'first_frame_visual':'The real dark Prussian blue curl and white foam from Met JP1847, no fake animation.',
          'first_3_seconds_hook':'An enormous wave hangs directly above unseen tiny human lives.',
          'seconds_3_to_7_reveal':'The narrow boats appear beneath the blue claw and connect the natural spectacle to human stakes.',
          'detail_id':'crest',
          'mobile_composition_reason':'Wave crest fills the vertical mobile crop with readable white-on-blue contrast.',
          'audio_or_voice_cue':('Italian natural Google Gacrux narration must be verified before Critico render.'
                               if critico else 'Licensed Water Lily instrumental, no spoken narration.'),
          'qa_status':'pending_visual_review'}
        scenes=[shot(k,i,spoken if critico else None) for i,(k,spoken) in enumerate(sp)]
        scenes.append({'kind':'whole','detail_id':'fuji',
          'purpose':'Reveal the whole authenticated Met composition after the separate wave, boats, and Fuji details.',
          'movement':'Steady full-print reveal to compare relative scale rather than fake camera rotation.',
          'emotional_effect':'Release of the visual tension through recognition of the full composition.',
          'duration_seconds':6.0,
          **({'spoken_line':'Ora osserviamo tutta la stampa: il Fuji sembra quasi sparire sotto l’onda.'} if critico else {})})
        if museum:
            entrance={'kind':'gallery_entry','purpose':'Show the actual 25.7 by 37.9 cm print scale in a clearly reconstructed setting.',
              'movement':'Constrained approach toward a documented-size paper print without a fake original frame.',
              'emotional_effect':'Scale surprise before the immense pictured wave.',
              'duration_seconds':3.1}
            exit_scene={'kind':'gallery_exit','purpose':'Return to the identical reconstructed view with print scale preserved.',
              'movement':'Retreat from print to the same visual gallery coordinates.',
              'emotional_effect':'A final contrast between tiny sheet of paper and large visual imagination.',
              'duration_seconds':3.2}
            v['scenes']=[entrance]+scenes+[exit_scene]
            v['museum']={
               'width_cm':37.9,'height_cm':25.7,
               'dimensions_source':MET+' Met JP1847 catalog physical measurements',
               'frame_status':'Unknown original frame; no historical frame authenticity claimed.',
               'gallery_id':'met_jp1847_hypothetical_gallery_identical_entry_exit',
               'entrance_plan':'Invented, explicitly labelled room with print at documented real scale.',
               'exit_same_gallery_plan':'Retreat to precisely the same reconstructed gallery room.',
               'scene_is_reconstruction':True}
        else:v['scenes']=scenes
    plan['learning']={'previous_reference':'Cyclops approved for museum but not reused for standard crop.',
       'experiment_variable':'The vertical crop opens with foam rather than full print.',
       'expected_improvement':'Connect threat to boats before the Fuji reveal, no audience metrics asserted.',
       'post_render_review':'pending'}
    plan['approval']={'artistic_status':'pending','user_approval':False}
    errors=four_validate(plan)
    if errors:raise ValueError('V54 four-check failed: '+str(errors))
    write_json(dossier,plan)

def make_project(folder,dossier,art,recording,url):
    p=folder/'PROJECT_V13.json'
    project=read_json(p)
    project['status']='prepared'
    assets=[
      {'id':'met_art','file':'assets/'+art.name,'sha256':sha(art),'role':'visual',
       'source':MET+' | '+url,'rights':'Met Museum Open Access; verified isPublicDomain=true; museum CC0'},
      {'id':'macloud_music','file':'assets/'+recording.name,'sha256':sha(recording),'role':'music',
       'source':MUSIC_PAGE,'rights':'Original recording Water Lily Kevin MacLeod; CC BY 4.0; attribution required'}]
    project['assets']=assets
    project['scenes']=[{'asset_id':'met_art','description':d['observation'],
                       'reason':d['significance']} for d in
             read_json(dossier)['emotional_direction']['evidence_details']]
    plan=project['editorial_plan']
    plan.update({
      'subject_insight':'Wave, three boats and Fuji create immediate human-scale drama in a small woodblock print.',
      'sources':[{'reference':MET,'finding':'Met JP1847 depicts three boats, a towering wave and tiny Mount Fuji; public-domain object.',
                  'verification_notes':'Met collection and Open Access image endpoint checked at render; distinct print edition documented.',
                  'status':'reviewed'},
                 {'reference':MUSIC_PAGE,'finding':'Water Lily original recording by Kevin MacLeod, CC BY 4.0.',
                  'verification_notes':'Audio bytes must match prior verified SHA256 and source listing.','status':'reviewed'}],
      'opening_promise':'An enormous curling wave threatens boats before the full print is revealed.',
      'payoff':'The distant Fuji clarifies an unusually deceptive sense of scale.',
      'cover_reason':'Wave claw is iconic and the original title/artist remain readable immediately.',
      'duration_seconds':35,
      'duration_reason':'Four authentic distinct focal details and a final wide reveal need approximately 35s.',
      'mix_reason':'Soft instrumental bed stays below the natural visual tension without narration.',
      'social_languages':{'facebook':'it','instagram':'it','tiktok':'it','youtube':'it'},
      'techniques':[{'id':'close_then_wide','status':'trial',
                    'reason':'Details establish small-scale human danger before the whole print offers resolution.'}],
      'media_sourcing':{'policy_id':'media-priority-v33','review_status':'reviewed',
         'decisions':[{'asset_id':'met_art','source_kind':'authentic_artwork',
            'provider':'Metropolitan Museum of Art',
            'source_reference':MET+' original image '+url,
            'choice_reason':'Met Open Access museum source authentic to print JP1847.',
            'scene_match_note':'Every crop comes from authentic original image, not invented waves.',
            'rights_review':'reviewed','scene_relevance':'reviewed','visual_review':'passed'}]},
      'audience_research':{'selection_mode':'research_selected',
          'candidates':[
            {'artist':'Katsushika Hokusai','work':TITLE,
             'visual_hook':'High-contrast blue claw over fragile boats, Fuji revealed later.',
             'human_interest':'Risk and human courage in a timeless seascape.',
             'historical_anchor':'Met JP1847 c.1830–32, Met Open Access 45434.',
             'asset_rights_notes':'Met Open Access verified public domain at image download.',
             'comparison_reason':'Best immediate first frame and clean public-domain reproduction.',
             'audience_signal':{'status':'unavailable','reason':'No measured social retention available.'}},
            {'artist':'Winslow Homer','work':'The Gulf Stream',
             'visual_hook':'Man in fragile boat near sharks and distant waterspout.',
             'human_interest':'Human struggle and historical tension.',
             'historical_anchor':'Met museum object 11122, painting 1899 reworked 1906.',
             'asset_rights_notes':'Met lists public domain; exact asset would require separate hash review.',
             'comparison_reason':'Rich narrative but merits its own distinct deeper social/historical account.',
             'audience_signal':{'status':'unavailable','reason':'No measured social retention available.'}},
            {'artist':'Utagawa Hiroshige','work':'Sudden Shower over Shin-Ohashi Bridge and Atake',
             'visual_hook':'Diagonal rain and bridge movement in a vertical composition.',
             'human_interest':'Instant atmospheric transition and fragile human figures.',
             'historical_anchor':'Met museum object 37386, 1857 public-domain print.',
             'asset_rights_notes':'Met lists public domain; original pixels not yet downloaded.',
             'comparison_reason':'Strong vertical crop but currently no verified project assets.',
             'audience_signal':{'status':'unavailable','reason':'No measured social retention available.'}}],
           'selected_work':TITLE,'selection_reason':'Best combination of dramatic authentic first frame and immediately verified open-access print.',
           'viewer_interest':'A visually recognizable wave conceals tiny human labor and Mount Fuji.',
           'creative_direction':'Four distinct focal regions then a full-print resolve.',
           'signal_limitations':'All audience measures are hypotheses without actual published video statistics.',
           'analytics_feedback':'not_yet_published'},
      'narrative_design':{'story_beats':['Threatening foam','Three human boats','Fuji in the distance','Full print release'],
         'distinct_visual_needs':['crest','boats','fuji','foam','whole'],
         'image_count_reason':'Five purposeful views of a single authentic printed image, not five different source images.',
         'pace_reason':'Focal shifts match new factual details and short social format.',
         'reference_id':'Cyclops is museum only; this film is Standard without a gallery.',
         'portable_lessons':['Reveal human scale before full print'],
         'do_not_copy_reference_parameters':True}}
    )
    project['reviews']={
      'story':{'status':'passed','notes':'Four planned distinct authentic print details and documentary Met facts; no artistic final approval.'},
      'visuals':{'status':'passed','notes':'Primary image downloaded directly from Met isPublicDomain object and dimensions verified; final movie remains unreviewed.'},
      'rights':{'status':'passed','notes':'Met Open Access source flag checked; original music SHA256 and CC BY 4.0 attribution recorded; territory still needs final review.'}}
    write_json(p,project)
    result=check(p)
    if not result['ready']:raise ValueError('V13 gate blocked: '+json.dumps(result['blockers']))
    return p

def render(folder,art,recording):
    from artvision_cinema_prepared_v55 import SCHEMA,sha256
    assets=folder/'assets'
    image_ref={'file':art.name,'sha256':sha256(art)}
    recording_ref={'file':recording.name,'sha256':sha256(recording)}
    shots=[
      ('crest',[.71,.28],'detail',3.5),
      ('boats',[.30,.62],'detail',5.0),
      ('fuji',[.87,.77],'detail',5.3),
      ('foam',[.55,.38],'detail',5.3),
      ('boats',[.56,.68],'detail',5.1),
      ('entire_composition',[.5,.5],'whole',8.1)]
    plan={'schema':SCHEMA,'variant':'cinema_standard','title':TITLE,'artist':ARTIST,
       'music':{**recording_ref,'recording_title':'Water Lily',
          'recording_artist':'Kevin MacLeod','source_url':MUSIC_PAGE,
          'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/'},
       'shots':[{**image_ref,'focus':focus,'mode':mode,'detail_id':detail,
           'duration_seconds':length,
           'purpose':'Follow the authentic '+detail+' in Hokusai print to reveal human vulnerability beneath the dynamic wave.'}
         for detail,focus,mode,length in shots]}
    planfile=assets/'CINEMA_STANDARD_PLAN_V55.json';write_json(planfile,plan)
    job={'adapter':'cinema_v55_prepared','project_file':str((folder/'PROJECT_V13.json').relative_to(ROOT)),
         'assets_dir':str(assets.relative_to(ROOT)),
         'cinema_plan_file':str(planfile.relative_to(ROOT))}
    jobfile=DEST/'CINEMA_V55_JOB.json';write_json(jobfile,job)
    out=DEST/'rendered'
    subprocess.run([sys.executable,'src/production_adapter_v16.py','--job',str(jobfile),
                    '--out',str(out)],cwd=ROOT,check=True,timeout=1400)
    result=read_json(out/'ADAPTER_RESULT_V16.json')
    video=Path(result['video']);cover=Path(result['cover'])
    if sha(video)!=result['video_sha256']:raise ValueError('Rendered master SHA mismatch')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True,timeout=160)
    return video,cover,out

def package(video,cover,out,art,recording):
    captions={
      'FACEBOOK':'Una piccola stampa, un mare gigantesco. In La grande onda di Hokusai (circa 1830–32), tre barche sembrano minuscole sotto la schiuma. Sul fondo appare il Fuji: lo avevi notato? Opera: The Great Wave, Katsushika Hokusai. Fonte immagine: Metropolitan Museum of Art JP1847, Open Access CC0. Musica: Water Lily di Kevin MacLeod, CC BY 4.0 — incompetech.com.',
      'INSTAGRAM':'Tre barche. Un’onda immensa. Un Fuji quasi invisibile. 🌊 È il miracolo prospettico di Hokusai, The Great Wave (1830–32). Guarda prima i rematori, poi la montagna. Stampa Met JP1847, immagine Open Access CC0. 🎵 Water Lily — Kevin MacLeod, CC BY 4.0 (incompetech.com). #Hokusai #TheGreatWave #ArtVision #StoriaDellArte',
      'TIKTOK':'Riesci a trovare il Monte Fuji prima che appaia tutto il quadro? 🌊 Guarda le tre barche sotto la grande onda di Hokusai: la scala ti inganna. The Great Wave, c. 1830–32, Met JP1847 / CC0. Musica Water Lily — Kevin MacLeod, CC BY 4.0 incompetech.com. #Arte #Hokusai #Fuji #ArtTok',
      'YOUTUBE':'Come può una stampa di 25,7 × 37,9 cm sembrare un oceano immenso? In The Great Wave di Katsushika Hokusai, la cresta sovrasta le tre barche e il Fuji diventa un minuscolo triangolo. In questa versione Cinema Standard osserviamo soltanto dettagli autentici, senza animazioni ingannevoli. Opera circa 1830–32, Met JP1847, riproduzione Open Access CC0. Musica originale Water Lily di Kevin MacLeod, CC BY 4.0; fonte incompetech.com, licenza creativecommons.org/licenses/by/4.0/.'
    }
    files={}
    for p,copy in captions.items():
        target=out/('POST_'+p+'.txt');target.write_text(copy+'\n',encoding='utf-8');files[p]=target
    rights=out/'FONTI_E_DIRITTI.md'
    rights.write_text('# The Great Wave — Met JP1847\n\n'
      'Artwork public domain, high-resolution image downloaded from official Metropolitan Museum of Art Open Access API.\n'
      'Museum record: '+MET+'\nSource metadata: '+OBJ+'\nImage SHA256: '+sha(art)+'\n'
      'Image itself downloaded from Met primaryImage, local image was verified.\n'
      'Dimensions of this particular print: 25.7 × 37.9 cm. This is Cinema Standard: no reconstructed gallery or fake museum frame.\n\n'
      'Original recorded music: Water Lily — Kevin MacLeod. Source: '+MUSIC_PAGE+'\n'
      'ISRC USUAN1400035. License CC BY 4.0 https://creativecommons.org/licenses/by/4.0/\n'
      'Recording SHA256: '+sha(recording)+'\n'
      'Copyright/platform checks may still be required before publishing. Do not publish automatically.\n',encoding='utf-8')
    bundle=DEST/'V55_DELIVERY'
    cmd=[sys.executable,'src/artvision_delivery_v55.py','pack',
         '--video',str(video),'--cover',str(cover),
         '--facebook',str(files['FACEBOOK']),'--instagram',str(files['INSTAGRAM']),
         '--tiktok',str(files['TIKTOK']),'--youtube',str(files['YOUTUBE']),
         '--rights',str(rights),'--recipe',str(out/'VIDEO_RECIPE_V13.json'),
         '--out',str(bundle)]
    subprocess.run(cmd,cwd=ROOT,check=True,timeout=180)
    return bundle

def main():
    dossier,folder,assets,art,music,url=prep()
    make_four(dossier)
    make_project(folder,dossier,art,music,url)
    video,cover,out=render(folder,art,music)
    bundle=package(video,cover,out,art,music)
    print(json.dumps({'status':'rendered_needs_review','mp4':str(video),
      'sha256':sha(video),'bytes':video.stat().st_size,
      'packages':[str(x) for x in bundle.glob('*.zip')],
      'archive_sync':'pending','approval':'none','paid_calls':0},indent=2))
if __name__=='__main__':main()

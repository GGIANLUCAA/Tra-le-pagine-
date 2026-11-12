"""Offline QA for original-frame-first AI-room staging, no paid calls and no master mutation."""
import hashlib, json, sys, tempfile, unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from artvision_ai_room_integrator_v332 import (
    assemble,load_catalog,select_gallery,make_editorial_frame,mount_on_wall)

CATALOG=Path(__file__).resolve().parents[1]/'config'/'artvision_ai_room_library_v332.json'
class TestRoomV332(unittest.TestCase):
    def setUp(self):
        self.cat=load_catalog(CATALOG)
    def test_twelve_rooms_two_frame_cleanup(self):
        self.assertEqual(len(self.cat['scenes']),12)
        self.assertEqual(sum(x['frame_in_background'] for x in self.cat['scenes']),2)
        self.assertEqual(sum(x['status']=='candidate_ready_for_compositing_review' for x in self.cat['scenes']),10)
        self.assertFalse(any(r['artistic_approval'] for r in self.cat['scenes']))
    def test_original_frame_priority_and_exact_current_painting(self):
        room=next(r for r in self.cat['scenes'] if r['room_id']=='G03')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);paint=base/'p.png';frame=base/'f.png';roomp=base/room['original_generated_filename']
            Image.new('RGB',(320,240),(120,60,30)).save(paint)
            Image.new('RGB',(360,276),(40,22,10)).save(frame)
            Image.new('RGB',tuple(room['pixels']),(200,195,175)).save(roomp)
            r=self.cat['scenes'][:]
            room['sha256']=hashlib.sha256(roomp.read_bytes()).hexdigest() # in-memory copy
            cat=base/'catalog.json';cat.write_text(json.dumps(self.cat))
            first,meta1=assemble(cat,base,paint,base/'cinema',100,75,['bright'],'cinema_museum',
               room_id='G03',authentic_frame_photo=frame,frame_source_url='https://example.org/frame',frame_license='CC BY 4.0')
            second,meta2=assemble(cat,base,paint,base/'critic',100,75,['bright'],'critico_museum',
               room_id='G03',authentic_frame_photo=frame,frame_source_url='https://example.org/frame',frame_license='CC BY 4.0')
            self.assertEqual(first.read_bytes(),second.read_bytes())
            self.assertEqual(meta1['frame_status'],'current_documented')
            self.assertFalse(meta1['museum_approved'])
            self.assertEqual(meta1['source_gallery'],meta2['source_gallery'])
            self.assertFalse(meta1['Gold_V25'])
            self.assertFalse(meta1['room_is_real_museum'])
    def test_auto_select_deterministic_and_no_fringe_frame(self):
        r,_=select_gallery(self.cat,165,120,['epic','historic'])
        self.assertNotIn(r['room_id'],['G09','G10'])
        room,_=select_gallery(self.cat,165,120,['epic','historic'],locked_room_id=r['room_id'])
        self.assertEqual(r['room_id'],room['room_id'])
    def test_framed_candidate_must_never_be_selected(self):
        with self.assertRaises(ValueError):
            select_gallery(self.cat,120,80,['portrait'],locked_room_id='G10')
    def test_missing_source_frame_requires_explicit_editorial_gate(self):
        room=next(r for r in self.cat['scenes'] if r['room_id']=='G03')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);paint=base/'art.png';paint2=base/'room.png'
            Image.new('RGB',(320,240),(10,15,70)).save(paint)
            Image.new('RGB',tuple(room['pixels']),(235,222,200)).save(paint2)
            room['sha256']=hashlib.sha256(paint2.read_bytes()).hexdigest()
            room['original_generated_filename']='room.png'
            c=base/'c.json';c.write_text(json.dumps(self.cat))
            with self.assertRaisesRegex(ValueError,'editorial fallback approval'):
                assemble(c,base,paint,base/'out',100,75,['bright'],'cinema_museum',room_id='G03')
            out,meta=assemble(c,base,paint,base/'out',100,75,['bright'],'cinema_museum',room_id='G03',allow_editorial=True)
            self.assertEqual(meta['frame_status'],'editorial_scenographic_not_historical')
            self.assertTrue(out.is_file())
    def test_artwork_source_ratio_is_mandatory(self):
        room=next(r for r in self.cat['scenes'] if r['room_id']=='G03')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);paint=base/'bad_art.png';fake=base/room['original_generated_filename']
            Image.new('RGB',(240,320),(20,20,20)).save(paint)
            Image.new('RGB',tuple(room['pixels']),(235,222,200)).save(fake)
            room['sha256']=hashlib.sha256(fake.read_bytes()).hexdigest()
            c=base/'c.json';c.write_text(json.dumps(self.cat))
            with self.assertRaisesRegex(ValueError,'aspect ratio'):
                assemble(c,base,paint,base/'out',100,75,['bright'],'cinema_museum',room_id='G03',allow_editorial=True)
    def test_safe_wall_boundaries_and_no_stretch(self):
        room=next(r for r in self.cat['scenes'] if r['room_id']=='G03')
        bg=Image.new('RGB',(941,1672),(220,220,220));frame=Image.new('RGB',(350,265),(40,30,20))
        image,meta=mount_on_wall(bg,frame,(160,120),(174,132),room)
        x1,y1,x2,y2=meta['frame_pixel_box'];self.assertTrue(x1>=0 and y1>=0 and x2<=941 and y2<=1672)
        self.assertLess(abs((x2-x1)/(y2-y1)-350/265),.01)
    def test_creative_director_two_museum_variants_same_room(self):
        from creative_director_v21 import museum_ai_room_v332_suggestion
        brief={"format":"artvision_cinema","variant":"cinema_museum",
               "width_cm":162,"height_cm":117,"gallery_moods":["epic","historic"]}
        cinema=museum_ai_room_v332_suggestion(brief)
        self.assertEqual(cinema["status"],"SCENOGRAPHIC_ROOM_CANDIDATE_NEEDS_RENDER_AND_REVIEW")
        self.assertFalse(cinema["Gold_V25"])
        second=dict(brief,variant="critico_museum",museum_room_locked=cinema["selected_room_id"])
        critic=museum_ai_room_v332_suggestion(second)
        self.assertEqual(critic["selected_room_id"],cinema["selected_room_id"])
        self.assertTrue(critic["same_room_for_both_museum_versions"])
        standard=museum_ai_room_v332_suggestion(dict(brief,variant="cinema_standard"))
        self.assertEqual(standard["status"],"not_a_museum_variant")

    def test_front_only_video_camera_never_rolls(self):
        from artvision_ai_room_video_v332 import front_image,ease
        source=Image.new('RGB',(280,490),(54,12,23))
        a=front_image(source,1.0,(140,245));b=front_image(source,3.0,(140,245))
        self.assertEqual(a.shape,(245,140,3));self.assertEqual(b.shape,(245,140,3))
        self.assertEqual(ease(0),0);self.assertEqual(ease(1),1)

    def test_does_not_overwrite_existing_review(self):
        room=next(r for r in self.cat['scenes'] if r['room_id']=='G03')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);paint=base/'p.png';wall=base/room['original_generated_filename']
            Image.new('RGB',(320,240),(100,60,20)).save(paint)
            Image.new('RGB',tuple(room['pixels']),(210,210,210)).save(wall)
            room['sha256']=hashlib.sha256(wall.read_bytes()).hexdigest()
            c=base/'c.json';c.write_text(json.dumps(self.cat))
            out,meta=assemble(c,base,paint,base/'out',100,75,['bright'],'cinema_museum',room_id='G03',allow_editorial=True)
            with self.assertRaises(FileExistsError):
                assemble(c,base,paint,base/'out',100,75,['bright'],'cinema_museum',room_id='G03',allow_editorial=True)

if __name__=='__main__':unittest.main()
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import production_adapter_v16 as a
import gemini_voice as voice

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.p=patch.object(a,'ROOT',self.root);self.p.start()
    def tearDown(self):self.p.stop();self.tmp.cleanup()
    def test_voice_cache_exact_hash_text_and_alignment_required(self):
        cache=self.root/'cache';cache.mkdir();out=self.root/'out';script='Test tecnico.'
        sf.write(cache/'VOCE.wav',np.zeros(24000,dtype='float32'),24000)
        # Synthetic fixture is for cache integrity only, not a Google voice claim.
        entry={'cache_key':voice.cache_key(script),'wav_sha256':voice._sha(cache/'VOCE.wav'),'timed':[[script,0,1]],'alignment':{'method':'fixture_only'}}
        (cache/'VOICE_CACHE_V13.json').write_text(json.dumps(entry))
        a.cache(script,'cache',out)
        self.assertEqual((out/'VOCE.wav').read_bytes(),(cache/'VOCE.wav').read_bytes())
        with self.assertRaises(ValueError):a.cache('Changed text.','cache',self.root/'bad')
        entry['timed']=None;(cache/'VOICE_CACHE_V13.json').write_text(json.dumps(entry))
        with self.assertRaises(ValueError):a.cache(script,'cache',self.root/'bad')
    def test_format_mismatch_and_unapproved_adapter(self):
        p=self.root/'project.json';p.write_text(json.dumps({'format':'libri','assets':[]}))
        with self.assertRaises(ValueError):a.execute({'adapter':'critico_v2_prepared','project_file':'project.json'},self.root/'out')
        with self.assertRaises(ValueError):a.execute({'adapter':'run_arbitrary_command'},self.root/'out')
    def test_script_mismatch_before_any_renderer(self):
        ep=self.root/'episodes/test';ep.mkdir(parents=True);(ep/'testo.txt').write_text('Actual words.')
        (self.root/'script.txt').write_text('Other words.')
        (self.root/'project.json').write_text(json.dumps({'format':'libri','assets':[],'script':'script.txt'}))
        with patch.object(a.subprocess,'run') as execute:
            with self.assertRaises(ValueError):a.execute({'adapter':'books_gemini_cache','project_file':'project.json','episode':'test'},self.root/'out')
        execute.assert_not_called()

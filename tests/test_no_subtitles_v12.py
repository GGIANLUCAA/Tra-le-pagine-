"""V12: ensure no subtitle burn-in, SRT/ASS outputs or subtitle tracks."""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"src"/"render.py"
SPEC=importlib.util.spec_from_file_location("video_render_v12",MODULE)


class SubtitleFreeV12Tests(unittest.TestCase):
    def test_no_caption_function_called_from_main(self):
        import ast
        tree=ast.parse(MODULE.read_text(encoding="utf-8"))
        main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=="main")
        calls=[x for x in ast.walk(main) if isinstance(x,ast.Call)]
        self.assertFalse(any(isinstance(x.func,ast.Name) and x.func.id=="subtitles" for x in calls))
        self.assertTrue(any(isinstance(x.func,ast.Name) and x.func.id=="final_video_command" for x in calls))
        self.assertFalse(any("ass=" in ast.unparse(x) for x in calls))
        self.assertIn("unlink(missing_ok=True)",ast.unparse(main))

    def test_old_subtitle_renderer_stored_as_backup(self):
        backup=ROOT/"legacy_backup"/"render_con_sottotitoli_v11.py"
        self.assertTrue(backup.is_file())
        s=backup.read_text(encoding="utf-8")
        self.assertIn('subtitles(timed,out)',s)
        self.assertIn('"-vf","ass="',s)

    def test_command_and_real_ffmpeg_no_subtitles(self):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            self.skipTest("ffmpeg/ffprobe unavailable in local environment")
        import sys
        sys.path.insert(0,str(ROOT/"src"))
        from render import final_video_command
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            segment=folder/"shots.mp4"
            voice=folder/"VOCE.wav"
            music=folder/"MUSICA_ORIGINALE.wav"
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                "-f","lavfi","-i","color=c=gray:s=360x640:r=12:d=1.3",
                "-c:v","libx264","-pix_fmt","yuv420p",str(segment)],check=True)
            for target,frequency in [(voice,"440"),(music,"230")]:
                subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                    "-f","lavfi","-i",f"sine=frequency={frequency}:duration=1.3",
                    "-acodec","pcm_s16le",str(target)],check=True)
            cmd=final_video_command(segment,folder)
            self.assertNotIn("-vf",cmd)
            self.assertNotIn("-filter:v",cmd)
            self.assertIn("-sn",cmd)
            self.assertFalse(any("ass=" in str(x) or ".srt" in str(x) for x in cmd))
            subprocess.run([str(x) for x in cmd],check=True)
            mp4=folder/"TRA_LE_PAGINE_EP01.mp4"
            self.assertTrue(mp4.is_file())
            info=json.loads(subprocess.run(
                ["ffprobe","-v","error","-show_entries",
                 "stream=codec_type","-of","json",str(mp4)],
                text=True,capture_output=True,check=True).stdout)
            types=[x["codec_type"] for x in info.get("streams",[])]
            self.assertIn("video",types)
            self.assertIn("audio",types)
            self.assertNotIn("subtitle",types)
            self.assertFalse((folder/"SOTTOTITOLI.srt").exists())
            self.assertFalse((folder/"captions.ass").exists())

if __name__=="__main__":
    unittest.main()

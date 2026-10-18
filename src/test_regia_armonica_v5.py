#!/usr/bin/env python3
"""Zero-cost tests of V5 story-led effects and very gentle color continuity."""
import json
import tempfile
import zipfile
from pathlib import Path

from PIL import Image
from regia_armonica_v5 import check_plan, prepare


def main():
    source=Path("episodes/01_scacchi/scene_premium.zip")
    cue_data=json.loads(Path("episodes/01_scacchi/scene_cues.json").read_text())
    plan=Path("episodes/01_scacchi/effetti_v4.json")
    config=json.loads(plan.read_text())
    out=Path("output_regia_v5")
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp=Path(tmpdir)
        with zipfile.ZipFile(source) as z:
            images={}
            for number in {c["asset"] for c in cue_data}:
                name=f"scena_{number:02d}.jpg"
                names=[m for m in z.namelist() if Path(m).name==name]
                if not names:raise RuntimeError("Missing premium scene "+name)
                dst=tmp/name
                dst.write_bytes(z.read(names[0]))
                images[number]=dst
            sequence=[images[c["asset"]] for c in cue_data]
            prepared,report=prepare(
                sequence,tmp/"graded",config_path=plan,
                report_path=out/"REGIA_ARMONICA_V5.json",
                contact_path=out/"CONTATTO_SCENE_V5.jpg")
            assert len(prepared)==len(cue_data)
            assert report["grading"]=="gentle"
            for row in report["scenes"]:
                assert all(abs(x)<=lim for x,lim in
                    zip(row["Lab_shift"],(4,3,3))),row
            sheet=Image.open(out/"CONTATTO_SCENE_V5.jpg")
            assert sheet.width>600 and sheet.height>300
            try:
                check_plan({"scenes":[
                    {"cue":0,"effect":"sketch_paint"},
                    {"cue":1,"effect":"brush_reveal"}]},3)
                raise AssertionError("Consecutive reveals were accepted")
            except ValueError:pass
            try:
                check_plan({"scenes":[{"cue":i,"postfx":"glow"}
                    for i in (0,2,4,6,8)]},9)
                raise AssertionError("Excessive postfx accepted")
            except ValueError:pass
    print("PASS V5 color: images",len(prepared),
          "effect budget",report["effect_budget"],
          "adjusted scenes",sum(x["light_grade_applied"] for x in report["scenes"]))


if __name__=="__main__":main()

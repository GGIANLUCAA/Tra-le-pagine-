#!/usr/bin/env python3
"""V238: one anonymous ZeroGPU FLUX.2 Klein 4B edit, source-locked V236.
No token, no paid credits, no retry, no final or human approval.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from PIL import Image, ImageDraw
from storia_rivive_v237_qwen_photo_ab import PROMPT,baseline_report,make_ab

SPACE='black-forest-labs/FLUX.2-klein-4B'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--prior',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--offline',action='store_true')
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    report=baseline_report(args.source,args.prior)
    report.update(version='V238_FLUX2_KLEIN4B_SOURCE_LOCKED_AB',alternative_provider=SPACE,
                  status='SOURCE_LOCKED_PROVIDER_NOT_CALLED')
    if not args.offline:
        from gradio_client import Client,handle_file
        client=Client(SPACE)
        # Official 4B distilled mode: 4 steps, no prompt upsampling / external paid LLM.
        result=client.predict(prompt=PROMPT,
                              input_images=[handle_file(str(args.source))],
                              mode_choice='Distilled (4 steps)',seed=42,
                              randomize_seed=False,width=576,height=1024,
                              num_inference_steps=4,guidance_scale=1.0,
                              prompt_upsampling=False,api_name='/infer')
        output=result[0] if isinstance(result,(tuple,list)) else result
        if isinstance(output,dict):output=output.get('path')
        if not output or not Path(output).is_file():
            raise ValueError('V238_NO_REAL_GENERATED_IMAGE')
        candidate=args.out/'V238_FLUX2_KLEIN4B_REAL_I2I_CANDIDATE.png'
        with Image.open(output) as im:im.convert('RGB').save(candidate)
        report.update(make_ab(args.source,args.prior,candidate,args.out))
        report['status']='V238_REAL_ALTERNATIVE_I2I_NEEDS_ARTISTIC_QA'
        sheet=args.out/'V237_REAL_QWEN_VS_REJECTED_FINEGRAIN.jpg'
        with Image.open(sheet) as im:
            canvas=im.convert('RGB')
            draw=ImageDraw.Draw(canvas)
            draw.rectangle((840,0,1260,44),fill=(23,23,23))
            draw.text((855,16),'FLUX2 KLEIN 4B I2I NEW / REVIEW',fill='white')
            canvas.save(args.out/'V238_REAL_FLUX4B_VS_REJECTED_FINEGRAIN.jpg',quality=91)
        sheet.unlink()
        report['comparison_sheet']='V238_REAL_FLUX4B_VS_REJECTED_FINEGRAIN.jpg'
        report['images'][-1]['name']='FLUX2 KLEIN 4B I2I NEW / REVIEW'
    (args.out/'V238_REAL_MEDIA_STATUS.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V238',report['status'],'FINAL_0_OF_4')
if __name__=='__main__':main()

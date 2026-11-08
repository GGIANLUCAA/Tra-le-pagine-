#!/usr/bin/env python3
"""Generate Italian story with Qwen3-TTS CustomVoice, never fallback to earlier rejected voices.
Each chapter is its own checked audio chunk; keeps one consistent speaker.
"""
import gc,json,os,time
from pathlib import Path
import numpy as np,torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
from storyboard import BEATS

torch.set_num_threads(4)
out=Path("output/bruegel_1559_critico_qwen_v3/build");out.mkdir(parents=True,exist_ok=True)
print("LOADING QWEN3-TTS",torch.__version__,flush=True)
model_id="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
model=Qwen3TTSModel.from_pretrained(model_id,device_map="cpu",dtype=torch.float32,attn_implementation="sdpa")
speaker="Ryan"
print("READY",model_id,"speaker",speaker,flush=True)
checks=[]
for i,beat in enumerate(BEATS):
    path=out/f"chapter_{i:02d}.wav"
    if path.exists():
        audio,sr=sf.read(path,dtype="float32")
    else:
        started=time.monotonic()
        audio_list,sr=model.generate_custom_voice(
            text=beat["spoken"],language="Italian",speaker=speaker,
            instruct="A deeply natural, warmly spoken Italian art-documentary narration: fluent, intimate, emotionally perceptive, real conversational pauses. No shouting or radio-presenter voice.",
            max_new_tokens=1200,
        )
        assert len(audio_list)==1
        audio=np.asarray(audio_list[0],dtype=np.float32).squeeze()
        if audio.ndim>1:audio=audio.mean(axis=-1)
        assert audio.ndim==1 and np.isfinite(audio).all()
        sf.write(path,audio,sr)
        print("CHAPTER",i,"COMPLETED",round(len(audio)/sr,2),"sec","in",round(time.monotonic()-started,1),"s",flush=True)
    dur=len(audio)/sr
    assert 5<=dur<=50,(i,dur)
    checks.append({"index":i,"seconds":dur,"sample_rate":sr,"file":path.name})
    (out/"chapters.json").write_text(json.dumps({"model":model_id,"speaker":speaker,"files":checks},indent=2))
print("VOICE_READY",round(sum(v["seconds"] for v in checks),2),"sec",flush=True)

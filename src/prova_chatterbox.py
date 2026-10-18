"""Provino di narrazione italiana espressiva con Chatterbox Multilingual V3.
Usa la voce predefinita, senza clonare alcuna voce reale.
"""
import time, torch, numpy as np, soundfile as sf, subprocess
from pathlib import Path
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

torch.set_num_threads(4)
out=Path("output");out.mkdir(exist_ok=True)
text = (
 "Immagina di essere rinchiuso in una stanza... "
 "Niente libri. Nessuna voce amica. "
 "E un silenzio che, giorno dopo giorno, ti divora la mente. "
 "Come sopravvivere? Giocando a scacchi! Senza nemmeno una scacchiera."
)
print("Carico Chatterbox Multilingual V3, CPU.",flush=True)
t=time.time()
model=ChatterboxMultilingualTTS.from_pretrained(device="cpu",t3_model="v3")
print("Modello caricato in",round(time.time()-t,1),"secondi",flush=True)
for name,parameters in (
    ("espressivo",{"exaggeration":0.72,"cfg_weight":0.30}),
    ("naturale",{"exaggeration":0.48,"cfg_weight":0.42}),
):
    print("Creo",name,parameters,flush=True)
    start=time.time()
    wav=model.generate(text,language_id="it",**parameters)
    audio=np.asarray(wav.detach().cpu().numpy()).reshape(-1)
    print(name,len(audio)/model.sr,"s audio in",round(time.time()-start,1),"s",flush=True)
    path=out/("CHATTERBOX_V3_"+name+".wav")
    sf.write(str(path),audio,model.sr)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(path),
     "-c:a","libmp3lame","-b:a","160k",str(path.with_suffix(".mp3"))],check=True)
print("Done",flush=True)

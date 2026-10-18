"""Provino di un modello TTS indipendente: Supertonic 3, italiano."""
from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
from supertonic import TTS

TEXT = (
    "Immagina di essere rinchiuso in una stanza. Niente libri. "
    "Nessuna voce amica. E un silenzio che, giorno dopo giorno, ti divora la mente. "
    "Come sopravvivere? Giocando a scacchi. Senza nemmeno una scacchiera."
)

out = Path("output"); out.mkdir(exist_ok=True)
model = TTS(model_dir="assets", auto_download=False)
for voice in ["M1", "M3"]:
    print("Genero voce open-weight italiana", voice, flush=True)
    style = model.get_voice_style(voice_name=voice)
    wav, duration = model.synthesize(
        text=TEXT, lang="it", voice_style=style,
        total_steps=8, speed=1.0,
    )
    source = out / f"SUPERTONIC3_{voice}.wav"
    sf.write(source, np.asarray(wav).squeeze(), 44100)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-codec:a", "libmp3lame", "-b:a", "128k", str(source.with_suffix(".mp3"))
    ], check=True)
print("Provini pronti", flush=True)

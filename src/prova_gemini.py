"""Provino voce Gemini. La chiave proviene solo dai secrets di GitHub."""
import base64
import io
import os
from pathlib import Path
import soundfile as sf
import subprocess
from google import genai

key=os.environ.get("GEMINI_API_KEY")
if not key:
    raise SystemExit("SEGRETO MANCANTE: configura GEMINI_API_KEY in Settings > Secrets and variables > Actions.")
text=("Immagina di essere rinchiuso in una stanza. <short pause> "
      "Niente libri. Nessuna voce amica. "
      "E un silenzio che, giorno dopo giorno, ti divora la mente. "
      "<short pause> Come sopravvivere? <short pause> "
      "Giocando a scacchi. Senza nemmeno una scacchiera.")
client=genai.Client(api_key=key)
r=client.interactions.create(
    model="gemini-3.8-flash-tts",
    input=[{"type":"user_input","content":[{
        "type":"text","text":text,
        "annotations":[{"type":"speech_metadata",
            "style":"Read this Italian passage as a natural, expressive Italian male literary narrator: mature, warm, intimate, articulate, subtle suspense. Respect full stops and rhetorical questions, no flat robotic rhythm, a moment of wonder at the end."}]
    }]}],
    response_format={"type":"audio"},
    generation_config={"speech_config":[{"voice":"Gacrux"}]},
)
if not r.output_audio or not r.output_audio.data:
    raise RuntimeError("API TTS non ha restituito audio")
raw=r.output_audio.data
if isinstance(raw,str):raw=base64.b64decode(raw)
out=Path("output");out.mkdir(exist_ok=True)
path=out/"PROVINO_GEMINI_ITALIANO.wav"
path.write_bytes(raw)
v,sr=sf.read(io.BytesIO(raw),dtype="float32")
print("OK: AUDIO GEMINI COMPLETO -",round(len(v)/sr,2),"secondi,",sr,"Hz")
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                "-i",str(path),"-c:a","libmp3lame","-b:a","160k",
                str(out/"PROVINO_GEMINI_ITALIANO.mp3")],check=True)

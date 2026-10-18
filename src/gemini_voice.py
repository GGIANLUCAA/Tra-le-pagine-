"""TTS narrativo Gemini 3.8 + allineamento parole con Whisper.
Richiede GEMINI_API_KEY come GitHub Actions secret. Mai salvare chiavi nel repository.
"""
import base64
import io
import os
import re
import subprocess
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import soundfile as sf

SAMPLE_RATE = 24000

def sentences(text):
    return [x.strip() for x in re.split(
        r'(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])',
        re.sub(r'\s+', ' ', text.strip())) if x.strip()]

def speech_directed(text):
    """Mantiene tutte le parole, ma aggiunge pochi silenzi narrativi."""
    markers = (
        ("Immagina di essere rinchiuso in una stanza.", "<short pause>"),
        ("Come sopravvivere?", "<short pause>"),
        ("Da dove arriva un talento tanto sorprendente?", "<short pause>"),
        ("E vince.", "<short pause>"),
        ("Ma accetta una seconda partita.", "<short pause>"),
        ("Rinuncia alla partita per salvare se stesso.", "<long pause>"),
        ("È aver trovato la forza di fermarsi.", "<long pause>"),
    )
    for anchor, pause in markers:
        if anchor in text:
            text = text.replace(anchor, anchor + " " + pause, 1)
    # Pause pertinenti al cambio di paragrafo, non ad ogni parola.
    return re.sub(r'\n\s*\n', '\n\n<short pause>\n\n', text)

def tokens(text):
    text = ''.join(c for c in unicodedata.normalize('NFKD', text.lower())
                   if not unicodedata.combining(c))
    return re.findall(r'[a-z0-9]+', text)

def _estimated_timing(phrases, duration):
    sizes = [max(1, len(tokens(s))) for s in phrases]
    total = sum(sizes); pos=0.0; timed=[]
    for k,(s,n) in enumerate(zip(phrases,sizes)):
        end=duration if k==len(phrases)-1 else pos+duration*n/total
        timed.append((s,pos,end));pos=end
    return timed

def align(phrases, audio_path, duration):
    """ASR solo per ricavare tempi: l'originale resta il testo in sovrimpressione."""
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel("base",device="cpu",compute_type="int8",cpu_threads=4)
        segments,_=model.transcribe(str(audio_path),language="it",
                                    beam_size=2,word_timestamps=True,
                                    vad_filter=False)
        heard=[]
        for segment in segments:
            for word in segment.words or []:
                for t in tokens(word.word):
                    heard.append((t,float(word.start),float(word.end)))
        expected=[t for phrase in phrases for t in tokens(phrase)]
        heard_tokens=[x[0] for x in heard]
        if not heard or not expected:
            raise ValueError("Nessuna parola da allineare")
        matcher=SequenceMatcher(None,expected,heard_tokens,autojunk=False)
        matchmap={}
        for block in matcher.get_matching_blocks():
            for off in range(block.size):
                a=block.a+off; b=block.b+off
                matchmap[a]=(heard[b][1],heard[b][2])
        if len(matchmap)<len(expected)*.38:
            raise ValueError("Corrispondenze troppo poche per allineamento affidabile")
        keys=sorted(matchmap)
        from bisect import bisect_left
        def approx(ix):
            if ix in matchmap:
                return matchmap[ix]
            k=bisect_left(keys,ix)
            if k==0:
                ref=keys[0];dt=min(.46,duration/max(1,len(expected)))
                a=max(0,matchmap[ref][0]-(ref-ix)*dt)
                return a,min(duration,a+dt)
            if k==len(keys):
                ref=keys[-1];dt=min(.46,duration/max(1,len(expected)))
                a=min(duration,matchmap[ref][1]+(ix-ref-1)*dt)
                return a,min(duration,a+dt)
            left,right=keys[k-1],keys[k]
            alpha=(ix-left)/(right-left)
            mid=matchmap[left][1]+alpha*(matchmap[right][0]-matchmap[left][1])
            return max(0,mid-.10),min(duration,mid+.10)
        times=[];p=0
        for phrase in phrases:
            count=len(tokens(phrase))
            a=approx(p)[0];b=approx(p+count-1)[1]
            a=max(0,min(duration,a));b=max(a+.05,min(duration,b))
            times.append((phrase,a,b))
            p+=count
        print("Allineamento ASR:",len(heard),"parole ascoltate;",
              len(expected),"parole copione;",len(matchmap),"corrispondenze",flush=True)
        return times
    except Exception as exc:
        print("ATTENZIONE: uso tempi stimati, ASR non disponibile:",exc,flush=True)
        return _estimated_timing(phrases,duration)

def synthesize(text,outdir):
    from google import genai
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    key=os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY non configurata: GitHub -> Settings -> "
            "Secrets and variables -> Actions -> New repository secret. "
            "Non inserirla mai nei file pubblici o nei messaggi.")
    spoken=speech_directed(text)
    print("Genero un'unica recitazione italiana completa con pause interpretative.",flush=True)
    client=genai.Client(api_key=key)
    interaction=client.interactions.create(
        model="gemini-3.8-flash-tts",
        input=[{
            "type":"user_input",
            "content":[{
                "type":"text",
                "text":spoken,
                "annotations":[{
                    "type":"speech_metadata",
                    "style":"intimate, expressive audiobook storytelling; natural human rhythm, dramatic but never exaggerated, curiosity in questions, brief reflective silences, tender restrained ending"
                }]
            }]
        }],
        response_format={"type":"audio"},
        generation_config={"speech_config":[{"voice":"Gacrux"}]},
    )
    if not interaction.output_audio or not interaction.output_audio.data:
        raise RuntimeError("Gemini TTS non ha restituito audio")
    b=interaction.output_audio.data
    if isinstance(b,str):
        b=base64.b64decode(b)
    data,sr=sf.read(io.BytesIO(b),dtype="float32")
    if data.ndim==2:
        data=data.mean(axis=1)
    if sr!=SAMPLE_RATE:
        from scipy.signal import resample_poly
        import math
        g=math.gcd(sr,SAMPLE_RATE)
        data=resample_poly(data,SAMPLE_RATE//g,sr//g)
    data=np.asarray(data,dtype=np.float32)
    if not data.size:
        raise ValueError("Audio vuoto")
    maxpeak=float(np.max(np.abs(data)))
    if maxpeak>.93:
        data=data*(.93/maxpeak)
    path=outdir/"VOCE.wav"
    sf.write(path,data,SAMPLE_RATE)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-i",str(path),"-c:a","libmp3lame","-b:a","160k",
         str(outdir/"VOCE_NATURALE.mp3")],check=True)
    duration=len(data)/SAMPLE_RATE
    print("Narrazione Gemini:",round(duration,2),"secondi",flush=True)
    timed=align(sentences(text),path,duration)
    (outdir/"INFO_VOCE_GEMINI.txt").write_text(
        "Motore: Gemini 3.8 Flash TTS. Profilo narratore maturo Gacrux.\n"
        "Testo recitato in unica sessione, pause naturali dirette.\n"
        "Allineamento parole con Whisper base, fallback proporzionale.\n"
        "L'utilizzo dell'API segue quote e condizioni Google AI Studio.\n",
        encoding="utf-8"
    )
    return data,timed

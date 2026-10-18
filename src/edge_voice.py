"""Sintesi narrativa italiana con Edge Neural e timestamp delle frasi.

Genera un intero paragrafo per richiesta, evitando il reset dell'intonazione
a ogni frase. I timestamp SentenceBoundary sono usati per sottotitoli e scene.
Nota: licenza commerciale di Edge Read Aloud non chiarita pubblicamente.
"""
import asyncio
import re
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import numpy as np
import soundfile as sf

VOICE = "it-IT-DiegoNeural"
RATE = "-5%"
PITCH = "-2Hz"
SAMPLE_RATE = 24000


def _sentences(text):
    normalized = re.sub(r"\s+", " ", text.strip())
    return [x.strip() for x in re.split(
        r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])", normalized
    ) if x.strip()]


async def _one_paragraph(text):
    """Scarica MP3 e metadati frase, riprovando problemi di rete temporanei."""
    for attempt in range(3):
        data = bytearray()
        spans = []
        try:
            stream = edge_tts.Communicate(
                text, voice=VOICE, rate=RATE, pitch=PITCH,
                boundary="SentenceBoundary"
            )
            async for chunk in stream.stream():
                if chunk["type"] == "audio":
                    data.extend(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    spans.append(chunk)
            if not data:
                raise RuntimeError("Nessun audio ricevuto da Edge TTS")
            return bytes(data), spans
        except Exception as exc:
            if attempt == 2:
                raise
            print("Riprovo sintesi, tentativo", attempt + 2, exc, flush=True)
            await asyncio.sleep(2.5 * (attempt + 1))


def _timebounds(sentences, events, seconds):
    """Allinea ogni frase ai confini dichiarati dal servizio, con fallback."""
    if len(events) == len(sentences):
        st = [max(0.0, float(e["offset"]) / 10_000_000) for e in events]
        en = [
            min(seconds, float(e["offset"] + e["duration"]) / 10_000_000)
            for e in events
        ]
        if st and all(0 <= x < seconds for x in st) and all(
            st[i] < st[i + 1] for i in range(len(st) - 1)
        ):
            return [
                (sentences[i], st[i], max(st[i] + .06, min(seconds, en[i])))
                for i in range(len(sentences))
            ], "SentenceBoundary"
    # Qualora Microsoft restituisca una segmentazione differente, manteniamo
    # il video funzionante usando una stima per lunghezza delle singole frasi.
    weights = [max(5, len(s)) for s in sentences]
    total = sum(weights)
    start = 0.0
    result = []
    for i, sentence in enumerate(sentences):
        finish = seconds if i == len(sentences) - 1 else start + seconds * weights[i] / total
        result.append((sentence, start, finish))
        start = finish
    return result, "stima_proporzionale"


async def _synthesize(text, outdir):
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in
                  re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        raise ValueError("Il copione non contiene testo")
    wave_parts = []
    all_timed = []
    timeline = 0
    modes = []
    with tempfile.TemporaryDirectory() as scratch:
        temp = Path(scratch)
        for i, paragraph in enumerate(paragraphs):
            print("Voce Edge, paragrafo", i + 1, "/", len(paragraphs), flush=True)
            data, events = await _one_paragraph(paragraph)
            input_mp3 = temp / f"p_{i:02}.mp3"
            input_wav = temp / f"p_{i:02}.wav"
            input_mp3.write_bytes(data)
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(input_mp3), "-ar", str(SAMPLE_RATE),
                "-ac", "1", str(input_wav)
            ], check=True)
            signal, sr = sf.read(str(input_wav), dtype="float32")
            if sr != SAMPLE_RATE:
                raise ValueError("Frequenza inattesa nell'audio Edge")
            if signal.ndim > 1:
                signal = signal.mean(axis=1)
            signal = np.asarray(signal, dtype=np.float32)
            secs = len(signal) / SAMPLE_RATE
            phrases = _sentences(paragraph)
            bounds, mode = _timebounds(phrases, events, secs)
            modes.append(mode)
            all_timed.extend((sentence, (timeline / SAMPLE_RATE) + start,
                              (timeline / SAMPLE_RATE) + finish)
                             for sentence, start, finish in bounds)
            wave_parts.append(signal)
            timeline += len(signal)
            silence_seconds = .44 if i < len(paragraphs) - 1 else .08
            pause = np.zeros(int(SAMPLE_RATE * silence_seconds), dtype=np.float32)
            wave_parts.append(pause)
            timeline += len(pause)
            print("  frasi:", len(phrases), "metadati:", len(events),
                  "allineamento:", mode, "durata:", round(secs, 1), flush=True)
    voice = np.concatenate(wave_parts)
    peak = float(np.max(np.abs(voice))) if voice.size else 0
    if peak > .92:
        voice *= (.92 / peak)
    sf.write(str(outdir / "VOCE.wav"), voice, SAMPLE_RATE)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(outdir / "VOCE.wav"), "-codec:a", "libmp3lame",
        "-b:a", "128k", str(outdir / "VOCE_NATURALE.mp3")
    ], check=True)
    (outdir / "ALLINEAMENTO_VOCE.txt").write_text(
        "Motore: Microsoft Edge TTS / it-IT-DiegoNeural\n"
        "Rate: -5%, pitch: -2Hz\n"
        "Metodo: paragrafi interi con metadati di frase\n"
        "Allineamenti: " + ", ".join(modes) + "\n"
        "NOTA: i diritti commerciali di Edge Read Aloud NON sono chiariti.\n",
        encoding="utf-8"
    )
    return voice, all_timed


def synthesize(text, outdir):
    return asyncio.run(_synthesize(text, Path(outdir)))

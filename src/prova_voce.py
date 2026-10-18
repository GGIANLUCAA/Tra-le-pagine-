"""Due provini della nuova voce italiana, senza modificare il video."""
import asyncio
from pathlib import Path
import edge_tts

TESTO = (
    "Immagina di essere rinchiuso in una stanza. Niente libri. "
    "Nessuna voce amica. E un silenzio che, giorno dopo giorno, ti divora la mente. "
    "Come sopravvivere? Giocando a scacchi. Senza nemmeno una scacchiera. "
    "È il segreto del dottor B., uno dei personaggi più tormentati di Stefan Zweig."
)

async def main():
    out = Path("output"); out.mkdir(exist_ok=True)
    for nome, velocita, tono in (
        ("DIEGO_NATURALE", "-4%", "-2Hz"),
        ("DIEGO_NARRATORE_CALMO", "-11%", "-4Hz"),
    ):
        print(f"Genero {nome} ({velocita}, {tono})", flush=True)
        com = edge_tts.Communicate(TESTO, voice="it-IT-DiegoNeural", rate=velocita, pitch=tono)
        await com.save(str(out / (nome + ".mp3")))
    (out / "LEGGIMI.txt").write_text(
        "Ascolta i due provini. Nessun credito, nessuna modifica del video.\n"
        "DIEGO_NATURALE: velocità -4%, tono -2Hz.\n"
        "DIEGO_NARRATORE_CALMO: velocità -11%, tono -4Hz.\n"
        "Questo accesso tramite Edge TTS NON dispone di diritti commerciali chiaramente confermati: "
        "utile come confronto qualitativo, non come pubblicazione commerciale senza autorizzazione.\n",
        encoding="utf-8",
    )

asyncio.run(main())

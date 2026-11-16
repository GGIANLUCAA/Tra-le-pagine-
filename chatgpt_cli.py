#!/usr/bin/env python3
"""
Piccola CLI per conversare con ChatGPT tramite l'API OpenAI.

Gestisce il contesto della conversazione (memoria dei turni precedenti),
permette di salvare/caricare una chat e di resettarla.

Uso:
    export OPENAI_API_KEY="la-tua-chiave"
    python chatgpt_cli.py
    python chatgpt_cli.py --model gpt-4o-mini --file mia_chat.json

Comandi durante la chat:
    /exit          esci
    /reset         azzera il contesto
    /save          salva la conversazione nel file JSON
    /load          ricarica la conversazione dal file JSON
"""

import argparse
import json
import os
import sys

# SDK ufficiale: pip install openai
from openai import OpenAI


def carica_storico(percorso: str) -> list:
    """Legge lo storico da un file JSON, se esiste."""
    if percorso and os.path.exists(percorso):
        with open(percorso, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salva_storico(percorso: str, messaggi: list) -> None:
    """Scrive lo storico su un file JSON."""
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(messaggi, f, ensure_ascii=False, indent=2)


def chiedi(client: OpenAI, modello: str, messaggi: list) -> str:
    """Invia la conversazione all'API e restituisce la risposta testuale."""
    risposta = client.chat.completions.create(
        model=modello,
        messages=messaggi,
    )
    return risposta.choices[0].message.content


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat con ChatGPT via API OpenAI")
    parser.add_argument("--model", default="gpt-4o-mini", help="modello da usare")
    parser.add_argument(
        "--file",
        default="conversazione.json",
        help="file JSON dove salvare/caricare la conversazione",
    )
    parser.add_argument(
        "--system",
        default="Sei un assistente utile e conciso.",
        help="messaggio di sistema (personalità dell'assistente)",
    )
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("Errore: variabile OPENAI_API_KEY non impostata.", file=sys.stderr)
        print('   export OPENAI_API_KEY="la-tua-chiave"', file=sys.stderr)
        return 1

    client = OpenAI()

    # Storico: inizia con il system prompt, oppure riprende dal file
    messaggi = carica_storico(args.file)
    if not messaggi:
        messaggi = [{"role": "system", "content": args.system}]

    print(f"ChatGPT via API (modello: {args.model}). Comandi: /exit /reset /save /load")

    while True:
        try:
            testo = input("tu> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not testo:
            continue

        if testo == "/exit":
            break
        if testo == "/reset":
            messaggi = [{"role": "system", "content": args.system}]
            print("(contesto azzerato)")
            continue
        if testo == "/save":
            salva_storico(args.file, messaggi)
            print(f"(salvato in {args.file})")
            continue
        if testo == "/load":
            messaggi = carica_storico(args.file)
            print(f"(caricati {len(messaggi)} messaggi)")
            continue

        # Aggiunge il messaggio dell'utente e chiede la risposta
        messaggi.append({"role": "user", "content": testo})
        try:
            risposta = chiedi(client, args.model, messaggi)
        except Exception as e:  # errore API / rete
            print(f"Errore API: {e}", file=sys.stderr)
            messaggi.pop()  # non tenere il turno fallito nello storico
            continue

        messaggi.append({"role": "assistant", "content": risposta})
        print(f"gpt> {risposta}")

    # Salvataggio automatico all'uscita
    salva_storico(args.file, messaggi)
    print(f"(conversazione salvata in {args.file})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Additive rights/publication checklist: does NOT authenticate licenses or publish videos."""
import argparse
import datetime as dt
import json
from pathlib import Path

SOURCES = {"external_licensed", "meta_sound_collection", "meta_native_library", "original"}
FORMATS = {"artvision_cinema", "artvision_critico", "libri", "controluce", "visual_music", "hyperlumen", "other"}
QA_FIELDS = ("music_fit_reviewed", "full_watch_listen", "audio_mix_reviewed",
             "visual_rights_reviewed", "caption_ready", "originality_reviewed")


def check(data):
    blockers, review, notes = [], [], []
    v = data.get("video") or {}
    m = data.get("music") or {}
    d = data.get("distribution") or {}
    q = data.get("qa") or {}
    release = data.get("release") or {}

    def missing(cond, reason):
        if not cond:
            review.append(reason)

    def bad(cond, reason):
        if cond:
            blockers.append(reason)

    missing(data.get("schema_version") == 1, "Schema V20 mancante/non riconosciuto")
    missing(bool(str(v.get("id") or "").strip()) and v.get("id") != "REPLACE_ID",
            "ID video reale mancante")
    missing(v.get("format") in FORMATS, "Formato video non riconosciuto")
    missing(bool(str(v.get("originality_statement") or "").strip()),
            "Manca descrizione del contributo editoriale originale")
    visuals = v.get("visual_rights_evidence")
    missing(isinstance(visuals, list) and bool(visuals) and all(
        isinstance(x, dict) and x.get("name") and x.get("proof_url") for x in visuals),
        "Prove di provenienza e diritti delle immagini incomplete")

    for key, label in (("title", "Titolo musica"), ("artist", "Autore/interprete"),
                       ("source_url", "URL origine audio"),
                       ("recording_proof_url", "Prova della specifica registrazione"),
                       ("license_name", "Nome/condizioni licenza"),
                       ("license_url", "URL condizioni della licenza"),
                       ("license_checked_on", "Data verifica licenza")):
        missing(bool(str(m.get(key) or "").strip()), label + " mancante")

    origin = m.get("origin")
    missing(origin in SOURCES, "Origine musica non riconosciuta")
    date = m.get("license_checked_on")
    if date:
        try:
            day = dt.date.fromisoformat(date)
            if day > dt.date.today():
                review.append("La data di verifica licenza e' nel futuro")
        except (ValueError, TypeError):
            review.append("Data licenza: usare AAAA-MM-GG")
    claim = m.get("rights_holder_claim_status")
    bad(claim == "disputed", "Contenzioso diritti audio irrisolto")
    missing(claim == "cleared", "Verificare/risolvere possibili claim musicali")

    targets = d.get("targets")
    missing(isinstance(targets, list) and bool(targets), "Piattaforme destinazione mancanti")
    targets = [str(t).lower() for t in targets] if isinstance(targets, list) else []
    allowed = m.get("permitted_platforms")
    missing(isinstance(allowed, list) and bool(allowed), "Piattaforme permesse non documentate")
    allowed = [str(t).lower() for t in allowed] if isinstance(allowed, list) else []
    for dest in targets:
        bad(dest not in allowed, "Licenza audio non documentata per: " + dest)

    for flag, label in (("commercial", "uso commerciale"), ("monetized", "monetizzazione"),
                        ("ads", "pubblicita' a pagamento")):
        missing(type(d.get(flag)) is bool, "Definire " + label + " con vero/falso")

    if d.get("commercial") is True:
        bad(m.get("allow_commercial") is False, "Musica vietata per uso commerciale dichiarato")
        missing(m.get("allow_commercial") is True, "Autorizzazione commerciale non verificata")
    if d.get("monetized") is True:
        bad(m.get("monetization_allowed") is False, "Musica non autorizzata alla monetizzazione")
        missing(m.get("monetization_allowed") is True, "Permesso monetizzazione non verificato")
    if d.get("ads") is True:
        bad(m.get("ads_allowed") is False, "Musica non autorizzata alla pubblicita'")
        missing(m.get("ads_allowed") is True, "Permesso ads non verificato")

    if origin == "meta_sound_collection":
        bad(any(t not in ("facebook", "instagram") for t in targets),
            "Sound Collection non e' licenza generale multipiattaforma: serve nuova fonte/licenza distinta")
        notes.append("Verificare termini Meta attuali e id specifico della traccia")
    if origin == "meta_native_library":
        bad(m.get("music_embedded") is True,
            "Audio da libreria nativa Meta non va incorporato nel master multipiattaforma")
        missing(d.get("platform_native_audio_confirmed") is True,
                "Audio nativo finale da selezionare e verificare nell'app social")
        bad(any(t not in ("facebook", "instagram") for t in targets),
            "Traccia nativa Meta non autorizzata per esportazione ad altri social")
        if d.get("commercial") is True or d.get("monetized") is True or d.get("ads") is True:
            missing(bool(str(m.get("permission_reference") or "").strip()),
                    "Musica nativa: serve permesso specifico documentato per uso commerciale/monetizzato/ads")
        notes.append("Disponibilita' nell'editor NON equivale a licenza commerciale")
    if origin == "original":
        missing(bool(str(m.get("permission_reference") or "").strip()),
                "Documentare titolarita' di composizione+registrazione e campioni")

    if m.get("credit_required") is True:
        missing(bool(str(m.get("credit_text") or "").strip()),
                "Testo attribuzione musicale obbligatorio mancante")
    else:
        missing(m.get("credit_required") is False,
                "Indicare se la licenza richiede attribuzione")

    missing(bool(str(m.get("emotional_direction") or "").strip()),
            "Direzione emotiva musicale non compilata")
    missing(bool(str(m.get("cue_notes") or "").strip()),
            "Note sincronizzazione/ingressi musicali non compilate")
    for item in QA_FIELDS:
        missing(q.get(item) is True, "Revisione richiesta: " + item)
    missing(bool(str(release.get("caption_text") or "").strip()),
            "Caption completa con eventuali crediti mancante")
    missing(release.get("user_authorized_publication") is True,
            "Autorizzazione alla pubblicazione ancora assente")

    if blockers:
        status = "BLOCKED"
    elif review:
        status = "REVIEW_REQUIRED"
    else:
        status = "READY_FOR_MANUAL_PUBLICATION"
    return {
        "version": "V20",
        "status": status,
        "publication_performed": False,
        "legal_certification": False,
        "blockers": list(dict.fromkeys(blockers)),
        "review_needed": list(dict.fromkeys(review)),
        "notes": notes,
        "disclaimer": "Verifica documentale autodichiarata: le licenze e il montaggio richiedono verifica reale. Nessuna garanzia contro mute, claim, limitazioni o ban."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    data = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    report = check(data)
    dest = Path(a.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report["status"], "| blocchi:", len(report["blockers"]),
          "| revisioni:", len(report["review_needed"]))
    return 2 if report["status"] == "BLOCKED" else 1 if report["status"] == "REVIEW_REQUIRED" else 0


if __name__ == "__main__":
    raise SystemExit(main())

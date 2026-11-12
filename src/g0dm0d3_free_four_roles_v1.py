#!/usr/bin/env python3
"""Isolated, owner-triggered FREE-ONLY four-role AI Director pilot.

Not G0DM0D3 source code: a bounded editorial adaptation, not a jailbreak.
Never renders, purchases, posts, publishes, or modifies existing masters.
Network POSTs happen only with an explicit action and an API key. Models
must be exact :free IDs with live zero token/request prices.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, InvalidOperation
import html
import json
import os
from pathlib import Path
import sys
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("google/gemma-4-26b-a4b-it:free",
          "google/gemma-4-31b-it:free")
ROLES = ("sceneggiatore", "storico", "regista", "critico")
MODEL_FOR_ROLE = (MODELS[0], MODELS[1], MODELS[0], MODELS[1])
ALLOWED_FORMATS = ("giuliano", "artvision_4x1", "storia_rivive", "documentario")
MAX_CALLS = 4
MAX_OUTPUT_TOKENS = 720
MAX_MODEL_JSON = 2_000_000
SYSTEM = ("Sei parte di uno studio cinematografico storico. Scrivi SOLO proposte "
          "editoriali non approvate. Distingui fatti da ipotesi e dubbi; cita "
          "solo le fonti effettivamente fornite; non inventare diritti, musei, "
          "citazioni, testimonianze, scene già filmate, o recensioni umane. "
          "Niente frasi generiche motivazionali o finali standard. "
          "Ogni scena proposta deve avere una precisa ragione narrativa. "
          "Non hai visto il video, non hai ascoltato l'audio, non hai accesso a "
          "Google, Vidu o al catalogo delle fonti.")
GUIDANCE = {
 "giuliano": "Documentario storico Giuliano: immagini diverse, flusso umano, voce-scena coerenti, niente flash da 1s.",
 "artvision_4x1": "ArtVision: rispettare quattro varianti, voce identica per i due critici, museo/cornice e scala reali da verificare.",
 "storia_rivive": "La Storia Rivive: film originale e ricostruzione distinti, colore autenticamente verificabile, niente foto statiche finte.",
 "documentario": "Documentario: concretezza, ritmo semantico, fonti prima delle affermazioni.",
}


class FreeOnlyError(ValueError):
    pass


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise FreeOnlyError("Redirect not allowed for paid-provider-protection")


def _get_json(url, *, token=None, timeout=23):
    hdr = {"Accept": "application/json", "User-Agent": "TraLePagine-FREE-ONLY-Pilot"}
    if token:
        hdr["Authorization"] = "Bearer " + token
    req = request.Request(url, headers=hdr)
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=timeout) as response:
            raw = response.read(MAX_MODEL_JSON + 1)
        if len(raw) > MAX_MODEL_JSON:
            raise FreeOnlyError("Public model catalogue too large")
        return json.loads(raw)
    except error.HTTPError as exc:
        raise FreeOnlyError("Provider GET HTTP " + str(exc.code)) from None
    except (error.URLError, TimeoutError, OSError, ValueError) as exc:
        if isinstance(exc, FreeOnlyError):
            raise
        raise FreeOnlyError("Provider model catalogue unavailable") from None


def _zero(value):
    if isinstance(value, bool) or value is None:
        return False
    try:
        return Decimal(str(value)) == Decimal("0")
    except (InvalidOperation, ValueError):
        return False


def attest_live_free_models(catalogue, names=MODELS):
    if not isinstance(catalogue, dict) or not isinstance(catalogue.get("data"), list):
        raise FreeOnlyError("Live model catalogue is malformed")
    index = {x.get("id"): x for x in catalogue["data"] if isinstance(x, dict)}
    for model in names:
        if not model.endswith(":free") or model not in MODELS:
            raise FreeOnlyError("Only the two explicitly pinned free IDs are allowed")
        entry = index.get(model)
        if not isinstance(entry, dict):
            raise FreeOnlyError("Pinned free model not in current official OpenRouter list")
        prices = entry.get("pricing")
        if not isinstance(prices, dict):
            raise FreeOnlyError("No live price evidence")
        for field in ("prompt", "completion", "request"):
            # Some providers omit the request surcharge, which is zero by default.
            if field in prices and not _zero(prices[field]):
                raise FreeOnlyError("Nonzero live " + field + " price for " + model)
        if not _zero(prices.get("prompt")) or not _zero(prices.get("completion")):
            raise FreeOnlyError("Price unknown or not free for " + model)
    return {"checked_models": list(names), "max_prompts": MAX_CALLS,
            "pricing_source": "live_openrouter_api_models_read_only",
            "price_checked": True,
            "billing_disabled_on_account_verified": False}


def _request_free(model, prompt, key, *, transport=None):
    if model not in MODELS or not model.endswith(":free"):
        raise FreeOnlyError("Only approved pinned free models")
    if not 40 < len(prompt) <= 6500:
        raise FreeOnlyError("Prompt length is outside safe pilot range")
    body = {"model": model,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": prompt}],
            "temperature": 0.45, "max_tokens": MAX_OUTPUT_TOKENS,
            "stream": False,
            "usage": {"include": True},
            "provider": {"allow_fallbacks": False,
                         "max_price": {"prompt": 0, "completion": 0}}}
    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        method="POST",
        data=json.dumps(body,ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key,
                 "X-Title": "Tra-le-Pagine FREE-only editorial experiment"})
    if transport is not None:
        response = transport(req)
    else:
        try:
            with request.build_opener(NoRedirect()).open(req, timeout=65) as resp:
                raw = resp.read(150_001)
            if len(raw) > 150_000:
                raise FreeOnlyError("Provider response oversized")
            response = json.loads(raw)
        except error.HTTPError as exc:
            raise FreeOnlyError("Free model request returned HTTP " + str(exc.code)) from None
        except (error.URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, FreeOnlyError):
                raise
            raise FreeOnlyError("Free model request failed; NO RETRY") from None
    if not isinstance(response, dict):
        raise FreeOnlyError("Response not JSON object")
    if response.get("model") != model:
        raise FreeOnlyError("Model identity mismatch - do not trust result")
    try:
        content = response["choices"][0]["message"]["content"]
    except (IndexError, KeyError, TypeError):
        raise FreeOnlyError("No free model text returned") from None
    if not isinstance(content, str) or not 40 <= len(content) <= 25000:
        raise FreeOnlyError("Free model response empty or oversized")
    cost = (response.get("usage") or {}).get("cost")
    if cost is not None and not _zero(cost):
        raise FreeOnlyError("Reported cost nonzero; pilot stopped")
    return {"text": content[:13000], "model": model,
            "reported_cost_usd": cost if cost is not None else "not_reported",
            "human_approved": False}


def _prompt(role, fmt, topic, existing):
    base=(GUIDANCE[fmt]+"\nSOGGETTO PUBBLICO: "+topic+
          "\nNon affermare che esistono asset non presenti. "
          "Suggerisci solo la regia, NON un video già realizzato.\n")
    if role == "sceneggiatore":
        return base+("RUOLO SCENEGGIATORE: proponi un gancio concreto, sei beat diversi, "
                     "frasi narrabili, dettagli specifici, finale non standard. "
                     "Segna le informazioni storiche da verificare.")
    if role == "storico":
        return base+("RUOLO STORICO: controlla criticamente la plausibilità delle idee "
                     "di sceneggiatura di seguito. Evidenzia errori, dubbi, fonti primarie "
                     "da cercare; NON inventare citazioni. TESTO IN VERIFICA:\n"+existing[0][:2200])
    if role == "regista":
        return base+("RUOLO REGISTA: ripensa tempi, immagini e movimento per i sei beat "
                     "seguenti; per ciascuno visuale, voce associata, durata orientativa. "
                     "Nessun flash, niente immagine che contraddice parole. "
                     "RISPONDI ALLA CRITICA STORICA; scegli soluzioni riproducibili "
                     "con media reali. SCRITTURA:\n"+existing[0][:1600]+
                     "\nVERIFICA STORICA:\n"+existing[1][:1600])
    if role == "critico":
        return base+("RUOLO CRITICO INDIPENDENTE: metti alla prova le tre bozze, "
                     "non fare complimenti. Individua almeno cinque difetti concreti, "
                     "false certezze, immagini assenti, ritmi piatti e incoerenze "
                     "fra racconto e immagini. Indica una sola modifica prioritaria "
                     "per il pilot. NON certificare il video.\n"+
                     "\n".join(f"{r}: {s[:1200]}" for r,s in zip(ROLES[:3],existing)))
    raise FreeOnlyError("Unknown role")


def experiment(fmt, topic, *, key, execute=False, catalogue=None, ask=None):
    if fmt not in ALLOWED_FORMATS or not isinstance(topic,str) or not 8 <= len(topic) <= 190:
        raise FreeOnlyError("Invalid public editorial subject")
    base={"schema":"g0dm0d3-free-four-role-pilot-v1",
          "format":fmt,"subject":topic,"models":list(MODELS),
          "roles":list(ROLES),"max_calls":MAX_CALLS,"model_calls":0,
          "output_kind":"editorial_draft_no_video",
          "publication_authorized":False,"video_rendered":False,
          "human_artistic_approval":False,"commercial_license_for_all_sources_verified":False,
          "billing_verified_zero_at_account_level":False,
          "no_paid_models":True, "no_retries":True}
    if not execute:
        base.update({"status":"dry_run_no_inference",
                     "prompts":[_prompt(role,fmt,topic,[]) if role=="sceneggiatore"
                                else "Depends on previous draft" for role in ROLES]})
        return base
    if not key or len(key) > 800 or any(c.isspace() for c in key):
        base["status"]="blocked_missing_openrouter_key"
        return base
    try:
        pricing=attest_live_free_models(
            catalogue if catalogue is not None
            else _get_json("https://openrouter.ai/api/v1/models"))
        base["price_evidence"]=pricing
    except FreeOnlyError as exc:
        base["status"]="blocked_live_zero_price_unverified"
        base["reason"]=str(exc)
        return base
    responses=[]
    for role,model in zip(ROLES,MODEL_FOR_ROLE):
        text = _prompt(role, fmt, topic, [s["text"] for s in responses])
        base["model_calls"]+=1
        try:
            out=(ask or _request_free)(model,text,key)
            responses.append({"role":role,**out})
        except Exception as exc:
            base["status"]="incomplete_no_retry"
            base["failure_reason"]=str(exc) if isinstance(exc,FreeOnlyError) else "Model unavailable"
            base["responses"]=responses
            return base
    base.update({"responses":responses,"status":"four_roles_returned_unapproved"})
    return base


def save(report, target):
    target=Path(target);target.mkdir(parents=True,exist_ok=True)
    (target/"REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                                      encoding="utf-8")
    rows=[]
    for x in report.get("responses",[]):
        rows.append("<section><h2>"+html.escape(x["role"])+"</h2><p>Modello: "+
                    html.escape(x["model"])+"</p><pre style='white-space:pre-wrap'>"+
                    html.escape(x["text"])+"</pre></section>")
    (target/"ANDROID_REPORT.html").write_text(
        '<!doctype html><html lang="it"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Quattro AI gratuite - Pilot</title><body style="font:16px system-ui;'
        'max-width:750px;margin:auto;padding:18px">'
        '<h1>Quattro ruoli · laboratorio Giuliano</h1><p>Stato: '+
        html.escape(report["status"])+
        ' · bozza NON approvata. Nessuna verifica artistica del film o dei diritti. '
        'Costi reali del singolo account NON certificati.</p>'+
        "".join(rows)+"</body></html>",encoding="utf-8")
    print("G0DM0D3_FREE_PILOT",report["status"],"attempts",report["model_calls"])


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--format",choices=ALLOWED_FORMATS,default="giuliano")
    p.add_argument("--topic",default="Anticitera: migliorare varietà dei meccanismi e corrispondenza voce-scene")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--execute",action="store_true")
    args=p.parse_args(argv)
    if args.execute and os.environ.get("G0DM0D3_FREE_PILOT_ONE_SHOT")!="1":
        raise FreeOnlyError("No explicit free-only single-run authorization")
    report=experiment(args.format,args.topic,key=os.environ.get("OPENROUTER_API_KEY",""),
                      execute=args.execute)
    save(report,args.out)
    return 0 if report["status"] in ("dry_run_no_inference","four_roles_returned_unapproved",
                                     "blocked_missing_openrouter_key") else 2


if __name__=="__main__":
    try:
        sys.exit(main())
    except FreeOnlyError as exc:
        print("G0DM0D3_FAIL_CLOSED",exc)
        sys.exit(2)

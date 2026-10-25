#!/usr/bin/env python3
"""Acquisizione immagini gratuita V1: AI Horde su richiesta, senza API a pagamento.

Non modifica episodi storici e non pubblica mai immagini o video. La scelta del
modello e la revisione manuale delle licenze restano obbligatorie.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

API = "https://aihorde.net/api/v2"
CLIENT = "TraLePagineImagePipeline:1.0:https://github.com/GGIANLUCAA/Tra-le-pagine-"
MAX_IMAGES = 3  # Test iniziale prudente; non promettere grandi batch prima del benchmark
MAX_SIZE = 12_000_000
ALLOWED_CDN_SUFFIXES = (
    "aihorde.net", "stablehorde.net", "haidra.net",
    "r2.dev", "cloudflarestorage.com",
)


class PipelineError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise PipelineError("Redirect automatici non permessi nel download di asset")


def request_json(method: str, url: str, *, payload: dict | None = None, key: str = "") -> dict | list:
    if not url.startswith(API + "/"):
        raise PipelineError("Endpoint non autorizzato")
    headers = {"Accept": "application/json", "Client-Agent": CLIENT}
    if key:
        headers["apikey"] = key
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            if int(response.headers.get("Content-Length", 0)) > 1_000_000:
                raise PipelineError("Risposta API troppo grande")
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise PipelineError("Risposta API troppo grande")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        # Non scrivere mai corpi d'errore che potrebbero contenere informazioni sensibili.
        if exc.code == 429:
            raise PipelineError("AI Horde: limite 429. Fermato senza retry automatici.") from exc
        raise PipelineError(f"AI Horde: errore HTTP {exc.code}. Nessun retry.") from exc


def validated_cdn(url: str) -> bool:
    try:
        p = urllib.parse.urlsplit(url)
        host = (p.hostname or "").lower().rstrip(".")
        if p.scheme != "https" or p.username or p.password or p.port:
            return False
        return bool(host and all(x not in host for x in ("\n", "\r")) and any(
            host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_CDN_SUFFIXES
        ))
    except (ValueError, TypeError):
        return False


def retrieve_image(url: str, out: Path) -> dict:
    if not validated_cdn(url):
        raise PipelineError("Host dell'immagine non nella lista consentita: asset non scaricato")
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": CLIENT})
    with opener.open(req, timeout=35) as response:
        if response.status != 200:
            raise PipelineError("Download non riuscito")
        if int(response.headers.get("Content-Length", 0)) > MAX_SIZE:
            raise PipelineError("Immagine oltre il limite consentito")
        raw = response.read(MAX_SIZE + 1)
    if not 8_000 <= len(raw) <= MAX_SIZE:
        raise PipelineError("Immagine mancante, troppo piccola o troppo grande")
    from PIL import Image, ImageOps
    try:
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
            img = ImageOps.exif_transpose(img).convert("RGB")
            if img.width < 384 or img.height < 384 or img.width * img.height > 18_000_000:
                raise PipelineError("Dimensioni immagine non ammesse")
            out.parent.mkdir(parents=True, exist_ok=True)
            img.save(out, format="JPEG", quality=93, optimize=True)
            dims = [img.width, img.height]
    except (OSError, ValueError) as exc:
        raise PipelineError("Il file ricevuto non è un'immagine utilizzabile") from exc
    return {"file": out.name, "width": dims[0], "height": dims[1],
            "sha256_source": hashlib.sha256(raw).hexdigest(),
            "sha256_output": hashlib.sha256(out.read_bytes()).hexdigest()}


def load_brief(path: Path, maximum: int) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PipelineError("Brief JSON non valido")
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not 1 <= len(scenes) <= maximum:
        raise PipelineError(f"Il test richiede da 1 a {maximum} scene, senza batch illimitati")
    if not 8 <= len(str(data.get("style_bible", "")).strip()) <= 1500:
        raise PipelineError("Manca lo stile coerente")
    if not 8 <= len(str(data.get("character_bible", "")).strip()) <= 1500:
        raise PipelineError("Manca il profilo del protagonista")
    ids = set()
    for item in scenes:
        if not isinstance(item, dict):
            raise PipelineError("Scena non valida")
        ident = item.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9_-]{1,35}", ident) or ident in ids:
            raise PipelineError("ID scene non valido o ripetuto")
        ids.add(ident)
        for field in ("narration_anchor", "description"):
            if not isinstance(item.get(field), str) or not 8 <= len(item[field]) <= 1400:
                raise PipelineError(f"Scena {ident}: manca {field}")
    return data


def prompt_for(brief: dict, scene: dict) -> str:
    # Il modello riceve una singola scena coerente con la narrazione. Niente collage.
    return (f"Original single-scene vertical storybook illustration. "
            f"Style guide: {brief['style_bible']}. "
            f"Characters: {brief['character_bible']}. "
            f"Exact visible action: {scene['description']}. "
            "Only the characters and objects required for this exact action. "
            "Cinematic framing; important faces fully visible; correct hands; "
            "no collage, no cut-off faces, no lettering, no logos, no watermark."
            "###text, captions, watermark, panel border, storyboard grid, duplicate bodies")


def make_request(brief: dict, scene: dict, model: str) -> dict:
    return {
        "prompt": prompt_for(brief, scene),
        "params": {"width": 512, "height": 768, "steps": 24, "n": 1,
                   "cfg_scale": 7.0},
        "models": [model],
        "nsfw": False,
        "censor_nsfw": True,
        "shared": False,
        "r2": True,
    }


def wait_for_job(job_id: str, key: str, deadline: float, interval: int = 12) -> dict:
    while time.monotonic() < deadline:
        check = request_json("GET", f"{API}/generate/check/{job_id}", key=key)
        if not isinstance(check, dict):
            raise PipelineError("Risposta di controllo inattesa")
        if check.get("faulted") or check.get("is_possible") is False:
            raise PipelineError("Coda non disponibile o job fallito")
        if check.get("done"):
            detail = request_json("GET", f"{API}/generate/status/{job_id}", key=key)
            if not isinstance(detail, dict) or not detail.get("generations"):
                raise PipelineError("Job completato senza immagini")
            return detail
        time.sleep(interval)
    raise PipelineError("Timeout di attesa: generazione non confermata")


def models(key: str = "") -> list:
    result = request_json("GET", f"{API}/status/models?type=image", key=key)
    if not isinstance(result, list):
        raise PipelineError("Catalogo modelli non disponibile")
    return [
        {"name": x.get("name"), "workers": x.get("count", 0),
         "queued": x.get("queued", 0)}
        for x in result if isinstance(x, dict) and x.get("name")
    ]


def execute(brief: dict, destination: Path, *, mode: str, model: str = "",
            key: str = "", wait_seconds: int = 240) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    report = {"version": "images-v1", "mode": mode, "provider": "ai-horde",
              "title": brief.get("title", ""), "images": [], "completed": False,
              "license_review_required": True, "automatic_video_render": False,
              "publication": False, "external_cost_authorized_eur": 0}
    if mode not in ("plan", "generate"):
        raise PipelineError("Modalità non valida")
    if mode == "generate" and (not key or not model.strip()):
        raise PipelineError("Per generare servono AIHORDE_API_KEY e un modello esplicito")
    for scene in brief["scenes"]:
        item = {"id": scene["id"], "narration_anchor": scene["narration_anchor"],
                "description": scene["description"], "provider": "ai-horde",
                "requested_model": model or "da selezionare", "status": "planned"}
        report["images"].append(item)
        if mode == "plan":
            continue
        payload = make_request(brief, scene, model)
        job_id = ""
        try:
            started = request_json("POST", f"{API}/generate/async", payload=payload, key=key)
            job_id = str(started.get("id", ""))
            uuid.UUID(job_id)
            status = wait_for_job(job_id, key, time.monotonic() + wait_seconds)
            generated = status["generations"][0]
            if not isinstance(generated, dict) or not generated.get("img"):
                raise PipelineError("Risultato privo di immagine")
            image_meta = retrieve_image(generated["img"], destination / f"scena_{scene['id']}.jpg")
            item.update(image_meta)
            item.update({"status": "needs_visual_review", "model_actual": generated.get("model"),
                         "seed": generated.get("seed"), "worker": generated.get("worker_name"),
                         "request_id": job_id,
                         "copyright_note": "Licenza del checkpoint e idoneita commerciale da verificare."})
        except (PipelineError, urllib.error.URLError, ValueError, KeyError) as exc:
            item.update({"status": "failed", "reason": str(exc)[:240]})
        finally:
            if job_id and item["status"] == "failed":
                try:
                    request_json("DELETE", f"{API}/generate/status/{job_id}", key=key)
                except Exception:
                    pass
            # Salvataggio parziale anche quando una scena fallisce.
            (destination / "MANIFEST_IMAGES_V1.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["completed"] = (mode == "plan" or all(
        x["status"] == "needs_visual_review" for x in report["images"]))
    (destination / "MANIFEST_IMAGES_V1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["plan", "generate", "models"], default="plan")
    parser.add_argument("--brief", default="config/image_pipeline_v1_demo.json")
    parser.add_argument("--out", default="output/image_pipeline_v1")
    parser.add_argument("--model", default="")
    parser.add_argument("--max-wait", type=int, default=240)
    args = parser.parse_args()
    if args.mode == "models":
        catalog = models()
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return
    if not 30 <= args.max_wait <= 900:
        parser.error("--max-wait tra 30 e 900 secondi")
    brief = load_brief(Path(args.brief), MAX_IMAGES)
    report = execute(brief, Path(args.out), mode=args.mode, model=args.model,
                     key=os.environ.get("AIHORDE_API_KEY", ""), wait_seconds=args.max_wait)
    print(json.dumps({"mode": args.mode, "completed": report["completed"],
                      "scenes": len(report["images"]),
                      "statuses": [x["status"] for x in report["images"]]},
                     ensure_ascii=False))
    if args.mode == "generate" and not report["completed"]:
        raise SystemExit("Almeno una scena non riuscita. Vedere MANIFEST_IMAGES_V1.json")


if __name__ == "__main__":
    main()

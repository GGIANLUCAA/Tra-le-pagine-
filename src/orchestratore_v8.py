#!/usr/bin/env python3
"""Tra le Pagine V8 — orchestratore additivo per scene esistenti e media locali.
NON usa rete/API, NON modifica V3–V7, NON pubblica o aggira protezioni.
Planning: solo stdlib. Prepare: Pillow per validare/converter immagini.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from studio_ibrido_v6 import build_plan, read_json

FORMATS = ("libri", "cronaca", "documentario", "fiabe", "social")
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TOKEN = re.compile(r"[a-zà-ÿ0-9]{3,}", re.IGNORECASE)


def words(value):
    return set(TOKEN.findall(str(value).lower()))


def similarity(a, b):
    aa, bb = words(a), words(b)
    return round(len(aa & bb) / len(aa | bb), 3) if aa and bb else 0.0


def safe_user_path(value, root):
    """Accept only existing paths within current GitHub checkout; no URLs, traversal or symlinks out."""
    root = Path(root).resolve()
    if not isinstance(value, str) or not value or "://" in value:
        raise ValueError("Percorso locale non valido.")
    candidate = (root / value).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise ValueError("Asset esterno o mancante: " + str(value))
    if candidate.stat().st_size > 12_000_000:
        raise ValueError("Asset maggiore di 12MB.")
    if candidate.suffix.lower() not in EXTENSIONS:
        raise ValueError("Solo immagini .jpg, .jpeg, .png, .webp.")
    return candidate


@dataclass
class Candidate:
    provider: str
    asset: int
    location: str
    description: str
    approved: bool
    private_only: bool
    source: str
    license: str
    member: str = ""


class EpisodePlugin:
    name = "episode"
    def __init__(self, root):
        self.root = Path(root)

    def find(self, episode, scene):
        ep = self.root / "episodes" / episode
        stem = f"scena_{scene['asset']:02d}"
        z = ep / "scene_premium.zip"
        # Existing renderer gives ZIP precedence if present.
        if z.exists():
            with zipfile.ZipFile(z) as archive:
                for entry in archive.infolist():
                    if Path(entry.filename).stem.casefold() == stem and Path(entry.filename).suffix.lower() in EXTENSIONS:
                        return Candidate(self.name, scene["asset"], str(z), scene["description"],
                                         True, True, "episodio_esistente", "da_verificare",
                                         member=entry.filename)
            return None
        for extension in (".jpg", ".jpeg", ".png", ".webp"):
            p = ep / "images" / (stem + extension)
            if p.exists() and p.is_file():
                return Candidate(self.name,scene["asset"],str(p),scene["description"],
                                 True,True,"episodio_esistente","da_verificare")
        return None


class ManualPlugin:
    name = "manifest"
    def __init__(self, root, manifest):
        self.root = Path(root)
        if manifest is None:
            self.mapping = {}
        else:
            data = read_json(safe_user_path_json(manifest, self.root))
            if not isinstance(data, dict):
                raise ValueError("Manifest V8 deve essere un oggetto JSON.")
            self.mapping = data

    def find(self, episode, scene):
        record = self.mapping.get(str(scene["asset"]))
        if record is None:
            return None
        if not isinstance(record, dict) or "path" not in record:
            raise ValueError("Manifest asset senza path.")
        p = safe_user_path(record["path"],self.root)
        approved = record.get("approved_for_private_project") is True
        private_only = record.get("private_only") is not False
        return Candidate(self.name,scene["asset"],str(p),scene["description"],
                         approved,private_only,str(record.get("source","materiale_fornito_utente")),
                         str(record.get("license","non_verificata")))


def safe_user_path_json(value, root):
    root = Path(root).resolve()
    p = (root / str(value)).resolve()
    if not p.is_relative_to(root) or not p.is_file() or p.suffix.lower() != ".json":
        raise ValueError("Manifest JSON fuori dal progetto o mancante.")
    if p.stat().st_size > 250_000:
        raise ValueError("Manifest troppo grande.")
    return p


def suggestions_from_history(root, episode, scene, limit=3):
    """Only suggest reuse, never silently copy images from unrelated stories."""
    entries = []
    source = EpisodePlugin(root)
    for other in sorted((Path(root) / "episodes").iterdir()):
        if not other.is_dir() or other.name == episode:
            continue
        cues_file = other / "scene_cues.json"
        if not cues_file.is_file():
            continue
        try:
            cues = read_json(cues_file)
        except (OSError,ValueError,TypeError):
            continue
        if not isinstance(cues,list):
            continue
        for candidate_cue in cues:
            if not isinstance(candidate_cue,dict):
                continue
            if not isinstance(candidate_cue.get("asset"),int):
                continue
            desc = str(candidate_cue.get("description",""))
            score = similarity(scene["description"],desc)
            if score < .42:
                continue
            available = source.find(other.name,{"asset":candidate_cue["asset"],"description":desc})
            if available:
                entries.append({
                    "episode": other.name, "asset": candidate_cue["asset"],
                    "score": score, "description":desc,
                    "status":"solo_suggerimento_non_approvato",
                })
    return sorted(entries,key=lambda x:-x["score"])[:limit]


def plan(root, episode, kind, manifest=None):
    root=Path(root).resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,70}",episode):
        raise ValueError("Slug episodio non valido.")
    registry=read_json(root/"config"/"studio_ibrido_tools.json")
    v6=build_plan(root/"episodes"/episode,kind,"zero",registry)
    base=EpisodePlugin(root)
    supplied=ManualPlugin(root,manifest)
    scenes=[]
    reused=0
    for cue in v6["scenes"]:
        # Existing episode assets always win; manual manifest only fills gaps.
        pick=base.find(episode,cue)
        if pick is None:
            pick=supplied.find(episode,cue)
        if pick and pick.provider=="episode":
            reused+=1
        scenes.append({
            "cue":cue["cue"],"asset":cue["asset"],"start_sentence":cue["start_sentence"],
            "description":cue["description"],
            "provider":pick.provider if pick else "missing",
            "location":pick.location if pick else "",
            "member":pick.member if pick else "",
            "source":pick.source if pick else "",
            "license":pick.license if pick else "",
            "approved_for_private_project":pick.approved if pick else False,
            "private_only":pick.private_only if pick else True,
            "suggestions": [] if pick else suggestions_from_history(root,episode,cue),
            "scene_will_render": bool(pick and pick.approved),
        })
    distinct={}
    for s in scenes:
        distinct.setdefault(s["asset"],s)
        # A repeated asset must have the same single selected source.
    missing=[v["asset"] for v in distinct.values() if not v["scene_will_render"]]
    return {
        "version":"V8","episode":episode,"format":kind,
        "gate1":"non_approvato","gate2":"non_approvato",
        "uses_google_gemini":True,"renderer_v5_unchanged":True,
        "private_preview_only":True,"publish_enabled":False,
        "will_call_api":False,"will_download":False,
        "complete":not missing and v6["puo_passare_a_revisione_editoriale"],
        "missing_assets":missing,
        "source_check":v6["stato_fonti"],
        "existing_assets_reused":reused,
        "unique_assets":len(distinct),
        "scenes":scenes,
        "note":"V8 usa asset esistenti e media locali; suggerimenti da altre storie non entrano automaticamente."
    }


def scene_html(report):
    blocks=[]
    for scene in report["scenes"]:
        ready=scene["scene_will_render"]
        suggestions="".join(
            "<li>"+html.escape(x["episode"])+" — "+html.escape(x["description"])+
            " (somiglianza "+str(int(x["score"]*100))+"%, solo proposta)</li>"
            for x in scene["suggestions"])
        blocks.append(
            "<article><small>SCENA "+str(scene["cue"]+1)+
            " · Asset "+str(scene["asset"])+"</small><h2>"+
            html.escape(scene["description"])+"</h2><p>"+
            ("Pronta" if ready else "Manca immagine autorizzata")+
            " · "+html.escape(scene["provider"])+
            "</p>"+("<ul>"+suggestions+"</ul>" if suggestions else "")+"</article>")
    return ('<!doctype html><html lang="it"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Tra le Pagine V8</title><style>body{font:16px system-ui;'
            'background:#102e3a;color:#f7f1e8;padding:20px}main{max-width:1000px;'
            'margin:auto}section{display:grid;grid-template-columns:repeat(auto-fit,'
            'minmax(260px,1fr));gap:13px}article{background:#204655;padding:16px;'
            'border-radius:13px}small{color:#dbc08f}</style><main><h1>'+
            html.escape(report["episode"])+'</h1><p>Materiale pronto: '+
            str(report["unique_assets"]-len(report["missing_assets"]))+
            '/'+str(report["unique_assets"])+
            ' · Nessuna voce o immagine generata. Gate 1 necessario prima della produzione.</p><section>'+
            "".join(blocks)+"</section></main></html>")


def read_candidate_bytes(scene):
    p=Path(scene["location"])
    if scene["provider"]=="episode" and scene["member"]:
        with zipfile.ZipFile(p) as z:
            name=scene["member"]
            entry=z.getinfo(name)
            if entry.file_size>12_000_000:
                raise ValueError("Immagine ZIP oltre 12 MB.")
            return z.read(name)
    if p.stat().st_size>12_000_000:
        raise ValueError("File troppo grande.")
    return p.read_bytes()


def prepare(root, report, out, gate1=False):
    if gate1 is not True:
        raise ValueError("Gate 1 mancante: autorizza copione e storyboard prima della preparazione.")
    if not report["complete"]:
        raise ValueError("Non tutti gli asset sono pronti; verifica anche le fonti editoriali.")
    from PIL import Image, ImageOps
    from io import BytesIO
    root=Path(root).resolve()
    out=Path(out).resolve()
    # Never stage into historical episode folder.
    if out.is_relative_to((root/"episodes").resolve()):
        raise ValueError("È vietato scrivere negli episodi esistenti.")
    ep=root/"episodes"/report["episode"]
    staged=out/"stage"/"episodes"/report["episode"]
    if staged.exists():
        raise ValueError("Lo staging esiste: usa una cartella output nuova.")
    staged.mkdir(parents=True)
    for name in ("testo.txt","metadata.json","scene_cues.json","DESCRIZIONE_SOCIAL.txt",
                 "effetti_v4.json"):
        source=ep/name
        if source.is_file():
            shutil.copy2(source,staged/name)
    (staged/"images").mkdir()
    unique={}
    hashes={}
    for scene in report["scenes"]:
        unique.setdefault(scene["asset"],scene)
    for asset, scene in unique.items():
        raw=read_candidate_bytes(scene)
        fingerprint=hashlib.sha256(raw).hexdigest()
        target=staged/"images"/f"scena_{asset:02d}.jpg"
        if fingerprint in hashes:
            shutil.copy2(hashes[fingerprint],target)
            continue
        with Image.open(BytesIO(raw)) as original:
            if original.width<250 or original.height<250:
                raise ValueError("Risoluzione immagine troppo bassa.")
            im=ImageOps.exif_transpose(original).convert("RGB")
            im.save(target,format="JPEG",quality=92,optimize=True)
        hashes[fingerprint]=target
    evidence={
        "version":"V8","episode":report["episode"],
        "gate1":"approvato_manualmente","gate2":"in_attesa",
        "images_prepared":len(unique),"sha256_inputs":list(hashes),
        "voice_engine":"Google Gemini TTS preesistente",
        "publish_enabled":False,"material_private_only":True,
        "notes":"Pacchetto locale compatibile con l'episodio V5. Non è un MP4. Non approvato per pubblicazione."
    }
    (out/"RAPPORTO_PREPARAZIONE_V8.json").write_text(
        json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return staged


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",required=True)
    p.add_argument("--format",choices=FORMATS,default="libri")
    p.add_argument("--mode",choices=("plan","prepare"),default="plan")
    p.add_argument("--manifest",default="")
    p.add_argument("--gate1-approved",action="store_true")
    p.add_argument("--out",default="output/orchestratore_v8")
    args=p.parse_args()
    root=Path.cwd()
    out=Path(args.out)
    report=plan(root,args.episode,args.format,args.manifest or None)
    out.mkdir(parents=True,exist_ok=True)
    (out/"PIANO_V8.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"REVISIONE_GATE1_V8.html").write_text(scene_html(report),encoding="utf-8")
    print("V8:",len(report["scenes"]),"scene,",len(report["missing_assets"]),
          "asset mancanti; chiamate API: 0")
    if args.mode=="prepare":
        print("STAGING:",prepare(root,report,out,args.gate1_approved))
    else:
        print("PLAN: nessun asset copiato. Se approvi, scegli prepare.")
    print("Voce Google e moduli V3-V7 invariati. Nessuna pubblicazione.")


if __name__=="__main__":
    main()

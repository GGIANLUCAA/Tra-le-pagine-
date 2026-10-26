#!/usr/bin/env python3
"""Video Boards V34: zero-image-API visual dossiers from existing PROJECT_V13.json.

Generates two branded boards and a contact sheet with Pillow. Does NOT call
image/TTS APIs, update project files, invent licenses, or approve a video.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

NAVY = "#10283A"
NAVY2 = "#18394B"
PAPER = "#F5F1E9"
IVORY = "#FFFDF7"
GOLD = "#C79C62"
INK = "#172938"
MUTED = "#60717B"
BORDER = "#DCD6CB"
W = 1600

def font(size=32, bold=False, serif=False):
    stem = "DejaVuSerif" if serif else "DejaVuSans"
    style = "-Bold" if bold else ""
    path = f"/usr/share/fonts/truetype/dejavu/{stem}{style}.ttf"
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

def normalize(value, fallback="Non disponibile"):
    value = str(value).strip() if value is not None else ""
    return value if value else fallback

def lines_for(draw, text, f, width):
    out = []
    for paragraph in str(text).split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = (line + " " + word).strip()
            if line and draw.textbbox((0, 0), candidate, font=f)[2] > width:
                out.append(line)
                line = word
            else:
                line = candidate
        out.append(line)
    return out

def wrapped(draw, text, xy, width, f=None, color=INK, max_lines=4, step=None):
    f = f or font(29)
    step = step or f.size + 14
    result = lines_for(draw, normalize(text), f, width)
    if len(result) > max_lines:
        result = result[:max_lines]
        tail = result[-1]
        while tail and draw.textbbox((0, 0), tail + "…", font=f)[2] > width:
            tail = tail[:-1]
        result[-1] = tail.rstrip() + "…"
    x, y = xy
    for line in result:
        draw.text((x, y), line, fill=color, font=f)
        y += step
    return y

def box(d, xy, color=IVORY, outline=BORDER, radius=22):
    d.rounded_rectangle(xy, radius=radius, fill=color, outline=outline, width=2)

def photo(path, size, crop=True):
    if path is None:
        return None
    try:
        with Image.open(path) as src:
            im = src.convert("RGB")
            return (ImageOps.fit(im, size, method=Image.Resampling.LANCZOS,
                    centering=(.5, .42)) if crop else
                    ImageOps.contain(im, size, method=Image.Resampling.LANCZOS))
    except (OSError, ValueError):
        return None

def place(im, d, path, xy, label, crop=True):
    x, y, w, h = xy
    d.rounded_rectangle((x, y, x+w, y+h), radius=15, fill="#DDD9D0")
    shot = photo(path, (w, h), crop)
    if shot:
        im.paste(shot, (x, y))
    else:
        wrapped(d, label, (x+22, y+h//2-32), w-44, font(24, bold=True),
                MUTED, max_lines=2)

def banner(im, d, heading, subheading):
    d.rectangle((0, 0, W, 238), fill=NAVY)
    d.text((80, 45), "TRA LE PAGINE   ·   STUDIO IBRIDO", font=font(27, bold=True), fill=GOLD)
    d.text((80, 94), heading, font=font(65, serif=True, bold=True), fill=IVORY)
    wrapped(d, subheading, (83, 188), 1400, font(22), "#CAD9DA", 1)

def asset_path(project_path, name):
    if not isinstance(name, str) or not name:
        return None
    base = project_path.parent.resolve()
    file = (base / name).resolve()
    if not file.is_relative_to(base) or not file.is_file() or file.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
        return None
    return file

def prepare(project_path):
    obj = json.loads(project_path.read_text(encoding="utf-8"))
    if obj.get("schema") != "video-project-v13":
        raise ValueError(f"Non è una scheda PROJECT_V13 valida: {project_path}")
    assets = {a.get("id"): a for a in obj.get("assets", []) if isinstance(a, dict) and a.get("id")}
    scenes = []
    for i, scene in enumerate(obj.get("scenes", [])):
        if not isinstance(scene, dict):
            continue
        a = assets.get(scene.get("asset_id"), {})
        scenes.append({"number": i+1,
                       "text": normalize(scene.get("description"), "Scena non descritta"),
                       "reason": normalize(scene.get("reason"), "Funzione da compilare"),
                       "asset": a,
                       "path": asset_path(project_path, a.get("file"))})
    plan = obj.get("editorial_plan") or {}
    decisions = (plan.get("media_sourcing") or {}).get("decisions") or []
    by_id = {v["asset_id"]: v for v in decisions if isinstance(v, dict) and v.get("asset_id")}
    visuals = []
    for aid, a in assets.items():
        if a.get("role") == "visual":
            visuals.append({"id": aid, "data": a, "decision": by_id.get(aid, {}),
                            "path": asset_path(project_path, a.get("file"))})
    cover = asset_path(project_path, obj.get("cover", "") if isinstance(obj.get("cover"), str) else "")
    if not cover:
        cover = asset_path(project_path, "COPERTINA.jpg")
    if not cover:
        cover = next((v["path"] for v in visuals if v["path"]), None)
    return obj, plan, scenes, visuals, cover

def make_concept(project_path, out, obj, plan, scenes, visuals, cover):
    im = Image.new("RGB", (W, 2400), PAPER)
    d = ImageDraw.Draw(im)
    banner(im, d, "VIDEO CONCEPT BOARD", normalize(obj.get("format"), "format sconosciuto") + " | Progetto V13 | senza chiamate API")
    box(d, (60, 270, 730, 1425))
    place(im, d, cover, (85, 295, 620, 1080), "Copertina da preparare")
    box(d, (755, 270, 1540, 1425))
    x, y, iw = 792, 308, 704
    y = wrapped(d, normalize(obj.get("topic"), "Titolo mancante"), (x, y), iw, font(54, bold=True, serif=True), INK, 3, 69) + 35
    fields = [
        ("PROMESSA INIZIALE", plan.get("opening_promise")),
        ("PERCHÉ QUESTO SOGGETTO", plan.get("subject_insight")),
        ("DURATA MOTIVATA", str(plan.get("duration_seconds") or "?") + " s · " + normalize(plan.get("duration_reason"), "da definire")),
        ("SCELTE DI REGIA", plan.get("mix_reason")),
        ("CHIUSURA NARRATIVA", plan.get("payoff"))
    ]
    for label, value in fields:
        d.text((x, y), label, font=font(23, bold=True), fill="#917044")
        y += 42
        y = wrapped(d, value, (x, y), iw, font(26), INK, 3, 38) + 28
        if y >= 1370:
            break
    d.text((72, 1460), "STORYBOARD · ANTEPRIMA DELLE SCENE", font=font(39, bold=True), fill=NAVY)
    tile_w, gap, h = 356, 22, 365
    for j, sc in enumerate(scenes[:8]):
        col, row = j % 4, j // 4
        x = 65 + col*(tile_w+gap)
        y = 1520 + row*(h+25)
        box(d, (x, y, x+tile_w, y+h))
        place(im, d, sc["path"], (x+12, y+12, tile_w-24, 206), "Scena " + str(sc["number"]))
        d.text((x+17, y+230), f"SCENA {sc['number']:02d}", font=font(23, bold=True), fill="#A77E48")
        wrapped(d, sc["text"], (x+16, y+271), tile_w-32, font(22), INK, 3, 29)
    if len(scenes) > 8:
        d.text((70, 2314), f"Altre {len(scenes)-8} scene nella contact sheet", font=font(21), fill=MUTED)
    d.text((70, 2360), "ANTEPRIMA EDITORIALE · non certifica sorgenti, diritti o revisione artistica", font=font(20), fill=MUTED)
    im.save(out/"CONCEPT_BOARD.png", optimize=True)

def status_for(visual):
    v = visual["decision"]
    okay = (visual["path"] is not None and
            v.get("rights_review") == "reviewed" and
            v.get("scene_relevance") == "reviewed" and
            v.get("visual_review") == "passed" and
            bool(v.get("source_reference")))
    return "REVISIONI REGISTRATE" if okay else "DA VERIFICARE"

def make_production(project_path, out, obj, plan, scenes, visuals, cover):
    im = Image.new("RGB", (W, 2400), PAPER)
    d = ImageDraw.Draw(im)
    banner(im, d, "PRODUCTION BOARD", "Fonti e revisioni: solo stati effettivamente presenti in PROJECT_V13")
    box(d, (60, 275, 1540, 610))
    place(im, d, cover, (82, 298, 176, 286), "Cover")
    d.text((290, 302), "SCHEDA OPERATIVA", font=font(25, bold=True), fill="#987349")
    wrapped(d, obj.get("topic"), (290, 349), 1180, font(44, bold=True, serif=True), INK, 2, 55)
    wrapped(d, "FORMAT: " + normalize(obj.get("format")) + "  ·  PRESET: " + normalize(obj.get("preset")),
            (290, 467), 1170, font(23), MUTED, 2, 33)
    wrapped(d, "STATO VIDEO: " + normalize(obj.get("status"), "non dichiarato") +
            "  ·  DURATA OBIETTIVO: " + normalize(plan.get("duration_seconds"), "?") + " s",
            (290, 530), 1170, font(22), MUTED, 2, 31)
    d.text((70, 652), "ASSET VISIVI · PROVENIENZA E DIRITTI", font=font(37, bold=True), fill=NAVY)
    max_rows = 9
    for i, visual in enumerate(visuals[:max_rows]):
        y = 710 + i*164
        box(d, (63, y, 1538, y+150))
        place(im, d, visual["path"], (79, y+12, 140, 125), "Senza file")
        d.text((240, y+17), normalize(visual["id"]), font=font(23, bold=True), fill=INK)
        dec = visual["decision"]
        src = normalize(dec.get("source_reference") or visual["data"].get("source"), "Sorgente da registrare")
        wrapped(d, "Fonte: " + src, (240, y+56), 850, font(18), MUTED, 2, 26)
        d.text((1120, y+22), status_for(visual), font=font(18, bold=True),
               fill="#36724D" if status_for(visual) == "REVISIONI REGISTRATE" else "#A56C26")
        wrapped(d, "Diritti: " + normalize(visual["data"].get("rights"), "non accertati"),
                (1120, y+66), 383, font(17), MUTED, 2, 23)
    if not visuals:
        d.text((92, 744), "Nessun asset visivo registrato: scheda incompleta.", font=font(27), fill=MUTED)
    if len(visuals) > max_rows:
        d.text((83, 2208), f"+{len(visuals)-max_rows} asset nel file JSON sorgente", font=font(22), fill=MUTED)
    d.text((70, 2310), "I campi mancanti NON diventano approvati · nessuna pubblicazione automatica", font=font(22), fill="#865D32")
    d.text((70, 2360), "Generato da metadata locali; verificare il video e le licenze prima della consegna", font=font(20), fill=MUTED)
    im.save(out/"PRODUCTION_BOARD.png", optimize=True)


def make_master(project_path, out, obj, plan, scenes, visuals, cover):
    """Sourced fourth board from recorded PROJECT_V13 fields. No model/API calls."""
    im = Image.new("RGB", (W, 3600), PAPER)
    d = ImageDraw.Draw(im)
    banner(im, d, "DOSSIER ILLUSTRATO COMPLETO", "PROJECT_V13 · Ricerca dichiarata · Nessuna generazione AI")
    bib = obj.get("bibliography") if isinstance(obj.get("bibliography"), dict) else {}
    meta = obj.get("editorial_metadata") if isinstance(obj.get("editorial_metadata"), dict) else {}
    business = obj.get("business") if isinstance(obj.get("business"), dict) else {}
    contract = obj.get("editorial_contract") if isinstance(obj.get("editorial_contract"), dict) else {}
    sources = plan.get("sources") if isinstance(plan.get("sources"), list) else []
    box(d, (60, 265, 535, 1130))
    place(im, d, cover, (82, 287, 432, 818), "Copertina da allegare")
    box(d, (565, 265, 1540, 1130))
    wrapped(d, obj.get("topic"), (595, 300), 890, font(48, bold=True, serif=True), INK, 3, 59)
    y = 450
    fields = [
        ("AUTORE / ANNO", normalize(bib.get("author")) + " · " + normalize(bib.get("publication_year"))),
        ("SERIE / FORMATO", normalize(meta.get("series")) + " · " + normalize(obj.get("format"))),
        ("HOOK", plan.get("opening_promise")),
        ("PERCHÉ QUESTO LIBRO", plan.get("subject_insight")),
        ("PUBBLICO", business.get("audience")),
        ("TEMI", meta.get("themes")),
        ("STILE E REGIA", plan.get("mix_reason")),
    ]
    for label, value in fields:
        d.text((602, y), label, font=font(20, bold=True), fill="#937045")
        y = wrapped(d, value, (602, y+30), 878, font(21), INK, 2, 27) + 18
        if y > 1090:
            break
    d.text((68, 1170), "STORYBOARD · SCENE DOCUMENTATE", font=font(38, bold=True), fill=NAVY)
    for n, scene in enumerate(scenes[:8]):
        x, y = 65+(n%4)*378, 1225+(n//4)*361
        box(d, (x, y, x+355, y+340))
        place(im, d, scene.get("path"), (x+13, y+14, 328, 197), "Asset non presente")
        d.text((x+16, y+220), "SCENA "+str(scene["number"]), font=font(21, bold=True), fill="#947047")
        wrapped(d, scene.get("text"), (x+15, y+257), 325, font(18), INK, 2, 25)
    if len(scenes)>8:
        d.text((80, 1971), f"+ {len(scenes)-8} scene nella contact sheet", font=font(21), fill=MUTED)
    d.text((68, 1998), "FONTI BIBLIOGRAFICHE · STATO DICHIARATO", font=font(35, bold=True), fill=NAVY)
    box(d, (65, 2055, 1538, 2450))
    if sources:
        y = 2082
        for i, src in enumerate(sources[:5], 1):
            if not isinstance(src, dict):
                continue
            value = (f"{i}. " + normalize(src.get("reference")) + " | " +
                     normalize(src.get("finding")) + " | Verifica: " + normalize(src.get("verification")))
            y = wrapped(d, value, (88, y), 1412, font(19), INK, 2, 26)+13
    else:
        wrapped(d, "Nessuna fonte registrata. Non dichiarare il soggetto verificato.",
                (90, 2090), 1380, font(26), MUTED, 3)
    d.text((68, 2496), "ASSET VISIVI · PROVENIENZA E DIRITTI", font=font(35, bold=True), fill=NAVY)
    box(d, (65, 2555, 1538, 3170))
    if visuals:
        y = 2585
        for i, v in enumerate(visuals[:7], 1):
            a, dec = v["data"], v["decision"]
            line = (f"{i}. "+normalize(v["id"])+" · "+normalize(a.get("file"))+
                    " | Fonte: "+normalize(dec.get("source_reference") or a.get("source"))+
                    " | Diritti: "+normalize(a.get("rights"))+" | "+status_for(v))
            y = wrapped(d, line, (88, y), 1412, font(18), INK, 2, 25)+15
    else:
        wrapped(d, "Nessun asset registrato: il video non è approvato.", (90, 2600), 1390, font(27), MUTED, 2)
    if len(visuals)>7:
        d.text((90, 3145), f"+{len(visuals)-7} asset nel PROJECT_V13 originale", font=font(20), fill=MUTED)
    box(d, (65, 3220, 1538, 3535))
    labels = [
        ("VOCE", contract.get("voice")),
        ("DURATA OBIETTIVO", str(plan.get("duration_seconds") or "Da definire")+" s"),
        ("SOCIAL", (obj.get("creative_v21") or {}).get("social_package_status")),
        ("DIRITTI", (obj.get("reviews") or {}).get("rights", {}).get("status")),
    ]
    y = 3250
    for label, value in labels:
        d.text((87, y), label, font=font(20, bold=True), fill="#987448")
        wrapped(d, value, (465, y), 1020, font(20), INK, 1)
        y += 56
    d.text((74, 3570), "Fonti dichiarate ≠ fonti verificate. Diritti da verificare prima della pubblicazione.", font=font(19), fill=MUTED)
    im.save(out / "MASTER_BOARD.png", optimize=True)

def make_contact(project_path, out, scenes, cover):
    cols, tile_h = 4, 430
    rows = max(1, math.ceil(len(scenes) / cols))
    h = 210 + rows*tile_h + 60
    im = Image.new("RGB", (W, h), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 160), fill=NAVY)
    d.text((62, 54), "SCENE CONTACT SHEET", font=font(55, bold=True), fill=IVORY)
    for i, scene in enumerate(scenes):
        x = 63 + (i % cols)*378
        y = 195 + (i // cols)*tile_h
        box(d, (x, y, x+354, y+404))
        place(im, d, scene["path"], (x+12, y+12, 330, 285), "Asset scena non disponibile")
        d.text((x+14, y+316), "SCENA " + str(scene["number"]), font=font(20, bold=True), fill="#987349")
        wrapped(d, scene["text"], (x+12, y+348), 328, font(18), INK, 2, 24)
    if not scenes:
        d.text((80, 245), "Storyboard non presente nel PROJECT_V13", font=font(32), fill=MUTED)
    im.save(out/"SCENE_CONTACT_SHEET.jpg", quality=87, optimize=True)

def generate(project_path, out):
    obj, plan, scenes, visuals, cover = prepare(project_path)
    out.mkdir(parents=True, exist_ok=True)
    make_concept(project_path, out, obj, plan, scenes, visuals, cover)
    make_production(project_path, out, obj, plan, scenes, visuals, cover)
    make_contact(project_path, out, scenes, cover)
    make_master(project_path, out, obj, plan, scenes, visuals, cover)
    manifest = {
        "schema": "video-boards-v34", "source_project": str(project_path),
        "source_sha256": hashlib.sha256(project_path.read_bytes()).hexdigest(),
        "uses_image_generation_api": False, "calls_paid_models": False,
        "scene_count": len(scenes), "visual_asset_count": len(visuals),
        "missing_visual_files": [v["id"] for v in visuals if v["path"] is None],
        "unreviewed_visual_assets": [v["id"] for v in visuals if status_for(v) != "REVISIONI REGISTRATE"],
        "status": "informational_not_approved",
        "files": ["CONCEPT_BOARD.png", "PRODUCTION_BOARD.png", "SCENE_CONTACT_SHEET.jpg", "MASTER_BOARD.png"]}
    (out/"BOARD_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--project", type=Path)
    grp.add_argument("--root", type=Path, help="Find PROJECT_V13.json recursively")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    projects = [args.project] if args.project else sorted(args.root.rglob("PROJECT_V13.json"))
    if not projects:
        raise SystemExit("Nessun PROJECT_V13.json trovato, non genero schede finte")
    success, errors = 0, []
    for project in projects:
        try:
            target = args.out if args.project else args.out/(project.parent.name + "-" + hashlib.sha1(str(project).encode()).hexdigest()[:8])
            result = generate(project, target)
            print(f"OK {project}: {result['scene_count']} scene, {result['visual_asset_count']} asset -> {target}")
            success += 1
        except (OSError, ValueError, KeyError, TypeError) as e:
            errors.append(f"{project}: {e}")
    for error in errors:
        print("ERRORE", error)
    print(f"Completati {success}/{len(projects)} dossier")
    if errors:
        raise SystemExit(2)

if __name__ == "__main__":
    main()

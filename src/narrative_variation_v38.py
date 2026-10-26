"""V38 creative preflight: diagnose avoidable repetition, never prescribe an artistic quota.

Runs entirely offline with no media-provider calls. An observation is not a veto,
a license, a verdict on beauty, or an authorization to publish.
"""
from __future__ import annotations

from collections import Counter


def _txt(value):
    return " ".join(str(value or "").split()).casefold()


def _finding(code, message, scenes=None):
    return {"code": code, "message": message,
            "scenes": list(scenes or ()), "level": "review"}


def inspect(project):
    """Assess narrative planning and scene repetition; never impose durations/counts.

    Fields are deliberately optional for legacy recipes. A repeated image is
    not inherently bad: the same illustration can serve multiple distinct beats.
    """
    design = (project.get("editorial_plan") or {}).get("narrative_design")
    scenes = project.get("scenes") or []
    if not isinstance(scenes, list):
        scenes = []
    findings = []
    beats = []

    if isinstance(design, dict):
        raw = design.get("story_beats")
        if isinstance(raw, list):
            beats = raw
        if beats and not design.get("distinct_visual_needs"):
            findings.append(_finding("VISUAL_NEEDS_NOT_PLANNED",
                "Beat narrativi presenti, ma le esigenze visuali distinte non sono state registrate."))
        if len(scenes) > 1 and not _txt(design.get("image_count_reason")):
            findings.append(_finding("VISUAL_COUNT_NOT_MOTIVATED",
                "Motivare la quantità di immagini con cambi effettivi del racconto, non con un numero fisso."))
        if len(scenes) > 1 and not _txt(design.get("pace_reason")):
            findings.append(_finding("RHYTHM_NOT_MOTIVATED",
                "Motivare il ritmo a partire da voce, significato ed emozioni, non dal video di riferimento."))
        if (design.get("reference_id") == "time_machine_20261026"
                and design.get("do_not_copy_reference_parameters") is False):
            findings.append(_finding("REFERENCE_TEMPLATE_RISK",
                "Il riferimento positivo non autorizza a replicare durata, immagini o regia."))
    elif scenes and project.get("editorial_contract"):
        findings.append(_finding("V38_PLAN_MISSING",
            "Piano narrative_design non disponibile: descrivere beat e bisogni visivi se applicabile."))

    for idx, (left, right) in enumerate(zip(scenes, scenes[1:]), start=2):
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        same_asset = _txt(left.get("asset_id")) and _txt(left.get("asset_id")) == _txt(right.get("asset_id"))
        same_description = _txt(left.get("description")) and _txt(left.get("description")) == _txt(right.get("description"))
        same_reason = _txt(left.get("reason")) and _txt(left.get("reason")) == _txt(right.get("reason"))
        justified = _txt(right.get("reuse_reason")) or _txt(right.get("camera_reason"))
        if same_asset and same_description and same_reason and not justified:
            findings.append(_finding("DUPLICATE_SHOT_WITHOUT_REASON",
                "Due scene consecutive riusano asset, soggetto e motivazione senza una ragione distinta.",
                [idx - 1, idx]))

    # Optional camera data: warn only when all movements in a consecutive sequence
    # repeat identically without ANY camera-specific explanation. This is advisory:
    # a steady visual style can be the correct choice for a contemplative story.
    camera_run = []
    last = None
    for idx, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            camera_run = []
            last = None
            continue
        move = _txt(scene.get("camera") or scene.get("camera_move"))
        justified = _txt(scene.get("camera_reason"))
        if not move or justified:
            camera_run = []
            last = None
            continue
        if move != last:
            if len(camera_run) >= 3:
                findings.append(_finding("REPEATED_CAMERA_UNEXPLAINED",
                    "Movimento della camera ripetuto in una sequenza: confermare che sia coerente con la storia.",
                    camera_run))
            camera_run = [idx]
        else:
            camera_run.append(idx)
        last = move
    if len(camera_run) >= 3:
        findings.append(_finding("REPEATED_CAMERA_UNEXPLAINED",
            "Movimento della camera ripetuto in una sequenza: confermare che sia coerente con la storia.",
            camera_run))

    distinct_assets = {
        _txt(x.get("asset_id")) for x in scenes if isinstance(x, dict) and _txt(x.get("asset_id"))
    }
    code_counts = Counter(x["code"] for x in findings)
    return {
        "schema": "narrative-variation-review-v38",
        "scene_count_observed": len(scenes),
        "distinct_visual_asset_ids_observed": len(distinct_assets),
        "story_beats_recorded": len(beats),
        "findings": findings,
        "finding_counts": dict(code_counts),
        "needs_creative_review": bool(findings),
        "automatic_artistic_approval": False,
        "hardcoded_target_duration_or_image_count": False,
        "note": "Numeri osservati, non target. Il controllo suggerisce revisioni, non certifica qualità o diritti."
    }

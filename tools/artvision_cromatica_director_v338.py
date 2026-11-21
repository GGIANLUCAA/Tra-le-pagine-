#!/usr/bin/env python3
"""ArtVision V338: individually authored, narrative-first directing plans.

The subject determines edit length, scene order and time of full canvas reveal.
No randomized 12-shot stencil. This module contains NO network calls or assets.
The caller must verify the exact original painting and audio rights separately.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import Any

# Manual, subject-specific beat notation:
# (kind, seconds, starting focus id, ending focus id, visual scale, dramatic reason)
# "detail": crop/pan on the original art (start=end is an intentional locked shot)
# "reveal": motivated zoom OUT to whole original, with continuous artwork-derived fill
# "whole": entirely visible, unchanged authentic original
# "approach": motivated zoom IN starting from whole original
# No novelty edits merely to reach a beat count; no automated dancing to arbitrary BPM.
# The 'focus' coordinates are preflight candidates; check original pixels/scene before approval.
DIRECTION = {
    "01_ARBO_WILD_HUNT": {
        "concept": "A wind-borne chase: chaos gives way to a sudden grasp of the entire sky",
        "title_mode": "low",
        "typography_seconds": 2.5,
        "beats": [
            ("detail", 2.4, 0, 0, 1.18, "The ghostly cavalcade enters without introductory full-frame"),
            ("detail", 6.3, 1, 2, 1.12, "Lateral travel along the advancing horses"),
            ("detail", 3.2, 2, 2, 1.34, "Still image: encounter the most charged detail"),
            ("reveal", 4.6, None, None, None, "Pull away on the musical phrase"),
            ("whole", 8.1, None, None, None, "Hold the vast true canvas, let scale register"),
            ("approach", 3.1, None, None, None, "Return to the spectral riders"),
            ("detail", 5.7, 3, 4, 1.19, "A long travelling view follows the direction of the chase"),
            ("detail", 2.6, 5, 5, 1.30, "Sudden silence of movement before the end"),
            ("reveal", 4.8, None, None, None, "Second revelation, now emotionally altered"),
            ("whole", 7.3, None, None, None, "End on the entire turbulent sky")
        ],
    },
    "02_DADD_FAIRY_FELLER": {
        "concept": "Curiosity before action: enter a miniature, crowded world from the whole scene",
        "title_mode": "top",
        "typography_seconds": 4.0,
        "beats": [
            ("whole", 6.8, None, None, None, "Begin with the densely populated whole painting"),
            ("approach", 5.6, None, None, None, "Descend deliberately into the central ritual"),
            ("detail", 6.4, 0, 0, 1.32, "Listen to the stillness of the axe about to fall"),
            ("detail", 3.0, 1, 2, 1.35, "Tiny figures emerge between stems"),
            ("detail", 2.1, 2, 2, 1.46, "Short isolating glance at an overlooked detail"),
            ("detail", 7.2, 3, 5, 1.23, "Slow walk through multiple nested scenes"),
            ("detail", 4.3, 4, 4, 1.39, "Hold on life at the edge of the painting"),
            ("reveal", 5.2, None, None, None, "The threads reunite as the camera retreats"),
            ("whole", 8.4, None, None, None, "Let the miniature universe become one composition"),
        ],
    },
    "03_REPIN_SADKO": {
        "concept": "Underwater wonder, then quiet recognition; the heroine is not treated as an action cut",
        "title_mode": "center",
        "typography_seconds": 3.2,
        "beats": [
            ("detail", 4.3, 2, 2, 1.27, "The underwater light comes first"),
            ("detail", 3.0, 0, 0, 1.35, "A human figure anchors the fantasy"),
            ("detail", 6.7, 1, 4, 1.22, "Travel upward through the submerged procession"),
            ("detail", 2.6, 5, 5, 1.42, "An enigmatic face held for emphasis"),
            ("reveal", 4.9, None, None, None, "The human story resolves into the full painting"),
            ("whole", 9.2, None, None, None, "Whole underwater composition, long uninterrupted hold"),
            ("approach", 4.0, None, None, None, "Return under the surface"),
            ("detail", 7.0, 3, 0, 1.18, "A slow, unhurried crossing between figures"),
            ("reveal", 3.8, None, None, None, "Return to painter's full architecture"),
            ("whole", 4.6, None, None, None, "Small contemplative whole-painting finale")
        ],
    },
    "04_PRINCESS_TARAKANOVA": {
        "concept": "One trapped person; dread comes from stillness, not constant movement",
        "title_mode": "top",
        "typography_seconds": 2.2,
        "beats": [
            ("detail", 8.3, 0, 0, 1.14, "Open with a locked composition on the person"),
            ("detail", 4.4, 3, 4, 1.18, "The water's approach, without an invented animation"),
            ("detail", 2.7, 1, 1, 1.27, "Silent, quick observation of the cell"),
            ("detail", 7.6, 5, 0, 1.13, "Slow camera approach returning to the human story"),
            ("reveal", 6.0, None, None, None, "Widen and expose the geometry of imprisonment"),
            ("whole", 11.2, None, None, None, "Entire painting, a long uncomfortable pause"),
            ("approach", 4.6, None, None, None, "Return into the confined space"),
            ("detail", 5.4, 0, 0, 1.20, "End without reassuring full-canvas closure")
        ],
    },
    "05_WATERHOUSE_MERMAID": {
        "concept": "Quiet shore: a lyrical passage from coast to person and back",
        "title_mode": "low",
        "typography_seconds": 3.5,
        "beats": [
            ("whole", 9.5, None, None, None, "Begin with the entire original composition"),
            ("approach", 5.4, None, None, None, "A gradual arrival at the mermaid"),
            ("detail", 8.1, 1, 0, 1.15, "Slow attentive look from sea to figure"),
            ("detail", 3.4, 2, 2, 1.32, "A short near-still study of face and hair"),
            ("detail", 6.9, 3, 4, 1.19, "Unhurried shore, waves and objects"),
            ("detail", 4.6, 5, 5, 1.25, "A pause on hands and light"),
            ("reveal", 5.8, None, None, None, "Leave the details and return to the coast"),
            ("whole", 8.1, None, None, None, "Full painting held again, no end card")
        ],
    },
    "06_DE_MORGAN_STORM_SPIRITS": {
        "concept": "Alternation of sweeping movement and still confrontation in the wind",
        "title_mode": "center",
        "typography_seconds": 2.8,
        "beats": [
            ("detail", 2.3, 1, 1, 1.38, "Abrupt encounter with one figure"),
            ("detail", 4.7, 1, 0, 1.19, "Wind direction: wide movement through the canvas"),
            ("detail", 2.1, 2, 2, 1.37, "Another figure, contrasting scale"),
            ("detail", 7.8, 5, 4, 1.14, "Let clouds and bodies cross the frame slowly"),
            ("reveal", 4.1, None, None, None, "Suddenly understand the full image"),
            ("whole", 7.1, None, None, None, "Whole canvas at the moment of maximum musical expansion"),
            ("approach", 3.0, None, None, None, "A second entry into turbulent matter"),
            ("detail", 5.3, 3, 2, 1.24, "Movement in reverse as the scene settles"),
            ("detail", 2.0, 0, 0, 1.31, "Held close-up; all movement stops"),
            ("reveal", 5.5, None, None, None, "Slow, continuous return to full painting"),
            ("whole", 5.7, None, None, None, "Final calm, complete image visible")
        ],
    },
    "07_RHEAM_SLEEPING_BEAUTY": {
        "concept": "Sleep as time held still; one slow awakening of the surrounding setting",
        "title_mode": "top",
        "typography_seconds": 4.2,
        "beats": [
            ("detail", 7.6, 0, 0, 1.12, "Long still opening, do not use a fake dramatic hook"),
            ("detail", 10.8, 1, 2, 1.11, "Slow movement across the wooded setting"),
            ("detail", 5.0, 3, 3, 1.24, "A meaningful pause on one real detail"),
            ("reveal", 5.7, None, None, None, "The whole setting slowly becomes clear"),
            ("whole", 12.9, None, None, None, "Extended full-artwork hold befitting a sleeping subject"),
            ("approach", 3.5, None, None, None, "Return gently towards the figure"),
            ("detail", 10.6, 4, 5, 1.12, "End with a very gradual passage; no mandatory final full shot")
        ],
    },
    "08_BRYULLOV_POMPEII": {
        "concept": "The catastrophe first appears as an immense painting; then the camera discovers families, falling stone and the glow above Pompeii. The film ends with a human detail, not another obligatory reveal.",
        "title_mode": "low",
        "typography_seconds": 3.1,
        "beats": [
            ("whole", 5.8, None, None, None, "The whole authentic monumental canvas opens the film; audience sees what is happening immediately"),
            ("approach", 4.2, None, None, None, "A gradual camera movement into the tragic event"),
            ("detail", 4.0, 0, 0, 1.17, "Hold the frightened people in the foreground"),
            ("detail", 6.8, 1, 2, 1.18, "A long movement across families, carrying the eye through the crowd"),
            ("detail", 3.1, 3, 3, 1.29, "A still observation of the fallen woman"),
            ("detail", 5.4, 4, 5, 1.16, "Rise from people towards the fiery light above the city"),
            ("reveal", 3.6, None, None, None, "Pull out at the dramatic peak and restore the painting's full scale"),
            ("whole", 9.4, None, None, None, "A long uninterrupted hold on the entire original: let the catastrophe register"),
            ("approach", 4.2, None, None, None, "Return towards the center of the scene, without a formulaic edit"),
            ("detail", 6.7, 5, 1, 1.13, "Trace the human motion across the original painting"),
            ("detail", 3.5, 2, 2, 1.27, "Brief observation of the last figures against the collapsing architecture"),
            ("detail", 5.0, 0, 0, 1.14, "A quiet human close, with no conventional closing-card or compulsory full canvas"),
        ],
    },
    # New subjects get their own researched plans after source approval.
    # Never silently generate a generic plan for an unfamiliar painting.
}

def shot_plan_for(work: dict[str, Any]) -> dict[str, Any]:
    slug = work.get("slug","")
    if slug not in DIRECTION:
        raise ValueError(f"V338 editorial plan missing for {slug}: artwork review required")
    entry = DIRECTION[slug]
    focus = work["focus"]
    shots = []
    for kind, duration, start_index, end_index, zoom, reason in entry["beats"]:
        if kind not in {"detail","reveal","whole","approach"}:
            raise ValueError(f"Unsupported scene kind {kind}")
        if kind == "detail":
            if start_index is None or end_index is None:
                raise ValueError("Visual focus not assigned")
            if max(start_index,end_index) >= len(focus):
                raise ValueError("Focus index unavailable on this work")
            shot = {"kind":kind,"dur":duration,"a":focus[start_index],
                    "b":focus[end_index],"z":zoom,"why":reason}
        else:
            shot = {"kind":kind,"dur":duration,"why":reason}
        if not (1.8 <= duration <= 13.0):
            raise ValueError("Scene duration unrealistic or unreviewed")
        shots.append(shot)
    total = round(sum(s["dur"] for s in shots),2)
    wholes = sum(s["dur"] for s in shots if s["kind"]=="whole")
    assert 44 <= total <= 75, f"Unreviewed overall duration: {total}"
    assert wholes >= 7.0, f"Missing full artwork display: {wholes}"
    assert len(shots) >= 7, "Insufficient meaningful scene construction"
    assert not any(a["kind"]==b["kind"]==c["kind"]=="whole"
                   for a,b,c in zip(shots,shots[1:],shots[2:])), "Repetitive static full-canvas shots"
    return {"slug":slug,"concept":entry["concept"],"title_mode":entry["title_mode"],
            "typography_seconds":entry["typography_seconds"],
            "shots":shots,"duration":total,"whole_seconds":wholes,
            "editing_signature":[s["kind"] for s in shots]}

def audit_uniqueness(works: list[dict[str,Any]]) -> dict[str, Any]:
    plans=[shot_plan_for(x) for x in works]
    signatures=[tuple(x["editing_signature"]) for x in plans]
    if len(signatures)!=len(set(signatures)):
        raise ValueError("V338 regression: identical edit structures among owner-selected reels")
    first=[p["editing_signature"][0] for p in plans]
    if len(set(first))<2:
        raise ValueError("V338 regression: all videos open with same shot type")
    final=[p["editing_signature"][-1] for p in plans]
    if len(set(final))<2:
        raise ValueError("V338 regression: all videos end with same shot type")
    lengths=[p["duration"] for p in plans]
    if max(lengths)-min(lengths)<5.0:
        raise ValueError("V338 regression: all videos share approximate fixed runtime")
    return {"plans":len(plans),"unique_signatures":len(set(signatures)),
            "unique_shot_counts":sorted(set(len(s) for s in signatures)),
            "openings":dict(Counter(first)),"finales":dict(Counter(final)),
            "duration_range_seconds":[min(lengths),max(lengths)],
            "minimum_entire_work_seconds":min(p["whole_seconds"] for p in plans)}

if __name__=="__main__":
    import json
    # Self-test with 6 focal points per work, no downloaded image needed.
    works=[{"slug":key,"focus":[(.5,.5)]*6} for key in DIRECTION]
    print(json.dumps(audit_uniqueness(works),indent=2,ensure_ascii=False))

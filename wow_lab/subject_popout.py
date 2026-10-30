"""WOW LAB: conservative source-verified silhouette preflight and 2.5D pop-out.

This module cannot certify semantic completeness or artistic quality. It must
be called BEFORE the first rendered frame. No paid APIs, core imports or uploads.
The extracted layer is 2.5D; it is NOT a 3D mesh.
"""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from subject_extractor import propose_mask
from mask_audit import audit

class PreflightRejected(RuntimeError):
    pass

def audit_clean_plate(source_bgr: np.ndarray, mask: np.ndarray,
                      clean_bgr: np.ndarray) -> dict:
    """Reject obvious invented backgrounds before any video is rendered.

    A subject surrounded by patterned scenery cannot safely be removed with
    a local inpaint. This tests the source ring AND the reconstructed region.
    It is conservative numerical evidence, never an artistic approval.
    """
    if (source_bgr is None or clean_bgr is None or mask is None or
            source_bgr.ndim != 3 or source_bgr.shape[2] != 3 or
            clean_bgr.shape != source_bgr.shape or
            mask.shape != source_bgr.shape[:2]):
        return {"pass": False, "reasons": ["invalid_clean_plate_inputs"],
                "artistic_approval": False}
    subject = np.uint8(mask >= 128)
    kernel = np.ones((17, 17), np.uint8)
    ring = (cv2.dilate(subject, kernel) != 0) & (subject == 0)
    if np.count_nonzero(ring) < 100 or np.count_nonzero(subject) < 100:
        return {"pass": False, "reasons": ["insufficient_background_ring"],
                "artistic_approval": False}
    original_lab = cv2.cvtColor(source_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    clean_lab = cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    background = np.median(original_lab[ring], axis=0)
    def q90_distance(pixels):
        return float(np.percentile(np.linalg.norm(pixels - background, axis=1), 90))
    background_variation = q90_distance(original_lab[ring])
    reconstructed_variation = q90_distance(clean_lab[subject != 0])
    reasons = []
    if background_variation > 18:
        reasons.append("complex_background_near_subject")
    if reconstructed_variation > 28:
        reasons.append("inpaint_inconsistent_with_background")
    return {
        "pass": not reasons,
        "reasons": reasons,
        "background_ring_lab_p90": round(background_variation, 2),
        "reconstructed_region_lab_p90": round(reconstructed_variation, 2),
        "synthetic_background": True,
        "artistic_approval": False,
        "requires_visual_review": True,
    }



def preflight_source(source: Image.Image, output: Path):
    """Return (cleaned_painting, original_resized, mask); persist audit first."""
    output.mkdir(parents=True, exist_ok=True)
    reduced = source.convert("RGB").copy()
    reduced.thumbnail((1100, 1100), Image.Resampling.LANCZOS)
    rgb = np.asarray(reduced)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    mask, proposal = propose_mask(bgr)
    geometry = audit(bgr, mask) if mask is not None else {
        "pass": False, "reasons": ["no_candidate_mask"]
    }
    approved = bool(proposal.get("pass") and geometry.get("pass"))
    report = {
        "schema": "wow-lab-mask-preflight-v1",
        "technical_pass": approved,
        "proposal": proposal,
        "geometry": geometry,
        "semantic_completeness_verified": False,
        "artistic_approval": False,
        "mask_review_required": True,
        "inpainting_disclosed": True,
    }
    (output / "SUBJECT_PREFLIGHT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if mask is not None:
        cv2.imwrite(str(output / "SUBJECT_MASK.png"), mask)
        preview = bgr.copy()
        preview[mask == 0] = np.uint8(preview[mask == 0].astype(np.float32) * .25)
        contour = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT,
                                   np.ones((3, 3), np.uint8)) != 0
        preview[contour] = (0, 255, 255)
        cv2.imwrite(str(output / "MASK_BEFORE_RENDER.jpg"), preview)
    if not approved:
        raise PreflightRejected(
            "WOW_LAB_MASK_REJECTED: " +
            ",".join(proposal.get("reasons", []) + geometry.get("reasons", []))
        )
    # Invented background reconstruction, never described as authentic source.
    # A small inpaint radius is conservative; artist still must inspect reveal.
    cleaned = cv2.inpaint(bgr, mask, 5, cv2.INPAINT_TELEA)
    plate_audit = audit_clean_plate(bgr, mask, cleaned)
    (output / "CLEAN_PLATE_AUDIT.json").write_text(
        json.dumps(plate_audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    if not plate_audit["pass"]:
        raise PreflightRejected(
            "WOW_LAB_CLEAN_PLATE_REJECTED: " + ",".join(plate_audit["reasons"])
        )
    cleaned_pil = Image.fromarray(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB))
    cleaned_pil.save(output / "CLEAN_PLATE_SYNTHETIC.jpg", quality=92)
    return cleaned_pil, reduced, Image.fromarray(mask, "L")


def make_subject_panel(source: Image.Image, mask: Image.Image,
                       panel_shape: tuple[int, int, int],
                       artwork_size: tuple[int, int]):
    """Place original subject pixels at exactly the painting's panel coordinates."""
    h, w = panel_shape[:2]
    resized = source.convert("RGB").copy()
    resized.thumbnail((artwork_size[0] - 30, artwork_size[1] - 30),
                      Image.Resampling.LANCZOS)
    alpha = mask.resize(resized.size, Image.Resampling.NEAREST)
    a = cv2.GaussianBlur(np.asarray(alpha), (3, 3), .65)
    # Mask remains bounded by the actual original silhouette.
    subject = np.zeros((h, w, 4), dtype=np.uint8)
    x, y = 22, 22  # Matches engine.prepare_panel()'s border offset.
    if y + resized.height > h or x + resized.width > w:
        raise PreflightRejected("SUBJECT_PANEL_ALIGNMENT_FAILED")
    subject[y:y + resized.height, x:x + resized.width, :3] = cv2.cvtColor(
        np.asarray(resized), cv2.COLOR_RGB2BGR
    )
    subject[y:y + resized.height, x:x + resized.width, 3] = a
    return subject


def audit_popout_projection(subject_bgra: np.ndarray, quad: np.ndarray,
                            progress: float = .78, horizontal_direction: int = 1,
                            width: int = 540, height: int = 960) -> dict:
    """Fail closed unless the extracted layer visibly crosses the frame.

    This is geometric evidence only, not artistic approval or true 3D.
    Called before soundtrack/FFmpeg creation.
    """
    if subject_bgra.ndim != 3 or subject_bgra.shape[2] != 4:
        return {"pass": False, "reasons": ["invalid_subject_layer"]}
    if quad.shape != (4, 2):
        return {"pass": False, "reasons": ["invalid_frame_quad"]}
    sh, sw = subject_bgra.shape[:2]
    # Match the final output canvas used by the isolated vertical renderer.
    w, h = width, height
    corners = np.float32([[0, 0], [sw-1, 0], [sw-1, sh-1], [0, sh-1]])
    matrix = cv2.getPerspectiveTransform(corners, quad.astype(np.float32))
    layer = cv2.warpPerspective(subject_bgra[:, :, 3], matrix, (w, h))
    initial = layer > 32
    frame = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(frame, np.round(quad).astype(np.int32), 255)
    initial_total = int(np.count_nonzero(initial))
    if initial_total == 0:
        return {"pass": False, "reasons": ["empty_projected_subject"]}
    initial_outside = float(np.count_nonzero(initial & (frame == 0))) / initial_total
    t = float(np.clip((progress - .22) / .46, 0, 1))
    lift = t*t*(3-2*t)
    center = (float(np.mean(quad[:, 0])), float(np.mean(quad[:, 1])))
    transform = cv2.getRotationMatrix2D(center, 0, 1 + .12*lift)
    transform[0, 2] += horizontal_direction * 16 * lift
    transform[1, 2] -= min(h*.105, 110) * lift
    moved = cv2.warpAffine(layer, transform, (w, h))
    final = moved > 32
    final_total = int(np.count_nonzero(final))
    final_outside = (float(np.count_nonzero(final & (frame == 0))) /
                     max(final_total, 1))
    reasons = []
    if initial_outside > .005:
        reasons.append("subject_already_outside_frame_at_opening")
    if final_outside < .012:
        reasons.append("no_visible_subject_frame_crossing")
    if final_outside > .65:
        reasons.append("excessive_subject_displacement")
    return {"pass": not reasons, "reasons": reasons,
            "opening_outside_ratio": round(initial_outside, 5),
            "reveal_outside_ratio": round(final_outside, 5),
            "true_3d": False, "artistic_approval": False}


def composite_popout(base_rgb: np.ndarray, subject_bgra: np.ndarray,
                     quad: np.ndarray, progress: float,
                     horizontal_direction: int = 1) -> np.ndarray:
    """Independent subject layer passes in front of virtual frame, with shadow."""
    h, w = base_rgb.shape[:2]
    sh, sw = subject_bgra.shape[:2]
    corners = np.float32([[0, 0], [sw-1, 0], [sw-1, sh-1], [0, sh-1]])
    matrix = cv2.getPerspectiveTransform(corners, quad.astype(np.float32))
    layer = cv2.warpPerspective(subject_bgra, matrix, (w, h),
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_CONSTANT,
                                borderValue=(0, 0, 0, 0))
    t = np.clip((progress - .22) / .46, 0, 1)
    lift = float(t*t*(3-2*t))
    # 0-2s: source painting. 2-7s: silhouette crosses frame. Final hold.
    center = (float(np.mean(quad[:, 0])), float(np.mean(quad[:, 1])))
    transform = cv2.getRotationMatrix2D(center, 0, 1 + .12*lift)
    transform[0, 2] += horizontal_direction * 16 * lift
    transform[1, 2] -= min(h*.105, 110) * lift
    moved = cv2.warpAffine(layer, transform, (w, h),
                            flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(0, 0, 0, 0))
    alpha = moved[:, :, 3].astype(np.float32) / 255
    if not np.any(alpha):
        raise PreflightRejected("EMPTY_SUBJECT_LAYER")
    # Shadow is offset from the moved silhouette, not from the whole painting.
    shadow = cv2.GaussianBlur(alpha, (0, 0), sigmaX=13)
    offset = np.float32([[1, 0, 13*lift], [0, 1, 17*lift]])
    shadow = cv2.warpAffine(shadow, offset, (w, h)) * (.42*lift)
    rgb = base_rgb.astype(np.float32) * (1 - shadow[:, :, None])
    subject_rgb = moved[:, :, :3][:, :, ::-1].astype(np.float32)
    rgb = rgb * (1 - alpha[:, :, None]) + subject_rgb * alpha[:, :, None]
    return np.uint8(np.clip(rgb, 0, 255))

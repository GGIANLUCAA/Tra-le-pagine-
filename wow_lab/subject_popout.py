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
    t = np.clip((progress - .13) / .49, 0, 1)
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

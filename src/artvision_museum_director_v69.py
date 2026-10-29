"""ArtVision Museum Director V69. Evidence validation only; no rendering."""
import argparse
import json
from pathlib import Path

def template():
    return {
        "artwork": {"title": "", "artist": "", "source_url": "",
                    "image_sha256": "", "rights": "", "width_cm": None,
                    "height_cm": None, "dimensions_source": ""},
        "frame": {"status": "scenic_reconstruction", "photo_source": "",
                  "photo_rights": "", "outer_width_cm": None,
                  "outer_height_cm": None, "material": "", "profile": "",
                  "disclosure": "Scenographic reconstruction"},
        "gallery": {"status": "declared_contemporary_reconstruction",
                    "photo_source": "", "disclosure": "Reconstructed gallery",
                    "architecture_rationale": ""},
        "camera": {"painting_center_x": 0.5, "painting_center_y": 0.5,
                   "continuous_entry_exit": True, "foreground_visitors": "none",
                   "scale_reference": "", "opening_wide_shot": True,
                   "return_same_room": True},
        "production": {"status": "planning_only", "render_authorized": False}
    }

def evaluate(data):
    errors = []
    art = data.get("artwork", {})
    for field in ("title", "artist", "source_url", "image_sha256", "rights",
                  "dimensions_source"):
        if not art.get(field):
            errors.append("Missing artwork " + field)
    width, height = art.get("width_cm"), art.get("height_cm")
    if any(type(value) not in (int, float) or value <= 0
           for value in (width, height)):
        errors.append("Documented positive artwork dimensions required")
    frame = data.get("frame", {})
    documented = ("original_documented", "current_documented", "historic_documented")
    reconstructed = ("partial_reconstruction", "scenic_reconstruction")
    if frame.get("status") not in documented + reconstructed + ("unframed",):
        errors.append("Invalid frame status")
    if frame.get("status") in documented:
        if not frame.get("photo_source") or not frame.get("photo_rights"):
            errors.append("Documented frame requires photo source and rights")
    if frame.get("status") in reconstructed and not frame.get("disclosure"):
        errors.append("Frame reconstruction requires disclosure")
    fw, fh = frame.get("outer_width_cm"), frame.get("outer_height_cm")
    if (fw is None) != (fh is None):
        errors.append("Frame dimensions must both be known or unknown")
    if fw is not None:
        if any(type(v) not in (int, float) or v <= 0 for v in (fw, fh)):
            errors.append("Invalid outer frame dimensions")
        elif type(width) in (int, float) and type(height) in (int, float):
            if fw < width or fh < height:
                errors.append("Outer frame smaller than artwork")
    gallery = data.get("gallery", {})
    states = ("actual_documented", "declared_historic_reconstruction",
              "declared_contemporary_reconstruction")
    if gallery.get("status") not in states:
        errors.append("Invalid gallery status")
    if gallery.get("status") == "actual_documented":
        if not gallery.get("photo_source"):
            errors.append("Actual gallery requires photo source")
    elif not gallery.get("disclosure"):
        errors.append("Gallery reconstruction requires disclosure")
    if not gallery.get("architecture_rationale"):
        errors.append("Gallery rationale missing")
    camera = data.get("camera", {})
    for field in ("painting_center_x", "painting_center_y"):
        value = camera.get(field)
        if type(value) not in (int, float) or not 0.2 <= value <= 0.8:
            errors.append("Invalid camera " + field)
    if camera.get("continuous_entry_exit") is not True:
        errors.append("Continuous camera required")
    if camera.get("foreground_visitors") not in (None, "none"):
        errors.append("Foreground visitors prohibited")
    if not camera.get("scale_reference"):
        errors.append("Scale reference missing")
    if not camera.get("opening_wide_shot") or not camera.get("return_same_room"):
        errors.append("Opening and return shot required")
    return {"status": "blocked" if errors else "planning_evidence_valid",
            "render_authorized": False, "pilot_lock_unchanged": True,
            "errors": errors}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("template", "check"))
    parser.add_argument("--file")
    parser.add_argument("--out")
    args = parser.parse_args()
    if args.command == "template":
        output = json.dumps(template(), ensure_ascii=False, indent=2)
        if args.out:
            target = Path(args.out)
            with target.open("x", encoding="utf-8") as handle:
                handle.write(output + "\n")
        else:
            print(output)
    else:
        if not args.file:
            parser.error("--file required")
        result = evaluate(json.loads(Path(args.file).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["errors"]:
            raise SystemExit(2)

if __name__ == "__main__":
    main()

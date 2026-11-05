from pathlib import Path

from PIL import Image, ImageDraw

from src.storia_rivive_v295_photo_identity_gate import evaluate


def _scene(path: Path, *, colour: bool, size=(720, 1280)) -> None:
    image = Image.new("RGB", size, (205, 185, 145) if colour else (185, 185, 185))
    draw = ImageDraw.Draw(image)
    draw.rectangle((60, 100, size[0] - 60, 760), fill=(65, 105, 150) if colour else (95, 95, 95))
    draw.ellipse((230, 390, 490, 650), fill=(190, 70, 40) if colour else (130, 130, 130))
    draw.line((0, 900, size[0], 1040), fill=(20, 70, 30) if colour else (60, 60, 60), width=35)
    image.save(path)


def test_accepts_structurally_identical_colour_candidate(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    _scene(source, colour=False)
    _scene(candidate, colour=True)
    result = evaluate(source, candidate)
    assert result["ready_for_artistic_review"] is True
    assert result["release_approved"] is False


def test_rejects_monochrome_candidate(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    _scene(source, colour=False)
    _scene(candidate, colour=False)
    result = evaluate(source, candidate)
    assert "real_colour_present" in result["blockers"]


def test_rejects_reframed_square_candidate(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    _scene(source, colour=False)
    _scene(candidate, colour=True, size=(1024, 1024))
    result = evaluate(source, candidate)
    assert "same_aspect_ratio" in result["blockers"]


def test_rejects_source_that_is_already_colourised(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    _scene(source, colour=True)
    _scene(candidate, colour=True)
    result = evaluate(source, candidate)
    assert "source_is_monochrome" in result["blockers"]

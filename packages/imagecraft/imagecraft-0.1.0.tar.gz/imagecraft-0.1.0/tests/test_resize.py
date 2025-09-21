import os
from imagecraft import resize, crop, convert

def test_resize(tmp_path):
    out_path = tmp_path / "resized.png"
    img = resize("tests/data/sample.jpg", width=200)
    img.save(out_path)
    assert out_path.exists()

def test_crop(tmp_path):
    out_path = tmp_path / "cropped.jpg"
    img = crop("tests/data/sample.jpg", size=(120, 120), position="center")
    img.save(out_path)
    assert out_path.exists()

def test_convert(tmp_path):
    out_path = tmp_path / "converted.jpg"
    result = convert("tests/data/sample.png", "JPEG", save_path=out_path)
    assert os.path.exists(result)
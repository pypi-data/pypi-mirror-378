import io
import pytest
from pathlib import Path
from PIL import Image
from imagecraft import ImageUtils

IMG_DIR = Path(__file__).parent / "img"


@pytest.fixture
def sample_jpg():
    return str(IMG_DIR / "sample.jpg")


@pytest.fixture
def sample_png():
    return str(IMG_DIR / "logo_horizontal.png")


def test_validate_and_load(sample_jpg):
    utils = ImageUtils(verbose=True)
    assert utils.validate_image(sample_jpg)
    img = utils.load_image(sample_jpg)
    assert isinstance(img, Image.Image)


def test_resize_to_square(sample_jpg):
    utils = ImageUtils()
    img = utils.load_image(sample_jpg)
    out = utils.resize_to_square(img, 256)
    assert out.size == (256, 256)


def test_resize_to_width(sample_jpg):
    utils = ImageUtils()
    img = utils.load_image(sample_jpg)
    out = utils.resize_to_width(img, 400)
    assert out.size[0] == 400


def test_crop_center(sample_png):
    utils = ImageUtils()
    img = utils.load_image(sample_png)
    out = utils.crop_center(img, (300, 300))
    assert out.size == (300, 300)


def test_adjustments(sample_jpg):
    utils = ImageUtils()
    img = utils.load_image(sample_jpg)
    sharp = utils.adjust_sharpness(img, 1.5)
    bright = utils.adjust_brightness(img, 1.2)
    assert isinstance(sharp, Image.Image)
    assert isinstance(bright, Image.Image)


def test_to_bytes_and_optimize(sample_jpg):
    utils = ImageUtils()
    img = utils.load_image(sample_jpg)
    buf = utils.to_bytes(img, format="JPEG", quality=70)
    assert isinstance(buf, io.BytesIO)
    optimized = utils.optimize_for_web(img, quality=70, max_size_kb=50)
    assert isinstance(optimized, Image.Image)
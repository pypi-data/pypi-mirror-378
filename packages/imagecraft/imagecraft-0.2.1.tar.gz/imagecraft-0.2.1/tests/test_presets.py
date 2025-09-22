import pytest
from pathlib import Path
from imagecraft import ImagePresets

IMG_DIR = Path(__file__).parent / "img"


@pytest.fixture
def sample_img():
    return str(IMG_DIR / "sample.jpg")

@pytest.fixture
def logo_img():
    return str(IMG_DIR / "logo_square.jpg")

def test_profile_preset(sample_img):
    presets = ImagePresets()
    out = presets.make_profile_image(sample_img)
    assert out.size == (256, 256)

def test_logo_square(logo_img):
    presets = ImagePresets()
    out = presets.logo_square(logo_img, size=512, sharpness=2.0, format="JPEG")
    assert out is not None
    assert out.size == (512, 512)  # square

def test_logo_horizontal(logo_img):
    presets = ImagePresets()
    out = presets.logo_horizontal(logo_img, width=512, sharpness=2.0, format="JPEG")
    assert out is not None
    assert out.size[0] == 512  # width fixed
    assert out.size[1] <= int(512 * 0.5)  # height <= target height (height_ratio=0.5 default)

def test_logo_vertical(logo_img):
    presets = ImagePresets()
    out = presets.logo_vertical(logo_img, height=512, sharpness=2.0, format="JPEG")
    assert out is not None
    assert out.size[1] == 512  # height fixed
    assert out.size[0] <= int(512 * 0.6)  # width <= target width (width_ratio=0.6 default)

def test_logo_square_png_transparency(logo_img):
    presets = ImagePresets()
    out = presets.logo_square(logo_img, size=512, sharpness=2.0, format="PNG")
    assert out.mode == "RGBA"  # transparency preserved

def test_icon_preset(sample_img):
    presets = ImagePresets()
    out = presets.make_icon(sample_img, size=64, sharpness=5.0)
    assert out.size == (64, 64)


def test_thumbnail_preset(sample_img):
    presets = ImagePresets()
    out = presets.make_thumbnail(sample_img, width=400)
    assert out.size[0] == 400


def test_banner_preset(sample_img):
    presets = ImagePresets()
    out = presets.make_banner(sample_img, size=(1920, 600))
    assert out.size == (1920, 600)
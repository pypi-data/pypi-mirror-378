import pytest
from pathlib import Path
from imagecraft import ImageDynamic

IMG_DIR = Path(__file__).parent / "img"


@pytest.fixture
def sample_jpg():
    return str(IMG_DIR / "sample.jpg")


def test_dynamic_square(sample_jpg):
    dyn = ImageDynamic()
    out = dyn.process(sample_jpg, 256)
    assert out.size == (256, 256)


def test_dynamic_rectangular(sample_jpg):
    dyn = ImageDynamic()
    out = dyn.process(sample_jpg, 400, 200)
    assert out.size == (400, 200)


def test_dynamic_with_kwargs(sample_jpg):
    dyn = ImageDynamic()
    out = dyn.process(sample_jpg, 256, sharpness=1.5, brightness=1.1, quality=70)
    assert out.size == (256, 256)
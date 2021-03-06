import os

from PIL import Image
import pytest
from smartcropper import SmartCropper

def path_to(name):
    """Simplify getting absolute path to a test image"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'files', name))

@pytest.fixture
def filename():
    return path_to('entropyish.png')

@pytest.fixture
def image():
    filename = path_to('entropyish.png')
    return Image.open(filename)

@pytest.fixture
def twenty_twenty():
    filename = path_to('20x20.png')
    return Image.open(filename)

def test_smartcropper_class(image):
    img = SmartCropper(image)
    assert isinstance(img, SmartCropper)

def test_smartcropper_from_file(filename):
    img = SmartCropper.from_file(filename)
    assert isinstance(img, SmartCropper)

def test_smartcropper_from_text_file_fails():
    text_file = path_to("entropyish.txt")

    # But are we testing SmartCropper or Pillow here?
    with pytest.raises(IOError):
        img = SmartCropper.from_file(text_file)

def test_smart_crop_to_100x100(image):
    img = SmartCropper(image)
    cropped = img.smart_crop(100, 100)
    size = [cropped.height, cropped.width]
    assert size == [100, 100]

def test_square_without_scaling(image):
    img = SmartCropper(image)
    squared = img.smart_square()
    assert squared.height == squared.width

def test_smart_crop_and_scale(image):
    img = SmartCropper(image)
    cropped = img.smart_crop_and_scale(100, 100)
    size = [cropped.height, cropped.width]
    assert size == [100,100]

def test_smart_crop_small_images(twenty_twenty):
    img = SmartCropper(twenty_twenty)
    cropped = img.smart_crop(100, 100)
    expected = [twenty_twenty.height, twenty_twenty.width]
    actual = [cropped.height, cropped.width]
    assert expected == actual

def test_smart_crop_one_pixel_slice(twenty_twenty):
    img = SmartCropper(twenty_twenty)
    cropped = img.smart_crop(19, 19)
    size = [cropped.height, cropped.width]
    assert size == [19, 19]

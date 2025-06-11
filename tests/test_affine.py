import numpy as np
import pytest
from plugins.Affine.Affine import Affine, AffineError

class DummyMask:
    def __init__(self, shape=(100, 100, 3)):
        self.img = np.ones(shape, dtype=np.uint8) * 255

@pytest.fixture
def affine():
    return Affine()

def test_affine_error_str():
    err = AffineError("fail", 2)
    assert "fail" in str(err)
    assert "Affine error Code: 2" in str(err)

def test_preprocess_img_gray():
    img = np.ones((10, 10, 3), dtype=np.uint8) * 128
    out = Affine._preprocess_img(img)
    assert out.shape == (10, 10)
    assert out.dtype == np.uint8

def test_preprocess_mask_gray():
    mask = np.ones((10, 10, 3), dtype=np.uint8) * 128
    out = Affine._preprocess_mask(mask)
    assert out.shape == (10, 10)
    assert out.dtype == np.uint8

def test_manual_transform_and_coords(affine):
    src = [(0,0), (1,0), (1,1), (0,1)]
    dst = [(10,10), (20,10), (20,20), (10,20)]
    img = np.zeros((30,30,3), dtype=np.uint8)
    mask = np.zeros((30,30,3), dtype=np.uint8)
    affine.manual_transform(src, dst, img, mask)
    assert affine.A.shape == (3,3)
    # Test coords
    x, y = affine.coords((0.5, 0.5))
    assert 10 <= x <= 20
    assert 10 <= y <= 20

def test_coords_no_transform(affine):
    with pytest.raises(AffineError):
        affine.coords((1,1))

def test_try_match_not_enough_matches(affine):
    # Use blank images to force not enough matches
    img = np.zeros((50,50,3), dtype=np.uint8)
    mask = np.zeros((50,50,3), dtype=np.uint8)
    affine.internal_mask = mask
    with pytest.raises(AffineError):
        affine.try_match(img)

def test_draw_keypoints_no_affine(affine):
    with pytest.raises(AffineError):
        affine.draw_keypoints()

def test_load_image_and_update_internal_mask(affine, tmp_path):
    import cv2
    img = np.ones((10,10,3), dtype=np.uint8) * 127
    path = tmp_path / "test.png"
    cv2.imwrite(str(path), img)
    loaded, filename = affine._load_image(str(path))
    assert loaded.shape == (10,10,3)
    mask = affine.update_interal_mask(str(path))
    assert mask.shape == (10,10,3)


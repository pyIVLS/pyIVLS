import pytest
from unittest.mock import MagicMock, patch
from plugins.VenusUSB2.VenusUSB2 import VenusUSB2, venusStatus

def test_venusstatus_str():
    err = venusStatus("Test error", 2)
    assert "Test error" in str(err)
    assert "VenusUSB error Code: 2" in str(err)

def test_open_success():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.isOpened.return_value = True
    v.cap.open.return_value = True
    v.cap.set.return_value = True
    status = v.open(source="dummy", exposure=10)
    assert status[0] == 0

def test_open_failure():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.isOpened.return_value = False
    v.cap.open.return_value = False
    status = v.open(source="dummy", exposure=10)
    assert status[0] == 4

def test_set_exposure_success():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.set.return_value = True
    result = v.set_exposure(10)
    assert result is None

def test_set_exposure_failure():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.set.return_value = False
    result = v.set_exposure(10)
    assert result[0] == 4

def test_close():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.close()
    v.cap.release.assert_called_once()

def test_capture_image_opened():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.isOpened.return_value = True
    v.cap.read.side_effect = [(True, "frame")] * v.bufferSize + [(True, "frame")]
    with patch("cv2.cvtColor", return_value="rgb_frame"):
        img = v.capture_image("src", 10)
        assert img == "rgb_frame"

def test_capture_image_not_opened_success():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.isOpened.return_value = False
    v.open = MagicMock(return_value=[0, {"Error message": "OK"}])
    v.cap.read.side_effect = [(True, "frame")] * v.bufferSize + [(True, "frame")]
    v.close = MagicMock()
    with patch("cv2.cvtColor", return_value="rgb_frame"):
        img = v.capture_image("src", 10)
        assert img == "rgb_frame"
        v.close.assert_called_once()

def test_capture_image_not_opened_failure():
    v = VenusUSB2()
    v.cap = MagicMock()
    v.cap.isOpened.return_value = False
    v.open = MagicMock(return_value=[4, {"Error message": "fail"}])
    with pytest.raises(venusStatus) as excinfo:
        v.capture_image("src", 10)
    assert "fail" in str(excinfo.value)
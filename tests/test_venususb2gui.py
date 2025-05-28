import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
import sys

# Import the class under test
sys.modules["VenusUSB2"] = MagicMock()
sys.modules["VenusUSB2"].VenusUSB2 = MagicMock()
sys.modules["VenusUSB2"].venusStatus = Exception

from plugins.VenusUSB2.VenusUSB2GUI import VenusUSB2GUI

@pytest.fixture(scope="module")
def app():
    # Needed for QWidget-based tests
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def gui():
    with patch("plugins.VenusUSB2.VenusUSB2GUI.uic.loadUi") as mock_loadUi:
        # Mock the UI widgets and their children
        mock_settings = MagicMock()
        mock_preview = MagicMock()
        mock_settings.findChild.return_value = MagicMock()
        mock_settings.cameraPreview = MagicMock()
        mock_settings.saveButton = MagicMock()
        mock_settings.directoryButton = MagicMock()
        mock_settings.exposure = MagicMock()
        mock_settings.cameraSource = MagicMock()
        mock_settings.lineEdit_path = MagicMock()
        mock_settings.lineEdit_filename = MagicMock()
        mock_settings.connectionIndicator = MagicMock()
        mock_settings.sourceBox = MagicMock()
        mock_preview.previewLabel = MagicMock()
        mock_loadUi.side_effect = [mock_settings, mock_preview]
        gui = VenusUSB2GUI()
        gui.settingsWidget = mock_settings
        gui.previewWidget = mock_preview
        gui.camera = MagicMock()
        gui.exposure = MagicMock()
        gui.preview_label = MagicMock()
        return gui

def test_parse_settings_preview(gui):
    gui.exposure.currentText.return_value = "100"
    gui.settingsWidget.cameraSource.text.return_value = "test_source"
    status = gui._parse_settings_preview()
    assert status[0] == 0
    assert gui.settings["exposure"] == 100
    assert gui.settings["source"] == "test_source"

def test_camera_open_calls_camera_open(gui):
    gui.settings = {"source": "src", "exposure": 50}
    gui.camera.open.return_value = (0, "ok")
    result = gui.camera_open()
    gui.camera.open.assert_called_with(source="src", exposure=50)
    assert result == (0, "ok")

def test_camera_close_calls_camera_close(gui):
    gui.camera_close()
    gui.camera.close.assert_called_once()

def test_camera_capture_image_success(gui):
    gui._parse_settings_preview = MagicMock(return_value=(0, {"source": "src", "exposure": 10}))
    gui.camera.capture_image.return_value = "image"
    img = gui.camera_capture_image()
    gui.camera.capture_image.assert_called_with("src", 10, full_size=False)
    assert img == "image"

def test_camera_capture_image_parse_fail(gui):
    gui._parse_settings_preview = MagicMock(return_value=(1, {}))
    gui.log_message = MagicMock()
    img = gui.camera_capture_image()
    assert img is None
    gui.log_message.emit.assert_called()

def test_parseSaveData_invalid_dir(gui):
    gui.settingsWidget.lineEdit_path.text.return_value = "not_a_dir"
    gui.settingsWidget.lineEdit_filename.text.return_value = "file"
    with patch("os.path.isdir", return_value=False):
        gui.log_message = MagicMock()
        status, info = gui._parseSaveData()
        assert status == 1
        assert "address string should point to a valid directory" in info["Error message"]

def test_parseSaveData_invalid_filename(gui):
    gui.settingsWidget.lineEdit_path.text.return_value = "C:\\"
    gui.settingsWidget.lineEdit_filename.text.return_value = "bad/file"
    with patch("os.path.isdir", return_value=True), \
         patch("plugins.VenusUSB2.VenusUSB2GUI.is_valid_filename", return_value=False):
        gui.log_message = MagicMock()
        gui.info_message = MagicMock()
        status, info = gui._parseSaveData()
        assert status == 1
        assert "filename is not valid" in info["Error message"]
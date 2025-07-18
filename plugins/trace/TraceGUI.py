import os
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QFileDialog, QCheckBox, QPlainTextEdit, QSpinBox


class TraceGui(QObject):

    def __init__(self):
        super().__init__()
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.current_log_level = "DEBUG"
        self.log_file_path = ""
        self.last_pos = 0
        self._create_settings_widget()
        self._create_mdi_widget()
        self._connect_signals()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_log_view)

    def _create_settings_widget(self):
        self.settingsWidget = QWidget()
        layout = QVBoxLayout()
        self.settingsWidget.setLayout(layout)
        self.logFileLabel = QLabel("Log file:")
        self.logFilePathEdit = QLabel("")
        self.browseButton = QPushButton("Browse...")
        self.levelLabel = QLabel("Log level:")
        self.levelCombo = QComboBox()
        self.levelCombo.addItems(self.log_levels)
        self.sessionOnlyCheck = QCheckBox("Show only current session")
        self.lineCountLabel = QLabel("Max displayed lines:")
        self.lineCountSpin = QSpinBox()
        self.lineCountSpin.setRange(100, 100000)
        layout.addWidget(self.logFileLabel)
        layout.addWidget(self.logFilePathEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.levelLabel)
        layout.addWidget(self.levelCombo)
        layout.addWidget(self.sessionOnlyCheck)
        layout.addWidget(self.lineCountLabel)
        layout.addWidget(self.lineCountSpin)

    def _create_mdi_widget(self):
        self.MDIWidget = QWidget()
        layout = QVBoxLayout()
        self.MDIWidget.setLayout(layout)
        self.logView = QPlainTextEdit()
        self.logView.setReadOnly(True)
        layout.addWidget(self.logView)

    def _connect_signals(self):
        self.browseButton.clicked.connect(self._browse_log_file)
        self.levelCombo.currentTextChanged.connect(self._set_log_level)
        self.sessionOnlyCheck.toggled.connect(self._set_session_only)
        self.lineCountSpin.valueChanged.connect(self._set_line_count)

    def _browse_log_file(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select log file", os.getcwd(), "Log Files (*.log);;All Files (*)")
        if file_path:
            self.log_file_path = file_path
            self.logFilePathEdit.setText(file_path)
            self.last_pos = 0
            self.logView.clear()
            self.timer.start(1000)  # Poll every second

    def _set_log_level(self, level):
        self.current_log_level = level
        self.last_pos = 0
        self.logView.clear()
        self._update_log_view()

    def _set_session_only(self, checked):
        self.last_pos = 0
        self.logView.clear()
        self._update_log_view()

    def _set_line_count(self, value):
        self.MAX_LOG_LINES = value
        self.logView.clear()
        self._update_log_view()

    def _update_log_view(self):
        if not self.log_file_path or not os.path.exists(self.log_file_path):
            return
        # Always read the last MAX_LOG_LINES from the file for robust updates
        with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
        # Remove empty lines and filter by log level
        filtered_lines = [line for line in all_lines if line.strip() and self._line_passes_filter(line)]
        # Limit to last MAX_LOG_LINES
        if len(filtered_lines) > self.MAX_LOG_LINES:
            filtered_lines = filtered_lines[-self.MAX_LOG_LINES:]
        # If session only, cut off at the session marker (but only within the last MAX_LOG_LINES)
        if self.sessionOnlyCheck.isChecked():
            session_marker = "pyIVLS session started"
            for i in range(len(filtered_lines)-1, -1, -1):
                if session_marker in filtered_lines[i]:
                    filtered_lines = filtered_lines[i:]
                    break
        # Print to the log view
        self.logView.setPlainText("".join(filtered_lines))
        self.logView.moveCursor(QTextCursor.MoveOperation.End)
        # Reset last_pos so that a new browse/settings change will reload from the end
        self.last_pos = 0

    def _line_passes_filter(self, line):
        # Simple filter: expects log lines to contain the level as a word
        levels = self.log_levels
        min_level_idx = levels.index(self.current_log_level)
        for idx, level in enumerate(levels):
            if level in line:
                return idx >= min_level_idx
        return False

    def parse_settings_widget(self):
        """Parse the current settings from the widget and return as a dict."""
        # nothing to check, just return
        settings = {
            "log_file": self.logFilePathEdit.text(),
            "show_current_session": str(self.sessionOnlyCheck.isChecked()),
            "show_level": self.levelCombo.currentText(),
            "display_line_count": str(self.lineCountSpin.value()),
            "poll_frequency": "1000" 
        }
        return 0, settings

    def set_settings_from_plugin_data(self, plugin_data):
        """Initialize the widget from .ini file settings.

        Args:
            plugin_data (dict): The plugin data just for the trace plugin.
        """
        settings = plugin_data["settings"]
        # All settings must be present, otherwise raise KeyError
        self.logFilePathEdit.setText(settings["log_file"])
        self.sessionOnlyCheck.setChecked(settings["show_current_session"] == "True")
        level = settings["show_level"]
        idx = self.levelCombo.findText(level)
        if idx != -1:
            self.levelCombo.setCurrentIndex(idx)
        self.lineCountSpin.setValue(int(settings["display_line_count"]))
        # poll_frequency is not used in the UI, but could be set here if needed
        # Automatically open the stored logfile if present
        log_file = settings["log_file"]
        if log_file and os.path.exists(log_file):
            self.log_file_path = log_file
            self.last_pos = 0
            self.logView.clear()
            self._update_log_view()
            self.timer.start(int(settings["poll_frequency"]))  # Ensure timer is started for live updates

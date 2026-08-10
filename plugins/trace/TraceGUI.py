import os

from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlighting_rules = []

        # Define formats for different log levels
        debug_format = QTextCharFormat()
        debug_format.setForeground(QColor("blue"))
        self.highlighting_rules.append(("DEBUG", debug_format))

        info_format = QTextCharFormat()
        info_format.setForeground(QColor("green"))
        self.highlighting_rules.append(("INFO", info_format))

        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor("orange"))
        self.highlighting_rules.append(("WARNING", warning_format))

        error_format = QTextCharFormat()
        error_format.setForeground(QColor("red"))
        self.highlighting_rules.append(("ERROR", error_format))

        critical_format = QTextCharFormat()
        critical_format.setForeground(QColor("darkred"))
        self.highlighting_rules.append(("CRITICAL", critical_format))

        # Format for session start
        session_format = QTextCharFormat()
        session_format.setBackground(QColor("yellow"))
        session_format.setForeground(QColor("black"))
        self.highlighting_rules.append(("pyIVLS session started", session_format))

    def highlightBlock(self, text):
        text = str(text)
        for pattern, fmt in self.highlighting_rules:
            start_index = text.find(pattern)
            while start_index != -1:
                self.setFormat(start_index, len(pattern), fmt)
                start_index = text.find(pattern, start_index + len(pattern))


class TraceGui(QObject):
    def __init__(self):
        super().__init__()
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.current_log_level = "DEBUG"
        self.log_file_path = ""
        self.last_pos = 0
        self.MAX_LOG_LINES = 1000  # Initialize with default value
        self._create_settings_widget()
        self._create_mdi_widget()
        self._connect_signals()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_log_view)
        self.highlighter = LogHighlighter(self.logView.document())

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
        self.liveUpdateCheck = QCheckBox("Live update")
        self.liveUpdateCheck.setChecked(True)

        layout.addWidget(self.logFileLabel)
        layout.addWidget(self.logFilePathEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.levelLabel)
        layout.addWidget(self.levelCombo)
        layout.addWidget(self.sessionOnlyCheck)
        layout.addWidget(self.lineCountLabel)
        layout.addWidget(self.lineCountSpin)
        layout.addWidget(self.liveUpdateCheck)

    def _create_mdi_widget(self):
        self.MDIWidget = QWidget()
        # Set size policy to expand in both directions
        self.MDIWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better space usage
        self.MDIWidget.setLayout(layout)

        self.logView = QPlainTextEdit()
        self.logView.setReadOnly(True)
        # Set size policy to expand and take all available space
        self.logView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Disable automatic scrolling behaviors
        self.logView.setCenterOnScroll(False)

        layout.addWidget(self.logView)

    def _connect_signals(self):
        self.browseButton.clicked.connect(self._browse_log_file)
        self.levelCombo.currentTextChanged.connect(self._set_log_level)
        self.sessionOnlyCheck.toggled.connect(self._set_session_only)
        self.lineCountSpin.valueChanged.connect(self._set_line_count)
        self.liveUpdateCheck.toggled.connect(self._set_live_update)

    def _set_live_update(self, checked):
        if checked:
            if self.log_file_path and os.path.exists(self.log_file_path):
                self.timer.start(1000)
        else:
            self.timer.stop()

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
        # Don't clear - let _update_log_view handle content update while preserving scroll
        self._update_log_view()

    def _set_session_only(self, checked):
        self.last_pos = 0
        # Don't clear - let _update_log_view handle content update while preserving scroll
        self._update_log_view()

    def _set_line_count(self, value):
        self.MAX_LOG_LINES = value
        # Don't clear - let _update_log_view handle content update while preserving scroll
        self._update_log_view()

    def _update_log_view(self):
        if not self.log_file_path or not os.path.exists(self.log_file_path):
            return

        # read file
        with open(self.log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
        # Remove empty lines and filter by log level
        filtered_lines = [line for line in all_lines if line.strip() and self._line_passes_filter(line)]
        # Limit to last MAX_LOG_LINES
        if len(filtered_lines) > self.MAX_LOG_LINES:
            filtered_lines = filtered_lines[-self.MAX_LOG_LINES :]
        # If session only, cut off at the session marker (but only within the last MAX_LOG_LINES)
        if self.sessionOnlyCheck.isChecked():
            session_marker = "pyIVLS session started"
            for i in range(len(filtered_lines) - 1, -1, -1):
                if session_marker in filtered_lines[i]:
                    filtered_lines = filtered_lines[i:]
                    break

        current_content = "".join(filtered_lines)
        previous_content = self.logView.toPlainText()

        # Only update if content actually changed
        if current_content != previous_content:
            # Store the current cursor position and scroll position
            cursor = self.logView.textCursor()
            cursor_position = cursor.position()
            scrollbar = self.logView.verticalScrollBar()
            scroll_value = scrollbar.value() if scrollbar is not None else 0

            # Block signals to prevent automatic scrolling during text update
            self.logView.blockSignals(True)

            try:
                # Update the content
                self.logView.setPlainText(current_content)

                # Restore cursor position (but make sure it's not beyond the new text length)
                new_text_length = len(current_content)
                cursor_position = min(cursor_position, new_text_length)

                cursor = self.logView.textCursor()
                cursor.setPosition(cursor_position)
                self.logView.setTextCursor(cursor)

                # Restore scroll position
                if scrollbar is not None:
                    scrollbar.setValue(scroll_value)

            finally:
                # Re-enable signals
                self.logView.blockSignals(False)

        # Reset last_pos so that a new browse/settings change will reload from the end
        self.last_pos = 0

    def _line_passes_filter(self, line):
        # Simple filter: check if line contains the current log level
        levels = self.log_levels
        min_level_idx = levels.index(self.current_log_level)
        for idx, level in enumerate(levels):
            if level in line:
                return idx >= min_level_idx
        return False

    def parse_settings_widget(self):
        """Parse the current settings from the widget and return as a dict."""
        settings = {
            "log_file": self.logFilePathEdit.text(),
            "show_current_session": str(self.sessionOnlyCheck.isChecked()),
            "show_level": self.levelCombo.currentText(),
            "display_line_count": str(self.lineCountSpin.value()),
            "poll_frequency": "1000",  # default, not possible to set in UI
            "live_update": str(self.liveUpdateCheck.isChecked()),
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
        self.liveUpdateCheck.setChecked(settings.get("live_update", "True") == "True")


        # Automatically open the stored logfile if present
        log_file = settings["log_file"]
        if log_file and os.path.exists(log_file):
            self.log_file_path = log_file
            self.last_pos = 0
            self.logView.clear()
            self._update_log_view()
            if self.liveUpdateCheck.isChecked():
                self.timer.start(int(settings["poll_frequency"]))  # Start update timer
            else:
                self.timer.stop()

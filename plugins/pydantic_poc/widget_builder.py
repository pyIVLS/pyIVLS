from typing import Literal, get_args, get_origin

from annotated_types import Ge, Gt, Le, Lt
from pydantic import BaseModel, DirectoryPath
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget


class WidgetAdapter:
    @staticmethod
    def get(widget: QtWidgets.QWidget):
        if isinstance(widget, QtWidgets.QLineEdit):
            return widget.text()
        elif isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QtWidgets.QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QtWidgets.QComboBox):
            return widget.currentText()
        else:
            raise TypeError(f"Unsupported widget type: {type(widget)}")

    @staticmethod
    def set(widget: QtWidgets.QWidget, value):
        if isinstance(widget, QtWidgets.QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QtWidgets.QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QtWidgets.QDoubleSpinBox):
            widget.setValue(float(value))
        elif isinstance(widget, QtWidgets.QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QtWidgets.QComboBox):
            index = widget.findText(str(value))
            if index != -1:
                widget.setCurrentIndex(index)
            else:
                raise ValueError(f"Value '{value}' not found in QComboBox for field: {value}")
        else:
            raise TypeError(f"Unsupported widget type: {type(widget)}")


class pyIVLS_settings_widget(QWidget):
    def __init__(self, settings_model: type[BaseModel], parent: QtWidgets.QWidget | None = None, name="Settings"):
        super().__init__(parent)
        self.settings_model = settings_model
        self.setwid = self
        self._build_form()
        self.setObjectName(name)
        self.setWindowTitle(name)
        test_enum = self.widgets.get("test_enum")
        if isinstance(test_enum, QtWidgets.QComboBox):
            test_enum.activated.connect(self.test_slot)

    def test_slot(self):
        print("kutittaa")

    def _get_widget_value(self, field_name: str):
        widget = self.findChild(QtWidgets.QWidget, field_name)
        if widget is None:
            raise ValueError(f"No widget found for field: {field_name}")
        return WidgetAdapter.get(widget)

    def to_model(self) -> BaseModel:
        """Get an instance of the pydantic base model"""
        return self.settings_model(**{name: self._get_widget_value(name) for name in self.settings_model.model_fields})

    def _set_widget_value(self, field_name: str, value):
        widget = self.findChild(QtWidgets.QWidget, field_name)
        if widget is None:
            raise ValueError(f"No widget found for field: {field_name}")
        WidgetAdapter.set(widget, value)

    def from_model(self, model_instance: BaseModel):
        """Set the values of the widgets based on an instance of the pydantic base model"""
        dict = model_instance.model_dump()
        for name, value in dict.items():
            self._set_widget_value(name, value)

    def _build_form(self):
        self.widgets = {}

        layout = QtWidgets.QFormLayout(self)

        for name, field in self.settings_model.model_fields.items():
            label = FormHelpers.create_label(name, field)
            widget = FormHelpers.create_widget(field)

            FormHelpers.apply_constraints(widget, field)
            FormHelpers.apply_default(widget, field)
            FormHelpers.apply_tooltips(label, widget, field)

            widget.setObjectName(name)
            self.widgets[name] = widget

            layout.addRow(label, widget)

        self.setLayout(layout)
        return self


class FormHelpers:
    @staticmethod
    def create_label(name, field):
        text = field.title or name.replace("_", " ").title()
        return QtWidgets.QLabel(text)

    @staticmethod
    def create_widget(field):

        annotation = field.annotation
        origin = get_origin(annotation)

        if origin is Literal:
            combo = QtWidgets.QComboBox()

            for value in get_args(annotation):
                combo.addItem(str(value))

            return combo

        if annotation is str:
            return QtWidgets.QLineEdit()

        if annotation is int:
            return QtWidgets.QSpinBox()

        if annotation is float:
            return QtWidgets.QDoubleSpinBox()

        if annotation is bool:
            return QtWidgets.QCheckBox()

        if annotation is DirectoryPath:
            return QtWidgets.QLineEdit()

        return QtWidgets.QLineEdit()

    @staticmethod
    def apply_constraints(widget, field):

        minimum = None
        maximum = None

        for meta in field.metadata:
            if isinstance(meta, Ge):
                minimum = meta.ge

            elif isinstance(meta, Gt):
                if isinstance(widget, QtWidgets.QSpinBox):
                    minimum = meta.gt + 1
                else:
                    minimum = meta.gt

            elif isinstance(meta, Le):
                maximum = meta.le

            elif isinstance(meta, Lt):
                if isinstance(widget, QtWidgets.QSpinBox):
                    maximum = meta.lt - 1
                else:
                    maximum = meta.lt

        if minimum is not None and isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            widget.setMinimum(minimum)

        if maximum is not None and isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            widget.setMaximum(maximum)

    @staticmethod
    def apply_default(widget, field):

        if field.default is None:
            return

        value = field.default

        if isinstance(widget, QtWidgets.QLineEdit):
            widget.setText(str(value))

        elif isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            widget.setValue(value)

        elif isinstance(widget, QtWidgets.QCheckBox):
            widget.setChecked(value)

        elif isinstance(widget, QtWidgets.QComboBox):
            index = widget.findText(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)

    @staticmethod
    def apply_tooltips(label, widget, field):

        if field.description is None:
            return

        label.setToolTip(field.description)
        widget.setToolTip(field.description)

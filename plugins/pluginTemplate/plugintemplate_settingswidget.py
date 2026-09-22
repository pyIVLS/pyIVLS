################################################################################
## Form generated from reading UI file 'pluginTemplate_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1128, 627)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1108, 607))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_dep = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_dep.setObjectName("groupBox_dep")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_dep)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.camlabel = QLabel(self.groupBox_dep)
        self.camlabel.setObjectName("camlabel")

        self.horizontalLayout.addWidget(self.camlabel)

        self.camBox = QComboBox(self.groupBox_dep)
        self.camBox.setObjectName("camBox")

        self.horizontalLayout.addWidget(self.camBox)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout.addWidget(self.groupBox_dep)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.combined_layout = QHBoxLayout()
        self.combined_layout.setObjectName("combined_layout")
        self.float_layout = QHBoxLayout()
        self.float_layout.setObjectName("float_layout")
        self.label_flot = QLabel(self.groupBox)
        self.label_flot.setObjectName("label_flot")

        self.float_layout.addWidget(self.label_flot)

        self.doubleSpinBox_float = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_float.setObjectName("doubleSpinBox_float")

        self.float_layout.addWidget(self.doubleSpinBox_float)

        self.label_floatUnit = QLabel(self.groupBox)
        self.label_floatUnit.setObjectName("label_floatUnit")

        self.float_layout.addWidget(self.label_floatUnit)

        self.combined_layout.addLayout(self.float_layout)

        self.integer_layout = QHBoxLayout()
        self.integer_layout.setObjectName("integer_layout")
        self.label_integer = QLabel(self.groupBox)
        self.label_integer.setObjectName("label_integer")

        self.integer_layout.addWidget(self.label_integer)

        self.spinBox_integer = QSpinBox(self.groupBox)
        self.spinBox_integer.setObjectName("spinBox_integer")

        self.integer_layout.addWidget(self.spinBox_integer)

        self.label_unitInteger = QLabel(self.groupBox)
        self.label_unitInteger.setObjectName("label_unitInteger")

        self.integer_layout.addWidget(self.label_unitInteger)

        self.combined_layout.addLayout(self.integer_layout)

        self.strLayout = QHBoxLayout()
        self.strLayout.setObjectName("strLayout")
        self.strLabel = QLabel(self.groupBox)
        self.strLabel.setObjectName("strLabel")

        self.strLayout.addWidget(self.strLabel)

        self.lineEdit_str = QLineEdit(self.groupBox)
        self.lineEdit_str.setObjectName("lineEdit_str")

        self.strLayout.addWidget(self.lineEdit_str)

        self.label_strUnit = QLabel(self.groupBox)
        self.label_strUnit.setObjectName("label_strUnit")

        self.strLayout.addWidget(self.label_strUnit)

        self.combined_layout.addLayout(self.strLayout)

        self.cat_layout = QHBoxLayout()
        self.cat_layout.setObjectName("cat_layout")
        self.label_cate = QLabel(self.groupBox)
        self.label_cate.setObjectName("label_cate")

        self.cat_layout.addWidget(self.label_cate)

        self.comboBox_categorical = QComboBox(self.groupBox)
        self.comboBox_categorical.setObjectName("comboBox_categorical")

        self.cat_layout.addWidget(self.comboBox_categorical)

        self.label_cateUnit = QLabel(self.groupBox)
        self.label_cateUnit.setObjectName("label_cateUnit")

        self.cat_layout.addWidget(self.label_cateUnit)

        self.combined_layout.addLayout(self.cat_layout)

        self.verticalLayout_2.addLayout(self.combined_layout)

        self.pushButton_doStuff = QPushButton(self.groupBox)
        self.pushButton_doStuff.setObjectName("pushButton_doStuff")

        self.verticalLayout_2.addWidget(self.pushButton_doStuff)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.verticalLayout.addWidget(self.groupBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Template settings widget", None))
        self.groupBox_dep.setTitle(QCoreApplication.translate("Form", "Dependencies", None))
        self.camlabel.setText(QCoreApplication.translate("Form", "Camera Plugin", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", "General", None))
        self.label_flot.setText(QCoreApplication.translate("Form", "Input for float", None))
        self.label_floatUnit.setText(QCoreApplication.translate("Form", "Float unit", None))
        self.label_integer.setText(QCoreApplication.translate("Form", "Input for integer", None))
        self.label_unitInteger.setText(QCoreApplication.translate("Form", "integer unit", None))
        self.strLabel.setText(QCoreApplication.translate("Form", "Input for string", None))
        self.label_strUnit.setText(QCoreApplication.translate("Form", "unit", None))
        self.label_cate.setText(QCoreApplication.translate("Form", "Input for categorical", None))
        self.label_cateUnit.setText(QCoreApplication.translate("Form", "Categorical Unit", None))
        self.pushButton_doStuff.setText(QCoreApplication.translate("Form", "Button", None))

    # retranslateUi

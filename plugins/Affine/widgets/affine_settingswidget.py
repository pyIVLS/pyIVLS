################################################################################
## Form generated from reading UI file 'Affine_settingsWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1231, 758)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1211, 738))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_general = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_general.setObjectName("groupBox_general")
        self.verticalLayout = QVBoxLayout(self.groupBox_general)
        self.verticalLayout.setObjectName("verticalLayout")
        self.maskBox = QGroupBox(self.groupBox_general)
        self.maskBox.setObjectName("maskBox")
        self.horizontalLayout_2 = QHBoxLayout(self.maskBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.maskButton = QPushButton(self.maskBox)
        self.maskButton.setObjectName("maskButton")

        self.horizontalLayout_2.addWidget(self.maskButton)

        self.label = QLabel(self.maskBox)
        self.label.setObjectName("label")

        self.horizontalLayout_2.addWidget(self.label)

        self.cameraComboBox = QComboBox(self.maskBox)
        self.cameraComboBox.setObjectName("cameraComboBox")

        self.horizontalLayout_2.addWidget(self.cameraComboBox)

        self.verticalLayout.addWidget(self.maskBox)

        self.affineBox = QGroupBox(self.groupBox_general)
        self.affineBox.setObjectName("affineBox")
        self.horizontalLayout = QHBoxLayout(self.affineBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.showButton = QPushButton(self.affineBox)
        self.showButton.setObjectName("showButton")

        self.horizontalLayout.addWidget(self.showButton)

        self.verticalLayout.addWidget(self.affineBox)

        self.groupBox = QGroupBox(self.groupBox_general)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.centerClicks = QCheckBox(self.groupBox)
        self.centerClicks.setObjectName("centerClicks")
        self.centerClicks.setChecked(True)

        self.horizontalLayout_3.addWidget(self.centerClicks)

        self.pointCount = QSpinBox(self.groupBox)
        self.pointCount.setObjectName("pointCount")
        self.pointCount.setMinimum(1)
        self.pointCount.setMaximum(4)

        self.horizontalLayout_3.addWidget(self.pointCount)

        self.pointName = QLineEdit(self.groupBox)
        self.pointName.setObjectName("pointName")

        self.horizontalLayout_3.addWidget(self.pointName)

        self.savePoints = QPushButton(self.groupBox)
        self.savePoints.setObjectName("savePoints")

        self.horizontalLayout_3.addWidget(self.savePoints)

        self.importPoints = QPushButton(self.groupBox)
        self.importPoints.setObjectName("importPoints")

        self.horizontalLayout_3.addWidget(self.importPoints)

        self.definedPoints = QListWidget(self.groupBox)
        self.definedPoints.setObjectName("definedPoints")
        self.definedPoints.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.definedPoints.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.horizontalLayout_3.addWidget(self.definedPoints)

        self.verticalLayout.addWidget(self.groupBox)

        self.verticalLayout_2.addWidget(self.groupBox_general)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "IR affine settings", None))
        self.groupBox_general.setTitle(QCoreApplication.translate("Form", "Coordinate conversion settings", None))
        self.maskBox.setTitle("")
        self.maskButton.setText(QCoreApplication.translate("Form", "upload mask", None))
        self.label.setText(QCoreApplication.translate("Form", "No mask loaded", None))
        self.affineBox.setTitle("")
        self.showButton.setText(QCoreApplication.translate("Form", "Match", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", "Mask measurement points", None))
        self.centerClicks.setText(QCoreApplication.translate("Form", "Center clicks on patch", None))
        # if QT_CONFIG(tooltip)
        self.pointName.setToolTip(QCoreApplication.translate("Form", "<html><head/><body><p>Enter name for set of points</p><p><br/></p></body></html>", None))
        # endif // QT_CONFIG(tooltip)
        self.pointName.setText(QCoreApplication.translate("Form", "Measurement point 1", None))
        self.savePoints.setText(QCoreApplication.translate("Form", "Write points to file", None))
        self.importPoints.setText(QCoreApplication.translate("Form", "Read points from file", None))

    # retranslateUi

################################################################################
## Form generated from reading UI file 'affinemove_Settings.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1002, 883)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 982, 863))
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.mmlay = QHBoxLayout()
        self.mmlay.setObjectName("mmlay")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")

        self.mmlay.addWidget(self.label_2)

        self.micromanipulatorBox = QComboBox(self.groupBox_2)
        self.micromanipulatorBox.setObjectName("micromanipulatorBox")

        self.mmlay.addWidget(self.micromanipulatorBox)

        self.horizontalLayout_6.addLayout(self.mmlay)

        self.poslay = QHBoxLayout()
        self.poslay.setObjectName("poslay")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")

        self.poslay.addWidget(self.label_3)

        self.positioningBox = QComboBox(self.groupBox_2)
        self.positioningBox.setObjectName("positioningBox")

        self.poslay.addWidget(self.positioningBox)

        self.horizontalLayout_6.addLayout(self.poslay)

        self.camlay = QHBoxLayout()
        self.camlay.setObjectName("camlay")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName("label")

        self.camlay.addWidget(self.label)

        self.cameraBox = QComboBox(self.groupBox_2)
        self.cameraBox.setObjectName("cameraBox")

        self.camlay.addWidget(self.cameraBox)

        self.horizontalLayout_6.addLayout(self.camlay)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.findSutter = QPushButton(self.groupBox_2)
        self.findSutter.setObjectName("findSutter")

        self.horizontalLayout_7.addWidget(self.findSutter)

        self.previewButton = QPushButton(self.groupBox_2)
        self.previewButton.setObjectName("previewButton")

        self.horizontalLayout_7.addWidget(self.previewButton)

        self.fetchMaskButton = QPushButton(self.groupBox_2)
        self.fetchMaskButton.setObjectName("fetchMaskButton")

        self.horizontalLayout_7.addWidget(self.fetchMaskButton)

        self.updateManipulatorsButton = QPushButton(self.groupBox_2)
        self.updateManipulatorsButton.setObjectName("updateManipulatorsButton")

        self.horizontalLayout_7.addWidget(self.updateManipulatorsButton)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.gridLayout_3.addWidget(self.groupBox_2, 4, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 264, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 7, 0, 1, 1)

        self.boundingBoxGroupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.boundingBoxGroupBox.setObjectName("boundingBoxGroupBox")
        self.verticalLayout_3 = QVBoxLayout(self.boundingBoxGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.manipulatorLabel = QLabel(self.boundingBoxGroupBox)
        self.manipulatorLabel.setObjectName("manipulatorLabel")

        self.horizontalLayout_4.addWidget(self.manipulatorLabel)

        self.manipulatorComboBox = QComboBox(self.boundingBoxGroupBox)
        self.manipulatorComboBox.setObjectName("manipulatorComboBox")

        self.horizontalLayout_4.addWidget(self.manipulatorComboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.setBoundingBoxButton = QPushButton(self.boundingBoxGroupBox)
        self.setBoundingBoxButton.setObjectName("setBoundingBoxButton")

        self.gridLayout_6.addWidget(self.setBoundingBoxButton, 0, 0, 1, 1)

        self.clearBoundingBoxButton = QPushButton(self.boundingBoxGroupBox)
        self.clearBoundingBoxButton.setObjectName("clearBoundingBoxButton")

        self.gridLayout_6.addWidget(self.clearBoundingBoxButton, 0, 1, 1, 1)

        self.refreshPositionsButton = QPushButton(self.boundingBoxGroupBox)
        self.refreshPositionsButton.setObjectName("refreshPositionsButton")

        self.gridLayout_6.addWidget(self.refreshPositionsButton, 1, 0, 1, 1)

        self.recalibrateManipulatorButton = QPushButton(self.boundingBoxGroupBox)
        self.recalibrateManipulatorButton.setObjectName("recalibrateManipulatorButton")

        self.gridLayout_6.addWidget(self.recalibrateManipulatorButton, 1, 1, 1, 1)

        self.verticalLayout_3.addLayout(self.gridLayout_6)

        self.goToClickButton = QPushButton(self.boundingBoxGroupBox)
        self.goToClickButton.setObjectName("goToClickButton")

        self.verticalLayout_3.addWidget(self.goToClickButton)

        self.gridLayout_3.addWidget(self.boundingBoxGroupBox, 0, 0, 1, 2)

        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pointsStatus = QLabel(self.groupBox)
        self.pointsStatus.setObjectName("pointsStatus")

        self.horizontalLayout_3.addWidget(self.pointsStatus)

        self.pointsIndicator = QLabel(self.groupBox)
        self.pointsIndicator.setObjectName("pointsIndicator")
        self.pointsIndicator.setMaximumSize(QSize(20, 20))
        self.pointsIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_3.addWidget(self.pointsIndicator)

        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mmStatus = QLabel(self.groupBox)
        self.mmStatus.setObjectName("mmStatus")

        self.horizontalLayout.addWidget(self.mmStatus)

        self.mmIndicator = QLabel(self.groupBox)
        self.mmIndicator.setObjectName("mmIndicator")
        self.mmIndicator.setMaximumSize(QSize(20, 20))
        self.mmIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout.addWidget(self.mmIndicator)

        self.horizontalLayout_5.addLayout(self.horizontalLayout)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.sampleStatus = QLabel(self.groupBox)
        self.sampleStatus.setObjectName("sampleStatus")

        self.horizontalLayout_2.addWidget(self.sampleStatus)

        self.sampleIndicator = QLabel(self.groupBox)
        self.sampleIndicator.setObjectName("sampleIndicator")
        self.sampleIndicator.setMaximumSize(QSize(20, 20))
        self.sampleIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_2.addWidget(self.sampleIndicator)

        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer)

        self.gridLayout_3.addWidget(self.groupBox, 6, 0, 1, 2)

        self.groupBox_4 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.showBoundingBoxesCheckBox = QCheckBox(self.groupBox_4)
        self.showBoundingBoxesCheckBox.setObjectName("showBoundingBoxesCheckBox")
        self.showBoundingBoxesCheckBox.setChecked(False)

        self.horizontalLayout_8.addWidget(self.showBoundingBoxesCheckBox)

        self.showTargetsCheckBox = QCheckBox(self.groupBox_4)
        self.showTargetsCheckBox.setObjectName("showTargetsCheckBox")

        self.horizontalLayout_8.addWidget(self.showTargetsCheckBox)

        self.showPositionsCheckBox = QCheckBox(self.groupBox_4)
        self.showPositionsCheckBox.setObjectName("showPositionsCheckBox")

        self.horizontalLayout_8.addWidget(self.showPositionsCheckBox)

        self.horizontalSpacer_2 = QSpacerItem(291, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_2)

        self.gridLayout_3.addWidget(self.groupBox_4, 1, 0, 1, 2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "AffineMove settings", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", "Dependencies", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Micromanipulator plugin", None))
        self.micromanipulatorBox.setPlaceholderText(QCoreApplication.translate("Form", "Micromanipulator", None))
        self.label_3.setText(QCoreApplication.translate("Form", "Positioning plugin", None))
        self.positioningBox.setPlaceholderText(QCoreApplication.translate("Form", "Positioning", None))
        self.label.setText(QCoreApplication.translate("Form", "Camera plugin", None))
        self.cameraBox.setPlaceholderText(QCoreApplication.translate("Form", "Camera", None))
        self.findSutter.setText(QCoreApplication.translate("Form", "Locate Micromanipulator", None))
        self.previewButton.setText(QCoreApplication.translate("Form", "Preview camera", None))
        self.fetchMaskButton.setText(QCoreApplication.translate("Form", "Fetch positioning data", None))
        self.updateManipulatorsButton.setText(QCoreApplication.translate("Form", "update Manipulator list", None))
        self.boundingBoxGroupBox.setTitle(QCoreApplication.translate("Form", "Manipulator Bounding Boxes", None))
        self.manipulatorLabel.setText(QCoreApplication.translate("Form", "Manipulator:", None))
        # if QT_CONFIG(tooltip)
        self.manipulatorComboBox.setToolTip(QCoreApplication.translate("Form", "Select which manipulator to set bounding box for", None))
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.setBoundingBoxButton.setToolTip(QCoreApplication.translate("Form", "Click 4 points on the camera view to define a bounding box", None))
        # endif // QT_CONFIG(tooltip)
        self.setBoundingBoxButton.setText(QCoreApplication.translate("Form", "Set Bounding Box", None))
        # if QT_CONFIG(tooltip)
        self.clearBoundingBoxButton.setToolTip(QCoreApplication.translate("Form", "Remove the bounding box for the selected manipulator", None))
        # endif // QT_CONFIG(tooltip)
        self.clearBoundingBoxButton.setText(QCoreApplication.translate("Form", "Clear Bounding Box", None))
        # if QT_CONFIG(tooltip)
        self.refreshPositionsButton.setToolTip(QCoreApplication.translate("Form", "Update cached manipulator positions from hardware", None))
        # endif // QT_CONFIG(tooltip)
        self.refreshPositionsButton.setText(QCoreApplication.translate("Form", "Refresh Positions", None))
        # if QT_CONFIG(tooltip)
        self.recalibrateManipulatorButton.setToolTip(QCoreApplication.translate("Form", "Recalibrate selected manipulator", None))
        # endif // QT_CONFIG(tooltip)
        self.recalibrateManipulatorButton.setText(QCoreApplication.translate("Form", "Recalibrate manipulator", None))
        self.goToClickButton.setText(QCoreApplication.translate("Form", "Go to clicked position", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", "Status", None))
        self.pointsStatus.setText(QCoreApplication.translate("Form", "Measurement points defined", None))
        self.pointsIndicator.setText("")
        self.mmStatus.setText(QCoreApplication.translate("Form", "Micromanipulators located", None))
        self.mmIndicator.setText("")
        self.sampleStatus.setText(QCoreApplication.translate("Form", "Sample located", None))
        self.sampleIndicator.setText("")
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", "Visualization", None))
        self.showBoundingBoxesCheckBox.setText(QCoreApplication.translate("Form", "Show bounding boxes on camera view", None))
        self.showTargetsCheckBox.setText(QCoreApplication.translate("Form", "Show targets on camera view", None))
        self.showPositionsCheckBox.setText(QCoreApplication.translate("Form", "Show probe positions on camera view", None))

    # retranslateUi

################################################################################
## Form generated from reading UI file 'touchDetect_Settings.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout, QWidget


class Ui_Form:
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(893, 551)
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
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 879, 537))
        self.verticalLayout_6 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.smuLay = QHBoxLayout()
        self.smuLay.setObjectName("smuLay")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName("label")

        self.smuLay.addWidget(self.label)

        self.smuBox = QComboBox(self.scrollAreaWidgetContents)
        self.smuBox.setObjectName("smuBox")

        self.smuLay.addWidget(self.smuBox)

        self.horizontalLayout.addLayout(self.smuLay)

        self.mmLay = QHBoxLayout()
        self.mmLay.setObjectName("mmLay")
        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName("label_2")

        self.mmLay.addWidget(self.label_2)

        self.micromanipulatorBox = QComboBox(self.scrollAreaWidgetContents)
        self.micromanipulatorBox.setObjectName("micromanipulatorBox")

        self.mmLay.addWidget(self.micromanipulatorBox)

        self.horizontalLayout.addLayout(self.mmLay)

        self.condetLay = QHBoxLayout()
        self.condetLay.setObjectName("condetLay")
        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName("label_3")

        self.condetLay.addWidget(self.label_3)

        self.condetBox = QComboBox(self.scrollAreaWidgetContents)
        self.condetBox.setObjectName("condetBox")

        self.condetLay.addWidget(self.condetBox)

        self.horizontalLayout.addLayout(self.condetLay)

        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.heightLay = QHBoxLayout()
        self.heightLay.setObjectName("heightLay")
        self.label_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName("label_4")

        self.heightLay.addWidget(self.label_4)

        self.spectro_height = QSpinBox(self.scrollAreaWidgetContents)
        self.spectro_height.setObjectName("spectro_height")
        self.spectro_height.setMaximum(25000)
        self.spectro_height.setSingleStep(100)

        self.heightLay.addWidget(self.spectro_height)

        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName("label_5")

        self.heightLay.addWidget(self.label_5)

        self.horizontalLayout_11.addLayout(self.heightLay)

        self.onSeqFailLay = QHBoxLayout()
        self.onSeqFailLay.setObjectName("onSeqFailLay")
        self.label_18 = QLabel(self.scrollAreaWidgetContents)
        self.label_18.setObjectName("label_18")

        self.onSeqFailLay.addWidget(self.label_18)

        self.comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")

        self.onSeqFailLay.addWidget(self.comboBox)

        self.horizontalLayout_11.addLayout(self.onSeqFailLay)

        self.verticalLayout_6.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.strideLay = QHBoxLayout()
        self.strideLay.setObjectName("strideLay")
        self.label_6 = QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName("label_6")

        self.strideLay.addWidget(self.label_6)

        self.stride = QSpinBox(self.scrollAreaWidgetContents)
        self.stride.setObjectName("stride")
        self.stride.setMinimum(1)
        self.stride.setMaximum(50)

        self.strideLay.addWidget(self.stride)

        self.label_7 = QLabel(self.scrollAreaWidgetContents)
        self.label_7.setObjectName("label_7")

        self.strideLay.addWidget(self.label_7)

        self.horizontalLayout_6.addLayout(self.strideLay)

        self.sampleWidthLay = QHBoxLayout()
        self.sampleWidthLay.setObjectName("sampleWidthLay")
        self.label_8 = QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName("label_8")

        self.sampleWidthLay.addWidget(self.label_8)

        self.sample_width = QSpinBox(self.scrollAreaWidgetContents)
        self.sample_width.setObjectName("sample_width")
        self.sample_width.setMaximum(400)

        self.sampleWidthLay.addWidget(self.sample_width)

        self.label_9 = QLabel(self.scrollAreaWidgetContents)
        self.label_9.setObjectName("label_9")

        self.sampleWidthLay.addWidget(self.label_9)

        self.horizontalLayout_6.addLayout(self.sampleWidthLay)

        self.verticalLayout_6.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.statusbox = QGroupBox(self.scrollAreaWidgetContents)
        self.statusbox.setObjectName("statusbox")
        self.verticalLayout_5 = QVBoxLayout(self.statusbox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.mmStatusLay = QHBoxLayout()
        self.mmStatusLay.setObjectName("mmStatusLay")
        self.sampleStatus = QLabel(self.statusbox)
        self.sampleStatus.setObjectName("sampleStatus")

        self.mmStatusLay.addWidget(self.sampleStatus)

        self.mmIndicator = QLabel(self.statusbox)
        self.mmIndicator.setObjectName("mmIndicator")
        self.mmIndicator.setMaximumSize(QSize(20, 20))
        self.mmIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.mmStatusLay.addWidget(self.mmIndicator)

        self.verticalLayout_5.addLayout(self.mmStatusLay)

        self.smuStatusLay = QHBoxLayout()
        self.smuStatusLay.setObjectName("smuStatusLay")
        self.mmStatus = QLabel(self.statusbox)
        self.mmStatus.setObjectName("mmStatus")

        self.smuStatusLay.addWidget(self.mmStatus)

        self.smuIndicator = QLabel(self.statusbox)
        self.smuIndicator.setObjectName("smuIndicator")
        self.smuIndicator.setMaximumSize(QSize(20, 20))
        self.smuIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.smuStatusLay.addWidget(self.smuIndicator)

        self.verticalLayout_5.addLayout(self.smuStatusLay)

        self.condetStatusLay = QHBoxLayout()
        self.condetStatusLay.setObjectName("condetStatusLay")
        self.pointsStatus = QLabel(self.statusbox)
        self.pointsStatus.setObjectName("pointsStatus")

        self.condetStatusLay.addWidget(self.pointsStatus)

        self.conIndicator = QLabel(self.statusbox)
        self.conIndicator.setObjectName("conIndicator")
        self.conIndicator.setMaximumSize(QSize(20, 20))
        self.conIndicator.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.condetStatusLay.addWidget(self.conIndicator)

        self.verticalLayout_5.addLayout(self.condetStatusLay)

        self.initButton = QPushButton(self.statusbox)
        self.initButton.setObjectName("initButton")

        self.verticalLayout_5.addWidget(self.initButton)

        self.horizontalLayout_12.addWidget(self.statusbox)

        self.groupBox_2 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.manipulator1 = QGroupBox(self.groupBox_2)
        self.manipulator1.setObjectName("manipulator1")
        self.horizontalLayout_8 = QHBoxLayout(self.manipulator1)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.mansmu_1 = QComboBox(self.manipulator1)
        self.mansmu_1.setObjectName("mansmu_1")

        self.horizontalLayout_2.addWidget(self.mansmu_1)

        self.mancon_1 = QComboBox(self.manipulator1)
        self.mancon_1.setObjectName("mancon_1")

        self.horizontalLayout_2.addWidget(self.mancon_1)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_10 = QLabel(self.manipulator1)
        self.label_10.setObjectName("label_10")

        self.horizontalLayout_7.addWidget(self.label_10)

        self.manres_1 = QSpinBox(self.manipulator1)
        self.manres_1.setObjectName("manres_1")
        self.manres_1.setMinimum(1)
        self.manres_1.setMaximum(20)

        self.horizontalLayout_7.addWidget(self.manres_1)

        self.label_11 = QLabel(self.manipulator1)
        self.label_11.setObjectName("label_11")

        self.horizontalLayout_7.addWidget(self.label_11)

        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8.addLayout(self.verticalLayout)

        self.manindicator_1 = QLabel(self.manipulator1)
        self.manindicator_1.setObjectName("manindicator_1")
        self.manindicator_1.setMaximumSize(QSize(20, 20))
        self.manindicator_1.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_8.addWidget(self.manindicator_1)

        self.gridLayout_4.addWidget(self.manipulator1, 0, 1, 1, 1)

        self.manipulator2 = QGroupBox(self.groupBox_2)
        self.manipulator2.setObjectName("manipulator2")
        self.horizontalLayout_16 = QHBoxLayout(self.manipulator2)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.mansmu_2 = QComboBox(self.manipulator2)
        self.mansmu_2.setObjectName("mansmu_2")

        self.horizontalLayout_3.addWidget(self.mansmu_2)

        self.mancon_2 = QComboBox(self.manipulator2)
        self.mancon_2.setObjectName("mancon_2")

        self.horizontalLayout_3.addWidget(self.mancon_2)

        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_12 = QLabel(self.manipulator2)
        self.label_12.setObjectName("label_12")

        self.horizontalLayout_15.addWidget(self.label_12)

        self.manres_2 = QSpinBox(self.manipulator2)
        self.manres_2.setObjectName("manres_2")
        self.manres_2.setMinimum(1)
        self.manres_2.setMaximum(20)

        self.horizontalLayout_15.addWidget(self.manres_2)

        self.label_13 = QLabel(self.manipulator2)
        self.label_13.setObjectName("label_13")

        self.horizontalLayout_15.addWidget(self.label_13)

        self.verticalLayout_4.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16.addLayout(self.verticalLayout_4)

        self.manindicator_2 = QLabel(self.manipulator2)
        self.manindicator_2.setObjectName("manindicator_2")
        self.manindicator_2.setMaximumSize(QSize(20, 20))
        self.manindicator_2.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_16.addWidget(self.manindicator_2)

        self.gridLayout_4.addWidget(self.manipulator2, 0, 2, 1, 1)

        self.manipulator4 = QGroupBox(self.groupBox_2)
        self.manipulator4.setObjectName("manipulator4")
        self.horizontalLayout_14 = QHBoxLayout(self.manipulator4)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.mansmu_4 = QComboBox(self.manipulator4)
        self.mansmu_4.setObjectName("mansmu_4")

        self.horizontalLayout_5.addWidget(self.mansmu_4)

        self.mancon_4 = QComboBox(self.manipulator4)
        self.mancon_4.setObjectName("mancon_4")

        self.horizontalLayout_5.addWidget(self.mancon_4)

        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_16 = QLabel(self.manipulator4)
        self.label_16.setObjectName("label_16")

        self.horizontalLayout_13.addWidget(self.label_16)

        self.manres_4 = QSpinBox(self.manipulator4)
        self.manres_4.setObjectName("manres_4")
        self.manres_4.setMinimum(1)
        self.manres_4.setMaximum(20)

        self.horizontalLayout_13.addWidget(self.manres_4)

        self.label_17 = QLabel(self.manipulator4)
        self.label_17.setObjectName("label_17")

        self.horizontalLayout_13.addWidget(self.label_17)

        self.verticalLayout_3.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14.addLayout(self.verticalLayout_3)

        self.manindicator_4 = QLabel(self.manipulator4)
        self.manindicator_4.setObjectName("manindicator_4")
        self.manindicator_4.setMaximumSize(QSize(20, 20))
        self.manindicator_4.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_14.addWidget(self.manindicator_4)

        self.gridLayout_4.addWidget(self.manipulator4, 1, 2, 1, 1)

        self.manipulator3 = QGroupBox(self.groupBox_2)
        self.manipulator3.setObjectName("manipulator3")
        self.horizontalLayout_10 = QHBoxLayout(self.manipulator3)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.mansmu_3 = QComboBox(self.manipulator3)
        self.mansmu_3.setObjectName("mansmu_3")

        self.horizontalLayout_4.addWidget(self.mansmu_3)

        self.mancon_3 = QComboBox(self.manipulator3)
        self.mancon_3.setObjectName("mancon_3")

        self.horizontalLayout_4.addWidget(self.mancon_3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_14 = QLabel(self.manipulator3)
        self.label_14.setObjectName("label_14")

        self.horizontalLayout_9.addWidget(self.label_14)

        self.manres_3 = QSpinBox(self.manipulator3)
        self.manres_3.setObjectName("manres_3")
        self.manres_3.setMinimum(1)
        self.manres_3.setMaximum(20)

        self.horizontalLayout_9.addWidget(self.manres_3)

        self.label_15 = QLabel(self.manipulator3)
        self.label_15.setObjectName("label_15")

        self.horizontalLayout_9.addWidget(self.label_15)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10.addLayout(self.verticalLayout_2)

        self.manindicator_3 = QLabel(self.manipulator3)
        self.manindicator_3.setObjectName("manindicator_3")
        self.manindicator_3.setMaximumSize(QSize(20, 20))
        self.manindicator_3.setStyleSheet("border-radius: 10px;\nbackground-color:rgb(165, 29, 45);\nmin-height: 20px;\nmin-width: 20px;")

        self.horizontalLayout_10.addWidget(self.manindicator_3)

        self.gridLayout_4.addWidget(self.manipulator3, 1, 1, 1, 1)

        self.horizontalLayout_12.addWidget(self.groupBox_2)

        self.verticalLayout_6.addLayout(self.horizontalLayout_12)

        self.buttonLay = QHBoxLayout()
        self.buttonLay.setObjectName("buttonLay")
        self.pushButton_2 = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_2.setObjectName("pushButton_2")

        self.buttonLay.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(self.scrollAreaWidgetContents)
        self.pushButton.setObjectName("pushButton")

        self.buttonLay.addWidget(self.pushButton)

        self.verticalLayout_6.addLayout(self.buttonLay)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "touchDetect settings", None))
        self.label.setText(QCoreApplication.translate("Form", "SMU plugin", None))
        self.smuBox.setProperty("placeholderText", QCoreApplication.translate("Form", "no SMU plugins found", None))
        self.label_2.setText(QCoreApplication.translate("Form", "Micromanipulator plugin", None))
        self.micromanipulatorBox.setProperty("placeholderText", QCoreApplication.translate("Form", "no Micromanipulators found", None))
        self.label_3.setText(QCoreApplication.translate("Form", "contact detection plugin", None))
        self.condetBox.setProperty("placeholderText", QCoreApplication.translate("Form", "No condet plugins found", None))
        self.label_4.setText(QCoreApplication.translate("Form", "Spectrometer height", None))
        self.label_5.setText(QCoreApplication.translate("Form", "\u03bcm", None))
        self.label_18.setText(QCoreApplication.translate("Form", "On sequence fail:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", "Stop sequence", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", "Move to next (WIP, currently silent fail)", None))

        self.label_6.setText(QCoreApplication.translate("Form", "stride", None))
        self.label_7.setText(QCoreApplication.translate("Form", "\u03bcm", None))
        self.label_8.setText(QCoreApplication.translate("Form", "Sample width (max distance)", None))
        self.label_9.setText(QCoreApplication.translate("Form", "\u03bcm", None))
        self.statusbox.setTitle("")
        self.sampleStatus.setText(QCoreApplication.translate("Form", "Microman OK", None))
        self.mmIndicator.setText("")
        self.mmStatus.setText(QCoreApplication.translate("Form", "smu OK", None))
        self.smuIndicator.setText("")
        self.pointsStatus.setText(QCoreApplication.translate("Form", "Contact detection OK", None))
        self.conIndicator.setText("")
        self.initButton.setText(QCoreApplication.translate("Form", "Initialize dependencies", None))
        self.groupBox_2.setTitle("")
        self.manipulator1.setTitle(QCoreApplication.translate("Form", "Manipulator 1", None))
        self.label_10.setText(QCoreApplication.translate("Form", "Resistance cutoff", None))
        self.label_11.setText(QCoreApplication.translate("Form", "\u03a9", None))
        self.manindicator_1.setText("")
        self.manipulator2.setTitle(QCoreApplication.translate("Form", "Manipulator 2", None))
        self.label_12.setText(QCoreApplication.translate("Form", "Resistance cutoff", None))
        self.label_13.setText(QCoreApplication.translate("Form", "\u03a9", None))
        self.manindicator_2.setText("")
        self.manipulator4.setTitle(QCoreApplication.translate("Form", "Manipulator 4", None))
        self.label_16.setText(QCoreApplication.translate("Form", "Resistance cutoff", None))
        self.label_17.setText(QCoreApplication.translate("Form", "\u03a9", None))
        self.manindicator_4.setText("")
        self.manipulator3.setTitle(QCoreApplication.translate("Form", "Manipulator 3", None))
        self.label_14.setText(QCoreApplication.translate("Form", "Resistance cutoff", None))
        self.label_15.setText(QCoreApplication.translate("Form", "\u03a9", None))
        self.manindicator_3.setText("")
        self.pushButton_2.setText(QCoreApplication.translate("Form", "Monitor 1", None))
        self.pushButton.setText(QCoreApplication.translate("Form", "test", None))

    # retranslateUi

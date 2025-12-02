# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'affineMatchDialogHUXkMY.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import QCoreApplication, QMetaObject, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(845, 763)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.otsuMask = QCheckBox(self.groupBox)
        self.otsuMask.setObjectName("otsuMask")

        self.horizontalLayout_11.addWidget(self.otsuMask)

        self.cannyMask = QCheckBox(self.groupBox)
        self.cannyMask.setObjectName("cannyMask")

        self.horizontalLayout_11.addWidget(self.cannyMask)

        self.invertMask = QCheckBox(self.groupBox)
        self.invertMask.setObjectName("invertMask")

        self.horizontalLayout_11.addWidget(self.invertMask)

        self.equalizeMask = QCheckBox(self.groupBox)
        self.equalizeMask.setObjectName("equalizeMask")

        self.horizontalLayout_11.addWidget(self.equalizeMask)

        self.blurMask = QCheckBox(self.groupBox)
        self.blurMask.setObjectName("blurMask")

        self.horizontalLayout_11.addWidget(self.blurMask)

        self.horizontalLayout_12.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_9.addWidget(self.label_5)

        self.sigmaMask = QComboBox(self.groupBox)
        self.sigmaMask.setObjectName("sigmaMask")

        self.horizontalLayout_9.addWidget(self.sigmaMask)

        self.horizontalLayout_12.addLayout(self.horizontalLayout_9)

        self.verticalLayout_2.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.otsuImage = QCheckBox(self.groupBox)
        self.otsuImage.setObjectName("otsuImage")

        self.horizontalLayout_13.addWidget(self.otsuImage)

        self.cannyImage = QCheckBox(self.groupBox)
        self.cannyImage.setObjectName("cannyImage")

        self.horizontalLayout_13.addWidget(self.cannyImage)

        self.invertImage = QCheckBox(self.groupBox)
        self.invertImage.setObjectName("invertImage")

        self.horizontalLayout_13.addWidget(self.invertImage)

        self.equalizeImage = QCheckBox(self.groupBox)
        self.equalizeImage.setObjectName("equalizeImage")

        self.horizontalLayout_13.addWidget(self.equalizeImage)

        self.blurImage = QCheckBox(self.groupBox)
        self.blurImage.setObjectName("blurImage")

        self.horizontalLayout_13.addWidget(self.blurImage)

        self.horizontalLayout_14.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_10.addWidget(self.label_4)

        self.sigmaImage = QComboBox(self.groupBox)
        self.sigmaImage.setObjectName("sigmaImage")

        self.horizontalLayout_10.addWidget(self.sigmaImage)

        self.horizontalLayout_14.addLayout(self.horizontalLayout_10)

        self.verticalLayout_2.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.morphologyImage = QCheckBox(self.groupBox)
        self.morphologyImage.setObjectName("morphologyImage")

        self.horizontalLayout_2.addWidget(self.morphologyImage)

        self.morphologyTypeImage = QComboBox(self.groupBox)
        self.morphologyTypeImage.setObjectName("morphologyTypeImage")
        self.morphologyTypeImage.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.morphologyTypeImage)

        self.morphologyStrengthImage = QSpinBox(self.groupBox)
        self.morphologyStrengthImage.setObjectName("morphologyStrengthImage")
        self.morphologyStrengthImage.setEnabled(False)
        self.morphologyStrengthImage.setMinimum(1)
        self.morphologyStrengthImage.setMaximum(15)
        self.morphologyStrengthImage.setValue(3)

        self.horizontalLayout_2.addWidget(self.morphologyStrengthImage)

        self.horizontalLayout_15.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.manualThresholdImage = QCheckBox(self.groupBox)
        self.manualThresholdImage.setObjectName("manualThresholdImage")

        self.horizontalLayout_3.addWidget(self.manualThresholdImage)

        self.thresholdImage = QSpinBox(self.groupBox)
        self.thresholdImage.setObjectName("thresholdImage")
        self.thresholdImage.setEnabled(False)
        self.thresholdImage.setMinimum(0)
        self.thresholdImage.setMaximum(255)
        self.thresholdImage.setValue(128)

        self.horizontalLayout_3.addWidget(self.thresholdImage)

        self.horizontalLayout_15.addLayout(self.horizontalLayout_3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.morphologyMask = QCheckBox(self.groupBox)
        self.morphologyMask.setObjectName("morphologyMask")

        self.horizontalLayout.addWidget(self.morphologyMask)

        self.morphologyTypeMask = QComboBox(self.groupBox)
        self.morphologyTypeMask.setObjectName("morphologyTypeMask")
        self.morphologyTypeMask.setEnabled(False)

        self.horizontalLayout.addWidget(self.morphologyTypeMask)

        self.morphologyStrengthMask = QSpinBox(self.groupBox)
        self.morphologyStrengthMask.setObjectName("morphologyStrengthMask")
        self.morphologyStrengthMask.setEnabled(False)
        self.morphologyStrengthMask.setMinimum(1)
        self.morphologyStrengthMask.setMaximum(15)
        self.morphologyStrengthMask.setValue(3)

        self.horizontalLayout.addWidget(self.morphologyStrengthMask)

        self.horizontalLayout_16.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.manualThresholdMask = QCheckBox(self.groupBox)
        self.manualThresholdMask.setObjectName("manualThresholdMask")

        self.horizontalLayout_4.addWidget(self.manualThresholdMask)

        self.thresholdMask = QSpinBox(self.groupBox)
        self.thresholdMask.setObjectName("thresholdMask")
        self.thresholdMask.setEnabled(False)
        self.thresholdMask.setMinimum(0)
        self.thresholdMask.setMaximum(255)
        self.thresholdMask.setValue(128)

        self.horizontalLayout_4.addWidget(self.thresholdMask)

        self.horizontalLayout_16.addLayout(self.horizontalLayout_4)

        self.verticalLayout_2.addLayout(self.horizontalLayout_16)

        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.residualTestSpinBox = QSpinBox(self.groupBox_2)
        self.residualTestSpinBox.setObjectName("residualTestSpinBox")

        self.horizontalLayout_6.addWidget(self.residualTestSpinBox)

        self.horizontalLayout_17.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName("label")

        self.horizontalLayout_5.addWidget(self.label)

        self.ratioTestSpinBox = QDoubleSpinBox(self.groupBox_2)
        self.ratioTestSpinBox.setObjectName("ratioTestSpinBox")
        self.ratioTestSpinBox.setMaximum(1.000000000000000)
        self.ratioTestSpinBox.setSingleStep(0.100000000000000)

        self.horizontalLayout_5.addWidget(self.ratioTestSpinBox)

        self.horizontalLayout_17.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_7.addWidget(self.label_3)

        self.backendCombo = QComboBox(self.groupBox_2)
        self.backendCombo.setObjectName("backendCombo")

        self.horizontalLayout_7.addWidget(self.backendCombo)

        self.horizontalLayout_17.addLayout(self.horizontalLayout_7)

        self.verticalLayout_3.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.crossCheck = QCheckBox(self.groupBox_2)
        self.crossCheck.setObjectName("crossCheck")

        self.horizontalLayout_18.addWidget(self.crossCheck)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")

        self.horizontalLayout_8.addWidget(self.label_6)

        self.scalingSpinBox = QDoubleSpinBox(self.groupBox_2)
        self.scalingSpinBox.setObjectName("scalingSpinBox")
        self.scalingSpinBox.setMinimum(0.100000000000000)
        self.scalingSpinBox.setMaximum(1.000000000000000)
        self.scalingSpinBox.setSingleStep(0.100000000000000)

        self.horizontalLayout_8.addWidget(self.scalingSpinBox)

        self.horizontalLayout_18.addLayout(self.horizontalLayout_8)

        self.verticalLayout_3.addLayout(self.horizontalLayout_18)

        self.statusText = QLabel(self.groupBox_2)
        self.statusText.setObjectName("statusText")

        self.verticalLayout_3.addWidget(self.statusText)

        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 2)

        self.groupBox_4 = QGroupBox(Dialog)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout = QVBoxLayout(self.groupBox_4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter_2 = QSplitter(self.groupBox_4)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Vertical)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.maskView = QGraphicsView(self.splitter)
        self.maskView.setObjectName("maskView")
        self.splitter.addWidget(self.maskView)
        self.imgView = QGraphicsView(self.splitter)
        self.imgView.setObjectName("imgView")
        self.splitter.addWidget(self.imgView)
        self.splitter_2.addWidget(self.splitter)
        self.resultView = QGraphicsView(self.splitter_2)
        self.resultView.setObjectName("resultView")
        self.splitter_2.addWidget(self.resultView)

        self.verticalLayout.addWidget(self.splitter_2)

        self.gridLayout.addWidget(self.groupBox_4, 2, 0, 1, 2)

        self.groupBox_3 = QGroupBox(Dialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_2 = QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.matchButton = QPushButton(self.groupBox_3)
        self.matchButton.setObjectName("matchButton")

        self.gridLayout_2.addWidget(self.matchButton, 0, 0, 1, 1)

        self.manualButton = QPushButton(self.groupBox_3)
        self.manualButton.setObjectName("manualButton")

        self.gridLayout_2.addWidget(self.manualButton, 0, 1, 1, 1)

        self.gridLayout.addWidget(self.groupBox_3, 7, 0, 1, 2)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Affine conversion", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", "Preprocessing settings", None))
        self.otsuMask.setText(QCoreApplication.translate("Dialog", "otsu mask", None))
        self.cannyMask.setText(QCoreApplication.translate("Dialog", "edge detect mask", None))
        self.invertMask.setText(QCoreApplication.translate("Dialog", "invert mask", None))
        self.equalizeMask.setText(QCoreApplication.translate("Dialog", "equalize mask", None))
        self.blurMask.setText(QCoreApplication.translate("Dialog", "blur mask", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", "sigma Mask", None))
        self.otsuImage.setText(QCoreApplication.translate("Dialog", "otsu img", None))
        self.cannyImage.setText(QCoreApplication.translate("Dialog", "edge detect image", None))
        self.invertImage.setText(QCoreApplication.translate("Dialog", "invert img", None))
        self.equalizeImage.setText(QCoreApplication.translate("Dialog", "equalize img", None))
        self.blurImage.setText(QCoreApplication.translate("Dialog", "blur image", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", "Sigma Image", None))
        self.morphologyImage.setText(QCoreApplication.translate("Dialog", "morphology img", None))
        self.manualThresholdImage.setText(QCoreApplication.translate("Dialog", "manual threshold img", None))
        self.morphologyMask.setText(QCoreApplication.translate("Dialog", "morphology mask", None))
        self.manualThresholdMask.setText(QCoreApplication.translate("Dialog", "manual threshold mask", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", "Feature detection settings", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "Residual threshold", None))
        self.label.setText(QCoreApplication.translate("Dialog", "ratio test ", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", "Backend", None))
        self.crossCheck.setText(QCoreApplication.translate("Dialog", "Crosscheck", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", "Scaling", None))
        self.statusText.setText(QCoreApplication.translate("Dialog", "Status", None))
        self.groupBox_4.setTitle("")
        self.groupBox_3.setTitle("")
        self.matchButton.setText(QCoreApplication.translate("Dialog", "Match", None))
        self.manualButton.setText(QCoreApplication.translate("Dialog", "Manual", None))

    # retranslateUi

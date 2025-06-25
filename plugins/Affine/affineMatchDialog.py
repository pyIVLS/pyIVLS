# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'affineMatchDialogUVdsJa.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import QCoreApplication, QMetaObject, Qt
from PyQt6.QtWidgets import QCheckBox, QComboBox, QGraphicsView, QGridLayout, QGroupBox, QLabel, QPushButton, QSplitter, QVBoxLayout


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(1600, 1200)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.equalizeImage = QCheckBox(self.groupBox)
        self.equalizeImage.setObjectName("equalizeImage")

        self.gridLayout_3.addWidget(self.equalizeImage, 1, 2, 1, 1)

        self.cannyMask = QCheckBox(self.groupBox)
        self.cannyMask.setObjectName("cannyMask")

        self.gridLayout_3.addWidget(self.cannyMask, 0, 3, 1, 1)

        self.blurImage = QCheckBox(self.groupBox)
        self.blurImage.setObjectName("blurImage")

        self.gridLayout_3.addWidget(self.blurImage, 1, 0, 1, 1)

        self.invertImage = QCheckBox(self.groupBox)
        self.invertImage.setObjectName("invertImage")

        self.gridLayout_3.addWidget(self.invertImage, 1, 1, 1, 1)

        self.blurMask = QCheckBox(self.groupBox)
        self.blurMask.setObjectName("blurMask")

        self.gridLayout_3.addWidget(self.blurMask, 0, 0, 1, 1)

        self.invertMask = QCheckBox(self.groupBox)
        self.invertMask.setObjectName("invertMask")

        self.gridLayout_3.addWidget(self.invertMask, 0, 1, 1, 1)

        self.equalizeMask = QCheckBox(self.groupBox)
        self.equalizeMask.setObjectName("equalizeMask")

        self.gridLayout_3.addWidget(self.equalizeMask, 0, 2, 1, 1)

        self.cannyImage = QCheckBox(self.groupBox)
        self.cannyImage.setObjectName("cannyImage")

        self.gridLayout_3.addWidget(self.cannyImage, 1, 3, 1, 1)

        self.sigmaImage = QComboBox(self.groupBox)
        self.sigmaImage.setObjectName("sigmaImage")

        self.gridLayout_3.addWidget(self.sigmaImage, 1, 4, 1, 1)

        self.sigmaMask = QComboBox(self.groupBox)
        self.sigmaMask.setObjectName("sigmaMask")

        self.gridLayout_3.addWidget(self.sigmaMask, 0, 4, 1, 1)

        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")

        self.gridLayout_4.addWidget(self.label_2, 1, 0, 1, 1)

        self.ratioCombo = QComboBox(self.groupBox_2)
        self.ratioCombo.setObjectName("ratioCombo")

        self.gridLayout_4.addWidget(self.ratioCombo, 0, 1, 1, 1)

        self.residualCombo = QComboBox(self.groupBox_2)
        self.residualCombo.setObjectName("residualCombo")

        self.gridLayout_4.addWidget(self.residualCombo, 1, 1, 1, 1)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName("label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.crossCheck = QCheckBox(self.groupBox_2)
        self.crossCheck.setObjectName("crossCheck")

        self.gridLayout_4.addWidget(self.crossCheck, 2, 0, 1, 1)

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
        self.equalizeImage.setText(QCoreApplication.translate("Dialog", "equalize img", None))
        self.cannyMask.setText(QCoreApplication.translate("Dialog", "edge detect mask", None))
        self.blurImage.setText(QCoreApplication.translate("Dialog", "blur image", None))
        self.invertImage.setText(QCoreApplication.translate("Dialog", "invert img", None))
        self.blurMask.setText(QCoreApplication.translate("Dialog", "blur mask", None))
        self.invertMask.setText(QCoreApplication.translate("Dialog", "invert mask", None))
        self.equalizeMask.setText(QCoreApplication.translate("Dialog", "equalize mask", None))
        self.cannyImage.setText(QCoreApplication.translate("Dialog", "edge detect image", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", "SIFT settings", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "Residual threshold (larger -> more matches but less accurate)", None))
        self.label.setText(QCoreApplication.translate("Dialog", "ratio test) ", None))
        self.crossCheck.setText(QCoreApplication.translate("Dialog", "Crosscheck", None))
        self.groupBox_4.setTitle("")
        self.groupBox_3.setTitle("")
        self.matchButton.setText(QCoreApplication.translate("Dialog", "Match", None))
        self.manualButton.setText(QCoreApplication.translate("Dialog", "Manual", None))

    # retranslateUi

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gdsLoaderDialogMdWqWC.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import QCoreApplication, QMetaObject, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(612, 473)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = QGraphicsView(Dialog)
        self.graphicsView.setObjectName("graphicsView")

        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 3)

        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.layerComboBox = QComboBox(self.groupBox)
        self.layerComboBox.setObjectName("layerComboBox")

        self.horizontalLayout_3.addWidget(self.layerComboBox)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.drawLayerCheckBox = QCheckBox(self.groupBox)
        self.drawLayerCheckBox.setObjectName("drawLayerCheckBox")

        self.verticalLayout.addWidget(self.drawLayerCheckBox)

        self.verticalLayout_4.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName("label")

        self.horizontalLayout.addWidget(self.label)

        self.widthSpinBox = QSpinBox(self.groupBox)
        self.widthSpinBox.setObjectName("widthSpinBox")
        self.widthSpinBox.setMinimum(200)
        self.widthSpinBox.setMaximum(6000)

        self.horizontalLayout.addWidget(self.widthSpinBox)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.aspectRatioCheckBox = QCheckBox(self.groupBox)
        self.aspectRatioCheckBox.setObjectName("aspectRatioCheckBox")

        self.verticalLayout_2.addWidget(self.aspectRatioCheckBox)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.heightSpinBox = QSpinBox(self.groupBox)
        self.heightSpinBox.setObjectName("heightSpinBox")
        self.heightSpinBox.setMinimum(200)
        self.heightSpinBox.setMaximum(6000)

        self.horizontalLayout_2.addWidget(self.heightSpinBox)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.applyResize = QPushButton(self.groupBox)
        self.applyResize.setObjectName("applyResize")

        self.verticalLayout_2.addWidget(self.applyResize)

        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.recolorCheckBox = QCheckBox(self.groupBox)
        self.recolorCheckBox.setObjectName("recolorCheckBox")

        self.verticalLayout_3.addWidget(self.recolorCheckBox)

        self.drawAllButton = QPushButton(self.groupBox)
        self.drawAllButton.setObjectName("drawAllButton")

        self.verticalLayout_3.addWidget(self.drawAllButton)

        self.hideAllButton = QPushButton(self.groupBox)
        self.hideAllButton.setObjectName("hideAllButton")

        self.verticalLayout_3.addWidget(self.hideAllButton)

        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "GDS Loader", None))
        self.groupBox.setTitle("")
        self.label_3.setText(QCoreApplication.translate("Dialog", "Layer", None))
        self.drawLayerCheckBox.setText(QCoreApplication.translate("Dialog", "Draw layer", None))
        self.label.setText(QCoreApplication.translate("Dialog", "w", None))
        self.aspectRatioCheckBox.setText(QCoreApplication.translate("Dialog", "Keep aspect ratio", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", "h", None))
        self.applyResize.setText(QCoreApplication.translate("Dialog", "apply", None))
        self.recolorCheckBox.setText(QCoreApplication.translate("Dialog", "Recolor  layers", None))
        self.drawAllButton.setText(QCoreApplication.translate("Dialog", "Draw all layers", None))
        self.hideAllButton.setText(QCoreApplication.translate("Dialog", "Hide all layers", None))

    # retranslateUi

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'affineMatchDialogTGyopU.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PyQt6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QGraphicsView, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSplitter, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(845, 756)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.equalizeImage = QCheckBox(self.groupBox)
        self.equalizeImage.setObjectName(u"equalizeImage")

        self.gridLayout_3.addWidget(self.equalizeImage, 1, 2, 1, 1)

        self.cannyMask = QCheckBox(self.groupBox)
        self.cannyMask.setObjectName(u"cannyMask")

        self.gridLayout_3.addWidget(self.cannyMask, 0, 3, 1, 1)

        self.blurImage = QCheckBox(self.groupBox)
        self.blurImage.setObjectName(u"blurImage")

        self.gridLayout_3.addWidget(self.blurImage, 1, 0, 1, 1)

        self.invertImage = QCheckBox(self.groupBox)
        self.invertImage.setObjectName(u"invertImage")

        self.gridLayout_3.addWidget(self.invertImage, 1, 1, 1, 1)

        self.blurMask = QCheckBox(self.groupBox)
        self.blurMask.setObjectName(u"blurMask")

        self.gridLayout_3.addWidget(self.blurMask, 0, 0, 1, 1)

        self.invertMask = QCheckBox(self.groupBox)
        self.invertMask.setObjectName(u"invertMask")

        self.gridLayout_3.addWidget(self.invertMask, 0, 1, 1, 1)

        self.equalizeMask = QCheckBox(self.groupBox)
        self.equalizeMask.setObjectName(u"equalizeMask")

        self.gridLayout_3.addWidget(self.equalizeMask, 0, 2, 1, 1)

        self.cannyImage = QCheckBox(self.groupBox)
        self.cannyImage.setObjectName(u"cannyImage")

        self.gridLayout_3.addWidget(self.cannyImage, 1, 3, 1, 1)

        self.sigmaImage = QComboBox(self.groupBox)
        self.sigmaImage.setObjectName(u"sigmaImage")

        self.gridLayout_3.addWidget(self.sigmaImage, 1, 4, 1, 1)

        self.sigmaMask = QComboBox(self.groupBox)
        self.sigmaMask.setObjectName(u"sigmaMask")

        self.gridLayout_3.addWidget(self.sigmaMask, 0, 4, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)

        self.groupBox_4 = QGroupBox(Dialog)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout = QVBoxLayout(self.groupBox_4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter_2 = QSplitter(self.groupBox_4)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Vertical)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.maskView = QGraphicsView(self.splitter)
        self.maskView.setObjectName(u"maskView")
        self.splitter.addWidget(self.maskView)
        self.imgView = QGraphicsView(self.splitter)
        self.imgView.setObjectName(u"imgView")
        self.splitter.addWidget(self.imgView)
        self.splitter_2.addWidget(self.splitter)
        self.resultView = QGraphicsView(self.splitter_2)
        self.resultView.setObjectName(u"resultView")
        self.splitter_2.addWidget(self.resultView)

        self.verticalLayout.addWidget(self.splitter_2)


        self.gridLayout.addWidget(self.groupBox_4, 2, 0, 1, 2)

        self.groupBox_3 = QGroupBox(Dialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_2 = QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.matchButton = QPushButton(self.groupBox_3)
        self.matchButton.setObjectName(u"matchButton")

        self.gridLayout_2.addWidget(self.matchButton, 0, 0, 1, 1)

        self.manualButton = QPushButton(self.groupBox_3)
        self.manualButton.setObjectName(u"manualButton")

        self.gridLayout_2.addWidget(self.manualButton, 0, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox_3, 8, 0, 1, 2)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.ratioLine = QLineEdit(self.groupBox_2)
        self.ratioLine.setObjectName(u"ratioLine")

        self.gridLayout_4.addWidget(self.ratioLine, 0, 1, 1, 1)

        self.crossCheck = QCheckBox(self.groupBox_2)
        self.crossCheck.setObjectName(u"crossCheck")

        self.gridLayout_4.addWidget(self.crossCheck, 1, 0, 1, 1)


        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 2)

        self.groupBox_5 = QGroupBox(Dialog)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.gridLayout.addWidget(self.groupBox_5, 4, 0, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Affine conversion", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Preprocessing settings", None))
        self.equalizeImage.setText(QCoreApplication.translate("Dialog", u"equalize img", None))
        self.cannyMask.setText(QCoreApplication.translate("Dialog", u"edge detect mask", None))
        self.blurImage.setText(QCoreApplication.translate("Dialog", u"blur image", None))
        self.invertImage.setText(QCoreApplication.translate("Dialog", u"invert img", None))
        self.blurMask.setText(QCoreApplication.translate("Dialog", u"blur mask", None))
        self.invertMask.setText(QCoreApplication.translate("Dialog", u"invert mask", None))
        self.equalizeMask.setText(QCoreApplication.translate("Dialog", u"equalize mask", None))
        self.cannyImage.setText(QCoreApplication.translate("Dialog", u"edge detect image", None))
        self.groupBox_4.setTitle("")
        self.groupBox_3.setTitle("")
        self.matchButton.setText(QCoreApplication.translate("Dialog", u"Match", None))
        self.manualButton.setText(QCoreApplication.translate("Dialog", u"Manual", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"SIFT settings", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"ratio test (larger ratio, less matches) ", None))
        self.crossCheck.setText(QCoreApplication.translate("Dialog", u"Crosscheck", None))
        self.groupBox_5.setTitle("")
    # retranslateUi


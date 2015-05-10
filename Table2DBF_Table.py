# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Table2DBF_Table.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Updates(object):
    def setupUi(self, Updates):
        Updates.setObjectName("Updates")
        Updates.resize(520, 441)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/main/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Updates.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Updates)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(Updates)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Updates)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Updates)
        self.buttonBox.accepted.connect(Updates.accept)
        self.buttonBox.rejected.connect(Updates.reject)
        QtCore.QMetaObject.connectSlotsByName(Updates)

    def retranslateUi(self, Updates):
        _translate = QtCore.QCoreApplication.translate
        Updates.setWindowTitle(_translate("Updates", "Dialog"))

import res_table2dbf_rc

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'conntest.ui'
#
# Created: Tue Jan 12 21:22:12 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_conntest(object):
    def setupUi(self, conntest):
        conntest.setObjectName("conntest")
        conntest.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(conntest)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtGui.QLabel(conntest)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.txtHost = QtGui.QLineEdit(conntest)
        self.txtHost.setObjectName("txtHost")
        self.horizontalLayout_3.addWidget(self.txtHost)
        self.spnPort = QtGui.QSpinBox(conntest)
        self.spnPort.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spnPort.setMinimum(1)
        self.spnPort.setMaximum(655535)
        self.spnPort.setProperty("value", 10123)
        self.spnPort.setObjectName("spnPort")
        self.horizontalLayout_3.addWidget(self.spnPort)
        self.btnConnect = QtGui.QPushButton(conntest)
        self.btnConnect.setObjectName("btnConnect")
        self.horizontalLayout_3.addWidget(self.btnConnect)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tableWidget = QtGui.QTableWidget(conntest)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.tableWidget)

        self.retranslateUi(conntest)
        QtCore.QMetaObject.connectSlotsByName(conntest)

    def retranslateUi(self, conntest):
        conntest.setWindowTitle(QtGui.QApplication.translate("conntest", "Connection Test", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("conntest", "Host:", None, QtGui.QApplication.UnicodeUTF8))
        self.txtHost.setText(QtGui.QApplication.translate("conntest", "127.0.0.1", None, QtGui.QApplication.UnicodeUTF8))
        self.spnPort.setPrefix(QtGui.QApplication.translate("conntest", ":", None, QtGui.QApplication.UnicodeUTF8))
        self.btnConnect.setText(QtGui.QApplication.translate("conntest", "Connect!", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("conntest", "Type", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("conntest", "Object Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("conntest", "Related Help", None, QtGui.QApplication.UnicodeUTF8))


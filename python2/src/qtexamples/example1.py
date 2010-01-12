#!/usr/bin/python
import sys, traceback
sys.path.insert(0,"../")
from irpc import tcpclient,tcpserver,irpcchatter

from PyQt4 import QtGui, QtCore

from qtui.conntest import Ui_conntest


class MainForm(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_conntest()
        
        self.ui.setupUi(self)
        self.resize(800, 500)
        self.connect(self.ui.btnConnect,QtCore.SIGNAL("clicked()"),self.btnConnect_clicked)
        
        self.remote = None

    def retrieveServerInfo(self):
	fnList = self.remote.call("getFunctionList")
	evList = self.remote.call("getEventList")
	self.ui.tableWidget.clearContents()
	self.ui.tableWidget.setRowCount(len(fnList)+len(evList))
	row = 0
	for fn in fnList:
	    self.ui.tableWidget.setItem(row,0,QtGui.QTableWidgetItem("function"))
	    self.ui.tableWidget.setItem(row,1,QtGui.QTableWidgetItem(fn))
	    help = self.remote.help(fn)
	    self.ui.tableWidget.setItem(row,2,QtGui.QTableWidgetItem(help))

	    row += 1
	    
	for ev in evList:
	    self.ui.tableWidget.setItem(row,0,QtGui.QTableWidgetItem("event"))
	    self.ui.tableWidget.setItem(row,1,QtGui.QTableWidgetItem(ev))
	    help = self.remote.help_ev(ev)
	    self.ui.tableWidget.setItem(row,2,QtGui.QTableWidgetItem(help))
	    row += 1
	    
	
	self.ui.tableWidget.resizeColumnToContents(0)
	self.ui.tableWidget.resizeColumnToContents(1)
	self.ui.tableWidget.resizeColumnToContents(2)
	for row in range(self.ui.tableWidget.rowCount()):
	    self.ui.tableWidget.resizeRowToContents(row)
	    

    def btnConnect_clicked(self):
	if self.remote: 
	    QtGui.QMessageBox.information(self, "Already Connected", "The client is already connected.")
	    return False
	host = str(self.ui.txtHost.text())
	port = int(self.ui.spnPort.value())
	try:
	    self.remote = tcpclient.RemoteIRPC(host,port)
	except:
	    errortitle =  "Error trying to connect to %s:%d" % (host,port)
	    errortext = errortitle + "\n\n"  + traceback.format_exc()
	    
	    QtGui.QMessageBox.critical (self, errortitle, errortext)
	    
	if self.remote: 
	    #QtGui.QMessageBox.information(self, "Connected", "Successfully connected to %s:%d" % (host,port))
	    self.retrieveServerInfo()
	    return True

	

app = QtGui.QApplication(sys.argv)
mainform = MainForm()
mainform.show()
sys.exit(app.exec_())
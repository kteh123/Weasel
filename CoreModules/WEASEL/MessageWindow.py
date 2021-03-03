from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow,  
        QStatusBar, QLabel, 
        QTreeWidgetItem,
        QProgressBar)

import logging
logger = logging.getLogger(__name__)


def displayMessageSubWindow(self, message, title="Loading DICOM files"):
        """
        Creates a subwindow that displays a message to the user. 
        """
        try:
            
            logger.info('LoadDICOM.displayMessageSubWindow called.')
            for subWin in self.mdiArea.subWindowList():
                if subWin.objectName() == "Msg_Window":
                    subWin.close()
                    
            widget = QWidget()
            widget.setLayout(QVBoxLayout()) 
            self.msgSubWindow = QMdiSubWindow(self)
            self.msgSubWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.msgSubWindow.setWidget(widget)
            self.msgSubWindow.setObjectName("Msg_Window")
            self.msgSubWindow.setWindowTitle(title)
            height, width = self.getMDIAreaDimensions()
            self.msgSubWindow.setGeometry(0,0,width*0.5,height*0.25)
            lblMsg = QLabel('<H4>' + message + '</H4>')
            widget.layout().addWidget(lblMsg)

            self.progBarMsg = QProgressBar(self)
            widget.layout().addWidget(self.progBarMsg)
            widget.layout().setAlignment(Qt.AlignTop)
            self.progBarMsg.hide()
            self.progBarMsg.setValue(0)

            self.mdiArea.addSubWindow(self.msgSubWindow)
            self.msgSubWindow.show()
            QApplication.processEvents()
        except Exception as e:
            print('Error in : Weasel.displayMessageSubWindow' + str(e))
            logger.error('Error in : Weasel.displayMessageSubWindow' + str(e))


def setMsgWindowProgBarMaxValue(self, maxValue):
    self.progBarMsg.show()
    self.progBarMsg.setMaximum(maxValue)


def setMsgWindowProgBarValue(self, value):
    self.progBarMsg.setValue(value)


def hideProgressBar(self):
    try:
        if self.progBarMsg.isHidden() == False:
            self.progBarMsg.hide()
    except Exception as e:
            print('Error in : Weasel.hideProgressBar: ' + str(e))
            logger.error('Error in : Weasel.hideProgressBar: ' + str(e))


def closeMessageSubWindow(self):
    try:
        if self.msgSubWindow.isEnabled() == True:
            self.msgSubWindow.close()
    except Exception as e:
            print('Error in : Weasel.closeMessageSubWindow: ' + str(e))
            logger.error('Error in : Weasel.closeMessageSubWindow: ' + str(e))
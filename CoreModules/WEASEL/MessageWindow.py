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
            
            logger.info('MessageWindow.displayMessageSubWindow called with title={}.'.format(title))
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
            self.lblMsg = QLabel('<H4>' + message + '</H4>')
            widget.layout().addWidget(self.lblMsg)

            self.progBarMsg = QProgressBar(self)
            widget.layout().addWidget(self.progBarMsg)
            widget.layout().setAlignment(Qt.AlignTop)
            self.progBarMsg.hide()
            self.progBarMsg.setValue(0)

            self.mdiArea.addSubWindow(self.msgSubWindow)
            self.msgSubWindow.show()
            QApplication.processEvents()
        except Exception as e:
            print('Error in MessageWindow.displayMessageSubWindow when title={}'.format(title) + str(e))
            logger.exception('Error in  MessageWindow.displayMessageSubWindow when title={}'.format(title) + str(e))


def setMsgWindowProgBarMaxValue(self, maxValue):
    self.progBarMsg.show()
    self.progBarMsg.setMaximum(maxValue)


def setMsgWindowProgBarValue(self, value, msg=None):
    try:
        self.progBarMsg.setValue(value)
        if msg is not None:
            self.lblMsg.setText(msg)
    except Exception as e:
            print('Error in MessageWindow.setMsgWindowProgBarValue when message={}'.format(msg) + str(e))
            logger.exception('Error in MessageWindow.setMsgWindowProgBarValue when message={}'.format(msg) + str(e))

def hideProgressBar(self):
    try:
        logger.info('MessageWindow.hideProgressBar called.')
        if self.progBarMsg:
            if self.progBarMsg.isHidden() == False:
                self.progBarMsg.hide()
    except AttributeError as e:
        logger.exception('Attribute Error in  MessageWindow.hideProgressBar: ' + str(e))
    except Exception as e:
            print('Error in  MessageWindow.hideProgressBar: ' + str(e))
            logger.exception('Error in  MessageWindow.hideProgressBar: ' + str(e))


def closeMessageSubWindow(self):
    try:
        logger.info('MessageWindow.closeMessageSubWindow called.')
        if self.msgSubWindow:
            if self.msgSubWindow.isEnabled() == True:
                self.msgSubWindow.close()
    except AttributeError as e:
        logger.exception('Attribute Error in  MessageWindow.closeMessageSubWindow: ' + str(e))
    except Exception as e:
            print('Error in MessageWindow.closeMessageSubWindow: ' + str(e))
            logger.exception('Error in  MessageWindow.closeMessageSubWindow: ' + str(e))
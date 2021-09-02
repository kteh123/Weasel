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


def displayMessageSubWindow(weasel, message, title="Loading DICOM files"):
        """
        Creates a subwindow that displays a message to the user. 
        """
        try:
            
            logger.info('MessageWindow.displayMessageSubWindow called with title={}.'.format(title))
            weasel.closeSubWindows("Msg_Window")
                    
            widget = QWidget()
            widget.setLayout(QVBoxLayout()) 
            msgSubWindow = QMdiSubWindow()
            msgSubWindow.setAttribute(Qt.WA_DeleteOnClose)
            msgSubWindow.setWidget(widget)
            msgSubWindow.setObjectName("Msg_Window")
            msgSubWindow.setWindowTitle(title)
            height, width = weasel.getMDIAreaDimensions()
            msgSubWindow.setGeometry(0,0,width*0.5,height*0.25)
            weasel.lblMsg = QLabel('<H4>' + message + '</H4>')
            widget.layout().addWidget(weasel.lblMsg)

            weasel.progBarMsg = QProgressBar(weasel)
            widget.layout().addWidget(weasel.progBarMsg)
            widget.layout().setAlignment(Qt.AlignTop)
            weasel.progBarMsg.hide()
            weasel.progBarMsg.setValue(0)

            weasel.mdiArea.addSubWindow(weasel.msgSubWindow)
            weasel.msgSubWindow.show()
            QApplication.processEvents()
        except Exception as e:
            print('Error in MessageWindow.displayMessageSubWindow when title={}'.format(title) + str(e))
            logger.exception('Error in  MessageWindow.displayMessageSubWindow when title={}'.format(title) + str(e))


def setMsgWindowProgBarMaxValue(weasel, maxValue):
    weasel.progBarMsg.show()
    weasel.progBarMsg.setMaximum(maxValue)


def setMsgWindowProgBarValue(weasel, value, msg=None):
    try:
        weasel.progBarMsg.setValue(value)
        if msg is not None:
            weasel.lblMsg.setText(msg)
    except Exception as e:
            print('Error in MessageWindow.setMsgWindowProgBarValue when message={}'.format(msg) + str(e))
            logger.exception('Error in MessageWindow.setMsgWindowProgBarValue when message={}'.format(msg) + str(e))

def hideProgressBar(weasel):
    try:
        logger.info('MessageWindow.hideProgressBar called.')
        if weasel.progBarMsg:
            if weasel.progBarMsg.isHidden() == False:
                weasel.progBarMsg.hide()
    except AttributeError as e:
        logger.exception('Attribute Error in  MessageWindow.hideProgressBar: ' + str(e))
    except Exception as e:
            print('Error in  MessageWindow.hideProgressBar: ' + str(e))
            logger.exception('Error in  MessageWindow.hideProgressBar: ' + str(e))

def closeMessageSubWindow(weasel):
    try:
        logger.info('MessageWindow.closeMessageSubWindow called.')
        if weasel.msgSubWindow:
            if weasel.msgSubWindow.isEnabled() == True:
                weasel.msgSubWindow.close()
    except AttributeError as e:
        logger.exception('Attribute Error in  MessageWindow.closeMessageSubWindow: ' + str(e))
    except Exception as e:
            print('Error in MessageWindow.closeMessageSubWindow: ' + str(e))
            logger.exception('Error in  MessageWindow.closeMessageSubWindow: ' + str(e))
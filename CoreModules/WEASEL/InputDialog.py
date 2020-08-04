from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys
import logging
logger = logging.getLogger(__name__)

class ParameterInputDialog(QDialog):

    #def __init__(self,   *args, title="Input Parameters", integer=True):
    #    super(ParameterInputDialog, self).__init__()
        
    #    self.setWindowTitle(title)
    #    self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
    #    self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
    #    #QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
    #    QBtn = QDialogButtonBox.Ok
    #    self.buttonBox = QDialogButtonBox(QBtn)
    #    self.buttonBox.accepted.connect(self.accept)
    #    #self.buttonBox.rejected.connect(self.reject)
    #    self.layout = QFormLayout()
    #    self.listWidget = []
    #    for  str in args:
    #        if integer:
    #            self.sBox = QSpinBox()
    #            self.sBox.setMaximum(1000)
    #        else:
    #            self.sBox = QDoubleSpinBox()
    #            self.sBox.setMaximum(1000.00)
    #        self.layout.addRow(str, self.sBox)
    #        self.listWidget.append(self.sBox)
    #    self.layout.addRow("", self.buttonBox)
    #    self.setLayout(self.layout)
    #    self.exec_()

    def __init__(self,   paramDict, title="Input Parameters"):
        try:
            super(ParameterInputDialog, self).__init__()
        
            self.setWindowTitle(title)
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
            #QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            QBtn = QDialogButtonBox.Ok
            self.buttonBox = QDialogButtonBox(QBtn)
            self.buttonBox.accepted.connect(self.accept)
            #self.buttonBox.rejected.connect(self.reject)
            self.layout = QFormLayout()
            self.listWidget = []
            for  key in paramDict:
                paramType = paramDict[key].lower()
                if paramType == "integer":
                    self.input = QSpinBox()
                    self.input.setMaximum(100)
                elif paramType == "float":
                    self.input = QDoubleSpinBox()
                    self.input.setMaximum(100.00)
                elif paramType == "string":
                    self.input = QLineEdit()
                self.layout.addRow(key,  self.input)
                self.listWidget.append(self.input)
            self.layout.addRow("", self.buttonBox)
            self.setLayout(self.layout)
            self.exec_()
        except Exception as e:
            print('Error in class ParameterInputDialog.__init__: ' + str(e))
            logger.error('Error in class ParameterInputDialog.__init__: ' + str(e)) 


    def returnListParameterValues(self):
        try:
            #paramList = [sBox.value() for sBox in self.listWidget]
            paramList = []
            for item in self.listWidget:
                if isinstance(item, QLineEdit):
                    paramList.append(item.text())
                else:
                    paramList.append(item.value())

            
            return paramList
        except Exception as e:
            print('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e))
            logger.error('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e)) 
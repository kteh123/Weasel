from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys

class ParameterInputDialog(QDialog):

    def __init__(self,   *args, title="Input Parameters", integer=True):
        super(ParameterInputDialog, self).__init__()
        
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
        #QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QFormLayout()
        self.listWidget = []
        for  str in args:
            if integer:
                self.sBox = QSpinBox()
                self.sBox.setMaximum(1000)
            else:
                self.sBox = QDoubleSpinBox()
                self.sBox.setMaximum(1000.00)
            self.layout.addRow(str, self.sBox)
            self.listWidget.append(self.sBox)
        self.layout.addRow("", self.buttonBox)
        self.setLayout(self.layout)
        self.exec_()

    def returnListParameterValues(self):
        paramList = [sBox.value() for sBox in self.listWidget]
        return paramList
      
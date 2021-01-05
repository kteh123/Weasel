"""The ParameterInputDialog class creates a pop-up input dialog that 
allows the user to input one or more integers, floats or strings.  
These data items can be returned to the calling program in a list. 

This class would be imported thus,
import CoreModules.WEASEL.InputDialog as inputDialog
and example usage within a while loop to validate the input data could be

paramDict = {"Lower Threshold":"integer", "Upper Threshold":"integer"}
helpMsg = "Lower threshold must be less than the upper threshold."
warning = True
while True:
    inputDlg = inputDialog.ParameterInputDialog(paramDict,helpText=helpMsg)
    listParams = inputDlg.returnListParameterValues()
    if listParams[0] < listParams[1]:
        break
    else:
        if warning:
            helpMsg = helpMsg + "<H4><font color=\"red\"> Check input parameter values.</font></H4>"
            warning = False #only show this message once
"""

from PyQt5.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, QComboBox,
                             QStyledItemDelegate, QLabel, QSpinBox, QMessageBox, QScrollBar,
                             QDoubleSpinBox, QLineEdit, QListWidget, QAbstractItemView )
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sys
import logging
logger = logging.getLogger(__name__)

# User-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class IncorrectParameterTypeError(Error):
   """Raised when a parameter type is not 'integer', 'float' or 'string'.
   A unit test for developers to avoid typos."""
   pass

class ParameterInputDialog(QDialog):
    """This class inherits from the Qt QDialog class and it generates a pop-up dialog
  window with one or more input widgets that can accept either an integer, float or string. 
  The order and type of input widgets is defined in the paramDict Python dictionary 
  input parameter in the class initialisation function. 
  
  Input Parameters
  *****************
  paramDict contains name:value pairs of strings in the form 'parmeter name':'parameter type' 
  Parameter type can only take the values: 'integer', 'float', 'string', 'dropdownlist'
  So 'Lower Threshold':'integer' would create a spin box labeled 'Lower Threshold' on the dialog
  So 'Upper Threshold':'float' would create a double spin box labeled 'Upper Threshold' on the dialog
  So 'Series Name':'string' would create a textbox labeled 'Series Name' on the dialog
  Thus,
  paramDict = {'Lower Threshold':'integer', 'Upper Threshold':'float', 'Series Name':'string', 
  'label name': 'dropdownlist',
  'second label name': 'dropdownlist'}
  list1=['item1', 'item2', 'item3']
  listOfList =[list1, list2]
  Widgets are created in the same order on the dialog they occupy in the dictionary; ie., 
  the first dictionary item is uppermost input widget on the dialog 
  and the last dictionary item is the last input widget on the dialog.
  
  title - optional string containing the input dialog title. Has a default string "Input Parameters"

  helpText - optional help text to be displayed above the input widgets.
  """
class ParameterInputDialog(QDialog):
    def __init__(self, paramDict, title="Input Parameters", helpText=None, lists=None):
        try:
            super(ParameterInputDialog, self).__init__()
            self.setWindowTitle(title)
            #Hide ? help button
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
            #Hide top right hand corner X close button
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
            QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel   #OK and Cancel button
            #QBtn = QDialogButtonBox.Ok    #OK button only
            self.buttonBox = QDialogButtonBox(QBtn)
            self.buttonBox.accepted.connect(self.accept)   #OK button
            self.buttonBox.rejected.connect(self.close)  #Cancel button
            self.closeDialog = False
            self.layout = QFormLayout()
            if helpText:
                self.helpTextLbl = QLabel("<H4>" + helpText  +"</H4>")
                self.helpTextLbl.setWordWrap(True)
                self.layout.addRow(self.helpTextLbl)
            self.listWidget = []
            listCounter = 0
            for key in paramDict:
                #paramType = paramDict[key].lower()
                paramType, value1, value2, value3 = self.getParamData(paramDict[key].lower())
                if paramType not in ("integer", "float", "string", "dropdownlist", "listview"):
                    #This unit test is for developers who mistype the above 3 parameter 
                    #types when they are developing new WEASEL tools that need
                    #an input dialog
                    raise IncorrectParameterTypeError
                if paramType == "integer":
                    self.input = QSpinBox()
                    if value2:
                        self.input.setMinimum(int(value2))
                    if value3:
                        self.input.setMaximum(int(value3))
                    if value1:
                        self.input.setValue(int(value1))
                elif paramType == "float":
                    self.input = QDoubleSpinBox()
                    if value2:
                        self.input.setMinimum(float(value2))
                    if value3:
                        self.input.setMaximum(float(value3))
                    if value1:
                        self.input.setValue(float(value1))
                elif paramType == "string":
                    self.input = QLineEdit()
                    if key=="Password": self.input.setEchoMode(QLineEdit.Password)
                    if value1:
                        self.input.setText(value1)
                    else:
                        self.input.setPlaceholderText("Enter your text")
                    #uncomment to set an input mask
                    #self.input.setInputMask('000.000.000.000;_')
                elif paramType == "dropdownlist":
                    self.input = QComboBox()
                    self.input.addItems(lists[listCounter])
                    listCounter += 1
                    if value1:
                        self.input.setCurrentIndex(int(value1))   
                elif paramType == "listview":
                    self.input = QListWidget()
                    self.input.setSelectionMode(QAbstractItemView.ExtendedSelection)
                    self.input.addItems(lists[listCounter])
                    #self.input.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    #self.input.setCheckState(Qt.Unchecked)
                    self.input.setFixedSize(self.input.sizeHintForColumn(0) + 
                                            2 * self.input.frameWidth(), 
                      self.input.sizeHintForRow(0) * self.input.count() + 2 * self.input.frameWidth())
                    # scroll bar 
                    scrollBar = QScrollBar(self) 
                    # setting vertical scroll bar to it 
                    self.input.setVerticalScrollBar(scrollBar) 
                    listCounter += 1
                    
                self.layout.addRow(key,  self.input)
                self.listWidget.append(self.input)
            self.layout.addRow("", self.buttonBox)
            self.setLayout(self.layout)
            self.exec_()  #display input dialog
        except IncorrectParameterTypeError:
            str1 = 'Cannot procede because the parameter type for an input field '
            str2 = 'in the parameter input dialog is incorrect. ' 
            str3 = chr(34) + paramType + chr(34)+  ' was used. '
            str4 = 'Permitted types are' + chr(34) + 'integer,' + chr(34) + 'float' + chr(34) 
            str5 = ' and ' + chr(34) + 'string' + chr(34) + ' input as strings.'
            warningString =  str1 + str2 + str3 + str4 + str5
            print(warningString)
            logger.info('InputDialog - ' + warningString)
            QMessageBox().critical( self,  "Parameter Input Dialog", warningString, QMessageBox.Ok)
        except Exception as e:
            print('Error in class ParameterInputDialog.__init__: ' + str(e))
            logger.error('Error in class ParameterInputDialog.__init__: ' + str(e)) 


    def getParamData(self, paramDescription):
        commaCount = paramDescription.count(',')
        if commaCount == 0:
            return paramDescription, None, None, None
        elif commaCount == 1:
            paramList = paramDescription.split(",")
            return paramList[0], paramList[1], None, None
        elif commaCount == 2:
            paramList = paramDescription.split(",")
            return paramList[0], paramList[1], paramList[2], None
        elif commaCount == 3:
            paramList = paramDescription.split(",")
            return paramList[0], paramList[1], paramList[2], paramList[3]


    def close(self):
        self.closeDialog =True
        #Now programmatically click OK to close the dialog
        self.accept()


    def closeInputDialog(self):
            return self.closeDialog


    def returnListParameterValues(self):
        """Returns a list of parameter values as input by the user, 
        in the same as order as the widgets
        on the input dialog from top most (first item in the list) 
        to the bottom most (last item in the list)."""
        try:
            paramList = []
            for item in self.listWidget:
                if isinstance(item, QLineEdit):
                    paramList.append(item.text())
                elif isinstance(item, QComboBox):
                    paramList.append(item.currentText())
                elif isinstance(item, QListWidget):
                    paramList.append([itemText.text() for itemText in item.selectedItems()])
                else:
                    paramList.append(item.value())

            return paramList
        except Exception as e:
            print('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e))
            logger.error('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e)) 



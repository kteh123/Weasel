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

from PyQt5.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, 
                             QLabel, QSpinBox, QDoubleSpinBox, QLineEdit )
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
  Parameter type can only take the values: 'integer', 'float', 'string'
  So 'Lower Threshold':'integer' would create a spin box labeled 'Lower Threshold' on the dialog
  So 'Upper Threshold':'float' would create a double spin box labeled 'Upper Threshold' on the dialog
  So 'Series Name':'string' would create a textbox labeled 'Series Name' on the dialog
  Thus,
  paramDict = {'Lower Threshold':'integer', 'Upper Threshold':'float', 'Series Name':'string'}

  Widgets are created in the same order on the dialog they occupy in the dictionary; ie., 
  the first dictionary item is uppermost input widget on the dialog 
  and the last dictionary item is the last input widget on the dialog.
  
  title - optional string containing the input dialog title. Has a default string "Input Parameters"

  helpText - optional help text to be displayed above the input widgets.
  """
class ParameterInputDialog(QDialog):
    def __init__(self,   paramDict, title="Input Parameters", helpText=None):
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
            self.closeInputDialog = False
            self.layout = QFormLayout()
            if helpText:
                self.helpTextLbl = QLabel("<H4>" + helpText  +"</H4>")
                self.helpTextLbl.setWordWrap(True)
                self.layout.addRow(self.helpTextLbl)
            self.listWidget = []
            for  key in paramDict:
                paramType = paramDict[key].lower()
                if paramType not in ("integer", "float", "string"):
                    #This unit test is for developers who mistype the above 3 parameter 
                    #types when they are developing new WEASEL tools that need
                    #an input dialog
                    raise IncorrectParameterTypeError
                if paramType == "integer":
                    self.input = QSpinBox()
                    self.input.setMaximum(100)
                elif paramType == "float":
                    self.input = QDoubleSpinBox()
                    self.input.setMaximum(100.00)
                elif paramType == "string":
                    self.input = QLineEdit()
                    self.input.setPlaceholderText("Enter your text")
                    #uncomment to set an input mask
                    #self.input.setInputMask('000.000.000.000;_')

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


    def close(self):
        self.closeInputDialog =True


    def closeInputDialog(self):
            return self.closeInputDialog


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
                else:
                    paramList.append(item.value())

            return paramList
        except Exception as e:
            print('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e))
            logger.error('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e)) 
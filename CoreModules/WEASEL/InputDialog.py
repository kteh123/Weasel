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
                             QStyledItemDelegate, QLabel, QSpinBox, QMessageBox,
                             QDoubleSpinBox, QLineEdit )
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
            for  key in paramDict:
                #paramType = paramDict[key].lower()
                paramType, value1, value2, value3 = self.getParamData(paramDict[key].lower())
                if paramType not in ("integer", "float", "string", "dropdownlist"):
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
                else:
                    paramList.append(item.value())

            return paramList
        except Exception as e:
            print('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e))
            logger.error('Error in class ParameterInputDialog.returnListParameterValues: ' + str(e)) 


class CheckableComboBox(QComboBox):

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = qApp.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res

#comunes = ['Ameglia', 'Arcola', 'Bagnone', 'Bolano', 'Carrara', 'Casola', 'Castelnuovo Magra', 
#    'Comano, località Crespiano', 'Fivizzano', 'Fivizzano località Pieve S. Paolo', 
#    'Fivizzano località Pieve di Viano', 'Fivizzano località Soliera', 'Fosdinovo', 'Genova', 
#    'La Spezia', 'Levanto', 'Licciana Nardi', 'Lucca', 'Lusuolo', 'Massa', 'Minucciano', 
#    'Montignoso', 'Ortonovo', 'Piazza al sercho', 'Pietrasanta', 'Pignine', 'Pisa',
#    'Podenzana', 'Pontremoli', 'Portovenere', 'Santo Stefano di Magra', 'Sarzana',
#    'Serravezza', 'Sesta Godano', 'Varese Ligure', 'Vezzano Ligure', 'Zignago' ]
#combo = CheckableComboBox()
#combo.addItems(comunes)
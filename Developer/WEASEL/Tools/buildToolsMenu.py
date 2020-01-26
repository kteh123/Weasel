import sys
import os
from PyQt5.QtWidgets import QAction
import invertDICOM_Image
import squareDICOM_Image
sys.path.append(os.path.join(sys.path[0],'Developer//WEASEL//Tools//'))
from weaselToolsXMLReader import WeaselToolsXMLReader


seriesOnlyTools = ['binaryOperationsButton']
imageAndSeriesTools = ['invertImageButton', 'squareImageButton' ]

def buildToolsMenu(self, toolsMenu):
        try:
            pass
            #self.objXMLReader = WeaselToolsXMLReader() 
            #tools = self.objXMLReader.getTools()
            
            #for tool in tools:
            #    print(tool.find('buttonName').text)
            #    objButton = getattr(
            #        self, tool.find('buttonName').text)
            #    print (objButton.text)
            #    objButton = QAction(tool.find('action').text, self) 
            #    objButton.setShortcut(tool.find('shortcut').text)
            #    objButton.setStatusTip(tool.find('tooltip').text)
            #    objButton.setEnabled(False)
            #    objButton.triggered.connect(
            #    self.displayBinaryOperationsWindow)
            #    toolsMenu.addAction(objButton)
            #print('loop finished')    


 

            #self.binaryOperationsButton = QAction('&Binary Operation', self)
            #self.binaryOperationsButton.setShortcut('Ctrl+B')
            #self.binaryOperationsButton.setStatusTip(
            #    'Performs binary operations on two images')
            #self.binaryOperationsButton.setEnabled(False)
            #toolsMenu.addAction(self.binaryOperationsButton)
            #binaryOperationsButton.triggered.connect(
            #    self.displayBinaryOperationsWindow)


            #self.invertImageButton = QAction('&Invert Image', self)
            #self.invertImageButton.setShortcut('Ctrl+I')
            #self.invertImageButton.setStatusTip('Invert a DICOM Image or series')
            #self.invertImageButton.triggered.connect(
            #    lambda: invertDICOM_Image.invertImage(self)
            #    )
            #self.invertImageButton.setEnabled(False)
            #toolsMenu.addAction(self.invertImageButton)

            #self.squareImageButton = QAction('&Square Image', self)
            #self.squareImageButton.setShortcut('Ctrl+S')
            #self.squareImageButton.setStatusTip('Square a DICOM Image or series')
            #self.squareImageButton.triggered.connect(
            #    lambda: squareDICOM_Image.squareImage(self)
            #    )
            #self.squareImageButton.setEnabled(False)
            #toolsMenu.addAction(self.squareImageButton)

        except Exception as e:
            print('Error in function buildToolsMenu.buildToolsMenu: ' + str(e))
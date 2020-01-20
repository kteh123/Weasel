from PyQt5.QtWidgets import QAction
import invertDICOM_Image
import copyDICOM_Image
import squareDICOM_Image

seriesOnlyTools = ['copySeriesButton', 'binaryOperationsButton']
imageAndSeriesTools = ['invertImageButton', 'squareImageButton' ]

def buildToolsMenu(self, toolsMenu):
        try:
            self.binaryOperationsButton = QAction('&Binary Operation', self)
            self.binaryOperationsButton.setShortcut('Ctrl+B')
            self.binaryOperationsButton.setStatusTip(
                'Performs binary operations on two images')
            self.binaryOperationsButton.triggered.connect(
                self.displayBinaryOperationsWindow)
            self.binaryOperationsButton.setEnabled(False)
            toolsMenu.addAction(self.binaryOperationsButton)

            self.copySeriesButton = QAction('&Copy Series', self)
            self.copySeriesButton.setShortcut('Ctrl+C')
            self.copySeriesButton.setStatusTip('Copy a DICOM series')
            self.copySeriesButton.triggered.connect(
                lambda:copyDICOM_Image.copySeries(self))
            self.copySeriesButton.setEnabled(False)
            toolsMenu.addAction(self.copySeriesButton)

            self.invertImageButton = QAction('&Invert Image', self)
            self.invertImageButton.setShortcut('Ctrl+I')
            self.invertImageButton.setStatusTip('Invert a DICOM Image or series')
            self.invertImageButton.triggered.connect(
                lambda: invertDICOM_Image.invertImage(self)
                )
            self.invertImageButton.setEnabled(False)
            toolsMenu.addAction(self.invertImageButton)

            self.squareImageButton = QAction('&Square Image', self)
            self.squareImageButton.setShortcut('Ctrl+S')
            self.squareImageButton.setStatusTip('Square a DICOM Image or series')
            self.squareImageButton.triggered.connect(
                lambda: squareDICOM_Image.squareImage(self)
                )
            self.squareImageButton.setEnabled(False)
            toolsMenu.addAction(self.squareImageButton)

        except Exception as e:
            print('Error in function buildToolsMenu.buildToolsMenu: ' + str(e))
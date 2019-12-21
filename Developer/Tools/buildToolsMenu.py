from PyQt5.QtWidgets import QAction
import invertDICOM_Image
import copyDICOM_Image

seriesOnlyTools = ['copySeriesButton', 'binaryOperationsButton']
imageAndSeriesTools = ['invertImageButton']

def buildToolsMenu(self, toolsMenu):
        try:
            self.binaryOperationsButton = QAction('Binary Operation', self)
            self.binaryOperationsButton.setShortcut('Ctrl+B')
            self.binaryOperationsButton.setStatusTip(
                'Performs binary operations on two images')
            self.binaryOperationsButton.triggered.connect(
                self.displayBinaryOperationsWindow)
            self.binaryOperationsButton.setEnabled(False)
            toolsMenu.addAction(self.binaryOperationsButton)

            self.copySeriesButton = QAction('Copy Series', self)
            self.copySeriesButton.setShortcut('Ctrl+C')
            self.copySeriesButton.setStatusTip('Copy a DICOM series')
            self.copySeriesButton.triggered.connect(
                lambda:copyDICOM_Image.copySeries(self))
            self.copySeriesButton.setEnabled(False)
            toolsMenu.addAction(self.copySeriesButton)

            self.invertImageButton = QAction('Invert Image', self)
            self.invertImageButton.setShortcut('Ctrl+I')
            self.invertImageButton.setStatusTip('Invert a DICOM Image or series')
            self.invertImageButton.triggered.connect(
                lambda: invertDICOM_Image.invertImage(self)
                )
            self.invertImageButton.setEnabled(False)
            toolsMenu.addAction(self.invertImageButton)

        except Exception as e:
            print('Error in function buildToolsMenu.buildToolsMenu: ' + str(e))
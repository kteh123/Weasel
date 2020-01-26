from PyQt5.QtWidgets import QAction
import invertDICOM_Image
import copyDICOM_Image
import squareDICOM_Image
import B0MapDICOM_Image

seriesOnlyTools = ['copySeriesButton', 'B0SeriesButton', 'binaryOperationsButton']
imageAndSeriesTools = ['invertImageButton', 'squareImageButton' ]

def buildToolsMenu(self, toolsMenu):
        try:
            #self.binaryOperationsButton = QAction('&Binary Operation', self)
            #self.binaryOperationsButton.setShortcut('Ctrl+B')
            #self.binaryOperationsButton.setStatusTip(
            #    'Performs binary operations on two images')
            #self.binaryOperationsButton.triggered.connect(
            #    self.displayBinaryOperationsWindow)
            #self.binaryOperationsButton.setEnabled(False)
            #toolsMenu.addAction(self.binaryOperationsButton)

            #self.copySeriesButton = QAction('&Copy Series', self)
            #self.copySeriesButton.setShortcut('Ctrl+C')
            #self.copySeriesButton.setStatusTip('Copy a DICOM series')
            #self.copySeriesButton.triggered.connect(
            #    lambda:copyDICOM_Image.copySeries(self))
            #self.copySeriesButton.setEnabled(False)
            #toolsMenu.addAction(self.copySeriesButton)

            self.B0SeriesButton = QAction('&B0 Map Calculation', self)
            self.B0SeriesButton.setShortcut('Ctrl+0')
            self.B0SeriesButton.setStatusTip('Extracts the B0 Map from the series if applicable')
            self.B0SeriesButton.triggered.connect(
                lambda:B0MapDICOM_Image.saveB0MapSeries(self))
            self.B0SeriesButton.setEnabled(False)
            toolsMenu.addAction(self.B0SeriesButton)

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
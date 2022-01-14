from PyQt5.QtWidgets import QHBoxLayout,  QLabel
from PyQt5.QtCore import  Qt

class PixelValueComponent:
    """
    Creates a label in a horizontal layout for the display
    of the value of the pixel under the mouse pointer.
    """
    def __init__(self):
        self.pixelValueLayout = QHBoxLayout()
        self.pixelValueLayout.setContentsMargins(0, 0, 0, 0)
        self.pixelValueLayout.setSpacing(0)

        self.lblPixelValue = QLabel()
        self.lblPixelValue.setMargin(0)
        self.lblPixelValue.setStyleSheet(
            "color : red; padding-left:0; margin-left:0; padding-right:0; margin-right:0; font-size:8pt;")
        self.pixelValueLayout.addWidget(self.lblPixelValue, alignment=Qt.AlignCenter)

    def getLayout(self):
        """
        Returns the horizontal layout containing the pixel value label.
        """
        return self.pixelValueLayout

    def getLabel(self):
        """
        Returns the pixel value label.
        """
        return self.lblPixelValue

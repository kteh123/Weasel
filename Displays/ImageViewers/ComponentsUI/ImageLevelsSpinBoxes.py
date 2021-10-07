from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QDoubleSpinBox, QLabel, QHBoxLayout)

import logging
import Displays.ImageViewers.ComponentsUI.FreeHandROI.Resources as icons

logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021

class ImageLevelsSpinBoxes:
    """This class creates two decimal spinboxes with labels to 
    display appropriate icons in a horizontal layout.
    This pair of spinboxes is used to adjust the intensity 
    and contrast of an image.
    
    This resulting composite component, two spinboxes in a horizontal layout, is returned
    to the calling function using the getCompositeComponent function. 
    
    The pair of spinboxes is return to the called function using the .getSpinBoxes function"""
    def __init__(self): 
        try:
            logger.info("created ImageLevelsSpinBoxes object.")

            self.spinBoxIntensity = QDoubleSpinBox()
            self.spinBoxIntensity.setToolTip("Adjust Image Intensity")
            self.spinBoxIntensity.setStyleSheet("padding-left:0;  margin-left:0;")
            self.spinBoxIntensity.setMinimum(-100000.00)
            self.spinBoxIntensity.setMaximum(1000000000.00)
            self.spinBoxIntensity.setWrapping(True)
            self.spinBoxIntensity.setSingleStep(1.0)
            self.spinBoxIntensity.setFixedWidth(75)

            self.spinBoxContrast = QDoubleSpinBox()
            self.spinBoxContrast.setToolTip("Adjust Image Contrast")
            self.spinBoxContrast.setStyleSheet("padding-left:0; margin-left:0;")
            self.spinBoxContrast.setMinimum(-100000.00)
            self.spinBoxContrast.setMaximum(1000000000.00)
            self.spinBoxContrast.setWrapping(True)
            self.spinBoxContrast.setSingleStep(1.0)
            self.spinBoxContrast.setFixedWidth(75)
    
            lblIntensity = QLabel()
            lblIntensity.setToolTip("Intensity")
            #set the size of the icon
            pixmap = QPixmap(icons.BRIGHTNESS_ICON).scaled(16, 16)
            lblIntensity.setPixmap(pixmap)
            lblIntensity.setStyleSheet("padding-right:0; padding-top:0; margin-top:3; margin-right:0;")

            lblContrast = QLabel()
            lblContrast.setToolTip("Contrast")
            #set the size of the icon
            pixmap = QPixmap(icons.CONTRAST_ICON).scaled(16, 16)
            lblContrast.setPixmap(pixmap)
            lblContrast.setStyleSheet("padding-right:0; padding-top:0; margin-top:3; margin-right:0;")
    
            self.layout = QHBoxLayout()
            self.layout.setAlignment(Qt.AlignLeft)
            self.layout.setContentsMargins(0,0,0,0)
            self.layout.setSpacing(0)
            self.layout.addWidget(lblContrast,Qt.AlignVCenter)
            self.layout.addWidget(self.spinBoxContrast)
            self.layout.addWidget(lblIntensity,Qt.AlignVCenter)
            self.layout.addWidget(self.spinBoxIntensity)
            self.layout.addStretch(400)
        except Exception as e:
            print('Error in ImageLevelsSpinBoxes.__init__: ' + str(e))
            logger.error('Error in ImageLevelsSpinBoxes.__init__: ' + str(e))


    def getCompositeComponent(self):
        """Returns the two spinboxes and thier labels in a horizontal layout"""
        return self.layout


    def getSpinBoxes(self):    
        """Returns the individual spinboxes so that their ValueChanged signals
        can be connected to functions in the calling program that adjust image
        intensity and contrast."""
        return self.spinBoxIntensity, self.spinBoxContrast
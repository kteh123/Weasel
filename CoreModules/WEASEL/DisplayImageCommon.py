"""This module contains helper functions used by functions in modules 
DisplayImageColour.py & DisplayImageROI.py"""
from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QDoubleSpinBox, QLabel)


import logging
import CoreModules.FreeHandROI.Resources as icons

logger = logging.getLogger(__name__)

#listImageTypes = ["SliceLocation", "AcquisitionTime", "AcquisitionNumber", "FlipAngle", "InversionTime", "EchoTime", (0x2005, 0x1572)] # This last element is a good example of private tag

def setUpLevelsSpinBoxes(imageLevelsLayout): 
    logger.info("DisplayImageCommon.setUpLevelsSpinBoxes called.")
    spinBoxIntensity = QDoubleSpinBox()
    spinBoxIntensity.setToolTip("Adjust Image Intensity")
    spinBoxIntensity.setStyleSheet("padding-left:0;  margin-left:0;")
    spinBoxContrast = QDoubleSpinBox()
    spinBoxContrast.setToolTip("Adjust Image Contrast")
    spinBoxContrast.setStyleSheet("padding-left:0; margin-left:0;")
    
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
    
    spinBoxIntensity.setMinimum(-100000.00)
    spinBoxContrast.setMinimum(-100000.00)
    spinBoxIntensity.setMaximum(1000000000.00)
    spinBoxContrast.setMaximum(1000000000.00)
    spinBoxIntensity.setWrapping(True)
    spinBoxContrast.setWrapping(True)
    
    imageLevelsLayout.setAlignment(Qt.AlignLeft)
    imageLevelsLayout.setContentsMargins(0,0,0,0)
    imageLevelsLayout.setSpacing(0)
    imageLevelsLayout.addWidget(lblContrast,Qt.AlignVCenter)
    imageLevelsLayout.addWidget(spinBoxContrast)
    imageLevelsLayout.addWidget(lblIntensity,Qt.AlignVCenter)
    imageLevelsLayout.addWidget(spinBoxIntensity)
    imageLevelsLayout.addStretch(400)
  
    return spinBoxIntensity, spinBoxContrast



#def getDICOMFileData(self):
#        """When a DICOM image is selected in the tree view, this function
#        returns its description in the form - study number: series number: image name
        
#         Input Parameters
#        ****************
#            self - an object reference to the WEASEL interface.


#        Output Parameters
#        *****************
#        fullImageName - string containing the full description of a DICOM image
#        """
#        try:
#            logger.info("DisplayImageCommon.getDICOMFileData called.")
#            selectedImage = self.treeView.selectedItems()
#            if selectedImage:
#                imageNode = selectedImage[0]
#                seriesNode  = imageNode.parent()
#                imageName = imageNode.text(0)
#                series = seriesNode.text(0)
#                studyNode = seriesNode.parent()
#                study = studyNode.text(0)
#                fullImageName = study + ': ' + series + ': '  + imageName 
#                return fullImageName
#            else:
#                return ''
#        except Exception as e:
#            print('Error in DisplayImageCommon.getDICOMFileData: ' + str(e))
#            logger.error('Error in DisplayImageCommon.getDICOMFileData: ' + str(e))


#def closeSubWindow(self, objectName):
#        """Closes a particular sub window in the MDI
        
#        Input Parmeters
#        ***************
#        self - an object reference to the WEASEL interface.
#        objectName - object name of the subwindow to be closed
#        """
#        logger.info("WEASEL closeSubWindow called for {}".format(objectName))
#        for subWin in self.mdiArea.subWindowList():
#            if subWin.objectName() == objectName:
#                QApplication.processEvents()
#                subWin.close()
#                QApplication.processEvents()
#                break
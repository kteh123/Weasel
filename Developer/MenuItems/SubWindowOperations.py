import logging
logger = logging.getLogger(__name__)

def closeAllImageWindows(self):
        """Closes all the sub windows in the MDI except for
        the sub window displaying the DICOM file tree view"""
        logger.info("Menus closeAllImageWindows called")
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == 'tree_view':
                continue
            subWin.close()


def tileAllSubWindows(self):
    logger.info("Menus.tileAllSubWindow called")
    height, width = self.getMDIAreaDimensions()
    for subWin in self.mdiArea.subWindowList():
        if subWin.objectName() == 'tree_view':
            subWin.setGeometry(0, 0, width * 0.4, height)
        elif subWin.objectName() == 'Binary_Operation':
            subWin.setGeometry(0,0,width*0.5,height*0.5)
        elif subWin.objectName() == 'metaData_Window':
            subWin.setGeometry(width * 0.4,0,width*0.6,height)
        elif subWin.objectName() == 'image_viewer':
            subWin.setGeometry(width * 0.4,0,width*0.3,height*0.5)
        self.mdiArea.tileSubWindows()

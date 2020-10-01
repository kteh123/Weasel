import logging
logger = logging.getLogger(__name__)

def main(self):
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

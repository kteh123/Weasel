import logging
logger = logging.getLogger(__name__)

def isEnabled(self):
    return True

def main(self):  
        """Closes all the sub windows open in the MDI"""
        logger.info("WEASEL CloseAllSubWindows.main called")
        self.mdiArea.closeAllSubWindows()
        self.treeView = None  

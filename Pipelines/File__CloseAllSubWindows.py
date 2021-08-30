import logging
logger = logging.getLogger(__name__)

def isEnabled(weasel):
    return True

def main(weasel):  
        """Closes all the sub windows open in the MDI"""
        logger.info("WEASEL CloseAllSubWindows.main called")
        weasel.close_all_windows()
        

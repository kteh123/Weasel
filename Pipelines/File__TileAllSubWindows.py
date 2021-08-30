import logging
logger = logging.getLogger(__name__)

def isEnabled(weasel):
    return True

def main(weasel):
    logger.info("Menus.tileAllSubWindow called")
    weasel.mdiArea.tileSubWindows()

import logging
logger = logging.getLogger(__name__)

def isEnabled(self):
    return True

def main(self):
    logger.info("Menus.tileAllSubWindow called")
    self.mdiArea.tileSubWindows()

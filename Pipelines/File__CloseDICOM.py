def isEnabled(weasel):
    return True
    
import logging
logger = logging.getLogger(__name__)

def isEnabled(weasel):
    return True

def main(weasel):
    """
    Close the DICOM folder and update display
    """
    try:
        logger.info("CloseDICOM.main called")
        weasel.close_dicom_folder() 
    except Exception as e:
        print('Error in function CloseDICOM.main: ' + str(e))
        logger.error('Error in function CloseDICOM.main: ' + str(e))

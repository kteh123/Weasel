import logging
logger = logging.getLogger(__name__)

def isEnabled(weasel):
    return True

def main(weasel):
    """
    Open a DICOM folder and update display.
    """
    try:
        logger.info("OpenDICOM.main called")
        weasel.open_dicom_folder()
    except Exception as e:
        print('Error in function OpenDICOM.main: ' + str(e))
        logger.error('Error in function OpenDICOM.main: ' + str(e))












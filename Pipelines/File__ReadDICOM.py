
import logging
logger = logging.getLogger(__name__)


def main(weasel):
    try:
        logger.info("ReadDICOM.main called")
        weasel.read_dicom_folder()
    except Exception as e:
        print('Error in function ReadDICOM.main: ' + str(e))
        logger.error('Error in function ReadDICOM.main: ' + str(e))










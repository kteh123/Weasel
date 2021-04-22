import xml.etree.cElementTree as ET
import logging
logger = logging.getLogger(__name__)


class WeaselConfigXMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = "config.xml"
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in WeaselConfigXMLReader.__init__: ' + str(e)) 
            logger.error('Error in WeaselConfigXMLReader.__init__: ' + str(e))


    def getMenuConfigFile(self):
        menu = self.root.find('./menu_config_file')
        if menu.text is None:
            return None
        else:
            return menu.text


    def getWeaselDataFolder(self):
        folder = self.root.find('./weasel_data_folder')
        if folder.text is None:
            return None
        else:
            return folder.text

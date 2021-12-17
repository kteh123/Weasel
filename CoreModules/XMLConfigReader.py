"""
Class for reading the Weasel XML configuration file.
"""
import os, sys
import xml.etree.cElementTree as ET
import logging
logger = logging.getLogger(__name__)


class XMLConfigReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = os.path.join(os.path.dirname(sys.argv[0]), "config.xml")
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in XMLConfigReader.__init__: ' + str(e)) 
            logger.exception('Error in XMLConfigReader.__init__: ' + str(e))


    def __repr__(self):
       return '{}, {!r}'.format(
           self.__class__.__name__,
           self.fullFilePath)


    def getMenuConfigFile(self):
        try:
            menu = self.root.find('./menu_config_file')
            if menu.text is None:
                return None
            else:
                return menu.text
        except Exception as e:
            print('Error in XMLConfigReader.getMenuConfigFile: ' + str(e)) 
            logger.exception('Error in XMLConfigReader.getMenuConfigFile: ' + str(e))


    def getWeaselDataFolder(self):
        try:
            folder = self.root.find('./weasel_data_folder')
            if folder.text is None:
                return os.path.dirname(sys.argv[0])
            elif folder.text == '':
                return os.path.dirname(sys.argv[0])
            else:
                return folder.text
        except Exception as e:
            print('Error in XMLConfigReader.getWeaselDataFolder: ' + str(e)) 
            logger.exception('Error in XMLConfigReader.getWeaselDataFolder: ' + str(e))

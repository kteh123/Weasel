import xml.etree.ElementTree as ET  
import logging
logger = logging.getLogger(__name__)


class WeaselToolsXMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = "Developer//WEASEL//toolsMenu.xml"
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            

            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in WeaselToolsXMLReader.__init__: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.__init__: ' + str(e))


    def getTools(self):
        return self.root.findall('./tool')
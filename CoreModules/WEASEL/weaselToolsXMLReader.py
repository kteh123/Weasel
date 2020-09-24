import xml.etree.cElementTree as ET  
import logging
logger = logging.getLogger(__name__)


class WeaselToolsXMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            #self.fullFilePath = "Developer//WEASEL//Tools//toolsMenu.xml"
            self.fullFilePath = "Developer//WEASEL//Tools//Menus.xml"
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            

            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in WeaselToolsXMLReader.__init__: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.__init__: ' + str(e))


    def getTools(self):
        return self.root.findall('./tool')


    def getMenus(self):
        return self.root.findall('./menu')


    def getContextMenuItems(self):
        xPath ="./menu/item[context_menu ='yes']"
        return self.root.findall(xPath)
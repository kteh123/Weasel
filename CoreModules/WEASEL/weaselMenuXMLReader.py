import xml.etree.cElementTree as ET  
import logging
import os
import pathlib
logger = logging.getLogger(__name__)


class WeaselMenuXMLReader:
    def __init__(self, menuXMLFile): 
        try:
            self.hasXMLFileParsedOK = True
            for dirpath, _, filenames in os.walk(pathlib.Path().absolute().parent):
                for individualFile in filenames:
                    if individualFile.endswith(".xml") and menuXMLFile in individualFile:
                        self.fullFilePath = os.path.join(dirpath, individualFile)
                        break
            
            # ISSUE 36
            # weasel_parent = parent_folder(parent_folder('Weasel.py'))
            # self.fullFilePath = search(weasel_parent, menuXMLFile)

            #self.fullFilePath = "MenuFiles\\" + menuXMLFile
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in WeaselMenuXMLReader.__init__: ' + str(e)) 
            logger.error('Error in WeaselMenuXMLReader.__init__: ' + str(e))


    def getMenus(self):
        return self.root.findall('./menu')


    def getContextMenuItems(self):
        xPath ="./menu/item[context_menu ='yes']"
        return self.root.findall(xPath)
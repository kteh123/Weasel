"""
Class for reading the XML file containing the definition of the Weasel menus.
"""
import xml.etree.cElementTree as ET  
import logging
import os
import pathlib
logger = logging.getLogger(__name__)


class XMLMenuReader:
    def __init__(self, menuXMLFile): 
        """
        Initiates an object created from the XMLMenuReader class.
        """
        try:
            self.hasXMLFileParsedOK = True
            for dirpath, _, filenames in os.walk(pathlib.Path().absolute().parent):
                for individualFile in filenames:
                    if individualFile.endswith(".xml") and menuXMLFile in individualFile:
                        self.fullFilePath = os.path.join(dirpath, individualFile)
                        break
            
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in XMLMenuReader.__init__: ' + str(e)) 
            logger.error('Error in XMLMenuReader.__init__: ' + str(e))


    def __repr__(self):
       """Represents this class's objects as a string"""
       return '{}, {!r}'.format(
           self.__class__.__name__,
           self.fullFilePath)


    def getMenus(self):
        """
        Returns all menu elements in the XML tree
        """
        return self.root.findall('./menu')


    def getContextMenuItems(self):
        """
        Returns all menu items in the XML tree 
        that are used in a context menu.
        """
        xPath ="./menu/item[context_menu ='yes']"
        return self.root.findall(xPath)

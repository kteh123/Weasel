import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def scan_tree(folder):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(folder):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry

class WeaselFiles():
    """Some tools for handling files and folders.
    """
    def files(self, folder):
        """Returns all files in folder.
        """
        files = [item.path for item in scan_tree(folder) if item.is_file()]
        return files

    def xml(self, folder):
        """
        Returnts the file path of the xml file in folder
        """
        return folder + '//' + os.path.basename(folder) + '.xml'

    def exists_xml(self, folder):
        """This function returns True if an XML file of scan images already
        exists in the scan directory."""
        flag = False
        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.is_file():
                    if entry.name.lower() == os.path.basename(folder).lower() + ".xml":
                        flag = True
                        break
        return flag 

    def save_as_xml(self, project, folder):
        """
        Saves an element tree as an XML file
        """
        self.message(msg="Saving XML file")
        xmlstr = ET.tostring(project, encoding='utf-8')
        xmlstr = minidom.parseString(xmlstr).toprettyxml(encoding="utf-8", indent="  ")
        filepath = self.xml(folder)
        with open(filepath, "wb") as f:
            f.write(xmlstr) 
        self.close_message() 
        return filepath

    def save_dataframe_as_xml(self, project, folder):
        """
        Saves a dataframe as an XML file
        """   
        project = self.element_tree(project)   
        xml = self.save_as_xml(project, folder)  
        return xml




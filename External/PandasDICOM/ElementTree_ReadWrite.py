import xml.etree.ElementTree as ET
from xml.dom import minidom



def write(element_tree, xml_file):
    """Saves an ElementTree as an XML file

    Parameters:
    ----------
    element_tree: An XML ElementTree
    xml_file: path to the xml file
    """

    xml_string = ET.tostring(element_tree, encoding='utf-8')
    xml_string = minidom.parseString(xml_string).toprettyxml(encoding="utf-8", indent="  ")
    
    with open(xml_file, "wb") as f:
        f.write(xml_string) 


def read(xml_file):
    """Creates an ElementTree from an XML file""" 

    return ET.parse(xml_file)




import CoreModules.WriteXMLfromDICOM
import DICOM.DeveloperTools
import External.ImagingTools
import Menus.Tutorial

"""
These modules are an important part of the Weasel infrastructure.  Users are
recommended not to amend these modules.

DICOMFolder.py - Class for reading and summarizing contents of a DICOM folder.
MenuBuilder.py - Class for building the menus in the menu bar of Weasel.
StyleSheet.py - Contains Cascading Style Sheet commands for the styling of the PyQt 
        widgets forming the Weasel GUI in a single string.
TreeView.py - Class for building a tree view showing a visual representation of DICOM file structure.
WeaselXMLReader.py - Class for reading, editing and writing the XML file summarising 
        the contents of a DICOM folder.
XMLConfigReader.py - Class for reading the Weasel XML configuration file.
XMLMenuBuilder.py - Module of helper functions for building the menus in the menu bar of the MDI 
        using the definition in an XML file.
XMLMenuReader.py - Class for reading the XML file containing the definition of the Weasel menus.
"""
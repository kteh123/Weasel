"""
This is a collection of essential python modules to start Weasel GUI.

Some of these classes do the following:
        - set a generic layout
        - read and manage configuration files
        - support customised menu building
        - read and store DICOM data in XML files
        - build a tree view index based on the DICOM data provided

**NOTE**: These modules are an important part of the Weasel infrastructure. Users are recommended not to amend these.
"""

import CoreModules.WriteXMLfromDICOM
import DICOM.DeveloperTools
import External.Tools.ImageProcessing
import Menus.Tutorial


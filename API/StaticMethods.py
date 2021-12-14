"""
A temporary class for some static methods that need to move to Library. 
"""

import re
import subprocess
import importlib
import logging
logger = logging.getLogger(__name__)


class StaticMethods():

    @staticmethod
    def unique_elements(inputList):
        """
        Returns unique elements of any list.
        """
        #output = list(inp for inp,_ in itertools.groupby(inputList))
        output = []
        for x in inputList:
            if x not in output:
                output.append(x)
        return output
    
    @staticmethod
    def match_search(regex_string, target):
        """
        Returns True if the regex "expression" is in the string target. 
        """
        return re.search(regex_string, target, re.IGNORECASE)
    
    @staticmethod
    def pip_install_external_package(package_name, module_name=None):
        # For example, "pip install ukat" and "import ukat"
        # But "pip install opencv-python" and "import cv2"
        try:
            try:
                subprocess.check_call(["pip", "install", package_name])
            except:
                subprocess.check_call(["pip3", "install", package_name])
            if module_name:
                module = importlib.import_module(module_name)
            else:
                module = importlib.import_module(package_name)
            importlib.reload(module)
        except Exception as e:
            print('Error in OriginalPipelines.pip_install_external_package: ' + str(e))
            logger.error('OriginalPipelines.pip_install_external_package: ' + str(e)) 


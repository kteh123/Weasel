import os
import re
import subprocess
import importlib
import pathlib
import logging
logger = logging.getLogger(__name__)


class StaticMethods():
    """
    A temporary class for some static methods that need to move to Library. 
    """

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

    @staticmethod
    def isPythonFile(fileName):
        flag = False
        if fileName.split(".")[-1].lower()  == 'py':
            flag = True
        return flag

    @staticmethod
    def isXMLFile(fileName):
        flag = False
        if fileName.split(".")[-1].lower()  == 'xml':
            flag = True
        return flag

    @staticmethod
    def returnListPythonFiles():
        listPythonFiles = []
        for dirpath, _, filenames in os.walk(pathlib.Path().absolute().parent):
            for individualFile in filenames:
                if individualFile.endswith(".py"):
                    listPythonFiles.append(os.path.join(dirpath, individualFile))
        return listPythonFiles

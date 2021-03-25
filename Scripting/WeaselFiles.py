import os

def folder_tree(folder):
    """
    Helper function
    Recursively yield DirEntry objects for given directory.
    """
    for entry in os.scandir(folder):
        if entry.is_dir(follow_symlinks=False):
            yield from folder_tree(entry.path)
        else:
            yield entry


class WeaselFiles():
    """Some tools for handling files and folders.
    """
    def project_open(self):
        """
        Returns True if a project is open and False otherwise.
        """
        return self.DICOMFolder !=  ''
        
    def folder_set(self, folder=''):
        """
        Sets weasel's working directory. 
        If a folder is not provided, the user is asked to select one
        returns True if the folder has been set
        returns False if the user hits cancel
        """
        if folder == '':
            folder = self.folder(msg='Please select a DICOM folder')
            if not folder: return False
        self.DICOMFolder = folder
        return True

    def derived_folder(self):
        """
        Returns the folder where all newly created DICOM files will be stored
        """  
        path = os.path.join(self.DICOMFolder, "derived_by_weasel")  
        try: os.mkdir(path)
        except: pass 
        return path  

    def derived_file(self, filename='weasel.dcm'):
        """
        Returns a new filepath in the derived data folder
        """  
        folder = self.derived_folder()
        filepath = os.path.join(folder, filename)
        return filepath

    def files(self):
        """
        Returns all files in the current project folder.
        """
        folder = self.DICOMFolder 
        files = [item.path for item in folder_tree(folder) if item.is_file()]
        return files

    def xml(self):
        """
        Returns the file path of the xml file in the current DICOM folder.
        """
        folder = self.DICOMFolder 
        return folder + '//' + os.path.basename(folder) + '.xml'

    def csv(self):
        """
        Returns the file path of the csv file in the current DICOM folder.
        """
        folder = self.DICOMFolder 
        return folder + '//' + os.path.basename(folder) + '.csv'

    def exists_xml(self):
        """
        This function returns True if an XML file of scan images already
        exists in the current DICOM folder.
        """
        folder = self.DICOMFolder 
        flag = False
        with os.scandir(folder) as entries:
            for entry in entries:
                if entry.is_file():
                    if entry.name.lower() == os.path.basename(folder).lower() + ".xml":
                        flag = True
                        break
        return flag 









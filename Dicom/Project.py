import pydicom

from Dicom.ProjectMessage import ProjectMessage
from Dicom.ProjectFiles import ProjectFiles
from Dicom.ProjectData import ProjectData
from Dicom.ProjectEtree import ProjectEtree
from Dicom.Object import Object
from Dicom.ObjectList import ObjectList

class Project(ProjectFiles, ProjectData, ProjectEtree):
    """
    A class for handling a DICOM project 
    Can be used as standalone in command lines mode
    or can be integrated in weasel
    """
    def __init__(self, folder, user_interface=None):
        """
        Initialise the project with a folder, store the folder path in the UID 
        The folder is stored in the UID so that a project can be accessd in the same way as DICOM objects
        Optionally save a reference to a UI for messaging to users       
        """
        self.UID = [folder]
        if user_interface is None:
            self.ui = ProjectMessage()
        else:
            self.ui = user_interface
            
        if self.exists(): 
            self.read()
        else:
            self.load()

    @property
    def folder(self):
        """
        Returns the folder holding the project data       
        """
        return self.UID[0]

    @property
    def key(self):
        """
        Returns the Keywords describing the Unique Identifiers of the project
        """
        return ['PatientID','StudyInstanceUID','SeriesInstanceUID','SOPInstanceUID']

    def new(self, UID):
        """
        Creates a new object in the project with a give UID
        """
        return Object(self, UID)

    def new_child(self):
        """ 
        Returns a new patient object (no data)
        """
        UID = pydicom.uid.generate_uid() 
        return self.new([UID])

    def children(self):
        """
        returns a list of patients in the project
        """
        PatientID = self.data['PatientID'].unique()
        children = ObjectList()
        for UID in PatientID:
            child = self.new([UID])
            children.append(child)
        return children

    def unique(self, level, files=[]):
        """
        Returns a list of unique UIDs at specified level.

        If files is specified, UIDs are only returned if all files are listed
        level 0: Patients, level 1: Studies, level 2: Series, level 3: Images
        """
        data = self.data[self.key[level]]
        if files == []:
            return data.unique().tolist()
        data_checked = data.loc[files]
        if level == 3:
            return data_checked.values.tolist()
        objs = []
        for obj in data_checked.unique():
            total = (data == obj).sum() 
            checked = (data_checked == obj).sum()
            if checked == total:
                objs.append(obj)
        return objs 

    def objects(self, level=3, files=[]):
        """
        Returns a list of all objects at specified level

        level 0: Patients, level 1: Studies, level 2: Series, level 3: Images
        If files is specified, the function returns only the objects
            that are fully listed in files
        """
        if level == 3:
            return self.images(files=files)
        objs = ObjectList()
        for obj in self.unique(level, files=files):
            obj = self.data[self.key[level]] == obj
            obj = self.data[obj].iloc[0,:]
            UID = obj.loc[self.key[:level+1]].values.tolist()
            objs.append(self.new(UID))
        return objs

    def images(self, files=[]):
        """
        Returns a list of all images in the project
        If files is specified, only those images are returned
        """
        data = self.data
        if files != []:
            data = data.loc[files,:]
        images = ObjectList()
        for _, image in data.iterrows():
            UID = image[self.key].tolist()
            images.append(self.new(UID)) 
        return images  







    
        
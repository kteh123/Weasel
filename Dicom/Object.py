import os
import pydicom
import pandas

from Dicom.ObjectList import ObjectList

class Object():
    """
    A class for handling DICOM objects. 
    """
    def __init__(self, project, UID):
        """
        Initialises a DICOM object
        Arguments:
            project: 
                the Project() that the Object is part of
            UID: 
                UID is a list with UIDs of the object and all of its ancestors. 
                The length of UID is 4 for an image, 3 for a series, 
                    2 for a study and 1 for a patient.
                The last element of the UID is the specific UID of the object
        """
        self.project = project
        self.UID = UID

    def __eq__(self, other):
        """
        Two DicomObjects are the same iff their UID's are the same. 
        """
        if isinstance(other, Object):
            return self.UID == other.UID
        else:
            return False

    @property
    def ui(self):
        """
        Returns the user interface object
        """ 
        return self.project.ui  

    @property
    def data(self):
        """
        Returns the pandas dataframe of the object 
        """
        data = self.project.data[self.key[-1]] == self.UID[-1]
        return self.project.data[data]

    @property
    def files(self):
        """
        Returns a list of filepaths of the images in the object
        """
        return self.data.index

    @property
    def file(self):
        """
        Returns the filepath of the first image
        """   
        return self.files[0] 

    def is_an_image(self):
        """
        Returns True if the object is an image and False otherwise 
        """
        return len(self.UID) == 4

    def is_a_patient(self):
        """
        Returns True if the object is a patient and False otherwise 
        """
        return len(self.UID) == 1

    @property
    def key(self):
        """
        Returns the Keywords describing the Unique Identifiers of the object
        """
        return self.project.key[:len(self.UID)]

    @property
    def child_key(self):
        """
        Returns the Keyword describing the Unique Identifiers of the children 
        """
        return self.project.key[len(self.UID)]

    def size(self):
        """
        Returns the number of children 
        """  
        if self.is_an_image():
            return 0     
        data = self.project.data[self.key[-1]] == self.UID[-1]
        return data.values.sum()

    def parent(self):
        """
        Returns the parent object 
        """
        if self.is_a_patient():
            return self.project
        return Object(self.project, self.UID[:-1])

    def children(self):
        """
        Returns a list of children 
        """
        children = ObjectList()
        if self.is_an_image():
            return children
        for UID in self.data[self.child_key].unique():
            child = Object(self.project, self.UID + [UID])
            children.append(child)
        return children 

    def images(self):
        """
        Returns a list of all images under the object
        """
        if self.is_an_image():
            return ObjectList([self])
        return self.children().images()

    def new_child(self):
        """ 
        Returns a new child of the object (no data)
        """
        if self.is_an_image():
            return
        UID = pydicom.uid.generate_uid() 
        return self.project.new(self.UID + [UID])

    def adopt(self, child, msg='Adopting..'):
        """
        Moves an existing child into the object
        """ 
        if child.is_an_image():
            self._adopt_image(child)
        else:
            parent = Object(self.project, self.UID + [child.UID[-1]]) 
            self.ui.progress_bar(max=self.size(), msg=msg)
            for i, child in enumerate(child.children()):  
                self.ui.update_progress_bar(index=i+1)
                parent.adopt(child)
            self.ui.close_progress_bar()            

    def copy(self, msg='Copying..'):
        """
        Returns a copy of the object as a sibling of the original
        """
        if self.is_an_image():
            copy = self._copy_image()
        else:
            copy = self.parent().new_child()
            self.ui.progress_bar(max=self.size(), msg=msg)
            for i, child in enumerate(self.children()):  
                self.ui.update_progress_bar(index=i+1)
                copy.adopt(child.copy())
            self.ui.close_progress_bar()
        return copy

    def delete(self,  msg='Deleting..'):
        """
        Deletes the object. 
        """
        if self.is_an_image():
            self._delete_image()
        else:
            self.ui.progress_bar(max=self.size(), msg=msg)
            for i, child in enumerate(self.children()):  
                self.ui.update_progress_bar(index=i+1)
                child.delete()
            self.ui.close_progress_bar()

    def _adopt_image(self, image):
        """
        Moves an existing image into a new parent
        """ 
        image.UID[:-1] = self.UID

        # overwrite Patient, Study, Series UID's in the file
        img = pydicom.dcmread(image.file)
        img[self.key[0]].value = self.UID[0]
        img[self.key[1]].value = self.UID[1]
        img[self.key[2]].value = self.UID[2]
        img.save_as(image.file)

        # Write UID's in the dataframe
        # or add a new row if this is the first image in the series
        self.project.data.loc[image.file, self.key] = self.UID

    def _copy_image(self):
        """
        Returns a copy of the image in the same series
        """ 
        # Generate new image object and filename
        copy = self.parent().new_child()
        copyfile = os.path.join(self.project.output_folder(), copy.UID[-1] + '.dcm')

        # Copy the file and overwrite SOPInstanceUID
        img = pydicom.dcmread(self.file)
        img[self.key[-1]].value = copy.UID[-1]
        img.save_as(copyfile)

        # Add a new row in the project data
        data = self.data
        img = pandas.Series(
            data = data.values[0,:],
            index = data.columns, 
            name = copyfile)
        img[self.key[-1]] = copy.UID[-1]
        self.project.data = self.project.data.append(img)
        
        return copy

        # This version appends in place so seems more suitable
        # but the first line seems to modify some of the labels

        self.project.data.loc[copyfile,:] = self.project.data.loc[self.file,:]
        self.project.data.loc[copyfile, self.key[-1]] = copy.UID[-1]

        return copy

    def _delete_image(self):
        """
        Deletes the image
        """ 
        file = self.file
        if os.path.exists(file):
            os.remove(file)
        self.project.data = self.project.data.drop(file) 
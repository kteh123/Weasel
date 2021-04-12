class ObjectList(list):
    """
    A class for handling a list of DICOM objects of the same type. 
    """
    def __init__(self, *args):
        if len(args) == 0:
            obj_list = []
        else:
            obj_list = args[0]
        super().__init__(obj_list)

    @property
    def files(self):
        """
        Returns a list of filepaths of the images in the list
        """
        files = []
        for item in self:
            files.append(item.files())
        return files

    @property
    def project(self):
        """
        Returns the project 
        """
        if self != []:
            return self[0].project

    @property
    def ui(self):
        """
        Returns the user interface object
        """ 
        if self != []: 
            return self.project.ui     

    @property
    def data(self):
        """
        Returns a DataFrame with all items in the list 
        """
        if self != []: 
            data = self.project.data
            data = data.loc[self.files, :]
            return data

    def is_an_image(self):
        """
        Returns True if the items in the list are images 
        """
        if self != []:
            return self[0].is_an_image()

    def is_a_patient(self):
        """
        Returns True if the items in the list are patients 
        """
        if self != []:
            return self[0].is_a_patient()

    def images(self):
        """
        Returns a list of all images in the list
        """        
        images = ObjectList()
        for item in self:
            images += item.images()                      
        return images 

    def copy(self, msg='Copying..'):
        """
        Returns a copy of the list. 
        """
        copy = ObjectList()
        if self == []: 
            return copy
        self.ui.progress_bar(max=len(self), msg=msg)
        for i, item in enumerate(self): 
            self.ui.update_progress_bar(index=i+1)
            copy.append(item.copy())
        self.ui.close_progress_bar()
        return copy

    def delete(self, msg='Deleting..'):
        """
        Deletes all items in the list. 
        """
        if self == []: 
            return
        self.ui.progress_bar(max=len(self), msg=msg)
        for i, item in enumerate(self):  
            self.ui.update_progress_bar(index=i+1)
            item.delete()
        self.ui.close_progress_bar()
        self.clear()
        
    def children(self):
        """
        Returns a list of all children of all items in the list 
        """
        children = ObjectList()
        for item in self:
            children += item.children()
        return children

    def parents(self):
        """
        Returns a list with the unique parents of all objects in the list
        """ 
        parents = ObjectList()
        for item in self:
            parent = item.parent()
            if parent not in parents:
                parents.append(parent)
        return parents

    def new_parent(self):
        """
        Creates a new parent for the items in the list
        """  
        if self == []: 
            return
        if self.is_a_patient():
            return self.project
        parents = self.parents()
        if len(parents) == 1:
            return parents[0].parent().new_child()
        else:
            return parents.new_parent().new_child()    
    
    def group(self, msg='Grouping..'):
        """
        Groups all items into a new parent
        """
        if self == []: 
            return
        if self.is_a_patient():
            return
        parent = self.new_parent()
        self.ui.progress_bar(max=len(self), msg=msg)
        for i, child in enumerate(self):  
            self.ui.update_progress_bar(index=i+1)
            parent.adopt(child)
        self.ui.close_progress_bar()
        return parent

    def merge(self, msg='Merging..'):
        """
        Groups all objects into a new object at the same level
        """ 
        if self == []: 
            return
        if self.is_an_image():
            return
        return self.children().group(msg=msg)


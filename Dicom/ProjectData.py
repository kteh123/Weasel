import pydicom
import pandas

class ProjectData():
    """
    Creates a pandas DataFrame instance.
    """

    def dataframe(self, files, tags=[]):
        """
        Read specified DICOM tags from files and return a pandas dataframe
        where each row corresponds to a valid DICOM file and 
        the columns present values of tags requested,
        except for the first column which indicates the checked state on the display.
        If no tags are provided, only the default tags are read.
        """

        default_tags = [ # These are used to construct human-readable labels
            'PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID', 
            'PatientName', 'StudyDescription', 'SeriesDescription', 'SeriesNumber', 'InstanceNumber', 
            'StudyDate', 'SeriesDate', 'AcquisitionDate',
            'StudyTime', 'SeriesTime', 'AcquisitionTime' ] 
        tags = list(set(default_tags + tags)) # Unique tags only

        self.ui.cursor_arrow_to_hourglass()
        self.ui.progress_bar(max=len(files), msg='Reading DICOM files')

        dicom_files = []
        array = []

        for i, filepath in enumerate(files):
            self.ui.update_progress_bar(index=i+1)
            dataset = pydicom.dcmread(filepath, specific_tags=tags, force=True) 
            if dataset.__class__.__name__ == 'FileDataset':
                if 'StudyInstanceUID' in dataset:
                    dicom_files.append(filepath)
                    row = [False]
                    for attribute in tags:
                        if attribute not in dataset:
                            setattr(dataset, attribute, 'Unknown')
                        row.append(dataset[attribute].value)
                    array.append(row)

        self.ui.close_progress_bar()  
        self.ui.cursor_hourglass_to_arrow()   

        return pandas.DataFrame(array, index=dicom_files, columns=['Checked']+tags)

    def load(self):
        """
        Loads the project data by reading all files in the project folder
        """  
        files = self.files()
        self.data = self.dataframe(files) 

    def write(self):
        """
        Writes the project data to disk
        """
        file = self.csv()
        self.data.to_csv(file)
        self.write_xml() # Retire

    def read(self):
        """
        Reads a DataFrame from a CSV file
        """  
        file = self.csv()  
        self.data = pandas.read_csv(file, index_col=0)

               



    




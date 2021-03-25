import pydicom
import pandas

class WeaselDicom():
    """
    Creates a pandas DataFrame instance.
    """

    def dataframe(self, files, tags=[]):
        """
        Read specified DICOM tags from files and return a pandas dataframe
        where each row corresponds to a valid DICOM file and 
        the columns present values of tags requested.
        If no tags are provided, a set of default tags is used.
        """
 
        if len(tags) == 0:
            tags = [
                'PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID', 
                'PatientName', 'StudyDescription', 'SeriesDescription', 'SeriesNumber', 'InstanceNumber', 
                'StudyDate', 'SeriesDate', 'AcquisitionDate',
                'StudyTime', 'SeriesTime', 'AcquisitionTime' ]

        self.cursor_arrow_to_hourglass()
        self.progress_bar(max=len(files), msg='Reading DICOM files')

        dicom_files = []
        array = []

        for i, filepath in enumerate(files):
            self.update_progress_bar(index=i+1)
            dataset = pydicom.dcmread(filepath, specific_tags=tags, force=True) 
            if dataset.__class__.__name__ == 'FileDataset':
                if hasattr(dataset, 'StudyInstanceUID'):
                    dicom_files.append(filepath)
                    row = []
                    for attribute in tags:
                        if hasattr(dataset, attribute):
                            row.append(dataset[attribute].value)
                        else:
                            row.append('Unknown')
                    array.append(row)

        self.close_progress_bar()  
        self.cursor_hourglass_to_arrow()   

        return pandas.DataFrame(array, index=dicom_files, columns=tags)

    def read_folder(self):
        """
        Reads default tags of all DICOM files in the project folder
        Saves the results as a dataframe in the project attribute 
        """
        files = self.files()
        self.project = self.dataframe(files)
        if not self.project.empty:
            self.write_xml()

    def write_csv(self):
        """
        Saves a DataFrame as a CSV file
        """
        self.message(msg="Writing CSV file")
        file = self.csv()
        self.project.to_csv(file)
        self.close_message() 

    def read_csv(self):
        """
        Reads a DataFrame from a CSV file
        """ 
        self.message(msg="Reading CSV file")
        file = self.csv()  
        self.project = pandas.read_csv(file, index_col=0)
        self.close_message()

    def copy_dicom_file(self, file):
        """
        Returns a copy of a dicom file in the same series
        """ 
        UID = pydicom.uid.generate_uid()
        copy = self.derived_file(UID + '.dcm')

        dataset = pydicom.dcmread(file)
        dataset.SOPInstanceUID = UID
        dataset.save_as(copy)

        row = self.project.loc[file]
        self.project.append(row, index=copy)
        self.project.loc[copy].SOPInstanceUID = UID

        return copy


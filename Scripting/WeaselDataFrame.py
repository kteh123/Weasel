import pydicom
import pandas

class WeaselDataFrame():
    """creates a pandas DataFrame instance.
    """

    def dataframe(self, files, tags=[]):
        """Read files and return a pandas dataframe
        where each row corresponds to a valid DICOM file and 
        the columns present values of tags requested.
        """
        if len(tags) == 0:
            tags = [
                'PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID', 
                'PatientName', 'StudyDescription', 'SeriesDescription', 'SeriesNumber', 'InstanceNumber', 
                'StudyDate', 'SeriesDate', 'AcquisitionDate',
                'StudyTime', 'SeriesTime', 'AcquisitionTime' ]
        array = []
        dicom_files = []
        self.progress_bar(max=len(files), msg='Reading DICOM folder')
        for i, filepath in enumerate(files):
            self.update_progress_bar(index = i+1)
            dataset = pydicom.dcmread(filepath, specific_tags=tags, force=True) 
            if dataset.__class__.__name__ == 'FileDataset':
                row = []
                for attribute in tags:
                    if hasattr(dataset, attribute):
                        row.append(dataset[attribute].value)
                    else:
                        row.append('Unknown')
                array.append(row)
                dicom_files.append(filepath)

        self.close_progress_bar()      
        return pandas.DataFrame(array, index=dicom_files, columns=tags)

    def folder_to_dataframe(self, folder):
        """ 
        Creates a Weasel dataframe directly from the folder
        """
        files = self.files(folder)
        return self.dataframe(files)
import pydicom
import pandas

def Files_to_DicomDataFrame(files, tags, weasel):
    """Read files and return a pandas dataframe
    where each row corresponds to a valid DICOM file and 
    the columns present values of tags requested.
    """
    array = []
    dicom_files = []
    weasel.progress_bar(max=len(files), msg='Reading DICOM folder')
    for i, filepath in enumerate(files):
        weasel.update_progress_bar(index = i+1)
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
            
    return pandas.DataFrame(array, index=dicom_files, columns=tags)
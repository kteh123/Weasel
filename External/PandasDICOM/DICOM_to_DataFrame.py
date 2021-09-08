import pydicom
import pandas


def DICOM_to_DataFrame(files, tags=[]):
    """Summarises a DICOM folder as a DataFrame.

    Parameters
    ----------
    files -- a list of filepaths to DICOM files
    tags -- a list of tags to be read. If not provided, a default list is used

    Returns
    -------
    A Pandas dataframe with one row per file
    The index is the file path 
    Each column corresponds to a Tag in the list of Tags
    """

    if tags == []:
        tags = [ 
            'PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID', 
            'PatientName', 'StudyDescription', 'SeriesDescription', 'SeriesNumber', 'InstanceNumber', 
            'StudyDate', 'SeriesDate', 'AcquisitionDate',
            'StudyTime', 'SeriesTime', 'AcquisitionTime' ] 

    array = []
    dicom_files = []
    
    for filepath in files:
        dataset = pydicom.dcmread(filepath, force=True)
        if isinstance(dataset, pydicom.dataset.FileDataset):
            if 'TransferSyntaxUID' in dataset.file_meta:
                row = []
                for tag in tags:
                    if tag not in dataset:
                        value = None
                    else:
                        value = dataset[tag].value
                    row.append(value)
                array.append(row)
                dicom_files.append(filepath) 

    return pandas.DataFrame(array, index=dicom_files, columns=tags)




               



    




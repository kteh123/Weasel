import os
from Scripting.Files_to_DicomDataFrame import Files_to_DicomDataFrame

def Folder_to_DicomDataFrame(folder, weasel):
    """Read all DICOM files in a folder and return a pandas dataframe
    where each row corresponds to a valid DICOM file and 
    the columns present values of tags requested.
    """
    files = [item.path for item in scan_tree(folder) if item.is_file()]
    tags = [
        'PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID', 
        'PatientName', 'StudyDescription', 'SeriesDescription', 'SeriesNumber', 'InstanceNumber', 
        'StudyDate', 'SeriesDate', 'AcquisitionDate',
        'StudyTime', 'SeriesTime', 'AcquisitionTime' ]
    return Files_to_DicomDataFrame(files, tags, weasel)

def scan_tree(folder):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(folder):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry
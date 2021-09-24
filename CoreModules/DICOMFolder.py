""" Class for reading and summarizing contents of a DICOM folder.

The DICOMfolder reads a folder containing DICOM files,
summarizes the content as a pandas DataFrame, and exports as csv.
DICOMFolder can also turn the DataFrame into an ElementTree and save
that as an XML file. DICOMfolder also handles conversion of multi-frame 
DICOM data into single frame.

    Examples:

    folder = DICOMfolder()
    for f in folder.files(): print(f)
    folder.read_dataframe()

"""

import os
import sys
import pathlib
import subprocess
import pydicom
import pandas
import xml.etree.ElementTree as ET
from xml.dom import minidom

from PyQt5.QtWidgets import (QApplication, QFileDialog, QWidget, QMainWindow)




class DICOMFolder():

    def __init__(self, parent=None, path=None):

        self.parent = parent
        self.path = path
        self.dataframe = None
        self.element_tree = None

        if self.parent is None:
            app = QApplication(sys.argv)
            self.parent = QMainWindow()
        if self.path is None:
            self.select_folder()
        
    def select_folder(self):

        self.path = QFileDialog.getExistingDirectory(
            parent = self.parent, 
            caption = "Please select a folder with DICOM data", 
            directory = os.path.dirname(sys.argv[0]), 
            options = QFileDialog.ShowDirsOnly)

    def files(self):
        """Returns all files in the folder."""

        return [item.path for item in scan_tree(self.path) if item.is_file()]

    def create_dataframe(self):
        """Summarises a DICOM folder as a DataFrame.

        Creates
        -------
        dataframe : pandas.DataFrame
            A Pandas dataframe with one row per file
            The index is the file path 
            Each column corresponds to a Tag in the list of Tags
        """
        all_files = self.files()
        self.dataframe = read_dataframe(all_files)

    def write_csv(self):
        """ Writes a DataFrame as a CSV file"""

        file = self.csv()
        self.dataframe.to_csv(file)

    def read_csv(self):
        """Reads the DataFrame from a CSV file """  

        file = self.csv()
        self.dataframe = pandas.read_csv(file, index_col=0)

    def csv(self):
        """ Returns the file path of the CSV file"""

        filename = os.path.basename(os.path.normpath(self.path)) + ".csv"
        return os.path.join(self.path, filename)

    def create_element_tree(self):
        """
        Converts a Pandas DataFrame representing a DICOM folder into an ElementTree. 

        Parameters
        ----------
        data_frame: pandas DataFrame created by DICOM_to_DataFrame

        Returns
        -------
        An XML ElementTree representing the DICOM object structure
        """   
        self.element_tree = element_tree_from_dataframe(self.dataframe)

    def write_xml(self):
        """Saves an ElementTree as an XML file

        Arguments
        ---------
        element_tree: An XML ElementTree
        xml_file: path to the xml file
        """
        file = self.xml()
        xml_string = ET.tostring(self.element_tree, encoding='utf-8')
        xml_string = minidom.parseString(xml_string).toprettyxml(encoding="utf-8", indent="  ")
        with open(file, "wb") as f: f.write(xml_string) 

    def read_xml(self):
        """Creates an ElementTree from an XML file""" 

        file = self.xml()
        self.element_tree = ET.parse(file)

    def xml(self):
        """ Returns the file path of the XML file"""

        filename = os.path.basename(os.path.normpath(self.path)) + ".xml"
        return os.path.join(self.path, filename)


    def drop_multiframe(self):
        """Drop multi-frame data from the dataframe without deleting the files"""

        singleframe = self.dataframe.NumberOfFrames.isnull() 
        multiframe = singleframe == False
        if multiframe.sum() != 0: 
            files = self.dataframe[multiframe].index.values.tolist()
            self.dataframe.drop(index=files, inplace=True) 
            self.write_csv()

    def convert_multiframe(self):
        """Converts multi-frame into single-frame data"""

        singleframe = self.dataframe.NumberOfFrames.isnull() 
        multiframe = singleframe == False
        if multiframe.sum() == 0: 
            return 
        for filepath, image in self.dataframe[multiframe].iterrows():
            singleframe_files, fail = split_multiframe(filepath, str(image.SeriesDescription))
            if fail == 0: 
                # add the single frame files to the dataframe
                singleframe_df = read_dataframe(singleframe_files) 
                self.dataframe = pandas.concat([self.dataframe, singleframe_df])
                # delete the original multiframe file
                os.remove(filepath)
                self.dataframe.drop(index=filepath, inplace=True)
        self.write_csv()


def read_dataframe(files):
    """Creates a dataframe from a list of files.

    Arguments
    ---------
    files : [str]
        A list of filepaths to read
    """
    tags = ['PatientID', 'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID',
            'PatientName', 'StudyDescription', 'SeriesDescription', 'SequenceName', 'SeriesNumber', 'InstanceNumber',
            'StudyDate', 'SeriesDate', 'AcquisitionDate',
            'StudyTime', 'SeriesTime', 'AcquisitionTime', 
            'NumberOfFrames']

    array = []
    dicom_files = []
    
    for file in files:
        # print(file)
        dataset = pydicom.dcmread(file, force=True)
        if isinstance(dataset, pydicom.dataset.FileDataset):
            if 'TransferSyntaxUID' in dataset.file_meta:
                row = [False]  # Default Check state
                for tag in tags:
                    if tag not in dataset:
                        value = None
                    else:
                        value = dataset[tag].value
                    row.append(value)
                array.append(row)
                dicom_files.append(file) 
    columns = ['Checked']
    columns.extend(tags)
    return pandas.DataFrame(array, index=dicom_files, columns=columns)


def element_tree_from_dataframe(df):
    """
    Converts a Pandas DataFrame representing a DICOM folder into an ElementTree. 

    Parameters
    ----------
    data_frame: pandas DataFrame created by DICOM_to_DataFrame

    Returns
    -------
    An XML ElementTree representing the DICOM object structure
    """   

    element_tree = ET.Element('DICOM')
    comment = ET.Comment('Element Tree representing a DICOM folder')
    element_tree.append(comment)

    df.sort_values(
        ['PatientID', 'StudyInstanceUID', 'SeriesNumber', 'InstanceNumber'], 
        inplace = True)

    for subject in df.PatientID.unique():
        subject = df[df.PatientID == subject]
        labels = label(subject.iloc[0])     
        subject_element = ET.SubElement(element_tree, 'subject')
        subject_element.set('id', labels[0])
        subject_element.set('expanded', 'False')  
        subject_element.set('checked', 'True' if subject.Checked.all() else 'False') 
        for study in subject.StudyInstanceUID.unique():
            study = subject[subject.StudyInstanceUID == study]
            labels = label(study.iloc[0])
            study_element = ET.SubElement(subject_element, 'study')
            study_element.set('id', labels[1])
            study_element.set('expanded', 'False') 
            study_element.set('checked', 'True' if study.Checked.all() else 'False')  
            for series in study.SeriesInstanceUID.unique():
                series = study[study.SeriesInstanceUID == series]
                labels = label(series.iloc[0])
                series_element = ET.SubElement(study_element, 'series')
                series_element.set('id', labels[2])
                series_element.set('expanded', 'False') 
                series_element.set('checked', 'True' if series.Checked.all() else 'False')  
                for filepath, image in series.iterrows():
                    labels = label(image)
                    image_element = ET.SubElement(series_element, 'image')
                    image_element.set('checked', 'True' if series.Checked.all() else 'False')  
                    ET.SubElement(image_element, 'label').text = labels[3]
                    ET.SubElement(image_element, 'name').text = filepath
                    ET.SubElement(image_element, 'time').text = labels[5]
                    ET.SubElement(image_element, 'date').text = labels[4]
    return element_tree


def label(image):
    """Creates human readable labels for a DICOM image.

    Arguments
    --------- 
    image: A row in a DataFrame or a pydicom DataSet

    Returns
    -------
    A tuple of strings
    """ 

    subject_label = 'Name: ' + str(image.PatientName)
    subject_label += ' [Patient ID = ' + str(image.PatientID) + ']'
    study_label = 'Description: ' + str(image.StudyDescription) 
    study_label += ' [Date = ' + str(image.StudyDate) + ", "
    study_label += 'Time = ' + str(image.StudyTime).split(".")[0] +']'
    series_label = 'Description: ' + str(image.SeriesDescription)
    series_label += '[Nr = ' + str(image.SeriesNumber) + "]"
    image_label = 'Nr: ' + str(image.InstanceNumber).zfill(6)

    SeriesTime = str(image.AcquisitionTime)
    SeriesDate = str(image.StudyDate)

    """Bugs - commenting out for now 
    if image.AcquisitionTime is not None:

    SeriesTime = str(image.SeriesTime)
    SeriesDate = str(image.SeriesDate)

        try:
            SeriesTime = datetime.datetime.strptime(str(image.AcquisitionTime), '%H%M%S').strftime('%H:%M')
        except:
            SeriesTime = datetime.datetime.strptime(str(image.AcquisitionTime), '%H%M%S.%f').strftime('%H:%M')
        try:
            SeriesDate = datetime.datetime.strptime(str(image.AcquisitionDate), '%Y%m%d').strftime('%d/%m/%Y')
        except:
            SeriesDate = datetime.datetime.strptime(str(image.StudyDate), '%Y%m%d').strftime('%d/%m/%Y')
    elif image.SeriesTime is not None:  # Enhanced MRI
        try:
            SeriesTime = datetime.datetime.strptime(str(image.SeriesTime), '%H%M%S').strftime('%H:%M')
        except:
            SeriesTime = datetime.datetime.strptime(str(image.SeriesTime), '%H%M%S.%f').strftime('%H:%M')
        try:
            SeriesDate = datetime.datetime.strptime(str(image.SeriesDate), '%Y%m%d').strftime('%d/%m/%Y')
        except:
            SeriesDate = datetime.datetime.strptime(str(image.StudyDate), '%Y%m%d').strftime('%d/%m/%Y')
    else:
        SeriesTime = datetime.datetime.strptime('000000', '%H%M%S').strftime('%H:%M')
        SeriesDate = datetime.datetime.strptime('20000101', '%Y%m%d').strftime('%d/%m/%Y')
    """

    return (subject_label, study_label, series_label, image_label, 
            SeriesDate, SeriesTime)
      

def split_multiframe(filepath, description):
    """Splits a multi-frame image into single frames"""

    # Run the dcm4che emf2sf
    script = 'emf2sf'
    multiframeDir = os.path.dirname(filepath)
    fileBase = "SingleFrame_"
    fileBaseFlag = fileBase + "000000_" + description
    command = [program(script), "--inst-no", "'%s'", "--not-chseries", "--out-dir", multiframeDir, "--out-file", fileBaseFlag, filepath]
    try:
        fail = subprocess.call(command, stdout=subprocess.PIPE)
    except Exception as e:
        fail = 1
        print('Error in ' + script + ': ' + str(e)) 
        print('Error in dcm4che: Could not split the detected Multi-frame DICOM file.\n'\
                'The DICOM file ' + filepath + ' was not deleted.')
        logger.exception('Error in ' + script + ': ' + str(e))

    # Return a list of newly created files
    multiframe_files_list = []
    if fail == 0:
        for new_file in os.listdir(multiframeDir):
            if new_file.startswith(fileBase):
                new_file_path = os.path.join(multiframeDir, new_file)
                multiframe_files_list.append(new_file_path)            
    return multiframe_files_list, fail


def program(script):
    """Helper function: Find the program for a given script"""

    if os.name =='nt': script += '.bat'
    program = script
    # If running Weasel as executable (SPS: THIS NEEDS TO CHANGE - CAN'T ACCOUNT FOR THAT INSIDE)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        directory = pathlib.Path(sys._MEIPASS)
    # If running Weasel as normal Python script
    else:
        directory = pathlib.Path().absolute()
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(script):
                sys.path.append(dirpath)
                program = os.path.join(dirpath, filename)
    return program


def scan_tree(directory):
    """Helper function: yield DirEntry objects for the directory."""

    for entry in os.scandir(directory):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry

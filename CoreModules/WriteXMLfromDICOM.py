"""
Class for reading the DICOM files and folders selected by the user and store its structure information in an XML file.

It ouptputs an XML file that describes a DICOM file structure that is used to build a tree view showing a visual representation of that file structure (see `TreeView.py`).
"""
import os
import sys
import time
import pathlib
import subprocess
import re
import datetime
import numpy as np
from pydicom import Dataset, DataElement, dcmread
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMessageBox)

import logging
logger = logging.getLogger(__name__)


def get_files_info(scan_directory):
    """This method returns the number of files and subfolders in a folder. It doesn't mean that they are all DICOM.
    """
    try:
        logger.info("WriteXMLfromDICOM.get_files_info called")
        number_files = 0
        number_folders = 0
        for _, sub_folders, file_list in os.walk(scan_directory):
            number_files += len(file_list)
            number_folders += len(sub_folders)
        if number_files == 0:
            raise FileNotFoundError('No files present in the selected folder')
        return number_files, number_folders
    except Exception as e:
        print('Error in WriteXMLfromDICOM.get_files_info: ' + str(e))
        logger.exception('Error in WriteXMLfromDICOM.get_files_info: ' + str(e))


def atof(text):
    """ This function is auxiliary for the natural sorting of the paths names"""
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    """
    return [atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text)]


def series_sort(elem):
    """
    This is a helper function that will be used in key argument of sorted()
    in order to sort the list of series by series number
    """
    # return int(elem.split("_")[-1]) # USE THIS IF %SeriesDescription_%SeriesNumber
    return int(elem.split("_")[0])


def scan_tree(scan_directory):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(scan_directory):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_tree(entry.path)
        else:
            yield entry


def get_scan_data(scan_directory, progBarMsg, self):
    """This method opens all DICOM files in the provided path recursively and saves 
        each file individually as a variable into a list/array.
    """
    try:
        logger.info("WriteXMLfromDICOM.get_scan_data called")
        list_paths = list()
        list_dicom = list()
        file_list = [item.path for item in scan_tree(scan_directory) if item.is_file()]
        file_list.sort(key=natural_keys)
        multiframe_files_list = list()
        self.progress_bar(max=len(file_list), index=0, msg=progBarMsg, title="Loading DICOM")
        fileCounter = 0
        multiframeCounter = 0
        for filepath in file_list:
            try:
                fileCounter += 1
                self.update_progress_bar(index=fileCounter)
                list_tags = ['InstanceNumber', 'SOPInstanceUID', 'PixelData', 'FloatPixelData', 'DoubleFloatPixelData', 'AcquisitionTime',
                             'AcquisitionDate', 'SeriesTime', 'SeriesDate', 'PatientName', 'PatientID', 'StudyDate', 'StudyTime', 
                             'SeriesDescription', 'StudyDescription', 'SequenceName', 'ProtocolName', 'SeriesNumber', 'PerFrameFunctionalGroupsSequence',
                             'StudyInstanceUID', 'SeriesInstanceUID']
                dataset = dcmread(filepath, specific_tags=list_tags) # Check the force=True flag once in a while
                if not hasattr(dataset, 'SeriesDescription') and not hasattr(dataset, 'StudyDescription'):
                    elemSeries = DataElement(0x0008103E, 'LO', 'No Series Description')
                    elemStudy = DataElement(0x00081030, 'LO', 'No Study Description')
                    with dcmread(filepath, force=True) as ds:
                        ds.add(elemSeries)
                        ds.add(elemStudy)
                        ds.save_as(filepath)
                    dataset.SeriesDescription = 'No Series Description'
                    dataset.StudyDescription = 'No Study Description'
                elif not hasattr(dataset, 'SeriesDescription'):
                    elem = DataElement(0x0008103E, 'LO', 'No Series Description')
                    with dcmread(filepath, force=True) as ds:
                        ds.add(elem)
                        ds.save_as(filepath)
                    dataset.SeriesDescription = 'No Series Description'
                elif not hasattr(dataset, 'StudyDescription'):
                    elem = DataElement(0x00081030, 'LO', 'No Study Description')
                    with dcmread(filepath, force=True) as ds:
                        ds.add(elem)
                        ds.save_as(filepath)
                    dataset.StudyDescription = 'No Study Description'
                # If Multiframe, use dcm4che to split into single-frame
                if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                    multiframeCounter += 1
                    if multiframeCounter == 1:
                        buttonReply = QMessageBox.question(self, "Multiframe DICOM files found",
                                      "Weasel detected the existence of multiframe DICOM in the selected directory and will convert these. This operation requires overwriting the original files. Do you wish to proceed?", 
                                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                        if buttonReply == QMessageBox.Cancel:
                            print("User chose not to convert Multiframe DICOM. Loading process halted.")
                            self.close_progress_bar()
                            return None, None
                    if os.name =='nt':
                        multiframeScript = 'emf2sf.bat'
                    else:
                        multiframeScript = 'emf2sf'
                    multiframeProgram = multiframeScript
                    # If running Weasel as executable
                    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                        search_directory = pathlib.Path(sys._MEIPASS)
                    # If running Weasel as normal Python script
                    else:
                        search_directory = pathlib.Path().absolute()
                    for dirpath, _, filenames in os.walk(search_directory):
                        for individualFile in filenames:
                            if individualFile.endswith(multiframeScript):
                                sys.path.append(dirpath)
                                multiframeProgram = os.path.join(dirpath, individualFile)
                    multiframeDir = os.path.dirname(filepath)
                    fileBase = "SingleFrame_"
                    fileBaseFlag = fileBase + "000000_" + str(dataset.SeriesDescription)
                    #if hasattr(dataset, 'SeriesDescription'):
                    #elif hasattr(dataset, 'ProtocolName'):
                    #    fileBaseFlag = fileBase + "00_" + str(dataset.ProtocolName)
                    #elif hasattr(dataset, 'SequenceName'):
                    #    fileBaseFlag = fileBase + "00_" + str(dataset.SequenceName)
                    # Run the dcm4che emf2sf
                    self.update_progress_bar(index=fileCounter, msg="Multiframe DICOM detected. Converting to single frame ...")
                    multiframeCommand = [multiframeProgram, "--inst-no", "'%s'", "--not-chseries", "--out-dir", multiframeDir, "--out-file", fileBaseFlag, filepath]
                    try:
                        commandResult = subprocess.call(multiframeCommand, stdout=subprocess.PIPE)
                    except Exception as e:
                        commandResult = 1
                        print('Error in ' + multiframeScript + ': ' + str(e)) 
                        logger.exception('Error in ' + multiframeScript + ': ' + str(e))
                    # Get list of filenames with fileBase and add to multiframe_files_list
                    if commandResult == 0:
                        for new_file in os.listdir(multiframeDir):
                            if new_file.startswith(fileBase):
                                multiframe_files_list.append(os.path.join(multiframeDir, new_file))
                        # Discussion about removing the original file or not
                        os.remove(filepath)
                    else:
                        print('Error in dcm4che: Could not split the detected Multi-frame DICOM file.\n'\
                              'The DICOM file ' + filepath + ' was not deleted.')
                    continue
                if (hasattr(dataset, 'InstanceNumber') and hasattr(dataset, 'SOPInstanceUID') and 
                    any(hasattr(dataset, attr) for attr in ['PixelData', 'FloatPixelData', 'DoubleFloatPixelData'])
                    and ('DIRFILE' not in filepath) and ('DICOMDIR' not in filepath)):
                    list_paths.extend([filepath])
                    list_dicom.extend([dataset])
            except:
                continue
        self.close_progress_bar()
        # The following segment is to deal with the multiframe images if there is any.
        # The np.unique removes files that might have appended more than once previously
        fileCounter = 0
        if len(np.unique(multiframe_files_list)) > 0:
            self.progress_bar(max=len(np.unique(multiframe_files_list)), index=0, msg="Reading {} single frame DICOM files converted earlier".format(len(np.unique(multiframe_files_list))), title="Load ROI")
            for singleframe in np.unique(multiframe_files_list):
                try:
                    fileCounter += 1
                    self.update_progress_bar(index=fileCounter)
                    list_tags = ['InstanceNumber', 'SOPInstanceUID', 'PixelData', 'FloatPixelData', 'DoubleFloatPixelData', 'SliceLocation', (0x2001, 0x100a),
                                 'AcquisitionTime', 'AcquisitionDate', 'SeriesTime', 'SeriesDate', 'PatientName', 'PatientID', 'StudyDate', 'StudyTime', 
                                 'SeriesDescription', 'StudyDescription', 'SequenceName', 'ProtocolName', 'SeriesNumber', 'StudyInstanceUID', 'SeriesInstanceUID']
                    dataset = dcmread(singleframe, specific_tags=list_tags) # Check the force=True flag once in a while
                    # The multiframe converter stores SliceLocation in tag (0x2001, 0x100a), so this step is to store it in SliceLocation.
                    dicomTag = (0x2001, 0x100a)
                    sliceValue = dataset[dicomTag].value
                    if not hasattr(dataset, 'SliceLocation'):
                        elem = DataElement(0x00201041, 'DS', sliceValue)
                        with dcmread(singleframe, force=True) as ds:
                            ds.add(elem)
                            ds.save_as(singleframe)
                    dataset.SliceLocation = sliceValue
                    if (hasattr(dataset, 'InstanceNumber') and hasattr(dataset, 'SOPInstanceUID') and 
                        any(hasattr(dataset, attr) for attr in ['PixelData', 'FloatPixelData', 'DoubleFloatPixelData'])
                        and ('DIRFILE' not in singleframe) and ('DICOMDIR' not in singleframe)):
                        list_paths.extend([singleframe])
                        list_dicom.extend([dataset])
                except:
                    continue
            self.close_progress_bar()
        if len(list_dicom) == 0:
            self.message(msg="No DICOM files present in the selected folder")
            raise FileNotFoundError('No DICOM files present in the selected folder')

        return list_dicom, list_paths
    except Exception as e:
        print('Error in WriteXMLfromDICOM.get_scan_data: ' + str(e))
        logger.exception('Error in function WriteXMLfromDICOM.get_scan_data: ' + str(e))


def get_study_series(dicom):
    """This method extracts information about subject, study and series 
    of a single DICOM file and returns a list of strings. It is used in the `build_dictionary` method.
    """
    try:
        logger.info("WriteXMLfromDICOM.get_study_series called")
        subject = str(dicom.PatientID)
        study = str(dicom.StudyDate) + "_" + str(dicom.StudyTime).split(".")[0] + "_" + str(dicom.StudyDescription)
        sequence = str(dicom.SeriesDescription)
        series_number = str(dicom.SeriesNumber)
        study_uid = str(dicom.StudyInstanceUID)
        series_uid = str(dicom.SeriesInstanceUID)
        return subject, study, sequence, series_number, study_uid, series_uid
    except Exception as e:
        print('Error in WriteXMLfromDICOM.get_study_series: ' + str(e))
        logger.exception('Error in WriteXMLfromDICOM.get_study_series: ' + str(e))


def build_dictionary(list_dicom):
    """This method takes the list of all DICOM files, extracts all the information regarding 
    the subjects, studies and series they belong to and store that in a hierarchical dictionary."""
    try:
        logger.info("WriteXMLfromDICOM.build_dictionary called")
        xml_dict = {}
        for dicomfile in list_dicom:
            subject, study, sequence, series_number, _, _ = get_study_series(dicomfile)
            if subject not in xml_dict:
                xml_dict[subject] = defaultdict(list)
            xml_dict[subject][study].append(series_number + "_" + sequence)
        for subject in xml_dict:
            for study in xml_dict[subject]:
                xml_dict[subject][study] = sorted(np.unique(xml_dict[subject][study]), key=series_sort)
        return xml_dict
    except Exception as e:
        print('Error in WriteXMLfromDICOM.build_dictionary: ' + str(e))
        logger.exception('Error in WriteXMLfromDICOM.build_dictionary: ' + str(e))


def open_dicom_to_xml(xml_dict, list_dicom, list_paths):
    """This method opens all DICOM files in the given list and saves 
        information from each file individually to an XML tree/structure.
    """
    try:    
        logger.info("WriteXMLfromDICOM.open_dicom_to_xml called")
        DICOM_XML_object = ET.Element('DICOM')
        comment = ET.Comment('WARNING: PLEASE, DO NOT MODIFY THIS FILE \n This .xml file is automatically generated by a script that reads folders containing DICOM files. \n Any changes can affect the software\'s functionality, so do them at your own risk')
        DICOM_XML_object.append(comment)

        for subject in xml_dict:
            subject_element = ET.SubElement(DICOM_XML_object, 'subject')
            subject_element.set('id', subject)
            subject_element.set('checked', 'False')  #added by SS 16.03.21
            for study in xml_dict[subject]:
                study_element = ET.SubElement(subject_element, 'study')
                study_element.set('id', study)
                study_element.set('checked', 'False')  #added by SS 16.03.21
                for series in xml_dict[subject][study]:
                    series_element = ET.SubElement(study_element, 'series')
                    series_element.set('id', series)
                    series_element.set('checked', 'False')  #added by SS 16.03.21
        for index, dicomfile in enumerate(list_dicom):
            subject, study, sequence, series_number, study_uid, series_uid = get_study_series(dicomfile)
            subject_search_string = "./*[@id='" + subject + "']"
            study_root = DICOM_XML_object.find(subject_search_string)
            study_search_string = "./*[@id='" + study + "']"
            series_root = study_root.find(study_search_string)
            series_search_string = "./*[@id='"+ series_number + "_" + sequence + "']"
            image_root = series_root.find(series_search_string)
            series_root.set('uid', study_uid)
            image_root.set('uid', series_uid)
            image_element = ET.SubElement(image_root, 'image')
            image_element.set('checked', 'False')  #added by SS 16.03.21
            label = ET.SubElement(image_element, 'label')
            name = ET.SubElement(image_element, 'name')
            time = ET.SubElement(image_element, 'time')
            date = ET.SubElement(image_element, 'date')
            label.text = str(dicomfile.InstanceNumber).zfill(6)
            #label.text = str(len(list(image_root.iter('image')))).zfill(6)
            name.text = os.path.normpath(list_paths[index])
            
            # The next lines save the time and date to XML - They consider multiple/eventual formats
            if len(dicomfile.dir("AcquisitionTime"))>0:
                try:
                    time.text = datetime.datetime.strptime(dicomfile.AcquisitionTime, '%H%M%S').strftime('%H:%M')
                except:
                    time.text = datetime.datetime.strptime(dicomfile.AcquisitionTime, '%H%M%S.%f').strftime('%H:%M')
                try:
                    date.text = datetime.datetime.strptime(dicomfile.AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
                except:
                    date.text = datetime.datetime.strptime(dicomfile.StudyDate, '%Y%m%d').strftime('%d/%m/%Y')
            elif len(dicomfile.dir("SeriesTime"))>0:
                # It means it's Enhanced MRI
                try:
                    time.text = datetime.datetime.strptime(dicomfile.SeriesTime, '%H%M%S').strftime('%H:%M')
                except:
                    time.text = datetime.datetime.strptime(dicomfile.SeriesTime, '%H%M%S.%f').strftime('%H:%M')
                try:
                    date.text = datetime.datetime.strptime(dicomfile.SeriesDate, '%Y%m%d').strftime('%d/%m/%Y')
                except:
                    date.text = datetime.datetime.strptime(dicomfile.StudyDate, '%Y%m%d').strftime('%d/%m/%Y')
            else:
                time.text = datetime.datetime.strptime('000000', '%H%M%S').strftime('%H:%M')
                date.text = datetime.datetime.strptime('20000101', '%Y%m%d').strftime('%d/%m/%Y')
        return DICOM_XML_object
    except Exception as e:
        print('Error in WriteXMLfromDICOM.open_dicom_to_xml: ' + str(e))
        logger.exception('Error in WriteXMLfromDICOM.open_dicom_to_xml: ' + str(e))


def create_XML_file(DICOM_XML_object, scan_directory):
    """This method creates a new XML file with the based on the structure of the selected DICOM folder"""
    try:
        logger.info("WriteXMLfromDICOM.create_XML_file called")
        xmlstr = ET.tostring(DICOM_XML_object, encoding='utf-8')
        XML_data = minidom.parseString(xmlstr).toprettyxml(encoding="utf-8", indent="  ")
        filename = os.path.basename(os.path.normpath(scan_directory)) + ".xml"
        with open(os.path.join(scan_directory, filename), "wb") as f:
            f.write(XML_data)  
        return os.path.join(scan_directory, filename)
    except Exception as e:
        print('Error in WriteXMLfromDICOM.create_XML_file: ' + str(e))
        logger.exception('Error in WriteXMLfromDICOM.create_XML_file: ' + str(e))


def getScanDirectory(self):
    """Displays an open folder dialog window to allow the
    user to select the folder holding the DICOM files"""
    try:
        logger.info('WriteXMLfromDICOM.getScanDirectory called.')
        #cwd = os.getcwd()

        scan_directory = QFileDialog.getExistingDirectory(
            self,
            'Select the directory containing the scan', 
            self.weaselDataFolder, 
            QFileDialog.ShowDirsOnly)
        return scan_directory
    except Exception as e:
        print('Error in function WriteXMLfromDICOM.getScanDirectory: ' + str(e))
        logger.exception('Error in function WriteXMLfromDICOM.getScanDirectory: ' + str(e))


def existsDICOMXMLFile(scanDirectory):
    """This function returns True if an XML file of scan images already
    exists in the scan directory."""
    try:
        logger.info("WriteXMLfromDICOM.existsDICOMXMLFile called")
        flag = False
        with os.scandir(scanDirectory) as entries:
                for entry in entries:
                    if entry.is_file():
                        if entry.name.lower() == \
                            os.path.basename(scanDirectory).lower() + ".xml":
                            flag = True
                            break
        return flag                   
    except Exception as e:
        print('Error in function WriteXMLfromDICOM.existsDICOMXMLFile: ' + str(e))
        logger.error('Error in function WriteXMLfromDICOM.existsDICOMXMLFile: ' + str(e))


def makeDICOM_XML_File(self, scan_directory):
    """Creates an XML file that describes the contents of the scan folder,
    scan_directory.  Returns the full file path of the resulting XML file,
    which takes it's name from the scan folder."""
    try:
        logger.info("WriteXMLfromDICOM.makeDICOM_XML_File called.")
        fullFilePath = ''
        if scan_directory:
            start_time=time.time()
            numFiles, numFolders = get_files_info(scan_directory)
            if numFolders == 0:
                folder = os.path.basename(scan_directory) + ' folder.'
            else:
                folder = os.path.basename(scan_directory) + ' folder and {} '.format(numFolders) \
                    + 'subdirectory(s)'

            progBarMsg = "Collecting {} files from the {}".format(numFiles, folder)
            scans, paths = get_scan_data(scan_directory, progBarMsg, self)
            if scans and paths:
                self.message(msg="Reading data from each DICOM file", title="Loading DICOM")
                dictionary = build_dictionary(scans)
                self.update_message("Writing DICOM data to an XML file")
                xml = open_dicom_to_xml(dictionary, scans, paths)
                self.update_message("Saving XML file")
                fullFilePath = create_XML_file(xml, scan_directory)
                self.close_message()
                end_time=time.time()
                xmlCreationTime = end_time - start_time 
                #print('XML file creation time = {}'.format(xmlCreationTime))
                logger.info("WriteXMLfromDICOM.makeDICOM_XML_File returns {}."
                            .format(fullFilePath))
        return fullFilePath
    except Exception as e:
        print('Error in function WriteXMLfromDICOM.makeDICOM_XML_File: ' + str(e))
        logger.exception('Error in function WriteXMLfromDICOM.makeDICOM_XML_File: ' + str(e))
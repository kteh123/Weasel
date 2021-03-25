import os
import time
import pathlib
import subprocess
import re
import datetime
import numpy as np
from pydicom import Dataset, DataElement, dcmread, filewriter
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
import CoreModules.WEASEL.iBeatImport as iBeatImport
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image

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


def get_scan_data(scan_directory, msgWindow, progBarMsg, self):
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
        msgWindow.setMsgWindowProgBarMaxValue(self, len(file_list))
        fileCounter = 0
        multiframeCounter = 0
        for filepath in file_list:
            try:
                fileCounter += 1
                msgWindow.setMsgWindowProgBarValue(self, fileCounter)
                list_tags = ['InstanceNumber', 'SOPInstanceUID', 'PixelData', 'FloatPixelData', 'DoubleFloatPixelData', 'AcquisitionTime',
                             'AcquisitionDate', 'SeriesTime', 'SeriesDate', 'PatientName', 'PatientID', 'StudyDate', 'StudyTime', 
                             'SeriesDescription', 'SequenceName', 'ProtocolName', 'SeriesNumber', 'PerFrameFunctionalGroupsSequence',
                             'StudyInstanceUID', 'SeriesInstanceUID']
                dataset = dcmread(filepath, specific_tags=list_tags) # Check the force=True flag once in a while
                if not hasattr(dataset, 'SeriesDescription'):
                    full_dataset = dcmread(filepath)
                    full_dataset.SeriesDescription = 'No Series Description'
                    saveDICOM_Image.saveDicomToFile(full_dataset, output_path=filepath)
                    del full_dataset
                    #elem = DataElement(0x0008103E, 'LO', 'No Series Description')
                    #filewriter.write_DTvalue(filepath, elem)
                    dataset.SeriesDescription = 'No Series Description'
                # If Multiframe, use dcm4che to split into single-frame
                if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                    multiframeCounter += 1
                    if multiframeCounter == 1:
                        buttonReply = QMessageBox.question(self, "Multiframe DICOM files found",
                                      "WEASEL detected the existence of multiframe DICOM in the selected directory and will convert these. This operation requires overwriting the original files. Do you wish to proceed?", 
                                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                        if buttonReply == QMessageBox.Cancel:
                            print("User chose not to convert Multiframe DICOM. Loading process halted.")
                            msgWindow.hideProgressBar(self)
                            msgWindow.closeMessageSubWindow(self)
                            return None
                    if os.name =='nt':
                        multiframeScript = 'emf2sf.bat'
                    else:
                        multiframeScript = 'emf2sf'
                    multiframeProgram = os.path.join(pathlib.Path().absolute(), "External", "dcm4che-5.23.1", "bin", multiframeScript)
                    multiframeDir = os.path.dirname(filepath)
                    #multiframeDir = os.path.join(os.path.dirname(filepath), "SingleFrames")
                    #os.makedirs(multiframeDir, exist_ok=True)
                    fileBase = "SingleFrame_"
                    #if hasattr(dataset, 'SeriesDescription'):
                    fileBaseFlag = fileBase + "00_" + str(dataset.SeriesDescription)
                    #elif hasattr(dataset, 'ProtocolName'):
                    #    fileBaseFlag = fileBase + "00_" + str(dataset.ProtocolName)
                    #elif hasattr(dataset, 'SequenceName'):
                    #    fileBaseFlag = fileBase + "00_" + str(dataset.SequenceName)
                    # Run the dcm4che emf2sf
                    msgWindow.displayMessageSubWindow(self, "Multiframe DICOM detected. Converting to single frame ...")
                    multiframeCommand = [multiframeProgram, "--not-chseries", "--out-dir", multiframeDir, "--out-file", fileBaseFlag, filepath]
                    commandResult = subprocess.call(multiframeCommand, stdout=subprocess.PIPE)
                    # Get list of filenames with fileBase and add to multiframe_files_list
                    if commandResult == 0:
                        for new_file in os.listdir(multiframeDir):
                            if new_file.startswith(fileBase):
                                multiframe_files_list.append(os.path.join(multiframeDir, new_file))
                        # Discussion about removing the original file or not
                        os.remove(filepath)
                        msgWindow.displayMessageSubWindow(self, progBarMsg)
                        msgWindow.setMsgWindowProgBarMaxValue(self, len(file_list))
                        msgWindow.setMsgWindowProgBarValue(self, fileCounter)
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
            
        # The following segment is to deal with the multiframe images if there is any.
        # The np.unique removes files that might have appended more than once previously
        fileCounter = 0
        for singleframe in np.unique(multiframe_files_list):
            try:
                fileCounter += 1
                msgWindow.displayMessageSubWindow(self, "Reading {} single frame DICOM files converted earlier".format(len(np.unique(multiframe_files_list))))
                msgWindow.setMsgWindowProgBarMaxValue(self, len(np.unique(multiframe_files_list)))
                msgWindow.setMsgWindowProgBarValue(self, fileCounter)
                list_tags = ['InstanceNumber', 'SOPInstanceUID', 'PixelData', 'FloatPixelData', 'DoubleFloatPixelData', 'AcquisitionTime',
                             'AcquisitionDate', 'SeriesTime', 'SeriesDate', 'PatientName', 'PatientID', 'StudyDate', 'StudyTime', 
                             'SeriesDescription', 'SequenceName', 'ProtocolName', 'SeriesNumber', 'StudyInstanceUID', 'SeriesInstanceUID']
                dataset = dcmread(singleframe, specific_tags=list_tags) # Check the force=True flag once in a while
                if (hasattr(dataset, 'InstanceNumber') and hasattr(dataset, 'SOPInstanceUID') and 
                    any(hasattr(dataset, attr) for attr in ['PixelData', 'FloatPixelData', 'DoubleFloatPixelData'])
                    and ('DIRFILE' not in singleframe) and ('DICOMDIR' not in singleframe)):
                    list_paths.extend([singleframe])
                    list_dicom.extend([dataset])
            except:
                continue

        if len(list_dicom) == 0:
            msgWindow.displayMessageSubWindow(self, "No DICOM files present in the selected folder")
            raise FileNotFoundError('No DICOM files present in the selected folder')

        return list_dicom, list_paths
    except Exception as e:
        print('Error in WriteXMLfromDICOM.get_scan_data: ' + str(e))


def get_study_series(dicom):
    try:
        logger.info("WriteXMLfromDICOM.get_study_series called")
        if hasattr(dicom, 'PatientID'):
            subject = str(dicom.PatientID)
        elif hasattr(dicom, 'PatientName'):
            subject = str(dicom.PatientName)
        else:
            subject = "No Subject Name"
        study = str(dicom.StudyDate) + "_" + str(dicom.StudyTime).split(".")[0]
        #if hasattr(dicom, "SeriesDescription"):
        sequence = str(dicom.SeriesDescription)
        #elif hasattr(dicom, "SequenceName"):
        #    sequence = str(dicom.SequenceName)
        #elif hasattr(dicom, "ProtocolName"):
        #    sequence = str(dicom.ProtocolName)
        #else:
        #    sequence = "No Sequence Name"
        series_number = str(dicom.SeriesNumber)
        study_uid = str(dicom.StudyInstanceUID)
        series_uid = str(dicom.SeriesInstanceUID)

        return subject, study, sequence, series_number, study_uid, series_uid
    except Exception as e:
        print('Error in WriteXMLfromDICOM.get_study_series: ' + str(e))


def build_dictionary(list_dicom, msgWindow, self):
    try:
        logger.info("WriteXMLfromDICOM.build_dictionary called")
        xml_dict = {}
        fileCounter = 0
        msgWindow.setMsgWindowProgBarMaxValue(self, len(list_dicom))
        for file in list_dicom:
            fileCounter += 1
            msgWindow.setMsgWindowProgBarValue(self, fileCounter)
            subject, study, sequence, series_number, _, _ = get_study_series(file)
            if subject not in xml_dict:
                xml_dict[subject] = defaultdict(list)
            xml_dict[subject][study].append(series_number + "_" + sequence)
        for subject in xml_dict:
            for study in xml_dict[subject]:
                xml_dict[subject][study] = sorted(np.unique(xml_dict[subject][study]), key=series_sort)
        return xml_dict
    except Exception as e:
        print('Error in WriteXMLfromDICOM.build_dictionary: ' + str(e))


def get_studies_series_iBEAT(list_dicom):
    try:
        logger.info("WriteXMLfromDICOM.get_studies_series_iBEAT called")
        xml_dict = defaultdict(list)
        for file in list_dicom:
            individualStudy, individualSeries = iBeatImport.getScanInfo(file)
            xml_dict[individualStudy].append(individualSeries)
        for study in xml_dict:
            xml_dict[study] = np.unique(xml_dict[study])

        return xml_dict
    except Exception as e:
        print('Error in WriteXMLfromDICOM.get_studies_series_iBEAT: ' + str(e))


def open_dicom_to_xml(xml_dict, list_dicom, list_paths, msgWindow, self):
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
            #added expanded attribute SS
            #subject branches always expanded
            subject_element.set('expanded', 'True')  #added by SS 12.03.21
            subject_element.set('checked', 'False')  #added by SS 16.03.21
            for study in xml_dict[subject]:
                study_element = ET.SubElement(subject_element, 'study')
                study_element.set('id', study)
                study_element.set('expanded', 'False') #added by SS 12.03.21
                study_element.set('checked', 'False')  #added by SS 16.03.21
                for series in xml_dict[subject][study]:
                    series_element = ET.SubElement(study_element, 'series')
                    series_element.set('id', series)
                    series_element.set('expanded', 'False') #added by SS 12.03.21
                    series_element.set('checked', 'False')  #added by SS 16.03.21
        fileCounter = 0
        msgWindow.setMsgWindowProgBarMaxValue(self, len(list_dicom))
        for index, file in enumerate(list_dicom):
            fileCounter += 1
            msgWindow.setMsgWindowProgBarValue(self, fileCounter)
            subject, study, sequence, series_number, study_uid, series_uid = get_study_series(file)
            subject_search_string = "./*[@id='" + subject + "']"
            study_root = DICOM_XML_object.find(subject_search_string)
            study_search_string = "./*[@id='" + study + "']"
            series_root = study_root.find(study_search_string)
            series_search_string = "./*[@id='"+ series_number + "_" + sequence + "']"
            study_root.set('uid', study_uid)
            series_root.set('uid', series_uid)
            image_root = series_root.find(series_search_string)
            image_element = ET.SubElement(image_root, 'image')
            image_element.set('checked', 'False')  #added by SS 16.03.21
            label = ET.SubElement(image_element, 'label')
            name = ET.SubElement(image_element, 'name')
            time = ET.SubElement(image_element, 'time')
            date = ET.SubElement(image_element, 'date')
            label.text = str(len(list(image_root.iter('image')))).zfill(6)
            name.text =  os.path.normpath(list_paths[index])
            
            # The next lines save the time and date to XML - They consider multiple/eventual formats
            if len(file.dir("AcquisitionTime"))>0:
                try:
                    time.text = datetime.datetime.strptime(file.AcquisitionTime, '%H%M%S').strftime('%H:%M')
                except:
                    time.text = datetime.datetime.strptime(file.AcquisitionTime, '%H%M%S.%f').strftime('%H:%M')
                date.text = datetime.datetime.strptime(file.AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
            elif len(file.dir("SeriesTime"))>0:
                # It means it's Enhanced MRI
                try:
                    time.text = datetime.datetime.strptime(file.SeriesTime, '%H%M%S').strftime('%H:%M')
                except:
                    time.text = datetime.datetime.strptime(file.SeriesTime, '%H%M%S.%f').strftime('%H:%M')
                date.text = datetime.datetime.strptime(file.SeriesDate, '%Y%m%d').strftime('%d/%m/%Y')
            else:
                time.text = datetime.datetime.strptime('000000', '%H%M%S').strftime('%H:%M')
                date.text = datetime.datetime.strptime('20000101', '%Y%m%d').strftime('%d/%m/%Y')
        return DICOM_XML_object
    except Exception as e:
        print('Error in WriteXMLfromDICOM.open_dicom_to_xml: ' + str(e))


def open_dicom_to_xml_iBEAT(xml_dict, list_dicom, list_paths):
    """This method opens all DICOM files in the given list and saves 
        information from each file individually to an XML tree/structure.
    """
    try:    
        logger.info("WriteXMLfromDICOM.open_dicom_to_xml_iBEAT called")
        DICOM_XML_object = ET.Element('DICOM')
        comment = ET.Comment('WARNING: PLEASE, DO NOT MODIFY THIS FILE \n This .xml file is automatically generated by a script that reads folders containing DICOM files. \n Any changes can affect the software\'s functionality, so do them at your own risk')
        DICOM_XML_object.append(comment)

        for study in xml_dict:
            study_element = ET.SubElement(DICOM_XML_object, 'study')
            study_element.set('id',study)
            for series in xml_dict[study]:
                series_element = ET.SubElement(study_element, 'series')
                series_element.set('id', series)

        for index, file in enumerate(list_dicom):
            study_search_string, series_search_string = iBeatImport.getScanInfo(file)
            study_search_string = "./*[@id='" + study_search_string + "']"
            series_search_string = "./*[@id='" + series_search_string + "']"
            series_root = DICOM_XML_object.find(study_search_string)
            image_root = series_root.find(series_search_string)
            image_element = ET.SubElement(image_root, 'image')
            name = ET.SubElement(image_element, 'name')
            time = ET.SubElement(image_element, 'time')
            date = ET.SubElement(image_element, 'date')
            name.text =  os.path.normpath(list_paths[index])
            # The next lines save the time and date to XML - They consider multiple/eventual formats
            if len(file.dir("AcquisitionTime"))>0:
                try:
                    time.text = datetime.datetime.strptime(file.AcquisitionTime, '%H%M%S').strftime('%H:%M')
                except:
                    time.text = datetime.datetime.strptime(file.AcquisitionTime, '%H%M%S.%f').strftime('%H:%M')
                date.text = datetime.datetime.strptime(file.AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
            elif len(file.dir("SeriesTime"))>0:
                # It means it's Enhanced MRI
                try:
                    time.text = datetime.datetime.strptime(file.SeriesTime, '%H%M%S').strftime('%H:%M')
                except:
                    time.text = datetime.datetime.strptime(file.SeriesTime, '%H%M%S.%f').strftime('%H:%M')
                date.text = datetime.datetime.strptime(file.SeriesDate, '%Y%m%d').strftime('%d/%m/%Y')
            else:
                time.text = datetime.datetime.strptime('000000', '%H%M%S').strftime('%H:%M')
                date.text = datetime.datetime.strptime('20000101', '%Y%m%d').strftime('%d/%m/%Y')
        return DICOM_XML_object
    except Exception as e:
        print('Error in WriteXMLfromDICOM.open_dicom_to_xml_iBEAT: ' + str(e))


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
        if scan_directory:
            start_time=time.time()
            numFiles, numFolders = get_files_info(scan_directory)
            if numFolders == 0:
                folder = os.path.basename(scan_directory) + ' folder.'
            else:
                folder = os.path.basename(scan_directory) + ' folder and {} '.format(numFolders) \
                    + 'subdirectory(s)'

            progBarMsg = "Collecting {} files from the {}".format(numFiles, folder)
            messageWindow.displayMessageSubWindow(self, progBarMsg)
            scans, paths = get_scan_data(scan_directory, messageWindow, progBarMsg, self)
            messageWindow.displayMessageSubWindow(self,"<H4>Reading data from each DICOM file</H4>")
            dictionary = build_dictionary(scans, messageWindow, self)
            messageWindow.displayMessageSubWindow(self,"<H4>Writing DICOM data to an XML file</H4>")
            xml = open_dicom_to_xml(dictionary, scans, paths, messageWindow, self)
            messageWindow.displayMessageSubWindow(self,"<H4>Saving XML file</H4>")
            fullFilePath = create_XML_file(xml, scan_directory)
            self.msgSubWindow.close()
            end_time=time.time()
            xmlCreationTime = end_time - start_time 
            print('XML file creation time = {}'.format(xmlCreationTime))
            logger.info("WriteXMLfromDICOM.makeDICOM_XML_File returns {}."
                        .format(fullFilePath))
        return fullFilePath
    except Exception as e:
        print('Error in function WriteXMLfromDICOM.makeDICOM_XML_File: ' + str(e))
        logger.error('Error in function WriteXMLfromDICOM.makeDICOM_XML_File: ' + str(e))
import os
from pyqtgraph.Qt import QtCore, QtGui
import pydicom
import xml.etree.ElementTree as ET
import datetime
import numpy as np
from collections import defaultdict
from xml.dom import minidom


def select_path():
    """This method opens a Dialog Box that allows the user to choose the folder containing the MRI scan.
        The path to the folder is what is returned in this method.
    """
    cwd = os.getcwd()
    app = QtGui.QApplication([])  # pylint: disable=unused-variable
    scan_directory = QtGui.QFileDialog.getExistingDirectory(None, 'Select the'
                                                            ' directory containing the scan', cwd, QtGui.QFileDialog.ShowDirsOnly)
    if len(scan_directory) == 0:
        raise SystemExit('No folder selected')

    return scan_directory


def get_scan_data(scan_directory):
    """This method opens all DICOM files in the provided path recursively and saves 
        each file individually as a variable into a list/array.
    """
    list_dicom = list()
    list_paths = list()
    for dir_name, _, file_list in os.walk(scan_directory):
        for filename in file_list:
            try:
                list_dicom.append(pydicom.dcmread(
                    os.path.join(dir_name, filename)))
                list_paths.append(os.path.join(dir_name, filename))
            except:
                continue
    if len(list_dicom) == 0:
        raise FileNotFoundError(
            'No DICOM files present in the selected folder')

    return list_dicom, list_paths


def get_studies_series(list_dicom):
    xml_dict = defaultdict(list)
    for file in list_dicom:
        xml_dict[str(file.StudyDescription) + "_" + str(file.PatientID)].append(str(file.SeriesDescription) + "_Series" + str(file.SeriesNumber))
        
    for study in xml_dict:
        xml_dict[study] = np.unique(xml_dict[study])

    return xml_dict


def open_dicom_to_xml(xml_dict, list_dicom, list_paths):
    """This method opens all DICOM files in the given list and saves 
        information from each file individually to an XML tree/structure.
    """
        
    DICOM_XML_object = ET.Element('DICOM')

    for study in xml_dict:
        study_element = ET.SubElement(DICOM_XML_object, 'study')
        study_element.set('id',study)
        for series in xml_dict[study]:
            series_element = ET.SubElement(study_element, 'series')
            series_element.set('id', series)
    
    for index, file in enumerate(list_dicom):
        study_search_string = "./*[@id='"+ str(file.StudyDescription) + "_" + str(file.PatientID) + "']"
        series_root = DICOM_XML_object.find(study_search_string)
        series_search_string = "./*[@id='"+ str(file.SeriesDescription) + "_Series" + str(file.SeriesNumber) + "']"
        image_root = series_root.find(series_search_string)
        image_element = ET.SubElement(image_root, 'image')
        name = ET.SubElement(image_element, 'name')
        time = ET.SubElement(image_element, 'time')
        date = ET.SubElement(image_element, 'date')
        name.text = list_paths[index]
        # The next lines save the time and date to XML - They consider multiple/eventual formats
        try:
            try:
                time.text = datetime.datetime.strptime(file.AcquisitionTime, '%H%M%S').strftime('%H:%M')
            except:
                time.text = datetime.datetime.strptime(file.AcquisitionTime, '%H%M%S.%f').strftime('%H:%M')
            date.text = datetime.datetime.strptime(file.AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
        except:
        # It means it's Enhanced MRI
            try:
                time.text = datetime.datetime.strptime(file.SeriesTime, '%H%M%S').strftime('%H:%M')
            except:
                time.text = datetime.datetime.strptime(file.SeriesTime, '%H%M%S.%f').strftime('%H:%M')
            date.text = datetime.datetime.strptime(file.SeriesDate, '%Y%m%d').strftime('%d/%m/%Y')


    return DICOM_XML_object


def create_XML_file(DICOM_XML_object, scan_directory):
    """This method creates a new XML file with the based on the structure of the selected DICOM folder"""
    xmlstr = ET.tostring(DICOM_XML_object, encoding='utf-8')
    XML_data = minidom.parseString(xmlstr).toprettyxml(encoding="utf-8", indent="  ")
    filename = os.path.basename(os.path.normpath(scan_directory)) + ".xml"
    with open(filename, "wb") as f:
        f.write(XML_data)  

    return


def main():
    generic_path = select_path()
    scans, paths = get_scan_data(generic_path)
    dictionary = get_studies_series(scans)
    xml = open_dicom_to_xml(dictionary, scans, paths)
    create_XML_file(xml, generic_path)


if __name__ == '__main__':
        main()
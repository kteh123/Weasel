import xml.etree.ElementTree as ET
from Scripting.dicom_labels import dicom_labels

def DicomDataFrame_to_ElementTree(project):
    """Converts a pandas DataFrame of a DICOM folder into
    an Element Tree.
    """   
    project_et = ET.Element('DICOM')
    comment = ET.Comment('WARNING: PLEASE, DO NOT MODIFY THIS FILE \n This .xml file is automatically generated by a script that reads folders containing DICOM files. \n Any changes can affect the software\'s functionality, so do them at your own risk')
    project_et.append(comment)

    for subject in project.PatientID.unique():
        subject = project[project.PatientID == subject]
        labels = dicom_labels(subject.iloc[0])     
        subject_element = ET.SubElement(project_et, 'subject')
        subject_element.set('id', labels[0])
        subject_element.set('expanded', 'True')  #added by SS 12.03.21
        subject_element.set('checked', 'False')  #added by SS 16.03.21
        for study in subject.StudyInstanceUID.unique():
            study = subject[subject.StudyInstanceUID == study]
            labels = dicom_labels(study.iloc[0])
            study_element = ET.SubElement(subject_element, 'study')
            study_element.set('id', labels[1])
            study_element.set('expanded', 'False') #added by SS 12.03.21
            study_element.set('checked', 'False')  #added by SS 16.03.21
            for series in study.SeriesInstanceUID.unique():
                series = study[study.SeriesInstanceUID == series]
                labels = dicom_labels(series.iloc[0])
                series_element = ET.SubElement(study_element, 'series')
                series_element.set('id', labels[2])
                series_element.set('expanded', 'False') #added by SS 12.03.21
                series_element.set('checked', 'False')  #added by SS 16.03.21
                for filepath, image in series.iterrows():
                    labels = dicom_labels(image)
                    image_element = ET.SubElement(series_element, 'image')
                    image_element.set('checked', 'False')  #added by SS 16.03.21
                    ET.SubElement(image_element, 'label').text = labels[3]
                    ET.SubElement(image_element, 'name').text = filepath
                    ET.SubElement(image_element, 'time').text = labels[4]
                    ET.SubElement(image_element, 'date').text = labels[5]
    return project_et



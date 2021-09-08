import xml.etree.ElementTree as ET


def DataFrame_to_ElementTree(data_frame):
    """
    Converts a Pandas DataFrame representing a DICOM folder into an ElementTree. 

    Parameters:
    -----------
    data_frame: pandas DataFrame created by DICOM_to_DataFrame

    Returns:
    -------
    an XML ElementTree as represented by the TreeView in Weasel
    """   

    element_tree = ET.Element('DICOM')
    comment = ET.Comment('Element Tree representing a DICOM folder')
    element_tree.append(comment)

    data_frame.sort_values(
        ['PatientID', 'StudyInstanceUID', 'SeriesNumber', 'InstanceNumber'], 
        inplace = True)

    for subject in data_frame.PatientID.unique():
        subject = data_frame[data_frame.PatientID == subject]
        labels = data_labels(subject.iloc[0])     
        subject_element = ET.SubElement(element_tree, 'subject')
        subject_element.set('id', labels[0])
        subject_element.set('expanded', 'True')  
        subject_element.set('checked', 'False') 
        for study in subject.StudyInstanceUID.unique():
            study = subject[subject.StudyInstanceUID == study]
            labels = data_labels(study.iloc[0])
            study_element = ET.SubElement(subject_element, 'study')
            study_element.set('id', labels[1])
            study_element.set('expanded', 'False') 
            study_element.set('checked', 'False')  
            for series in study.SeriesInstanceUID.unique():
                series = study[study.SeriesInstanceUID == series]
                labels = data_labels(series.iloc[0])
                series_element = ET.SubElement(study_element, 'series')
                series_element.set('id', labels[2])
                series_element.set('expanded', 'False') 
                series_element.set('checked', 'False')  
                for filepath, image in series.iterrows():
                    labels = data_labels(image)
                    image_element = ET.SubElement(series_element, 'image')
                    image_element.set('checked', 'False')  
                    ET.SubElement(image_element, 'label').text = labels[3]
                    ET.SubElement(image_element, 'name').text = filepath
                    ET.SubElement(image_element, 'time').text = labels[4]
                    ET.SubElement(image_element, 'date').text = labels[5]

    return element_tree


def data_labels(image):
    """Creates human readable labels for a DICOM image.

    Parameters:
    ----------- 
    image: either a row in a DataFrame or pyDicom DataSet

    Returns:
    -------
    A tuple of strings
    """ 
    subject_label = str(image.PatientName)
    subject_label += ' [' + str(image.PatientID) + ' ]'
    study_label = str(image.StudyDescription) + "_"
    study_label += str(image.StudyDate) + "_"
    study_label += str(image.StudyTime).split(".")[0]
    series_label = str(image.SeriesNumber) + "_"
    series_label += str(image.SeriesDescription)
    image_label = str(image.InstanceNumber).zfill(6)

    AcquisitionTime = str(image.AcquisitionTime)
    AcquisitionDate = str(image.AcquisitionDate)
    SeriesTime = str(image.SeriesTime)
    SeriesDate = str(image.SeriesDate)

    return subject_label, study_label, series_label, image_label, SeriesDate, SeriesTime, AcquisitionTime, AcquisitionDate




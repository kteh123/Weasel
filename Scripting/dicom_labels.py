
import datetime

def dicom_labels(image):
    """Returns a set of human readable labels for a row in a DataFrame.
    input: row in a DataFrame
    output: tuple of strings
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
    if not AcquisitionTime == 'Unknown':
        try:
            time_label = datetime.datetime.strptime(AcquisitionTime, '%H%M%S').strftime('%H:%M')
        except:
            time_label = datetime.datetime.strptime(AcquisitionTime, '%H%M%S.%f').strftime('%H:%M')
        date_label = datetime.datetime.strptime(AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
    elif not SeriesTime == 'Unknown': # It means it's Enhanced MRI
        try:
            time_label = datetime.datetime.strptime(SeriesTime, '%H%M%S').strftime('%H:%M')
        except:
            time_label = datetime.datetime.strptime(SeriesTime, '%H%M%S.%f').strftime('%H:%M')
        date_label = datetime.datetime.strptime(SeriesDate, '%Y%m%d').strftime('%d/%m/%Y')
    else:
        time_label = datetime.datetime.strptime('000000', '%H%M%S').strftime('%H:%M')
        date_label = datetime.datetime.strptime('20000101', '%Y%m%d').strftime('%d/%m/%Y')

    return subject_label, study_label, series_label, image_label, date_label, time_label
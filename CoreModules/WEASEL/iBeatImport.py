import pydicom
import datetime
import re
import pandas as pd
#Also need to do pip install xlrd
import warnings
import readDICOM_Image as readDICOM_Image


def getScanInfo(dicomData):
    try:
        date = datetime.datetime.strptime(dicomData.StudyDate, '%Y%m%d').strftime('%d/%m/%Y')
        studyName = "iBEAt_" + str(dicomData.PatientName) + "_" + date + "_" + str(dicomData.Manufacturer.split(' ', 1)[0])
        acquisitionTypeFlags = readDICOM_Image.checkAcquisitionType(dicomData)
        imageTypeFlags = readDICOM_Image.checkImageType(dicomData)
        seriesName = getSeriesNameFromTable(dicomData)

        if acquisitionTypeFlags[0]:
            seriesName = seriesName + '_Water'
        elif acquisitionTypeFlags[1]:
            seriesName = seriesName + '_Fat'
        elif acquisitionTypeFlags[2]:
            seriesName = seriesName + '_In-Phase'
        elif acquisitionTypeFlags[3]:
            seriesName = seriesName + '_Out-Phase'
        else: pass

        if imageTypeFlags[0]:
            seriesName = seriesName + '_Magnitude'
        elif imageTypeFlags[1]:
            seriesName = seriesName + '_Phase'
        elif imageTypeFlags[2]:
            seriesName = seriesName + '_Real'
        elif imageTypeFlags[3]:
            seriesName = seriesName + '_Imaginary'
        elif imageTypeFlags[4]:
            seriesName = seriesName + '_' + imageTypeFlags[4]
        else: pass

        seriesName = seriesName + '_' + str(dicomData.SeriesNumber)

        return studyName, seriesName
    except Exception as e:
        print('Error in iBeatImport.getScanInfo: ' + str(e))
        

def getSeriesNameFromTable(dicomData):
    try:
        parametersTable = pd.read_excel('iBEAT-Scan-Parameters-DTI-DCE.xlsx', sheet_name=str(dicomData.InstitutionName))
        tagsList = parametersTable['DICOM Tag']
        tagsFormated = ["0x" + re.sub("[(, )]","", tag) for tag in tagsList]
        datasetParametersList = []
        # First, it gets all DICOM values from the file being analysed (only the tags in the excel table)
        for tag in tagsFormated:
            try:
                datasetParametersList.append(str(dicomData[tag].value))
            except:
                datasetParametersList.append(str("nan"))

        # With the list of values from the DICOM file, we will now compare with the values in the table
        for key, value in parametersTable.iteritems():
            columnParametersList = [str(element) for element in list(value)] # Maybe add a if/else
            comparisonList = [datasetParametersList[i] if columnParametersList[i] != "nan" 
                              else "nan" for i in range(len(value))]
            booleanList = ["True" if (re.search(columnParametersList[i], comparisonList[i]) or
                                      columnParametersList[i] == comparisonList[i])
                                      else "False" for i in range(len(value))]

            if "False" not in booleanList:
                sequenceName = str(key)
                break
        
        return sequenceName
    except Exception as e:
        try:
            # If sequenceName doesn't exist, then print Warning message
            try:
                sequenceName = str(dicomData.SeriesDescription)
            except:
                sequenceName = str(dicomData.SequenceName)
            date = datetime.datetime.strptime(dicomData.StudyDate, '%Y%m%d').strftime('%d/%m/%Y')
            message = ("No match found in the parameters table... Using the default series name."
                      + "Subject: " + str(dicomData.PatientName) + ", Scan Date: " + date + ", Series: " + sequenceName)
            warnings.warn(message)
            return sequenceName
        except Exception as e:
            print('Error in iBeatImport.getSeriesNameFromTable: ' + str(e))

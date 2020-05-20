import pydicom
import datetime
import re

def getScanInfo(dicomData):
    try:
        date = datetime.datetime.strptime(dicomData.AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
        studyName = "iBEAt_" + dicomData.PatientName + "_" + date + "_" + dicomData.Manufacturer.split(' ', 1)[0]
        if len(dicomData.dir("SeriesDescription"))>0:
            series = str(dicomData.SeriesDescription)
        elif len(dicomData.dir("SequenceName"))>0 & len(dicomData.dir("PulseSequenceName"))==0:
            series = str(dicomData.SequenceName)
        elif len(dicomData.dir("ProtocolName"))>0:
            series = str(dicomData.ProtocolName) 
        else:
            series = "No Sequence Name"
        
        seriesName = getSeriesName(series)
        seriesName = seriesName + "_" + str(dicomData.SeriesNumber)
        
        return studyName, seriesName
    except Exception as e:
            print('Error in iBeatImport.getScanInfo: ' + str(e))



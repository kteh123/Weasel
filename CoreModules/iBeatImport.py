import pydicom
import datetime
import re
import CoreModules.readDICOM_Image as readDICOM_Image


def getScanInfo(dicomData):
    try:
        date = datetime.datetime.strptime(dicomData.AcquisitionDate, '%Y%m%d').strftime('%d/%m/%Y')
        studyName = "iBEAt_" + dicomData.PatientName + "_" + date + "_" + dicomData.Manufacturer.split(' ', 1)[0]
        if len(dicomData.dir("SeriesDescription"))>0:
            seriesRegex = str(dicomData.SeriesDescription)
        elif len(dicomData.dir("SequenceName"))>0 & len(dicomData.dir("PulseSequenceName"))==0:
            seriesRegex = str(dicomData.SequenceName)
        elif len(dicomData.dir("ProtocolName"))>0:
            seriesRegex = str(dicomData.ProtocolName)
        else:
            seriesRegex = "No Sequence Name"
        typeFlags = readDICOM_Image.checkImageType(dicomData)
        seriesName = getSeriesName(seriesRegex, typeFlags)
        seriesID = '_'.join(str(dicomData.SeriesNumber))
        series = seriesName.join(seriesID)
        
        return studyName, series
    except Exception as e:
            print('Error in iBeatImport.getScanInfo: ' + str(e))


def getSeriesName(series, flags):
    try:
        seriesName = series
        dictOfSequences = {
            'localizer_bh_fix' : ['.*localizer.*fix.*', '.*survey.*fix.*'],
            'localizer_bh_ISO' : ['.*localizer.*iso.*', '.*survey.*iso.*'],
            'T2w_abdomen_haste_tra_mbh' : '.*t2w.*',
            'T1w_abdomen_dixon_cor_bh' : '.*t1w.*dixon.*',
            'PC_RenalArtery_Right_EcgTrig_fb_120' : '.*pc.*right.*',
            'PC_RenalArtery_Left_EcgTrig_fb_120' : '.*pc.*left.*',
            'T2star_map_pancreas_tra_mbh' : ['.*t2star.*pancreas.*', '.*t2\*.*pancreas.*'],
            'T1w_kidneys_cor-oblique_mbh' : '.*t1w.*kidney.*',
            'T1map_kidneys_cor-oblique_mbh' : '.*t1map.*kidney.*',
            'T2map_kidneys_cor-oblique_mbh' : '.*t2map.*kidney.*',
            'T2star_map_kidneys_cor-oblique_mbh' : ['.*t2star.*kidneys.*', '.*t2\*.*kidneys.*'],
            'IVIM_kidneys_cor-oblique_fb' : '.*ivim.*', # Also ep_b when compared to DTI
            'DTI_kidneys_cor-oblique_fb' : ['.*dti.*','.*ep_b.*'],
            'MT_OFF_kidneys_cor-oblique_bh' : '.*mt.*off.*',
            'MT_ON_kidneys_cor-oblique_bh' : '.*mt.*on.*',
            'ASL_planning_bh' : ['.*asl.*plan.*', '\*tfi2d1_154.*'],
            'ASL_kidneys_pCASL_cor-oblique_fb' : ['.*asl.*pcasl.*', '.*tgse.*'],
            'DCE_kidneys_cor-oblique_fb' : ['.*dce.*', '\*tfl2d1_16.*'],
            'T1w_abdomen_post_contrast_dixon_cor_bh' : '.*t1w.*contrast.*'
        }

        # The following method loops through the dictionary until it finds the first match
        seriesName = loopDict(dictOfSequences, series)

        # This code loops through the entire dictionary
        #for key, value in dictOfSequences.items():
            #if isinstance(value,list):
                #for val in value:
                    #if re.match(val, series.lower()):
                        #seriesName = key
            #else:
                #if re.match(value, series.lower()):
                    #seriesName = key

        if flags[0]:
            seriesName.join('_Magnitude')
        elif flags[1]:
            seriesName.join('_Phase')
        elif flags[2]:
            seriesName.join('_Real')
        elif flags[3]:
            seriesName.join('_Imaginary')
        elif flags[4]:
            seriesName.join('_Map')
        
        return seriesName
    except Exception as e:
            print('Error in iBeatImport.getSeriesName: ' + str(e))


def loopDict(dictionary, series):
    try:
        for key, value in dictionary.items():
            if isinstance(value, list):
                for val in value:
                    if re.match(val, series.lower()):
                        return key
            else:
                if re.match(value, series.lower()):
                    return key
        return series
    except Exception as e:
            print('Error in iBeatImport.getSeriesName: ' + str(e))

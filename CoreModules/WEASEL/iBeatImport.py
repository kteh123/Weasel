import pydicom
import datetime
import re
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image


def getScanInfo(dicomData):
    try:
        date = datetime.datetime.strptime(dicomData.StudyDate, '%Y%m%d').strftime('%d/%m/%Y')
        studyName = "iBEAt_" + str(dicomData.PatientName) + "_" + date + "_" + str(dicomData.Manufacturer.split(' ', 1)[0])
        acquisitionTypeFlags = readDICOM_Image.checkAcquisitionType(dicomData)
        imageTypeFlags = readDICOM_Image.checkImageType(dicomData)
        
        if re.match("siemens", str(dicomData.Manufacturer).lower()):
            seriesName = getSeriesNameSiemens(dicomData)
        elif re.match("ge", str(dicomData.Manufacturer).lower()) or re.match("general electric", str(dicomData.Manufacturer).lower()):
            seriesName = getSeriesNameSiemens(dicomData)
        elif re.match("philips", str(dicomData.Manufacturer).lower()):
            seriesName = getSeriesNameSiemens(dicomData)

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


def getSeriesNameSiemens(dicomData):
    try:
        try: series = str(dicomData.SequenceName)
        except: series = str(dicomData.SeriesDescription)
        seriesName = series
        if series == '*tfi2d1_192':
            if dicomData.SliceThickness == 8.5: seriesName = 'localizer_bh_fix'
            elif dicomData.SliceThickness == 4: seriesName = 'localizer_bh_ISO'
        elif series == '*h2d1_320': seriesName = 'T2w_abdomen_haste_tra_mbh'
        elif series == '*fl3d2':
            try:
                if dicomData.ContrastBolusVolume > 0: seriesName = 'T1w_abdomen_post_contrast_dixon_cor_bh'
                else: seriesName = 'T1w_abdomen_dixon_cor_bh'
            except: 
                seriesName = 'T1w_abdomen_dixon_cor_bh'
        elif series == '*fl2d1r4':
            if str(dicomData[0x0051100d].value).startswith('SP R'): seriesName = 'PC_RenalArtery_Right_EcgTrig_fb'
            elif str(dicomData[0x0051100d].value).startswith('SP L'): seriesName = 'PC_RenalArtery_Left_EcgTrig_fb'
        elif series == '*fl2d1_v120in':
            if str(dicomData[0x0051100d].value).startswith('SP R'): seriesName = 'PC_RenalArtery_Right_EcgTrig_fb_120'
            elif str(dicomData[0x0051100d].value).startswith('SP L'): seriesName = 'PC_RenalArtery_Left_EcgTrig_fb_120'
        elif series == '*fl2d12':
            if str(dicomData.InPlanePhaseEncodingDirection) == 'ROW': seriesName = 'T2star_map_kidneys_cor-oblique_mbh'
            elif str(dicomData.InPlanePhaseEncodingDirection) == 'COL': seriesName = 'T2star_map_pancreas_tra_mbh'
        elif series == '*fl2d1': seriesName = 'T1w_kidneys_cor-oblique_mbh'
        elif series == '*tfl2d1r106': seriesName = 'T1map_kidneys_cor-oblique_mbh'
        elif series == '*tfl2d1r96': seriesName = 'T2map_kidneys_cor-oblique_mbh'
        elif series == '*fl3d1':
            if ('MTC' in dicomData.SequenceVariant) and ('MT' in dicomData.ScanOptions): seriesName = 'MT_ON_kidneys_cor-oblique_bh'
            else: seriesName = 'MT_OFF_kidneys_cor-oblique_bh'
        elif series == '*tfi2d1_154': seriesName = 'ASL_planning_bh'
        elif series == 'tgse3d1_512': seriesName = 'ASL_kidneys_pCASL_cor-oblique_fb'
        elif series == '*tfl2d1_16': 
            try:
                if dicomData.ContrastBolusVolume > 0: seriesName = 'DCE_kidneys_cor-oblique_fb'
                else: seriesName = 'DCE_kidneys_cor-oblique_dry-run_fb'
            except: 
                seriesName = 'DCE_kidneys_cor-oblique_dry-run_fb'
        elif re.match(".*ep_b.*", series):
            if str(dicomData[0x0051100a].value).startswith('TA 0'): seriesName = 'IVIM_kidneys_cor-oblique_fb'
            elif str(dicomData[0x0051100a].value).startswith('TA 1'): seriesName = 'DTI_kidneys_cor-oblique_fb'
        else: pass

        return seriesName
    except Exception as e:
            print('Error in iBeatImport.getSeriesNameSiemens: ' + str(e))


def getSeriesNameGE(dicomData):
    try:
        return 
    except Exception as e:
            print('Error in iBeatImport.getSeriesNameGE: ' + str(e))


def getSeriesNamePhilips(dicomData):
    try:
        return 
    except Exception as e:
            print('Error in iBeatImport.getSeriesNamePhilips: ' + str(e))

# First draft in May 2020
####################################################################################################

def getScanInfoGeneric(dicomData):
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
        seriesName = getSeriesNameGeneric(seriesRegex, typeFlags)
        seriesID = '_'.join(str(dicomData.SeriesNumber))
        series = seriesName.join(seriesID)
        
        return studyName, series
    except Exception as e:
            print('Error in iBeatImport.getScanInfoGeneric: ' + str(e))


def getSeriesNameGeneric(series, flags):
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
            print('Error in iBeatImport.getSeriesNameGeneric: ' + str(e))


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
            print('Error in iBeatImport.loopDict: ' + str(e))

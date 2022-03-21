import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# These 2 lines are required if you're importing an external
# python package that doesn't have "pip install" and that's located
# in the same folder as the current menu script.
from MDR import MDR, Tools
#import concurrent.futures
import numpy as np
import importlib
import matplotlib.pyplot as plt
from models.two_compartment_filtration_model_DCE import main as model_DCE
#***************************************************************************
## PS: code adapted from MDR so some function names may be misleading - script only for pilot analysis
def isSeriesOnly(self):
    return True

def main(weasel, series=None):
    try:
        if series is None:
            series = weasel.series()

        for i,series in enumerate (series): # loop to find the mask (needs to be a single image)

          if 'DCE_ART' in series[0]['SeriesDescription']:
            mask_DCE_ART = series.PixelArray
          
          elif series[0]['SeriesDescription'] == "DCE_kidneys_cor-oblique_fb": 
              # Get Pixel Array and format it accordingly
              series_magnitude = series.Magnitude.sort("SliceLocation","AcquisitionTime")
              pixel_array = series_magnitude.PixelArray

        # display the new sorted series
        sorted_series_magnitude = series_magnitude.new(series_name="DCE_Series_Sorted")
        sorted_series_magnitude.write(pixel_array)
       
        # Display sorted series
        sorted_series_magnitude.display()
        
        pixel_array = np.transpose(pixel_array)  
       
        mask_DCE_ART = np.transpose(mask_DCE_ART)
       
        #TODO: read number of dynamics from dicom series
        reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1],int(np.shape(pixel_array)[2]/265),265)
        magnitude_array = pixel_array.reshape(reformat_shape)
        
        pixelArray_DCE_ART = np.squeeze(magnitude_array[:, :, 8, :]) #np.squeeze(pixel_array[:,:,8,:])  # slice with the arteria
        DCE_timecourse = np.zeros(np.shape(pixelArray_DCE_ART)[2])

       # plt.imshow(np.squeeze(pixelArray_DCE_ART[:,:,0]) + mask_DCE_ART*1000)
       # plt.show
        aif = []
        time = []
        for k in range(np.shape(pixelArray_DCE_ART)[2]): #loop to average ROIs
                tempPixelMask = np.squeeze(pixelArray_DCE_ART[:,:,k])*np.squeeze(mask_DCE_ART)
                DCE_timecourse[k] = np.median(tempPixelMask[tempPixelMask!=0])
                aif.append(DCE_timecourse[k])

        DCE_time = np.arange(0, 1.61*len(DCE_timecourse), 1.61)
        time = DCE_time.tolist()
       
       # plt.plot(DCE_time, DCE_timecourse)
       # plt.show()

        # filename_log = weasel.DICOMFolder.split('/')[-1] + "_DCE_Joao_ROI.txt"
        # file = open(filename_log, 'a')
        # file.write(str(DCE_timecourse) + "\t" + str(DCE_time))
        # file.close()
        #np.sys.exit()

        affine_array = series_magnitude.Affine
        parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series[0].path))[:2]
        print("parameters")
        print(parameters)#

        images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], 265))
        Fp = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
        Tp = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
        Ps = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
        Te = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))

        for index in range(np.shape(magnitude_array)[2]):

            if index ==4:
                print("index")
                print(index)
                images = np.squeeze(magnitude_array[:, :, index, :]) 
                # import the DCE module
                full_module_name = "models.two_compartment_filtration_model_DCE"
                # generate a module named as a string 
                model = importlib.import_module(full_module_name)
                print("model")
                print(model)
                fit, fitted_parameters = motion_pipeline(weasel, images, parameters, model, [weasel, images, aif, time, affine_array])
                fit = np.reshape(fit,((np.shape(pixel_array)[0]),(np.shape(pixel_array)[1]),265))
               
                Fp_DCE = fitted_parameters[0,:]
                Fp = np.reshape(Fp_DCE, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 

                Tp_DCE = fitted_parameters[1,:]
                Tp = np.reshape(Tp_DCE, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]])

                Ps_DCE = fitted_parameters[2,:]
                Ps = np.reshape(Ps_DCE, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 

                Te_DCE = fitted_parameters[3,:]
                Te = np.reshape(Te_DCE, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]])

                
        fit = np.transpose(fit, (2, 1, 0)) 

        print("Finished modelling for DCE sequence!")

        Fp = np.transpose(Fp)
        Tp = np.transpose(Tp)
        Ps = np.transpose(Ps)
        Te = np.transpose(Te)

        corrected_series = series_magnitude.new(series_name="DCE_Series_model_fit")
        corrected_series.write(fit)
        
        # Display series
        corrected_series.display()
        output_folder = weasel.select_folder()
        corrected_series.export_as_nifti(directory=output_folder)

        # display maps
        Fp_final = series_magnitude.new(series_name="Fp_final")
        Fp = np.nan_to_num(Fp, posinf=0, neginf=0)
        Fp_final.write(Fp,value_range=[0, 0.10])
        #Fp_final.write(Fp)
        Fp_final.display()
        Fp_final.export_as_nifti(directory=output_folder)

        Tp_final = series_magnitude.new(series_name="Tp_final")
        Tp = np.nan_to_num(Tp, posinf=0, neginf=0)
        Tp_final.write(Tp,value_range=[0, 50])
        #Tp_final.write(Tp)
        Tp_final.display()
        Tp_final.export_as_nifti(directory=output_folder)

        Ps_final = series_magnitude.new(series_name="Ps_final")
        Ps = np.nan_to_num(Ps, posinf=0, neginf=0)
        Ps_final.write(Ps,value_range=[0, 0.01])
       # Ps_final.write(Ps)
        Ps_final.display()
        Ps_final.export_as_nifti(directory=output_folder)

        Te_final = series_magnitude.new(series_name="Te_final")
        Te = np.nan_to_num(Te, posinf=0, neginf=0)
        Te_final.write(Te,value_range=[0, 150])
        #Te_final.write(Te)
        Te_final.display()
        Te_final.export_as_nifti(directory=output_folder)

        # Refresh Weasel
        weasel.refresh()

    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))


def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        DCE_timecourse = model_arguments[2]
        DCE_time = model_arguments[3]
        signal_model_parameters = read_signal_model_parameters(DCE_timecourse, DCE_time)
        images_to_model= np.reshape(images,(np.shape(images)[0]*np.shape(images)[1], 265))
        fit, fitted_parameters = model_DCE(images_to_model, signal_model_parameters)
        return fit, fitted_parameters
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))
    
    ## read sequence acquisition parameter for signal modelling
def read_signal_model_parameters(aif, time):
    times = time
    timepoint = 15
    Hct = 0.45
    # input signal model parameters
    signal_model_parameters = [aif, times, timepoint, Hct]
    return signal_model_parameters


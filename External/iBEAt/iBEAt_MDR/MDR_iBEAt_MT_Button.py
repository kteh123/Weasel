import os
from MDR import MDR, Tools
import numpy as np
import importlib

#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel, series=None):
    try:
        if series is None:
            weasel.message(msg="Please Select MT_OFF and MT_ON series from list!")
            list_of_series = weasel.series()
        else:
            list_of_series = series
        # series_MT_OFF = weasel.series()[0] #TODO: TBC how to find correct series name in weasel?
        # print("series_MT_OFF['SeriesName']")
        # print(series_MT_OFF['SeriesName'])
        # series_MT_ON = weasel.series()[1]
        # print("series_MT_ON['SeriesName']")
        # print(series_MT_ON['SeriesName'])
        if len(list_of_series) <= 1: return
        #if series_MT_OFF['SeriesName'] == "32_MT_OFF_kidneys_cor-oblique_bh" & series_MT_ON['SeriesName'] == "33_MT_ON_kidneys_cor-oblique_bh":
        series_magnitude = list_of_series.copy().merge(series_name='Merged_MT_Series')
        pixel_array = series_magnitude.PixelArray
        series_magnitude.write(pixel_array)
        # Display sorted series
        series_magnitude.display()
        weasel.refresh()

        if len(pixel_array) == 32:
            # Get Pixel Array and format it accordingly
            pixel_array = np.transpose(pixel_array)
            magnitude_array = pixel_array
            affine_array = series_magnitude.Affine
            parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series_magnitude[0].path))[:2]
         
            images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], 2))
            final_image = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], 2))
            MTR_map = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
  
            for index in range(np.shape(magnitude_array)[2]):

                if index ==7: # select slice 7
                    images[:,:,0] = magnitude_array[:, :, index]
                if index ==23: # select slice 23
                    images[:,:,1] = magnitude_array[:, :, index]
                
        
            # import the MT module
            full_module_name = "models.constant_model"
            # generate a module named as a string 
            model = importlib.import_module(full_module_name)
            output_motion = motion_pipeline(weasel, images, parameters, model, [weasel, images, affine_array])
            final_image = output_motion[0]
            MTR = output_motion[3]
            MTR_map = np.reshape(MTR, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 
            
            final_image = np.transpose(final_image, (2, 1, 0))
            MTR_map = np.transpose(MTR_map)
            print("Finished motion correction for MT series!")

            corrected_series = series_magnitude.new(series_name="MT_Registered")
            corrected_series.write(final_image)
            # Display series
            #corrected_series.display()
            #output_folder = weasel.select_folder()
            #corrected_series.export_as_nifti(directory=output_folder)
            # Display map
            MTR_final = series_magnitude.new(series_name="MTR_Map_Registered")

            MTR_map = np.nan_to_num(MTR_map, posinf=0, neginf=0)
            MTR_final.write(MTR_map,value_range=[0, 100])
            #MTR_final.write(MTR_map)
            #MTR_final['WindowCenter'] = 0
            #MTR_final['WindowWidth'] = 100
            #MTR_final.display()
            #MTR_final.export_as_nifti(directory=output_folder)

            # Refresh Weasel
            weasel.refresh()
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the MTR Map.", "MT Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))


def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        elastix_parameters = Tools.read_elastix_model_parameters(script_dir + r'\models\Elastix_Parameters_Files\iBEAt\BSplines_MT.txt', ['MaximumNumberOfIterations', 256])
        image_parameters  =  parameters
        signal_model_parameters = read_signal_model_parameters()
        output_images = MDR.model_driven_registration(images, image_parameters, model, signal_model_parameters, elastix_parameters, precision = 1, function = 'main', log = False)
        return output_images
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))
    

 ## read sequence acquisition parameter for signal modelling
def read_signal_model_parameters(): 
  
    independent_variable = 0 # initialised for constant model
    return independent_variable

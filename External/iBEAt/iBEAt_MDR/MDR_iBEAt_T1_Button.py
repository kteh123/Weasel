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
            series = weasel.series()[0]
   
        InversionTime = series["InversionTime"]
       
        if len(InversionTime) == 140:
            # Get Pixel Array and format it accordingly 
            print("sorting according to inversion times")
            series_magnitude = series.Magnitude.sort("SliceLocation","InversionTime") 
            # read pixel information and reformat shape
            pixel_array = series_magnitude.PixelArray
             # display the new sorted series
            sorted_series_magnitude = series_magnitude.new(series_name="T1_Map_Sorted_Series")
            sorted_series_magnitude.write(pixel_array)
            # Display sorted series
            sorted_series_magnitude.display() #TODO: check if sorting correct based on 28 inversion times only
            InversionTime_slices = sorted_series_magnitude["InversionTime"]
            InversionTime_slice_3 = InversionTime_slices[56:84] #ok
           
            pixel_array = np.transpose(pixel_array)
            reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1],5, len(InversionTime_slice_3))
            magnitude_array = pixel_array.reshape(reformat_shape) 
           
            affine_array = series_magnitude.Affine
            parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series[0].path))[:2]
           
            final_image = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], len(InversionTime_slice_3)))
            images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], len(InversionTime_slice_3)))
            T1_estimated_map = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            T1_apparent_map = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            
            for index in range(np.shape(magnitude_array)[2]):
                if index ==2:
                  
                    images = np.squeeze(magnitude_array[:, :, index, :]) 
                    # import the T1 module
                    full_module_name = "models.T1"
                    # generate a module named as a string 
                    model = importlib.import_module(full_module_name)
                    output_motion = motion_pipeline(weasel, images, parameters, model, [weasel, images, InversionTime_slice_3, affine_array])
                    final_image = output_motion[0]
                    T1_estimated = output_motion[3][0,:]
                    T1_estimated_map = np.reshape(T1_estimated, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 
                    T1_apparent = output_motion[3][1,:]
                    T1_apparent_map = np.reshape(T1_apparent, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 
           
            final_image = np.transpose(final_image, (2, 1, 0)) 
           
            print("Finished motion correction for T1 mapping sequence!")

            T1_estimated_map = np.transpose(T1_estimated_map)
            T1_apparent_map = np.transpose(T1_apparent_map)

            corrected_series = series_magnitude.new(series_name="T1_Map_Series_Registered")
            corrected_series.write(final_image)
            # Display series
            #corrected_series.display()
            #output_folder = weasel.select_folder() 
            #corrected_series.export_as_nifti(directory=output_folder)

             # display maps
            T1_estimated_map_final = series_magnitude.new(series_name="T1_estimated_map_Final_Registered")
            T1_estimated_map_final['WindowCenter'] = 1200
            T1_estimated_map_final['WindowWidth'] = 300
            T1_estimated_map_final.write(T1_estimated_map)
            #T1_estimated_map_final.display()
            #T1_estimated_map_final.export_as_nifti(directory=output_folder)

            T1_apparent_map_Final = series_magnitude.new(series_name="T1_apparent_map_Final_Registered")
            T1_apparent_map_Final.write(T1_apparent_map)
            #T1_apparent_map_Final.display()
            #T1_apparent_map_Final.export_as_nifti(directory=output_folder)
            # Refresh Weasel
            weasel.refresh()
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the T1 Map.", "T1 Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))


def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        elastix_parameters = Tools.read_elastix_model_parameters(script_dir + r'\models\Elastix_Parameters_Files\iBEAt\BSplines_T1.txt', ['MaximumNumberOfIterations', 256])
        image_parameters  =  parameters
        InversionTime_slice_3 = model_arguments[2]
        signal_model_parameters = InversionTime_slice_3
        output_images = MDR.model_driven_registration(images, image_parameters, model, signal_model_parameters, elastix_parameters, precision = 1, function = 'main', log = False)
        return output_images
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))
    

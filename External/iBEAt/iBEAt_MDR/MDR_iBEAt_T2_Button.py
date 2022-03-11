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
        
        T2_prep_times = [0,30,40,50,60,70,80,90,100,110,120]
        
        if len(T2_prep_times) == 11:
            # Get Pixel Array and format it accordingly 
            series_magnitude = series.Magnitude.sort("SliceLocation") 
             # read pixel information and reformat shape
            pixel_array = series_magnitude.PixelArray
             # display the new sorted series
            sorted_series_magnitude = series_magnitude.new(series_name="T2_Map_Series_Sorted")
            sorted_series_magnitude.write(pixel_array)
            # Display sorted series
            sorted_series_magnitude.display()
            
            pixel_array = np.transpose(pixel_array)
            reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1],int(np.shape(pixel_array)[2]/len(T2_prep_times)),len(T2_prep_times))
            magnitude_array = pixel_array.reshape(reformat_shape) 
        
            affine_array = series_magnitude.Affine
            #read image parameters
            parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series[0].path))[:2]

            images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], len(T2_prep_times)))
            final_image = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], len(T2_prep_times)))
            T2_map = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            T2_S0 = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            
           
            for index in range(np.shape(magnitude_array)[2]):

                if index ==2:
                    
                    images = np.squeeze(magnitude_array[:, :, index, :])
                    # import the T2* module
                    full_module_name = "models.T2"
                    # generate a module named as a string 
                    model = importlib.import_module(full_module_name)
                    output_motion = motion_pipeline(weasel, images, parameters, model, [weasel, images, T2_prep_times, affine_array])
                    final_image = output_motion[0]
                    S0 = output_motion[3][0,:]
                    T2_S0 = np.reshape(S0, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 
                    T2_par_map = output_motion[3][1,:]
                    T2_map = np.reshape(T2_par_map, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 

            final_image = np.transpose(final_image, (2, 1, 0)) 
         
            print("Finished motion correction for T2 series!")

            T2_S0 = np.transpose(T2_S0)
            T2_map = np.transpose(T2_map)

            corrected_series = series_magnitude.new(series_name="T2_Series_Registered")
            corrected_series.write(final_image)
            # Display series
            #corrected_series.display()
            #output_folder = weasel.select_folder()
            #corrected_series.export_as_nifti(directory=output_folder)
            # display maps
            T2_star_map_final = series_magnitude.new(series_name="T2_Map_Final_Registered")
            T2_star_map_final.write(T2_map)
            #T2_star_map_final.display()
            #T2_star_map_final.export_as_nifti(directory=output_folder)

            T2_star_S0_final = series_magnitude.new(series_name="T2_S0_Final_Registered")
            T2_star_S0_final.write(T2_S0)
            #T2_star_S0_final.display()
            #T2_star_S0_final.export_as_nifti(directory=output_folder)

            # Refresh Weasel
            weasel.refresh()
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the T2 Map.", "T2 Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))


def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        elastix_parameters = Tools.read_elastix_model_parameters(script_dir + r'\models\Elastix_Parameters_Files\iBEAt\BSplines_T2.txt', ['MaximumNumberOfIterations', 256])
        image_parameters  =  parameters
        T2_prep_times = model_arguments[2]
        signal_model_parameters = T2_prep_times
        output_images = MDR.model_driven_registration(images, image_parameters, model, signal_model_parameters, elastix_parameters, precision = 1, function = 'main', log = False)
        return output_images
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))
    

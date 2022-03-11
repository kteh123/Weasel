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
        
        echo_list = weasel.unique_elements(series["EchoTime"])
        print("T2* sequence TE list")
        print(echo_list)
        
        if len(echo_list) == 12:
            # Get Pixel Array and format it accordingly
            series_magnitude = series.Magnitude.sort("SliceLocation", "EchoTime") 
            # read pixel information and reformat shape
            pixel_array = series_magnitude.PixelArray
             # display the new sorted series
            sorted_series_magnitude = series_magnitude.new(series_name="T2_Star_Map_Sorted")
            sorted_series_magnitude.write(pixel_array)
            # Display sorted series
            sorted_series_magnitude.display()
          
            pixel_array = np.transpose(pixel_array) # CHECK MEMORY ALLOCATION
            reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1],int(np.shape(pixel_array)[2]/len(echo_list)),len(echo_list))
            magnitude_array = pixel_array.reshape(reformat_shape) #(512, 512, 5, 12)
            #TODO: do we need the affine array for MDR?
            affine_array = series_magnitude.Affine
            #read image parameters
            parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series[0].path))[:2]
        
            final_image = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], len(echo_list)))
            images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], len(echo_list)))
            T2_star_map = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            T2_star_S0 = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
           
            for index in range(np.shape(magnitude_array)[2]):

                if index ==2:
                    images = np.squeeze(magnitude_array[:, :, index, :])
                    # import the T2* module
                    full_module_name = "models.T2star"
                    # generate a module named as a string 
                    model = importlib.import_module(full_module_name)
                    #print("model")
                    #print(model)
                    output_motion = motion_pipeline(weasel, images, parameters, model, [weasel, images, echo_list, affine_array])
                    final_image = output_motion[0]
                    S0 = output_motion[3][0,:]
                    T2_star_S0 = np.reshape(S0, (np.shape(final_image)[0], np.shape(final_image)[1])) 
                    T2_star_par_map = output_motion[3][1,:]
                    T2_star_map = np.reshape(T2_star_par_map, (np.shape(final_image)[0], np.shape(final_image)[1])) 
                
            final_image = np.transpose(final_image, (2, 1, 0))
            T2_star_S0 = np.transpose(T2_star_S0)
            T2_star_map = np.transpose(T2_star_map)

            corrected_series = series_magnitude.new(series_name="T2star_MDR_Registered")
            corrected_series.write(final_image)
            
            print("Finished motion correction for iBEAt Siemens Leeds T2* sequence!")
            
            # Display series
            #corrected_series.display()
            #output_folder = weasel.select_folder()# WHAT HAPPENS ON CANCEL?
            #corrected_series.export_as_nifti(directory=output_folder)
           
            # display maps
            T2_star_map_final = series_magnitude.new(series_name="T2star_Map_Final_Registered")
            T2_star_map_final.write(T2_star_map)
            #T2_star_map_final.display()
            #T2_star_map_final.export_as_nifti(directory=output_folder)

            T2_star_S0_final = series_magnitude.new(series_name="T2star_S0_Final_Registered")
            T2_star_S0_final.write(T2_star_S0)
            #T2_star_S0_final.display()
            #T2_star_S0_final.export_as_nifti(directory=output_folder)
            # Refresh Weasel
            weasel.refresh()
            
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the T2Star Map.", "T2Star Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))


def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        elastix_parameters = Tools.read_elastix_model_parameters(script_dir + r'\models\Elastix_Parameters_Files\iBEAt\BSplines_T2star.txt', ['MaximumNumberOfIterations', 256])
        image_parameters  =  parameters
        echo_times = model_arguments[2]
        signal_model_parameters = echo_times
        output_images = MDR.model_driven_registration(images, image_parameters, model, signal_model_parameters, elastix_parameters, precision = 1, function = 'main', log = False)
        return output_images
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))
    


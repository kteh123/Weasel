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
    
        b_values_original = []
        b_Vec_original = []
        image_orientation_patient_original = []
        b_values_original = series[(0x19, 0x100c)]
        b_Vec_original = series[(0x19, 0x100e)] # ok
        image_orientation_patient_original = series['ImageOrientationPatient']
      
        if len(b_values_original) >= 146: #146 x number of slices being processed
            # Get Pixel Array and format it accordingly
            series_magnitude = series.sort("SliceLocation")
            slice_locations_DTI = weasel.unique_elements(series["SliceLocation"])
            pixel_array = series_magnitude.PixelArray
            # display the new sorted series
            sorted_series_magnitude = series_magnitude.new(series_name="DTI_Sorted_Series")
            sorted_series_magnitude.write(pixel_array)
            # Display sorted series
            sorted_series_magnitude.display()

            pixel_array = np.transpose(pixel_array)
            reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1], int(len(slice_locations_DTI)), 146)
            magnitude_array = pixel_array.reshape(reformat_shape) 
           
            affine_array = series_magnitude.Affine
            parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series[0].path))[:2]
          
            final_image = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], 146))
            images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], 146))
            FA = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            ADC = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
  
            for index in range(np.shape(magnitude_array)[2]):
                if index == int(np.shape(magnitude_array)[2]/2):
                   
                    images = np.squeeze(magnitude_array[:, :, index,:]) 
                    # import the DTI module
                    full_module_name = "models.DTI"
                    # generate a module named as a string 
                    model = importlib.import_module(full_module_name)
                    output_motion = motion_pipeline(weasel, images, parameters, model, [weasel, images, b_values_original, b_Vec_original, image_orientation_patient_original, affine_array])
                    final_image = output_motion[0]
                    FA_DTI = output_motion[3][0,:]
                    FA = np.reshape(FA_DTI, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 
                    ADC_DTI = output_motion[3][1,:]
                    ADC = np.reshape(ADC_DTI, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]])
                    
         
            final_image = np.transpose(final_image, (2, 1, 0)) 

            print("Finished motion correction for DTI sequence!")

            FA = np.transpose(FA)
            ADC = np.transpose(ADC)

            corrected_series = series_magnitude.new(series_name="DTI_Registered")
            corrected_series.write(final_image)
            # Display series
            #corrected_series.display()
            #output_folder = weasel.select_folder()
            #corrected_series.export_as_nifti(directory=output_folder)

            # display maps
            FA_final = series_magnitude.new(series_name="FA_DTI_final_Registered")
            FA_final.write(FA)
            #FA_final.display()
            #FA_final.export_as_nifti(directory=output_folder)

            ADC_final = series_magnitude.new(series_name="ADC_DTI_final_Registered")
            ADC_final.write(ADC)
            #ADC_final.display()
            #ADC_final.export_as_nifti(directory=output_folder)

            # Refresh Weasel
            weasel.refresh()
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the DTI FA Map.", "DTI Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))

def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        elastix_parameters = Tools.read_elastix_model_parameters(script_dir + r'\models\Elastix_Parameters_Files\iBEAt\BSplines_DTI.txt', ['MaximumNumberOfIterations', 256])
        image_parameters  =  parameters
        b_values_original = model_arguments[2]
        b_values = b_values_original[2044:2190] #ok (2190-146:146x15)
        
        b_Vec_original = model_arguments[3]
        b_Vec = b_Vec_original[2044:2190]
        
        image_orientation_patient_original = model_arguments[4]
        image_orientation_patient = image_orientation_patient_original[2044:2190]
        
        signal_model_parameters = []
        signal_model_parameters.append(b_values)
        signal_model_parameters.append(b_Vec)
        signal_model_parameters.append(image_orientation_patient)

        output_images = MDR.model_driven_registration(images, image_parameters, model, signal_model_parameters, elastix_parameters, precision = 1, function = 'main', log = False)
        return output_images
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))
    


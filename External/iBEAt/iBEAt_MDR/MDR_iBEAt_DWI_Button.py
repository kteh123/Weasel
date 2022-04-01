import os
from MDR import MDR, Tools
import numpy as np
import importlib
from itertools import repeat
#***************************************************************************

def isSeriesOnly(self):
    return True

def main(weasel, series=None):
    try:
        if series is None:
            series = weasel.series()[0]
    
        b_values_original = [0,10.000086, 19.99908294, 30.00085926, 50.00168544, 80.007135, 100.0008375, 199.9998135, 300.0027313, 600.0]
        
        b_values = []
        b_values = list(repeat(b_values_original, 3)) # repeated 3 times for 3 sets of IVIM images
        b_Vec_original = series[(0x19, 0x100e)] # none - weasel cannot read this tag (likely not available in dicom header)
        image_orientation_patient = series['ImageOrientationPatient']
        if len(b_values) >= 3: # list of 3 sets of b values

            series_magnitude = series.sort("SliceLocation")
            pixel_array = series_magnitude.PixelArray
            # display the new sorted series
            sorted_series_magnitude = series_magnitude.new(series_name="DWI_series_sorted") 
            sorted_series_magnitude.write(pixel_array)
            # Display sorted series
            sorted_series_magnitude.display()
            
            pixel_array = np.transpose(pixel_array)
            #print(np.shape(pixel_array)) # (172, 172, 900)
            reformat_shape = (np.shape(pixel_array)[0], np.shape(pixel_array)[1], int(np.shape(pixel_array)[2]/30), 30)
            #print(reformat_shape) #(172, 172, 30, 30)
            magnitude_array = pixel_array.reshape(reformat_shape)
          
            affine_array = series_magnitude.Affine
            parameters = Tools.get_sitk_image_details_from_DICOM(os.path.dirname(series[0].path))[:2]
           
            final_image = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], int(len(b_values)*10)))
            images =  np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1], int(len(b_values)*10)))
            S0 = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
            ADC = np.empty((np.shape(pixel_array)[0], np.shape(pixel_array)[1]))
  
            for index in range(np.shape(magnitude_array)[2]):

                if index ==int(np.shape(magnitude_array)[2]/2):
                   
                    images = np.squeeze(magnitude_array[:, :, index, :]) 
                    # import the DWI module
                    full_module_name = "models.DWI_monoexponential"
                    # generate a module named as a string 
                    model = importlib.import_module(full_module_name)
                    output_motion = motion_pipeline(weasel, images, parameters, model, [weasel, images, b_values, b_Vec_original, image_orientation_patient, affine_array])
                    final_image = output_motion[0]
                    S0_DWI = output_motion[3][0,:]
                    S0 = np.reshape(S0_DWI, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]]) 
                    ADC_DWI = output_motion[3][1,:]
                    ADC = np.reshape(ADC_DWI, [np.shape(pixel_array)[0], np.shape(pixel_array)[1]])
                   
           
            final_image = np.transpose(final_image, (2, 1, 0)) 
            
            print("Finished motion correction for IVIM sequence!")

            S0 = np.transpose(S0)
            ADC = np.transpose(ADC)

            corrected_series = series_magnitude.new(series_name="IVIM_Registered")
            corrected_series.write(final_image)
            # Display series
            #corrected_series.display()
            #output_folder = weasel.select_folder()
            #corrected_series.export_as_nifti(directory=output_folder)

            # display maps
            S0_final = series_magnitude.new(series_name="S0_final_Registered")
            S0_final.write(S0)
            #S0_final.display()
            #S0_final.export_as_nifti(directory=output_folder)

            ADC_final = series_magnitude.new(series_name="ADC_final_Registered")
            ADC_final.write(ADC)
            #ADC_final.display()
            #ADC_final.export_as_nifti(directory=output_folder)
            # Refresh Weasel
            weasel.refresh()
        else:
            weasel.warning("The selected series doesn't have sufficient requirements to calculate the IVIM ADC Map.", "IVIM Sequence not selected")
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.main: ' + str(e))


def motion_pipeline(weasel, images, parameters, model, model_arguments):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        elastix_parameters = Tools.read_elastix_model_parameters(script_dir + r'\models\Elastix_Parameters_Files\iBEAt\BSplines_IVIM.txt', ['MaximumNumberOfIterations', 256])
        image_parameters  =  parameters
        b_values = model_arguments[2]
        
        b_Vec_original = []
        g_dir_01 = [1,0,0]
        g_dir_02 = [0,1,0]
        g_dir_03 = [0,0,1]

        for i in range(10):
            b_Vec_original.append(g_dir_01)

        for i in range(10,20):
            b_Vec_original.append(g_dir_02)

        for i in range(21,30):
            b_Vec_original.append(g_dir_03)


        image_orientation_patient = model_arguments[4]

        signal_model_parameters = []
        signal_model_parameters.append(b_values)
        signal_model_parameters.append(b_Vec_original)
        signal_model_parameters.append(image_orientation_patient)

        output_images = MDR.model_driven_registration(images, image_parameters, model, signal_model_parameters, elastix_parameters, precision = 1, function = 'main', log = False)
        return output_images
    except Exception as e:
        weasel.log_error('Error in function MDR-iBEAt.motion_pipeline: ' + str(e))


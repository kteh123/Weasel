import matplotlib.pyplot as plt
import numpy as np

def isEnabled(weasel):
    return True

def main(weasel):
    # Get series checked by the user
    list_of_series = weasel.series()
    if len(list_of_series) < 2:
        weasel.error(msg="Please select 2 or more series in the Treeview", title="Series not selected")
        return

    # Get list of the selected series (in the string format)
    inputList = [series.seriesID for series in list_of_series] # series is an instance of class Series and seriesID is the attribute with the series Number and Description
    
    cancel, fields = weasel.user_input(
            {"type":"dropdownlist", "label":"Signal Image", "default":0, "list":inputList},
            {"type":"dropdownlist", "label":"Mask Image", "default":1, "list":inputList},
            title = "Select Series")
    if cancel: return
    
    series_signal = list_of_series[fields[0]['value']]
    series_mask = list_of_series[fields[1]['value']]

    ROI_signal_values = []
    ROI_time_values = []
    
    # We'll assume that series_signal and series_mask sizes are the same
    weasel.message(msg="Loading Signal and Mask arrays...", title="Ferret Joao")
    mask = series_mask.PixelArray
    signal = series_signal.PixelArray
    for i, image in enumerate(signal):
        weasel.progress_bar(max=len(signal), index=i+1, msg="Calculating mean of Image {}", title="Ferret Joao")
        mean_signal = round(np.nanmean(np.extract(mask[i], image)), 3)
        ROI_signal_values.append(mean_signal)
    
    #Still need to test the ROI argument
    #signal_masked = series_signal.PixelArray(ROI=series_mask)
    #for image in signal_masked:
    #    mean_signal = round(np.nanmean(image), 3)
    #    ROI_signal_values.append(mean_signal)

    ROI_time_values = series_signal["AcquisitionTime"]
    print(ROI_time_values)
    print(ROI_signal_values)
    ROI_curve = np.array([ROI_time_values, ROI_signal_values])

    new_series = series_signal.new(suffix = '_ROI_Curve')
    new_series.write(ROI_curve)

    #weasel.plot(ROI_time_values, ROI_signal_values)
    #weasel.histogram(ROI_time_values, ROI_signal_values)

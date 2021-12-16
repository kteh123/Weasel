"""
Find all series with the same acquisition time and merge them into a new series of the same study.
"""

import numpy as np

def enable(weasel):
    return False

def main(weasel):
    seriesList = weasel.series()
    for series in seriesList:
        for time in weasel.unique_elements(series["AcquisitionTime"]):
            series_time = series.copy().where("AcquisitionTime", "==", time) # Without copy, you overwrite
            series_time["SeriesDescription"] = '[ Acquisition time: ' + time + ' ]'
    weasel.refresh()


def suggestion(weasel):
    # Get all series selected by the user
    series = weasel.series()
    # Loop over the studies that the series are part of
    for study in series.studies():
        # Get the series that are part of the study
        series_of_study = series.of(study)
        # Loop over the unique acquisition times
        for time in series_of_study.AcquisitionTime.unique():
            # Get the series with the given acquisition times
            series_time = series_of_study.where("AcquisitionTime" == time)
            # Merge a copy of them into a new series
            series_time = series_time.copy().merge()
            # rename the series description
            series_time.SeriesDescription += '[ Acquisition time: ' + time + ' ]'


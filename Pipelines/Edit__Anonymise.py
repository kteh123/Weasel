
"""
Anonymises the checked images showing progress with a status bar.
"""

import pydicom
from pydicom.dataset import Dataset

def main(weasel):
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in enumerate(list_of_images):      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Anonymising images {}")

        image["PatientName"] = "Anonymous"    # replace PatientName
        image["PatientID"] = "Anonymous"
        image["PatientBirthDate"] = "19000101"
        image["OtherPatientNames"] = ["Anonymous 1", "Anonymous 2"]
        image["OtherPatientIDsSequence"] = [Dataset(),Dataset()]
        image["ReferencePatientPhotoSequence"] = [Dataset(),Dataset()]

    weasel.refresh()                # Refresh weasel


    

    
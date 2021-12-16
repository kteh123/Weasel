"""
Anonymises a copy of the checked images showing progress with a status bar.
"""

from pydicom.dataset import Dataset

def main(weasel):
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in enumerate(list_of_images):      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Anonymising images {}")

        new_image = image.copy()
        new_image["PatientName"] = "Anonymous"    # replace PatientName
        new_image["PatientID"] = "Anonymous"
        new_image["PatientBirthDate"] = "19000101"
        new_image["OtherPatientNames"] = ["Anonymous 1", "Anonymous 2"]
        new_image["OtherPatientIDsSequence"] = [Dataset(),Dataset()]
        new_image["ReferencePatientPhotoSequence"] = [Dataset(),Dataset()]         

    weasel.refresh()                # Refresh weasel


    

    
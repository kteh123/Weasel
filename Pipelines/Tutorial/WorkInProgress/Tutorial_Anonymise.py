#**************************************************************************
# Template part of a tutorial 
# Anonymises the checked images
# showing progress with a status bar 
#***************************************************************************

from pydicom.dataset import Dataset

def main(weasel):
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in list_of_images.enumerate():      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=list_of_images.length(), index=i+1, msg="Anonymising images {}")

        image.read()         # should become obsolete
        image.PatientName = "Anonymous"   
        image.PatientID = "Anonymous"
        image.PatientBirthDate = "19000101"
        image.OtherPatientNames = ["Anonymous 1", "Anonymous 2"]
        image.OtherPatientIDsSequence = [Dataset(),Dataset()]
        image.ReferencePatientPhotoSequence = [Dataset(),Dataset()]
        image.save()                  # write the dataset to disk
        weasel.refresh()                # Refresh weasel

"""
        ds = image.read()               # Load the dataset into memory
        ds.PatientName = "Anonymous"    # replace PatientName
        ds.PatientID = "Anonymous"
        ds.PatientBirthDate = "19000101"
        ds.OtherPatientNames = ["Anonymous 1", "Anonymous 2"]
        ds.OtherPatientIDsSequence = [Dataset(),Dataset()]
        ds.ReferencePatientPhotoSequence = [Dataset(),Dataset()]
        image.save(ds)                  # write the dataset to disk
"""


    

    
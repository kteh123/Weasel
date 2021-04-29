#**************************************************************************
# Template part of a tutorial 
# Anonymises the Patient ID of the checked images
# showing progress with a status bar 
#***************************************************************************

import pydicom

def main(weasel):

    #NewPatientID = pydicom.uid.generate_uid()
    # ID and UID are different things
    #NewPatientID = "Patient Identification Dummy"
    
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in enumerate(list_of_images):      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Anonymising images {}")
        image['PatientID'] = NewPatientID

    weasel.refresh()                # Refresh weasel


    

    

    
#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked studies
# showing progress with a status bar 
#***************************************************************************

def main(weasel):
    list_of_studies = weasel.studies()                # get the list of studies checked by the user
    for i, study in enumerate(list_of_studies):      # Loop over studies in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_studies), index=i+1, msg="Copying studies {}")
        study.copy()                       # Copy and Display the new study  
    weasel.refresh()                       # Refresh Weasel
    
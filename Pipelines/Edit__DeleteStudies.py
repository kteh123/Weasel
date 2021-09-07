
    
#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked studies
# showing progress with a status bar 
#***************************************************************************

def main(weasel):
    list_of_studies = weasel.studies() # Get the list of studies checked by the user
    for i, study in enumerate(list_of_studies): # Loop over studies in the list and display a progress bar
        weasel.progress_bar(max=len(list_of_studies), index=i+1, msg="Deleting studies {}")
        study.delete()
    weasel.refresh()
    
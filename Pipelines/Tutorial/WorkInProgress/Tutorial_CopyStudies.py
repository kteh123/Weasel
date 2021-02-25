#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked studies
# showing progress with a status bar 
#***************************************************************************

def main(Weasel):
    List = Weasel.studies()                # get the list of studies checked by the user
    for i, Study in List.enumerate:      # Loop over studies in the list and display a progress Bar
        Weasel.progress_bar(max=List.length, index=i+1, msg="Copying studies {}")
        Study.copy()                       # Copy and Display the new study  
    Weasel.refresh()                       # Refresh Weasel
    
#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked studies
# showing progress with a status bar 
#***************************************************************************

def main(Weasel):
    List = Weasel.Studies()                # get the list of studies checked by the user
    for i, Study in List.Enumerate():      # Loop over studies in the list and display a progress Bar
        Weasel.ProgressBar(max=List.Count(), index=i+1, msg="Copying studies {}")
        Study.Copy()                       # Copy and Display the new study  
    Weasel.Refresh()                       # Refresh Weasel
    
#**************************************************************************
# Template part of a tutorial 
# Merges the Images checked by the user into a new series under the same study
#***************************************************************************


def main(weasel):
    
    list_of_studies = weasel.studies() 
    if len(list_of_studies) <= 1: return
    list_of_studies.merge(study_name='MergedStudyDescription')
    weasel.refresh()
    
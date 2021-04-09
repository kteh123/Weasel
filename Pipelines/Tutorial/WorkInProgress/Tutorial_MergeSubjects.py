#**************************************************************************
# Template part of a tutorial 
# Merges the Images checked by the user into a new series under the same study
#***************************************************************************


def main(weasel):
    
    list_of_subjects = weasel.subjects() 
    if len(list_of_subjects) <= 1: return
    list_of_subjects.merge(subject_name='MergedSubJoao')
    weasel.refresh()
    
#****************************************************************
# Create new series holding images of the same slice location
# If images are selected from multiple studies  
# then a new series is created inside each study
#****************************************************************

def main(weasel):

    # Get all images checked by the user
    images = weasel.images()
    # Loop over the studies that the images are part of
    for study in images.studies():
        # Get the part of the images that are in the study
        imgs = images.of(study)
        # Create a new study
        new_study = study.new_sibling(StudyDescription = 'Sorted by slice location')
        # Loop over the unique slice locations
        for loc in imgs.SliceLocation.unique():
            # get the images at slice location loc
            imgs_loc = imgs.where("SliceLocation" == loc)
            # store those images in a new series of the new study
            series = new_study.new_child(imgs_loc)
            # rename the series with the slice location
            series.SeriesDescription = 'Slice location [' + str(loc) + ']'
            

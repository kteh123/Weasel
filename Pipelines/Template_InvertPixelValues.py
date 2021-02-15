def main(Weasel):
    images = Weasel.images()
    if len(images) == 0: return 
    for i, image in enumerate(images):
        Weasel.progressBar(maxNumber=len(images), index=i, msg="Inverting image {}", title="Invert pixel values ")
        image.write(-image.PixelArray) 
    Weasel.closeProgressBar()
    Weasel.DisplayImages(images)
    # better would be
    # images.display()
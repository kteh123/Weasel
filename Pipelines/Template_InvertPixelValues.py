def main(Weasel):
    Images = Weasel.Images()
    if Images.Empty(): return
    for i, Image in enumerate(Images.List):
        Weasel.ProgressBar(max=Images.Count(), index=i, msg="Inverting image {}", title="Invert pixel values ")
        Image.write(-Image.PixelArray) 
    Weasel.CloseProgressBar()
    Images.Display()
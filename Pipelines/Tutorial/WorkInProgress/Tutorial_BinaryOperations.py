#**************************************************************************
# Template part of a tutorial 
# Performs a binary operation on two images and saves them in a new series, 
# image by image and showing a progress bar. 
#**************************************************************************

def main(Weasel):
    Images = Weasel.images(msg = "Please select the images")     
    if Images.empty: return    
    cancel, width, A, B, operation = Weasel.user_input(title="Settings for binary operation", 
        {"type":"list", "label":"Image A", "default":0,  "list": Images(0x0018, 0x0024)}
        {"type":"list", "label":"Image B", "default":0,  "list": Images(0x0018, 0x0024)}
        {"type":"list", "label":"operation", "default":0,  "list": ["A * B", "A / B", "A + B", "A - B"]}
        )
    if cancel: return
    Result = Images[A].copy(series_name=operation) 
    if operation == "A * B":
        Result.write(Images[A].PixelArray * Images[B].PixelArray)
    elif operation == "A / B":
        Result.write(Images[A].PixelArray / Images[B].PixelArray)
    elif operation == "A + B":
        Result.write(Images[A].PixelArray + Images[B].PixelArray)
    elif operation == "A - B":
        Result.write(Images[A].PixelArray - Images[B].PixelArray)
    Result.display()            
    Weasel.refresh()
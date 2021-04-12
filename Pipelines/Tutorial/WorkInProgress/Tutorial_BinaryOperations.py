#**************************************************************************
# Template part of a tutorial 
# Performs a binary operation on two images and saves them in a new series, 
# image by image and showing a progress bar. 
#**************************************************************************

def main(weasel):
    images = weasel.images(msg = "Please select the images")     
    if images.empty: return    
    cancel, fields = weasel.user_input(title="Settings for binary operation", 
        {"type":"list", "label":"Image A", "default":0,  "list": images.label()}
        {"type":"list", "label":"Image B", "default":0,  "list": images.label()}
        {"type":"list", "label":"operation", "default":0,  "list": ["A * B", "A / B", "A + B", "A - B"]}
        )
    if cancel: return

    result = images[A].copy(series_name=operation) 

    if operation == "A * B":
        result.write(images[A].PixelArray * Images[B].PixelArray)
    elif operation == "A / B":
        result.write(images[A].PixelArray / Images[B].PixelArray)
    elif operation == "A + B":
        result.write(images[A].PixelArray + Images[B].PixelArray)
    elif operation == "A - B":
        result.write(images[A].PixelArray - Images[B].PixelArray)
        
    result.display()            
    weasel.refresh()
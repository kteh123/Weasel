"""
This custom, composite widget allows the user to draw around and/or
paint a ROI.  

The user may draw around the boundary of the ROI and it is automatically
flood filled.  If the start and end positions of the drawn boundary do
not meet, they are automatically connected by a straight line prior to 
flood filling.

The user may also adjust the size of the ROI using an eraser tool.
The size of the paint and eraser tools may be changed by right-clicking 
on the image and selecting a size from a pop-up context menu. 

The image is displayed in an instance of the GraphicsItem class, 
which is contained in an instance of the GraphicView class. 
An instance of the  GraphicView class forms a custom widget that is
added to a layout on the MDI subwindow used to display the image.

ROI_Storage.py contains the class ROIs that provides a data structure 
for storing ROI data.  It links ROI name to the ROI drawn on 1 or more
images in a series. 

The Icons folder contains the graphic files containing the icons used 
identify buttons on the MDI subwindow and to change the appearance of the
mouse pointer when the zoom, draw, paint and eraser functions are selected.

In Resources.py, constants are defined that hold strings containing the file paths to
the above icons. 
"""

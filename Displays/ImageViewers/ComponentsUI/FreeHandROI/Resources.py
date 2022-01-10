"""
In this module string constants are defined that hold the file paths 
to graphic files containing icon images.
"""

import os, sys, pathlib
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    directory = os.path.join(sys._MEIPASS, 'Displays')
else:
    directory = os.path.join(pathlib.Path().absolute(), 'Displays')


MAGNIFYING_GLASS_CURSOR = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','Magnifying_Glass.png')
PEN_CURSOR = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','pencil.png')
BRUSH_CURSOR = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','paint_brush.png')
ERASER_CURSOR = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','erasor.png')
DELETE_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','delete_icon.png')
NEW_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','new_icon.png')
RESET_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','reset_icon.png')
SAVE_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','save_icon.png')
LOAD_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','load_icon.png')
EXPORT_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','export.png')
CONTRAST_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','contrast_icon.png')
BRIGHTNESS_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','brightness_icon.png')
APPLY_SERIES_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','applySeries_icon.png')
SLIDER_ICON = os.path.join(directory,'ImageViewers','ComponentsUI','FreeHandROI','Icons','slider_icon.png')
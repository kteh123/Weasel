from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom

def main(objWeasel):
    inputDict = {"DICOM Tag":"string", "Value":"string"}
    helpMsg = 'The DICOM Tag can be inserted in string or hexadecimal format.\nExample:\n'\
              '(0010,0010) => type PatientName or 0x00100010'
    paramList = ui.inputWindow(inputDict, title="Insert DICOM Tag element to change and its new value", helpText=helpMsg)
    if paramList is None: return # Exit function if the user hits the "Cancel" button
    tag = paramList[0]
    value = paramList[1]
    imageList = ui.getCheckedImages(objWeasel)
    ui.showMessageWindow(objWeasel, msg="Overwriting the checked DICOM files with the typed values", title="Edit DICOM")
    for image in imageList:
        image.Item(tag, value)
    ui.closeMessageWindow(objWeasel)
    imageList[0].DisplayMetadata()
    # Or image.DisplayMetadata(objWeasel)

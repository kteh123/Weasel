from Developer.MenuItems.DeveloperTools import UserInterfaceTools as ui
from Developer.MenuItems.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.MenuItems.DeveloperTools import GenericDICOMTools as dicom
import Developer.MenuItems.ViewMetaData as viewMetaData

def main(objWeasel):
    inputDict = {"DICOM Tag":"string", "Value":"string"}
    helpMsg = 'The DICOM Tag can be inserted in string or hexadecimal format.\nExample:\n'\
              '(0010,0010) => type PatientName or 0x00100010'
    paramList = ui.inputWindow(inputDict, title="Insert DICOM Tag element to change and its new value", helpText=helpMsg)
    if paramList is not None: 
        tag = paramList[0]
        value = paramList[1]
        imagePath = ui.getAllSelectedImages(objWeasel)
        ui.showMessageWindow(objWeasel, msg="Overwriting the DICOM files with the typed values", title="Edit DICOM")
        dicom.editDICOMTag(imagePath, tag, value)
        ui.closeMessageWindow(objWeasel)
        viewMetaData.main(objWeasel) # Put it in Developer Tool


#Hard-coded values alternative
#def editDICOM_Image(objWeasel):
#    # tag = "ImageType"
#    # value = "[DERIVED, JOAO_TYPE]"
#    tag = "0x00100010" # (0010, 0010) or PatientName
#    value = "Anonymous"
#    ui.showMessageWindow(objWeasel, "Overwriting the DICOM files with the typed values", title="Edit DICOM")
#    imagePath = ui.getAllSelectedImages(objWeasel)
#    dicom.editDICOMTag(imagePath, tag, value)
#    ui.closeMessageWindow(objWeasel)
#    viewMetaData.main(objWeasel) # Put it in Developer Tool
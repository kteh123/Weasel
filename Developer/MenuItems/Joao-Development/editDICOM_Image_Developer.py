import Developer.MenuItems.developerToolsModule as tool
import Developer.MenuItems.ViewMetaData as viewMetaData

def main(objWeasel):
    inputDict = {"DICOM Tag":"string", "Value":"string"}
    helpMsg = 'The DICOM Tag can be inserted in string or hexadecimal format.\nExample:\n'\
              '(0010,0010) => type PatientName or 0x00100010'
    paramList = tool.inputWindow(inputDict, title="Insert DICOM Tag element to change and its new value", helpText=helpMsg)
    tag = paramList[0]
    value = paramList[1]
    #tool.showProcessingMessageBox(objWeasel, msg="")
    imagePath = tool.getImagePathList(objWeasel)
    tool.editDICOMTag(imagePath, tag, value)
    #tool.messageWindow.closeMessageSubWindow(objWeasel)
    viewMetaData.main(objWeasel) # Put it in Developer Tool


#Hard-coded values alternative
#def editDICOM_Image(objWeasel):
#    # tag = "ImageType"
#    # value = "[DERIVED, JOAO_TYPE]"
#    tag = "0x00100010" # (0010, 0010) or PatientName
#    value = "Anonymous"
#    #tool.showProcessingMessageBox(objWeasel, msg="")
#    imagePath = tool.getImagePathList(objWeasel)
#    tool.editDICOMTag(imagePath, tag, value)
#    tool.messageWindow.closeMessageSubWindow(objWeasel)
#    viewMetaData.main(objWeasel) # Put it in Developer Tool
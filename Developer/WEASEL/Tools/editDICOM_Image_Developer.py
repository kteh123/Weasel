import Developer.WEASEL.Tools.developerToolsModule as tool
import Developer.WEASEL.Tools.ViewMetaData as viewMetaData

def editDICOM(objWeasel):
    # tag = "ImageType"
    # value = "[DERIVED, JOAO_TYPE]"
    # tag = "0x00100010" # (0010, 0010) or PatientName
    # value = "Anonymous"
    inputDict = {"DICOM Tag":"string", "Value":"string"}
    helpMsg = 'The DICOM Tag can be inserted in string or hexadecimal format.\nExample:\n'\
              '(0010,0010) => type PatientName or 0x00100010'
    paramList = tool.inputWindow(inputDict, title="Insert DICOM Tag element to change and its new value", helpText=helpMsg)
    tag = paramList[0]
    value = paramList[1]
    tool.showProcessingMessageBox(objWeasel)
    imagePath = tool.getImagePathList(objWeasel)
    tool.editDICOMTag(imagePath, tag, value)
    tool.messageWindow.closeMessageSubWindow(objWeasel)
    viewMetaData.viewMetadata(objWeasel)
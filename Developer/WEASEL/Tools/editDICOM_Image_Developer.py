import Developer.WEASEL.Tools.developerToolsModule as tool
import Developer.WEASEL.Tools.ViewMetaData as ViewMetaData
# from ast import literal_eval # Convert strings to their actual content. Eg. "[a, b]" becomes the actual list [a, b]

def editDICOM(objWeasel):
    tool.showProcessingMessageBox(objWeasel)
    # tag = "ImageType"
    # value = "[DERIVED, JOAO_TYPE]"
    # literal_eval(value)
    tag = "0x00100010" # (0010, 0010) or PatientName
    value = "JoaoSousaTest"
    imagePath = tool.getImagePathList(objWeasel)
    tool.editDICOMTag(imagePath, tag, value)
    tool.messageWindow.closeMessageSubWindow(objWeasel)
    # For some reason, the line below is not working and it makes Weasel crash
    # The following line should display the metadata of the updated/overwritten data
    # ViewMetaData.viewMetaData(objWeasel)
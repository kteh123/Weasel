from CoreModules.WEASEL.TreeView import refreshDICOMStudiesTreeView

def isEnabled(weasel):
    return True

def main(weasel):
    
    refreshDICOMStudiesTreeView(weasel)
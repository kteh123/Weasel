import Developer.DeveloperTools as tools
from Developer.DeveloperTools import UserInterfaceTools as ui
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
import MenuItems.UKRIN_MAPS.B0MapDICOM_Image as b0
import MenuItems.UKRIN_MAPS.T1MapMolliDICOM_Image as t1
import MenuItems.UKRIN_MAPS.T2StarMapDICOM_Image as t2_star

#***************************************************************************

def main(objWeasel):
    if tools.treeView.isASeriesSelected(objWeasel):
        # Setting Window Input window
        inputDict = {"Algorithm":"dropdownlist", "Dummy":"listview"}
        scriptsList = ["B0", "T2*", "T1 Molli"]
        dummyList = ["Animals", "Plants", "Trees"]
        info = "Choose one of the options in the dropdown list"
        paramList = ui.inputWindow(inputDict, title="UKRIN-MAPS Calculation", helpText=info, lists=[scriptsList, dummyList])
        choice = paramList[0]
        if choice == "B0":
            b0.main(objWeasel)
        if choice == "T2*":
            t2_star.main(objWeasel)
        if choice == "T1 Molli":
            t1.main(objWeasel)
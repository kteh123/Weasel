import Developer.WEASEL.Tools.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
import Developer.WEASEL.Tools.B0MapDICOM_Image as b0
import Developer.WEASEL.Tools.T1MapMolliDICOM_Image as t1
import Developer.WEASEL.Tools.T2StarMapDICOM_Image as t2_star

#***************************************************************************

def chooseAndRunAlgorithm(objWeasel):
    if tool.treeView.isASeriesSelected(objWeasel):
        # Lower and upper threshold from the input window. No parameter validation here
        inputDict = {"Algorithm":"dropdownlist", "Dummy":"listview"}
        scriptsList = ["B0", "T2*", "T1 Molli"]
        dummyList = ["Animals", "Plants", "Trees"]
        info = "Choose one of the options in the dropdown list"
        paramList = tool.inputWindow(inputDict, title="UKRIN-MAPS Calculation", helpText=info, lists=[scriptsList, dummyList])
        choice = paramList[0]
        if choice == "B0":
            b0.saveB0MapSeries(objWeasel)
        if choice == "T2*":
            t2_star.saveT2StarMapSeries(objWeasel)
        if choice == "T1 Molli":
            t1.saveT1MapSeries(objWeasel)
from PyQt5.QtCore import  Qt

class State():
    """
    Helper methods to extraction information about the current state of Weasel 
    """
    
    def getMDIAreaDimensions(self):
        """
        Dimensions of the weasel canvas
        """
        return self.mdiArea.height(), self.mdiArea.width() 

    @property
    def isAnImageChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedImagesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    imagesCount = series.childCount()
                    for k in range(imagesCount):
                        image = series.child(k)
                        if image.checkState(0) == Qt.Checked:
                            flag = True
                            break
        return flag

    @property
    def isASeriesChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedSeriesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    if series.checkState(0) == Qt.Checked:
                        flag = True
                        break
        return flag
     
    @property
    def isAStudyChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedStudiesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)   
                if study.checkState(0) == Qt.Checked:
                    flag = True
                    break
        return flag

    @property
    def isASubjectChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedSubjectsList = []
        for i in range(subjectCount):
            subject = root.child(i)
            if subject.checkState(0) == Qt.Checked:
                flag = True
                break
        return flag
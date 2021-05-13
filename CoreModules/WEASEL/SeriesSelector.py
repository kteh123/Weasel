from PyQt5.QtWidgets import (QComboBox, QGroupBox,
                             QFormLayout, QApplication, 
                             QLabel)
import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"

class SeriesSelector:
    """This class creates three linked cascading lists in a 
    group box with the title groupBoxTitle.
    Together with an adjacent label, the lists are arranged 
    vertically in a column. 
    The top list allows the user to select the subject. 
    The subject selection dynamically determines the contents 
    of the middle study list. Only studies belonging to the 
    selected subject are displayed. 
    The study selected dynamically determines the contents 
    of the bottom series list.  Only series belonging to the
    selected study are displayed. 

    The property selectedSeriesData returns the names of selected
    subject, study and series in that order. 
    """
    def __init__(self, pointerToWeasel, groupBoxTitle=""):
        try:
            logger.info("SeriesSelect object created")
            self.title = groupBoxTitle
            self.weasel = pointerToWeasel
        except Exception as e:
            print('Error in class SeriesSelector.__init__: ' + str(e))
            logger.error('Error in class SeriesSelector.__init__: ' + str(e))


    def createSeriesSelector(self):
        try:
            formLayout = QFormLayout()
            self.groupBox = QGroupBox(self.title)
            self.groupBox.setLayout(formLayout)
            labelSubject = QLabel("Subject")
            labelStudy = QLabel("Study")
            labelSeries = QLabel("Series")
            self.listSubjects = QComboBox()
            self.listStudies = QComboBox()
            self.listSeries = QComboBox()
            formLayout.addRow(labelSubject, self.listSubjects)
            formLayout.addRow(labelStudy, self.listStudies)
            formLayout.addRow(labelSeries, self.listSeries)
            self.initialiseLists()
            self.setUpEvents()

            return self.groupBox
        except Exception as e:
            print('Error in SeriesSelector.createSeriesSelector: ' + str(e))
            logger.exception('Error in SeriesSelector.createSeriesSelector: ' + str(e))


    def initialiseLists(self):
        try:
            subjectList = self.weasel.objXMLReader.getSubjectList()
            self.listSubjects.addItems(subjectList)
            QApplication.processEvents()
            subjectID = subjectList[0]
            studyList = self.weasel.objXMLReader.getStudyList(subjectID)
            studyID = studyList[0]
            self.listStudies.addItems(studyList)
            QApplication.processEvents()
            seriesList = self.weasel.objXMLReader.getSeriesList(subjectID, studyID)
            self.listSeries.addItems(seriesList)

        except Exception as e:
            print('Error in SeriesSelector.initialiseLists: ' + str(e))
            logger.exception('Error in SeriesSelector.initialiseLists: ' + str(e))


    def setUpEvents(self):
        try:
            self.listSubjects.currentIndexChanged.connect(self.updateStudy)
            self.listStudies.currentIndexChanged.connect(self.updateSeries)
        except Exception as e:
            print('Error in SeriesSelector.setUpEvents: ' + str(e))
            logger.exception('Error in SeriesSelector.setUpEvents: ' + str(e))


    def updateStudy(self):
        subjectID = self.listSubjects.currentText()
        studyList = self.weasel.objXMLReader.getStudyList(subjectID)
        self.listStudies.clear()
        self.listStudies.addItems(studyList)


    def updateSeries(self):
        subjectID = self.listSubjects.currentText()
        studyID = self.listStudies.currentText()
        seriesList = self.weasel.objXMLReader.getSeriesList(subjectID, studyID)
        self.listSeries.clear()
        self.listSeries.addItems(seriesList)
             

    @property
    def selectedSeriesData(self):
        return [self.listSubjects.currentText(),
            self.listStudies.currentText(),
            self.listSeries.currentText()]

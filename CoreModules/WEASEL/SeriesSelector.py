from PyQt5.QtWidgets import (QComboBox, QGroupBox,
                             QFormLayout, QApplication, 
                             QLabel)
import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"

class SeriesSelector:
    """description of class"""
    def __init__(self, title, pointerToWeasel, mask=False):
        try:
            logger.info("SeriesSelect object created")
            self.title = title
            self.weasel = pointerToWeasel
            self.mask = mask
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
            if self.mask:
                maskList = self.weasel.objXMLReader.getMaskList(subjectID, studyID)
                self.listSeries.addItems(maskList)
            else:
                seriesList = self.weasel.objXMLReader.getNonMaskSeriesList(subjectID, studyID)
                self.listSeries.addItems(seriesList)

        except Exception as e:
            print('Error in SeriesSelector.initialiseLists: ' + str(e))
            logger.exception('Error in SeriesSelector.initialiseLists: ' + str(e))


    def setUpEvents(self):
        try:
            self.listSubjects.currentIndexChanged.connect(self.updateStudy)
            if self.mask:
                self.listStudies.currentIndexChanged.connect(self.updateMasks)
            else:
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
        seriesList = self.weasel.objXMLReader.getNonMaskSeriesList(subjectID, studyID)
        self.listSeries.clear()
        self.listSeries.addItems(seriesList)
        

    def updateMasks(self):
        subjectID = self.listSubjects.currentText()
        studyID = self.listStudies.currentText()
        maskList = self.weasel.objXMLReader.getMaskList(subjectID, studyID)
        self.listSeries.clear()
        self.listSeries.addItems(maskList)
        

    @property
    def selectedSeriesData(self):
        return [self.listSubjects.currentText(),
            self.listStudies.currentText(),
            self.listSeries.currentText()]

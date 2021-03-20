import xml.etree.cElementTree as ET  
from pathlib import Path
from datetime import datetime
import logging
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image

logger = logging.getLogger(__name__)

class WeaselXMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = ""
            self.tree = None 
            self.root = None 

            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in WeaselXMLReader.__init__: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.__init__: ' + str(e)) 
            

    def parseXMLFile(self, fullFilePath): 
        """Loads and parses the XML configuration file at fullFilePath.
       After successful parsing, the XML tree and its root node
      is stored in memory."""
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = fullFilePath
            self.tree = ET.parse(fullFilePath)
            self.root = self.tree.getroot()
            return self.root
            # Uncomment to test XML file loaded OK
            #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
           
            logger.info('In module ' + __name__ 
                    + 'WeaselXMLReader.parseConfigFile ' + fullFilePath)

        except ET.ParseError as et:
            print('WeaselXMLReader.parseConfigFile error: ' + str(et)) 
            logger.error('WeaselXMLReader.parseConfigFile error: ' + str(et))
            self.hasXMLFileParsedOK = False
            
        except Exception as e:
            print('Error in WeaselXMLReader.parseConfigFile: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.parseConfigFile: ' + str(e)) 
            self.hasXMLFileParsedOK = False
    

    def getXMLRoot(self):
        return self.root


    def getStudies(self):
        return self.root.findall('.//subject/study')


    def getSubjects(self):
        try:
            return self.root.findall('.//subject')
        except Exception as e:
            print('Error in WeaselXMLReader.getSubjects: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getSubjects: ' + str(e))

   
    def getImageList(self, subjectID, studyID, seriesID):
        """Returns a list of image elements in a specific series"""
        try:
            #print("getImageList: studyID={}, seriesID={}".format(studyID, seriesID))

            xPath = './/subject[@id='+ chr(34) + subjectID + chr(34) + \
                    ']/study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'        
            return self.root.findall(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getImageList: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageList: ' + str(e))


    def saveXMLFile(self, filePath=None):
        try:
            if filePath is None:
                filePath = self.fullFilePath
            self.tree.write(filePath)
        except Exception as e:
            print('Error in WeaselXMLReader.saveXMLFile: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.saveXMLFile: ' + str(e))


    def getSubject(self, subjectID):
        try:
            xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) + ']'
            #print(xPath)
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getSubject: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getSubject: ' + str(e))


    def setSubjectExpandedState(self, subjectID, expandedState='True'):
        try:
            subjectElement = self.getSubject(subjectID)
            subjectElement.set('expanded', expandedState)
        except Exception as e:
            print('Error in WeaselXMLReader.setSubjectExpandedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setSubjectExpandedState: ' + str(e))


    def setSubjectCheckedState(self, subjectID, checkedState='True'):
        try:
            subjectElement = self.getSubject(subjectID)
            subjectElement.set('checked', checkedState)
        except Exception as e:
            print('Error in WeaselXMLReader.setSubjectExpandedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setSubjectExpandedState: ' + str(e))


    def getStudy(self, subjectID, studyID):
        try:
            xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) +  \
                    ']/study[@id=' + chr(34) + studyID + chr(34) + ']'
            #print(xPath)
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getStudy: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getStudy: ' + str(e))

    
    def setStudyExpandedState(self, subjectID, studyID, expandedState='True'):
        try:
            studyElement = self.getStudy(subjectID, studyID)
            studyElement.set('expanded', expandedState)
        except Exception as e:
            print('Error in WeaselXMLReader.setStudyExpandedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setStudyExpandedState: ' + str(e))


    def setStudyCheckedState(self, subjectID, studyID, checkedState='True'):
        try:
            studyElement = self.getStudy(subjectID, studyID)
            studyElement.set('checked', checkedState)
        except Exception as e:
            print('Error in WeaselXMLReader.setStudyCheckedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setStudyCheckedState: ' + str(e))


    def getSeries(self, subjectID, studyID, seriesID):
        try: 
            xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) + ']' \
                    '/study[@id=' + chr(34) + studyID + chr(34) + ']' + \
                    '/series[@id=' + chr(34) + seriesID + chr(34) + ']'
            #print ("get series Xpath = {}".format(xPath))
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getSeries: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getSeries_: ' + str(e))

    
    def setSeriesExpandedState(self, subjectID, studyID, seriesID, expandedState='True'):
        try:
            seriesElement = self.getSeries(subjectID, studyID, seriesID)
            seriesElement.set('expanded', expandedState)
        except Exception as e:
            print('Error in WeaselXMLReader.setSeriesExpandedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setSeriesExpandedState: ' + str(e))


    def setSeriesCheckedState(self, subjectID, studyID, seriesID, checkedState='True'):
        try:
            seriesElement = self.getSeries(subjectID, studyID, seriesID)
            seriesElement.set('checked', checkedState)
            #print("series {} checked {}".format(seriesElement, checkedState))
        except Exception as e:
            print('Error in WeaselXMLReader.setSeriesCheckedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setSeriesCheckedState: ' + str(e))


    def getImage(self, subjectID, studyID, seriesID, imageName):
        try:
            xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) +  \
                    ']/study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34)  + \
                    ']/image[name=' + chr(34) + imageName + chr(34) +']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getImage: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImage: ' + str(e))


    def setImageCheckedState(self, subjectID, studyID, seriesID, imageName, checkedState="True"):
        try:
            imageElement = self.getImage(subjectID, studyID, seriesID, imageName)
            #print("Image {} checked {}".format(imageElement, checkedState))
            if imageElement:
                imageElement.set('checked', checkedState)
                #print("Image {} checked {}".format(imageElement, checkedState))
        except Exception as e:
            print('Error in WeaselXMLReader.setImageCheckedState: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.setImageCheckedState: ' + str(e))


    def getImagePathList(self, subjectID, studyID, seriesID):
        try:
            xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) +  \
                    ']/study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
            # print(xPath)
            images = self.root.findall(xPath)
            #print("images={}".format(images))
            imageList = [image.find('name').text for image in images]
            #print("length imageList={}".format(len(imageList)))
            return imageList
        except Exception as e:
            print('Error in weaselXMLReader.getImagePathList: ' + str(e))
            logger.error('Error in weaselXMLReader.getImagePathList: ' + str(e))
    

    def getNumberItemsInTreeView(self):
        """Counts the number of elements in the DICOM XML file to
        determine the number of items forming the tree view"""
        try:
            logger.info("weaselXMLReader.getNumberItemsInTreeView called")
            numSubjects = len(self.root.findall('.//subject'))
            numStudies = len(self.root.findall('.//subject/study'))
            numSeries = len(self.root.findall('.//subject/study/series'))
            numImages = len(self.root.findall('.//subject/study/series/image'))
            numItems = numSubjects + numStudies + numSeries + numImages
            return numSubjects, numStudies, numSeries, numImages, numItems
        except Exception as e:
            print('Error in function weaselXMLReader.getNumberItemsInTreeView: ' + str(e))
            logger.error('Error in weaselXMLReader.getNumberItemsInTreeView: ' + str(e))

    #redundant?
    def getNumberImagesInSeries(self, studyID, seriesID):
        try:
            xPath = './/subject/study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                    '/image'
            return len(self.root.find(xPath))
        except Exception as e:
            print('Error in WeaselXMLReader.getNumberImagesInSeries: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getNumberImagesInSeries: ' + str(e))


    def removeOneImageFromSeries(self, subjectID, studyID, seriesID, imagePath):
        try:
            #Get the series (parent) containing this image (child)
            #then remove child from parent
            series = self.getSeries(subjectID, studyID, seriesID)
            if series:
                for image in series:
                    if image.find('name').text == imagePath:
                        series.remove(image)
                       # print("removed image {}".format(imagePath))
                        #self.tree.write(self.fullFilePath)
                        break
        except Exception as e:
            print('Error in WeaselXMLReader.removeOneImageFromSeries: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.removeOneImageFromSeries: ' + str(e))


    def removeSeriesFromXMLFile(self, subjectID, studyID, seriesID):
        """Removes a whole series from the DICOM XML file"""
        try:
            logger.info("weaseXMLReader.removeSeriesFromXMLFile called")
            study = self.getStudy(subjectID, studyID)
            series = self.getSeries(subjectID, studyID, seriesID)
            if study and series:
                study.remove(series)
                ##print("removed series {}".format(seriesID))
                #self.tree.write(self.fullFilePath)
            else:
                print("Unable to remove series {}".format(seriesID))
        except AttributeError as e:
            print('Attribute Error in weaseXMLReader.removeSeriesFromXMLFile : ' + str(e))
            logger.error('Attribute Error in weaseXMLReader.removeSeriesFromXMLFile: ' + str(e))
        except Exception as e:
            print('Error in weaseXMLReader.removeSeriesFromXMLFile : ' + str(e))
            logger.error('Error in weaseXMLReader.removeSeriesFromXMLFile: ' + str(e))


    def getImageLabel(self, subjectID, studyID, seriesID, imageName = None):
        try:
            if imageName is None:
                return "000000"
            else:
                xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) +  \
                        ']/study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34)  + \
                        ']/image[name=' + chr(34) + imageName + chr(34) +']/label'
                return self.root.find(xPath).text
        except Exception as e:
            print('Error in WeaselXMLReader.getImageLabel: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageLabel: ' + str(e))


    def getImageTime(self, subjectID, studyID, seriesID, imageName = None):
        try:
            if imageName is None:
                now = datetime.now()
                return now.strftime("%H:%M:%S")
            else:
                xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) +  \
                        ']/study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34)  + \
                        ']/image[name=' + chr(34) + imageName + chr(34) +']/time'
                return self.root.find(xPath).text
        except Exception as e:
            print('Error in WeaselXMLReader.getImageTime: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageTime: ' + str(e))

    
    def getImageDate(self, subjectID, studyID, seriesID, imageName = None):
        try:
            if imageName is None:
                now = datetime.now()
                return now.strftime("%d/%m/%Y") 
            else:
                xPath = './/subject[@id=' + chr(34) + subjectID + chr(34) +  \
                        ']/study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34)  + \
                        ']/image[name=' + chr(34) + imageName + chr(34) +']/date'
            
                return self.root.find(xPath).text
                 
        except Exception as e:
            print('Error in WeaselXMLReader.getImageDate: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageDate: ' + str(e))


    def insertNewSeriesInXML(self, origImageList, newImageList, subjectID,
                     studyID, newSeriesID, seriesID, suffix):
        try:
            dataset = readDICOM_Image.getDicomDataset(newImageList[0])
            currentStudy = self.getStudy(subjectID, studyID)
            newAttributes = {'id':newSeriesID, 
                             'typeID':suffix,
                             'expanded':'False',
                             'uid':str(dataset.SeriesInstanceUID),
                              'checked': 'False'}

                   
            #Add new series to study to hold new images
            newSeries = ET.SubElement(currentStudy, 'series', newAttributes)           
            #comment = ET.Comment('This series holds a whole series of new images')
            #newSeries.append(comment)
            #Get image date & time from original image
            for index, imageNewName in enumerate(newImageList): #origImageList
                #imageLabel = self.getImageLabel(studyID, seriesID, imageName)
                imageTime = self.getImageTime(subjectID, studyID, seriesID)# , imageName)
                imageDate = self.getImageDate(subjectID, studyID, seriesID)#, imageName)
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                labelNewImage = ET.SubElement(newImage, 'label')
                labelNewImage.text = str(index + 1).zfill(6)
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = imageNewName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate

            #self.tree.write(self.fullFilePath)
        except Exception as e:
            print('Error in WeaselXMLReader.insertNewSeriesInXML: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.insertNewSeriesInXML: ' + str(e))

  
    def insertNewImageInXML(self, imageName,
                   newImageFileName, subjectID, studyID, seriesID, suffix, newSeriesName=None):
        try:
            dataset = readDICOM_Image.getDicomDataset(newImageFileName)
            if newSeriesName:
                newSeriesID = str(dataset.SeriesNumber) + "_" + newSeriesName
            else:
                if hasattr(dataset, "SeriesDescription"):
                    newSeriesID = str(dataset.SeriesNumber) + "_" + dataset.SeriesDescription
                elif hasattr(dataset, "SequenceName"):
                    newSeriesID = str(dataset.SeriesNumber) + "_" + dataset.SequenceName
                elif hasattr(dataset, "ProtocolName"):
                    newSeriesID = str(dataset.SeriesNumber) + "_" + dataset.ProtocolName
                else:
                    newSeriesID = str(dataset.SeriesNumber) + "_" + "No Sequence Name"
            # Check if the newSeries exists or not
            series = self.getSeries(subjectID, studyID, newSeriesID)
            #Get image label, date & time of Original image in case it's needed.
            imageLabel = self.getImageLabel(subjectID, studyID, seriesID, imageName)
            imageTime = self.getImageTime(subjectID, studyID, seriesID)#, imageName)
            imageDate = self.getImageDate(subjectID, studyID, seriesID)#, imageName)
            if series is None:
                #Need to create a new series to hold this new image
                #Get study branch
                currentStudy = self.getStudy(subjectID, studyID)
                newAttributes = {'id':newSeriesID, 
                                 'typeID':suffix,
                                 'uid':str(dataset.SeriesInstanceUID),
                                 'checked':'False'}

                #Add new series to study to hold new images
                newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
                #comment = ET.Comment('This series holds new images')
                #newSeries.append(comment)
                    
                #print("image time {}, date {}".format(imageTime, imageDate))
                #Now add image element
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                labelNewImage = ET.SubElement(newImage, 'label')
                labelNewImage.text = imageLabel
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                #self.tree.write(self.fullFilePath)
                return newSeriesID
            else:
                #A series already exists to hold new images from
                #the current parent series
                newImage = ET.SubElement(series,'image')
                #Add child nodes of the image element
                labelNewImage = ET.SubElement(newImage, 'label')
                labelNewImage.text = imageLabel + suffix
                #labelNewImage.text = str(len(series)).zfill(6)
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                #self.tree.write(self.fullFilePath)
                return series.attrib['id']
        except Exception as e:
            print('Error in WeaselXMLReader.insertNewImageInXML: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.insertNewImageInXML: ' + str(e))


    def renameSeriesinXMLFile(self, subjectID, studyID, seriesID, xmlSeriesName):
        try:
            series = self.getSeries(subjectID, studyID, seriesID)
            series.attrib['id'] = xmlSeriesName
            #self.tree.write(self.fullFilePath)
        except Exception as e:
            print('Error in WeaselXMLReader.renameSeriesinXMLFile: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.renameSeriesinXMLFile: ' + str(e))


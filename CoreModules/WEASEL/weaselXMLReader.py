import xml.etree.cElementTree as ET  
from pathlib import Path
from datetime import datetime
import logging
import readDICOM_Image as readDICOM_Image

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
        return self.root.findall('./subject/study')

    def getSubjects(self):
        return self.root.findall('./subject')


    def getImageList(self, studyID, seriesID):
        try:
            xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'        
            return self.root.findall(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getImageList: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageList: ' + str(e))


    def getSeries(self, studyID, seriesID):
        try:
            xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getSeries: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getSeries_: ' + str(e))


    def saveXMLFile(self, filePath):
        try:
            self.tree.write(filePath)
        except Exception as e:
            print('Error in WeaselXMLReader.saveXMLFile: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.saveXMLFile: ' + str(e))


    def getStudy(self, studyID):
        try:
            xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + ']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getStudy: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getStudy: ' + str(e))


    def getSeriesOfSpecifiedType(self, studyID, seriesID, newSeriesID, suffix):
        try:
            xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
             ']/series[@id=' + chr(34) + newSeriesID + chr(34) + ']' \
             '[@parentID=' + chr(34) + seriesID + chr(34) + ']' \
             '[@typeID=' + chr(34) + suffix + chr(34) +']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselXMLReader.getSeriesOfSpecifiedType_: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getSeriesOfSpecifiedType_: ' + str(e))


    def getImagePathList(self, studyID, seriesID):
        try:
            xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
            ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
            #print(xPath)
            images = self.root.findall(xPath)
            imageList = [image.find('name').text for image in images]
            return imageList
        except Exception as e:
            print('Error in weaselXMLReader.getImagePathList: ' + str(e))
            logger.error('Error in weaselXMLReader.getImagePathList: ' + str(e))
    

    def getNumberItemsInTreeView(self):
        """Counts the number of elements in the DICOM XML file to
        determine the number of items forming the tree view"""
        try:
            logger.info("weaselXMLReader.getNumberItemsInTreeView called")
            numSubjects = len(self.root.findall('./subject'))
            numStudies = len(self.root.findall('./subject/study'))
            numSeries = len(self.root.findall('./subject/study/series'))
            numImages = len(self.root.findall('./subject/study/series/image'))
            numItems = numSubjects + numStudies + numSeries + numImages
            return numSubjects, numStudies, numSeries, numImages, numItems
        except Exception as e:
            print('Error in function weaselXMLReader.getNumberItemsInTreeView: ' + str(e))
            logger.error('Error in weaselXMLReader.getNumberItemsInTreeView: ' + str(e))


    def getNumberImagesInSeries(self, studyID, seriesID):
        try:
            xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                        '/image'
            return len(self.root.find(xPath))
        except Exception as e:
            print('Error in WeaselXMLReader.getNumberImagesInSeries: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getNumberImagesInSeries: ' + str(e))


    def removeOneImageFromSeries(self, studyID, seriesID, imagePath):
        try:
            #Get the series (parent) containing this image (child)
            #then remove child from parent
            series = self.getSeries(studyID, seriesID)
            for image in series:
                if image.find('name').text == imagePath:
                    series.remove(image)
                    self.tree.write(self.fullFilePath)
                    break
        except Exception as e:
            print('Error in WeaselXMLReader.removeOneImageFromSeries: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.removeOneImageFromSeries: ' + str(e))


    def removeSeriesFromXMLFile(self, studyID, seriesID):
        """Removes a whole series from the DICOM XML file"""
        try:
            logger.info("weaseXMLReader.removeSeriesFromXMLFile called")
            study = self.getStudy(studyID)
            #print('XML = {}'.format(ET.tostring(study)))
            for series in study:
                if series.attrib['id'] == seriesID:
                    study.remove(series)
                    self.tree.write(self.fullFilePath)
                    break
        except Exception as e:
            print('Error in weaseXMLReader.removeSeriesFromXMLFile: ' + str(e))
            logger.error('Error in weaseXMLReader.removeSeriesFromXMLFile: ' + str(e))


    def getImageLabel(self, studyID, seriesID, imageName = None):
        try:
            if imageName is None:
                return "000000"
            else:
                xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                        '/image[name=' + chr(34) + imageName + chr(34) +']/label'
                return self.root.find(xPath).text
        except Exception as e:
            print('Error in WeaselXMLReader.getImageLabel: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageLabel: ' + str(e))


    def getImageTime(self, studyID, seriesID, imageName = None):
        try:
            if imageName is None:
                now = datetime.now()
                return now.strftime("%H:%M:%S")
            else:
                xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                        '/image[name=' + chr(34) + imageName + chr(34) +']/time'
                return self.root.find(xPath).text
        except Exception as e:
            print('Error in WeaselXMLReader.getImageTime: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageTime: ' + str(e))

    
    def getImageDate(self, studyID, seriesID, imageName = None):
        try:
            if imageName is None:
                now = datetime.now()
                return now.strftime("%d/%m/%Y") 
            else:
                xPath = './subject/study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                    '/image[name=' + chr(34) + imageName + chr(34) +']/date'
            
                return self.root.find(xPath).text
                 
        except Exception as e:
            print('Error in WeaselXMLReader.getImageDate: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.getImageDate: ' + str(e))


    def insertNewSeriesInXML(self, origImageList, newImageList,
                     studyID, newSeriesID, seriesID, suffix):
        try:
            currentStudy = self.getStudy(studyID)
            newAttributes = {'id':newSeriesID, 
                                'parentID':seriesID,
                                'typeID':suffix}
                   
            #Add new series to study to hold new images
            newSeries = ET.SubElement(currentStudy, 'series', newAttributes)           
            comment = ET.Comment('This series holds a whole series of new images')
            newSeries.append(comment)
            #Get image date & time from original image
            for index, imageNewName in enumerate(newImageList): #origImageList
                #imageLabel = self.getImageLabel(studyID, seriesID, imageName)
                imageTime = self.getImageTime(studyID, seriesID)# , imageName)
                imageDate = self.getImageDate(studyID, seriesID)#, imageName)
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

            self.tree.write(self.fullFilePath)
        except Exception as e:
            print('Error in WeaselXMLReader.insertNewSeriesInXML: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.insertNewSeriesInXML: ' + str(e))


    def insertNewImageInXML(self, imageName,
                   newImageFileName, studyID, seriesID, suffix, newSeriesName=None):
        #First determine if a series with parentID=seriesID exists
        #and typeID=suffix
        try:
            dataset = readDICOM_Image.getDicomDataset(newImageFileName)
            if newSeriesName:
                newSeriesID = str(dataset.SeriesNumber) + "_" + newSeriesName
            else:
                newSeriesID = str(dataset.SeriesNumber) + "_" + dataset.SeriesDescription
            series = self.getSeriesOfSpecifiedType(
                studyID, seriesID, newSeriesID, suffix)
            #Get image label, date & time
            imageLabel = self.getImageLabel(studyID, seriesID, imageName)
            imageTime = self.getImageTime(studyID, seriesID)#, imageName)
            imageDate = self.getImageDate(studyID, seriesID)#, imageName)
            if series is None:
                #Need to create a new series to hold this new image
                #Get study branch
                currentStudy = self.getStudy(studyID)
                newAttributes = {'id':newSeriesID, 
                                    'parentID':seriesID, 
                                    'typeID':suffix}
                   
                #Add new series to study to hold new images
                newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
                comment = ET.Comment('This series holds new images')
                newSeries.append(comment)
                    
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
                self.tree.write(self.fullFilePath)
                return newSeriesID
            else:
                #A series already exists to hold new images from
                #the current parent series
                newImage = ET.SubElement(series,'image')
                #Add child nodes of the image element
                labelNewImage = ET.SubElement(newImage, 'label')
                labelNewImage.text = imageLabel
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.tree.write(self.fullFilePath)
                return series.attrib['id']
        except Exception as e:
            print('Error in WeaselXMLReader.insertNewImageInXML: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.insertNewImageInXML: ' + str(e))


    def renameSeriesinXMLFile(self, studyID, seriesID, xmlSeriesName):
        try:
            series = self.getSeries(studyID, seriesID)
            series.attrib['id'] = xmlSeriesName
            self.tree.write(self.fullFilePath)
        except Exception as e:
            print('Error in WeaselXMLReader.renameSeriesinXMLFile: ' + str(e)) 
            logger.error('Error in WeaselXMLReader.renameSeriesinXMLFile: ' + str(e))


import xml.etree.ElementTree as ET  
from pathlib import Path
from datetime import datetime
import logging
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image

logger = logging.getLogger(__name__)

class WeaselToolsXMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = "Developer//WEASEL//Tools//toolsMenu.xml"
            self.tree = ET.parse(self.fullFilePath)
            self.root = self.tree.getroot()
            

            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in WeaselToolsXMLReader.__init__: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.__init__: ' + str(e)) 
            
    #def parseXMLFile(self): 
    #    """Loads and parses the XML configuration file at fullFilePath.
    #   After successful parsing, the XML tree and its root node
    #  is stored in memory."""
    #    try:
    #        self.hasXMLFileParsedOK = True
    #        self.tree = ET.parse(self.fullFilePath)
    #        self.root = self.tree.getroot()
    #        return self.root
    #        # Uncomment to test XML file loaded OK
    #        #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
           
    #        logger.info('In module ' + __name__ 
    #                + 'WeaselToolsXMLReader.parseConfigFile ' + fullFilePath)

    #    except ET.ParseError as et:
    #        print('WeaselToolsXMLReader.parseConfigFile error: ' + str(et)) 
    #        logger.error('WeaselToolsXMLReader.parseConfigFile error: ' + str(et))
    #        self.hasXMLFileParsedOK = False
            
    #    except Exception as e:
    #        print('Error in WeaselToolsXMLReader.parseConfigFile: ' + str(e)) 
    #        logger.error('Error in WeaselToolsXMLReader.parseConfigFile: ' + str(e)) 
    #        self.hasXMLFileParsedOK = False
    
    def getXMLRoot(self):
        return self.root


    def getTools(self):
        return self.root.findall('./tool')

    def getImageList(self, studyID, seriesID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'        
            return self.root.findall(xPath)
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getImageList: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getImageList: ' + str(e))


    def getSeries(self, studyID, seriesID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getSeries: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getSeries_: ' + str(e))


    def saveXMLFile(self, filePath):
        try:
            self.tree.write(filePath)
        except Exception as e:
            print('Error in WeaselToolsXMLReader.saveXMLFile: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.saveXMLFile: ' + str(e))


    def getStudy(self, studyID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + ']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getStudy: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getStudy: ' + str(e))


    def getSeriesOfSpecifiedType(self, studyID, seriesID, suffix):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
             ']/series[@parentID=' + chr(34) + seriesID + chr(34) + ']' \
             '[@typeID=' + chr(34) + suffix + chr(34) +']'
            return self.root.find(xPath)
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getSeriesOfSpecifiedType_: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getSeriesOfSpecifiedType_: ' + str(e))


    def getImagePathList(self, studyID, seriesID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
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
            numStudies = len(self.root.findall('./study'))
            numSeries = len(self.root.findall('./study/series'))
            numImages = len(self.root.findall('./study/series/image'))
            numItems = numStudies + numSeries + numImages
            return numStudies, numSeries, numImages, numItems
        except Exception as e:
            print('Error in function weaselXMLReader.getNumberItemsInTreeView: ' + str(e))
            logger.error('Error in weaselXMLReader.getNumberItemsInTreeView: ' + str(e))


    def getNumberImagesInSeries(self, studyID, seriesID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                        '/image'
            return len(self.root.find(xPath))
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getNumberImagesInSeries: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getNumberImagesInSeries: ' + str(e))


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
            print('Error in WeaselToolsXMLReader.removeOneImageFromSeries: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.removeOneImageFromSeries: ' + str(e))


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


    def getImageTime(self, studyID, seriesID, imageName):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                        '/image[name=' + chr(34) + imageName + chr(34) +']/time'
            return self.root.find(xPath).text
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getImageTime: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getImageTime: ' + str(e))

    
    def getImageDate(self, studyID, seriesID, imageName):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                    '/image[name=' + chr(34) + imageName + chr(34) +']/date'
            return self.root.find(xPath).text
        except Exception as e:
            print('Error in WeaselToolsXMLReader.getImageDate: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.getImageDate: ' + str(e))


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
            for index, imageName in enumerate(origImageList): 
                imageTime = self.getImageTime(studyID, seriesID, imageName)
                imageDate = self.getImageDate(studyID, seriesID, imageName)
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageList[index]
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate

            self.tree.write(self.fullFilePath)
        except Exception as e:
            print('Error in WeaselToolsXMLReader.insertNewSeriesInXML: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.insertNewSeriesInXML: ' + str(e))


    def insertNewImageInXML(self, imageName,
                   newImageFileName, studyID, seriesID, suffix):
        #First determine if a series with parentID=seriesID exists
        #and typeID=suffix
        try:
            series = self.getSeriesOfSpecifiedType(
                studyID, seriesID, suffix)    
            #Get image date & time
            imageTime = self.getImageTime(studyID, seriesID, imageName)
            imageDate = self.getImageDate(studyID, seriesID, imageName)

            if series is None:
                #Need to create a new series to hold this new image
                dataset = readDICOM_Image.getDicomDataset(newImageFileName)
                newSeriesID = dataset.SeriesDescription + "_" + str(dataset.SeriesNumber)
                #Get study branch
                currentStudy = self.getStudy(studyID)
                newAttributes = {'id':newSeriesID, 
                                    'parentID':seriesID, 
                                    'typeID':suffix}
                   
                #Add new series to study to hold new images
                newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
                comment = ET.Comment('This series holds new images')
                newSeries.append(comment)
                #Get image date & time
                imageTime = self.getImageTime(studyID, seriesID, imageName)
                imageDate = self.getImageDate(studyID, seriesID, imageName)
                    
                #print("image time {}, date {}".format(imageTime, imageDate))
                #Now add image element
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
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
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.tree.write(self.fullFilePath)
                return series.attrib['id']
        except Exception as e:
            print('Error in WeaselToolsXMLReader.insertNewImageInXML: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.insertNewImageInXML: ' + str(e))


    def insertNewBinOpsImageInXML(self, newImageFileName,
                                  studyID, seriesID, suffix):
        #First determine if a series with parentID=seriesID exists
        #and typeID=suffix for a binary operation
        try:
            series = self.getSeriesOfSpecifiedType(
                studyID, seriesID, suffix)
            #image date & time are set to current date and time
            now = datetime.now()
            imageTime = now.strftime("%H:%M:%S")
            imageDate = now.strftime("%d/%m/%Y")        
            if series is None:
                #Need to create a new series to hold this new image
                dataset = readDICOM_Image.getDicomDataset(newImageFileName)
                newSeriesID = dataset.SeriesDescription + "_" + str(dataset.SeriesNumber)
                #Get study branch
                currentStudy = self.getStudy(studyID)
                newAttributes = {'id':newSeriesID, 
                                    'parentID':seriesID, 
                                    'typeID':suffix}
                   
                #Add new series to study to hold new images
                newSeries = ET.SubElement(currentStudy, 
                                            'series', newAttributes)
                    
                comment = ET.Comment(
                    'This series holds images derived from binary operations on 2 images')
                newSeries.append(comment)   
                
                #Now add image element
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
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
                newImage = ET.SubElement(series,'image')#error
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.tree.write(self.fullFilePath)
                return series.attrib['id']
        except Exception as e:
            print('Error in WeaselToolsXMLReader.insertNewBinOpsImageInXML: ' + str(e)) 
            logger.error('Error in WeaselToolsXMLReader.insertNewBinOpsImageInXML: ' + str(e))
import pydicom
import os
import numpy as np

def returnPixelArray(imagePath):
    """This method reads the DICOM file in imagePath and returns the Image/Pixel array"""
    try:
        if os.path.exists(imagePath):
            dataset = getDicomDataset(imagePath)
            pixelArray = getPixelArray(dataset)
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.returnPixelArray: ' + str(e))


def getDicomDataset(imagePath):
    """This method reads the DICOM file in imagePath and returns the DICOM Dataset object/class"""
    try:
        if os.path.exists(imagePath):
            dataset = pydicom.dcmread(imagePath)
            return dataset
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getDicomDataset: ' + str(e))


def getPixelArray(dataset):
    """This method reads the DICOM Dataset object/class and returns the Image/Pixel array"""
    try:
        if hasattr(dataset, 'PixelData'):
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                slope = float(getattr(dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleSlope', 1)) * np.ones(dataset.pixel_array.shape)
                intercept = float(getattr(dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleIntercept', 0)) * np.ones(dataset.pixel_array.shape)
                pixelArray = dataset.pixel_array.astype(np.float32) * slope + intercept
            else:
                slope = float(getattr(dataset, 'RescaleSlope', 1)) * np.ones(dataset.pixel_array.shape)
                intercept = float(getattr(dataset, 'RescaleIntercept', 0)) * np.ones(dataset.pixel_array.shape)
                pixelArray = dataset.pixel_array.astype(np.float32) * slope + intercept
            return np.rot90(pixelArray, 3) # KEEP AN EYE ON THIS
            #return dataset.pixel_array # KEEP AN EYE ON THIS
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getPixelArray: ' + str(e))


def returnAffineArray(dataset):
    """This method reads the DICOM Dataset object/class and returns the Affine/Orientation matrix"""
    try:
        if hasattr(dataset, 'PixelData'):
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                image_orientation = dataset.PerFrameFunctionalGroupsSequence[0].PlaneOrientationSequence[0].ImageOrientationPatient
                row_cosine = np.array(image_orientation[:3])
                column_cosine = np.array(image_orientation[3:])
                slice_cosine = np.cross(row_cosine, column_cosine)
                row_spacing, column_spacing = dataset.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing
                slice_spacing = dataset.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].SpacingBetweenSlices

                affine = np.identity(4, dtype=np.float32)
                affine[:3, 0] = row_cosine * column_spacing
                affine[:3, 1] = column_cosine * row_spacing
                affine[:3, 2] = slice_cosine * slice_spacing
                affine[:3, 3] = dataset.PerFrameFunctionalGroupsSequence[0].PlanePositionSequence[0].ImagePositionPatient

            else:
                image_orientation = dataset.ImageOrientationPatient
                row_cosine = np.array(image_orientation[:3])
                column_cosine = np.array(image_orientation[3:])
                slice_cosine = np.cross(row_cosine, column_cosine)
                row_spacing, column_spacing = dataset.PixelSpacing
                slice_spacing = dataset.SliceThickness

                affine = np.identity(4, dtype=np.float32)
                affine[:3, 0] = row_cosine * column_spacing
                affine[:3, 1] = column_cosine * row_spacing
                affine[:3, 2] = slice_cosine * slice_spacing
                affine[:3, 3] = dataset.ImagePositionPatient
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.returnAffineArray: ' + str(e))

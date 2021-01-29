import numpy as np
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image

class TRISTAN():
    """Package containing algorithms that return deliverables
    of the IMI-TRISTAN project.
    
    Attributes
    ----------
    See parameters of __init__ class

    """

    def __init__(self, pixelArray):
        """Initialise an IMI-TRISTAN class instance.
        


        Parameters
        ----------
        pixelArray : np.ndarray of N-dimensions,
         where axes=0 corresponds to number of timepoints
         axes=1 corresponds to number of slices
        """

        self.pixelArray = pixelArray


    def MIP(self):
        try:
            mip = []
            for index in range(np.shape(self.pixelArray)[0]):
                mip.append(np.max(self.pixelArray[index, ...], axis=0))
            return np.array(mip)
        except Exception as e:
            print('Error in function TRISTAN.MIP: ' + str(e))
import numpy as np
from CoreModules.imagingTools import resizePixelArray, formatArrayForAnalysis, unWrapPhase

class ukrinMaps():
    """Package containing algorithms that calculate parameter maps 
    of the MRI scans acquired during the UKRIN-MAPS project.
    
    Attributes
    ----------
    See parameters of __init__ class

    """

    def __init__(self, pixelArray):
        """Initialise a UKRIN-MAPS class instance.
        
        Parameters
        ----------
        pixelArray : np.ndarray of N-dimensions
        """

        self.pixelArray = pixelArray

    # Consider splitting these methods into SubClasses at some point - Inheritance
    # Could create a Diffusion Toolbox where BValues are an atribute. Or Fitting, where Inversion Time and Echo Time are attributes.
    # https://www.youtube.com/watch?v=RSl87lqOXDE

    def B0MapOriginal(self, echoList):
        try:
            if len(echoList) == 2: # Is the given array already a Difference Phase?
                phaseDiffOriginal = np.squeeze(self.pixelArray[1, ...]) - np.squeeze(self.pixelArray[0, ...])
                deltaTE = np.absolute(echoList[1] - echoList[0]) * 0.001 # Conversion from ms to s
            else:
                phaseDiffOriginal = self.pixelArray
                deltaTE = echoList[0] * 0.001 # Conversion from ms to s
            phaseDiff = phaseDiffOriginal / ((1 / (2 * np.pi)) * np.amax(phaseDiffOriginal) * np.ones(np.shape(phaseDiffOriginal)))
            #phaseDiff = unWrapPhase(phaseDiffNormalised * (2 * np.pi * np.ones(np.shape(phaseDiffNormalised))))
            derivedImage = unWrapPhase(phaseDiff) / ((2 * np.pi * deltaTE) * np.ones(np.shape(phaseDiff)))
            del phaseDiffOriginal, phaseDiff, deltaTE
            return derivedImage
        except Exception as e:
            print('Error in function ukrinAlgorithms.B0MapOriginal: ' + str(e))
        

    def T2StarNottingham(self, echoList):
        try:
            self.pixelArray[self.pixelArray == 0] = 1E-10
            # If raw data is 2D (3D inc echo times) then add a dimension so it can be processed in the same way as 3D data
            if len(self.pixelArray.shape) == 3:
                self.pixelArray = np.expand_dims(self.pixelArray, 2)

            t2star = np.zeros(self.pixelArray.shape[0:3])
            r2star = np.zeros(self.pixelArray.shape[0:3])
            m0 = np.zeros(self.pixelArray.shape[0:3])
            with np.errstate(invalid='ignore', over='ignore'):
                for s in range(self.pixelArray.shape[2]):
                    for x in range(np.shape(self.pixelArray)[0]):
                        for y in range(np.shape(self.pixelArray)[1]):
                            noise = 0.0
                            sd = 0.0
                            s_w = 0.0
                            s_wx = 0.0
                            s_wx2 = 0.0
                            s_wy = 0.0
                            s_wxy = 0.0
                            for d in range(self.pixelArray.shape[3]):
                                noise = noise + self.pixelArray[x, y, s, d]
                                sd = sd + self.pixelArray[x, y, s, d] * \
                                    self.pixelArray[x, y, s, d]
                            noise = noise / self.pixelArray.shape[3]
                            sd = sd / self.pixelArray.shape[3] - noise ** 2
                            sd = sd ** 2
                            sd = np.sqrt(sd)
                            for d in range(self.pixelArray.shape[3]):
                                te_tmp = echoList[d] * 0.001  # Conversion from ms to s
                                if self.pixelArray[x, y, s, d] > sd:
                                    sigma = np.log(
                                        self.pixelArray[x, y, s, d] / (self.pixelArray[x, y, s, d] - sd))
                                    sig = self.pixelArray[x, y, s, d]
                                    weight = 1 / (sigma ** 2)
                                else:
                                    sigma = np.log(self.pixelArray[x, y, s, d] / 0.0001)
                                    sig = np.log(self.pixelArray[x, y, s, d])
                                    weight = 1 / (sigma ** 2)
                                weight = 1 / (sigma ** 2)
                                s_w = s_w + weight
                                s_wx = s_wx + weight * te_tmp
                                s_wx2 = s_wx2 + weight * te_tmp ** 2
                                s_wy = s_wy + weight * sig
                                s_wxy = s_wxy + weight * te_tmp * sig
                            delta = (s_w * s_wx2) - (s_wx ** 2)
                            if (delta == 0.0) or (np.isinf(delta)) or (np.isnan(delta)):
                                t2star[x, y, s] = 0
                                r2star[x, y, s] = 0
                                m0[x, y, s] = 0
                            else:
                                a = (1 / delta) * (s_wx2 * s_wy - s_wx * s_wxy)
                                b = (1 / delta) * (s_w * s_wxy - s_wx * s_wy)
                                t2stars_temp = np.real(-1 / b)
                                r2stars_temp = np.real(-b)
                                m0_temp = np.real(np.exp(a))
                                if (t2stars_temp < 0) or (t2stars_temp > 500):
                                    t2star[x, y, s] = 0
                                    r2star[x, y, s] = 0
                                    m0[x, y, s] = 0
                                else:
                                    t2star[x, y, s] = t2stars_temp
                                    r2star[x, y, s] = r2stars_temp
                                    m0[x, y, s] = m0_temp
            del t2stars_temp, r2stars_temp, m0_temp, delta
            return t2star, r2star, m0
        except Exception as e:
            print('Error in function ukrinAlgorithms.T2StarNottingham: ' + str(e))


    def T2Star(self, echoList):
        try:
            self.pixelArray[self.pixelArray == 0] = 1E-10
            # If raw data is 2D (3D inc echo times) then add a dimension so it can be processed in the same way as 3D data
            if len(self.pixelArray.shape) == 3:
                self.pixelArray = np.expand_dims(self.pixelArray, 2)

            t2star = np.zeros(self.pixelArray.shape[0:3])
            r2star = np.zeros(self.pixelArray.shape[0:3])
            m0 = np.zeros(self.pixelArray.shape[0:3])
            with np.errstate(invalid='ignore', over='ignore'):
                for s in range(self.pixelArray.shape[2]):
                    for x in range(np.shape(self.pixelArray)[0]):
                        for y in range(np.shape(self.pixelArray)[1]):
                            noise = 0.0
                            sd = 0.0
                            s_w = 0.0
                            s_wx = 0.0
                            s_wx2 = 0.0
                            s_wy = 0.0
                            s_wxy = 0.0
                            for d in range(self.pixelArray.shape[3]):
                                noise = noise + self.pixelArray[x, y, s, d]
                                sd = sd + self.pixelArray[x, y, s, d] * \
                                    self.pixelArray[x, y, s, d]
                            noise = noise / self.pixelArray.shape[3]
                            sd = sd / self.pixelArray.shape[3] - noise ** 2
                            sd = sd ** 2
                            sd = np.sqrt(sd)
                            for d in range(self.pixelArray.shape[3]):
                                te_tmp = echoList[d] * 0.001  # Conversion from ms to s
                                if self.pixelArray[x, y, s, d] > sd:
                                    sigma = np.log(
                                        self.pixelArray[x, y, s, d] / (self.pixelArray[x, y, s, d] - sd))
                                    sig = self.pixelArray[x, y, s, d]
                                    weight = 1 / (sigma ** 2)
                                else:
                                    sigma = np.log(self.pixelArray[x, y, s, d] / 0.0001)
                                    sig = np.log(self.pixelArray[x, y, s, d])
                                    weight = 1 / (sigma ** 2)
                                weight = 1 / (sigma ** 2)
                                s_w = s_w + weight
                                s_wx = s_wx + weight * te_tmp
                                s_wx2 = s_wx2 + weight * te_tmp ** 2
                                s_wy = s_wy + weight * sig
                                s_wxy = s_wxy + weight * te_tmp * sig
                            delta = (s_w * s_wx2) - (s_wx ** 2)
                            if (delta == 0.0) or (np.isinf(delta)) or (np.isnan(delta)):
                                t2star[x, y, s] = 0
                                r2star[x, y, s] = 0
                                m0[x, y, s] = 0
                            else:
                                a = (1 / delta) * (s_wx2 * s_wy - s_wx * s_wxy)
                                b = (1 / delta) * (s_w * s_wxy - s_wx * s_wy)
                                t2stars_temp = np.real(-1 / b)
                                r2stars_temp = np.real(-b)
                                m0_temp = np.real(np.exp(a))
                                if (t2stars_temp < 0) or (t2stars_temp > 500):
                                    t2star[x, y, s] = 0
                                    r2star[x, y, s] = 0
                                    m0[x, y, s] = 0
                                else:
                                    t2star[x, y, s] = t2stars_temp
                                    r2star[x, y, s] = r2stars_temp
                                    m0[x, y, s] = m0_temp
            del t2stars_temp, r2stars_temp, m0_temp, delta
            return t2star, r2star, m0
        except Exception as e:
            print('Error in function ukrinAlgorithms.T2StarNottingham: ' + str(e))

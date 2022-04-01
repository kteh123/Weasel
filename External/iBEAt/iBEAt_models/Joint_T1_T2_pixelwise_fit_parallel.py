"""
@author: Joao Periquito
iBEAt study T1 & T2 joint model-fit 
Siemens 3T PRISMA - Leeds (T1 & T2 sequence)
2021
"""
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.abspath(os.path.join('..', 'GitHub')))
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tqdm import tqdm
import multiprocessing

from iBEAt_Model_Library.single_pixel_forward_models import iBEAT_T1_FM, iBEAT_T2_FM 

global x1
global x2

#T1 Fit Model
def mod1(TI, Eff, M_eq, T1, FA_Eff, T2): # not all parameters are used here
    """ mod1 is T1 Fit Model used for joint T1 & T2 fit
    
    TI: list of inversion times
    Eff: 180 Ref Pulse efficency
    M_eq: equilibrim magnetization state
    T1: T1 value
    FA_Eff: Flip Angle Efficency
    T2: T2 value (not used in mod1)
    
    """

    TR      = 4.6# TR in ms (hardcoded from Siemens protocol)
    FA_Cat  = [(-12/5)/360*(2*np.pi), (2*12/5)/360*(2*np.pi), (-3*12/5)/360*(2*np.pi), (4*12/5)/360*(2*np.pi), (-5*12/5)/360*(2*np.pi)] #Catalization module confirmed by Siemens (Peter Schmitt): Magn Reson Med 2003 Jan;49(1):151-7. doi: 10.1002/mrm.10337
    N_T1    = 66# Number of k-space lines (hardcoded from Siemens protocol)
    FA      = 12/360*(2*np.pi)# Flip angle in degrees (hardcoded from Siemens protocol) converted to radians

    #T1 Forward Model    
    M_result = iBEAT_T1_FM.signalSequenceT1_FLASH(M_eq, T1, TI, FA,FA_Eff, TR, N_T1, Eff, FA_Cat)
        
    return M_result

#T2 Fit Model
def mod2(Tprep, Eff, M_eq, T1, FA_Eff, T2): # not all parameters are used here
    """ mod1 is T1 Fit Model used for joint T1 & T2 fit
    
    Tprep: list of T2 preparation times
    Eff: 180 Ref Pulse efficency (not used in mod2)
    M_eq: equilibrim magnetization state
    T1: T1 value
    FA_Eff: Flip Angle Efficency
    T2: T2 value
    
    """

    Tspoil = 1# Spoil time in ms
    N_T2   = 72# Number of k-space lines (hardcoded from Siemens protocol)
    Trec   = 463*2# Recovery time in ms (hardcoded from Siemens protocol)
    TR     = 4.6# TR in ms (hardcoded from Siemens protocol)
    FA     = 12/360*(2*np.pi) # Flip angle in degrees (hardcoded from Siemens protocol) converted to radians

    #T2 Forward Model 
    M_result = iBEAT_T2_FM.signalSequenceT2prep(Tprep, M_eq, T2, T1 , Tspoil, FA,FA_Eff, TR, N_T2, Trec)
        
    return M_result

#Join T1 & T2 Fit model to perform a joint fit
def comboFunc(comboX, Eff, M_eq, T1, FA_Eff, T2):
    """ combine mod1 and mod2 for joint T1 & T2 fit
    
    comboX: a list that combines inversion times and echo times
    Eff: 180 Ref Pulse efficency
    M_eq: equilibrim magnetization state
    T1: T1 value
    FA_Eff: Flip Angle Efficency
    T2: T2 value
    
    """

    extract1 = comboX[:28]
    extract2 = comboX[28:] 

    result1 = mod1(extract1, Eff, M_eq, T1, FA_Eff, T2)
    result2 = mod2(extract2, Eff, M_eq, T1, FA_Eff, T2)

    return np.append(result1, result2)


def parallel_curve_fit(arguments):
    try:
        x1, x2, x, y, comboFunc, comboX, Kidney_pixel_T1, Kidney_pixel_T2, initialParameters, l_bound, u_bound, method, maxfev = arguments
        comboY = np.append(Kidney_pixel_T1, Kidney_pixel_T2)
        fittedParameters, _ = curve_fit(comboFunc, comboX, comboY, initialParameters, bounds=(l_bound, u_bound), method=method, maxfev=maxfev)
        #Fitted Parameters: [180 Efficency, Signal at equilibrium, T1 value,Flip Angle Efficency,T2 value]
        Eff, M_eq, T1, FA_Eff, T2 = fittedParameters
        #residuals calculation
        residuals_T1 = Kidney_pixel_T1-mod1(x1, Eff, M_eq, T1, FA_Eff, T2)
        residuals_T2 = Kidney_pixel_T2-mod2(x2, Eff, M_eq, T1, FA_Eff, T2)
        #r squared calculation 
        ss_res_T1 = np.sum(np.nan_to_num(residuals_T1**2))
        ss_res_T2 = np.sum(np.nan_to_num(residuals_T2**2))
        ss_tot_T1 = np.sum(np.nan_to_num((Kidney_pixel_T1-np.nanmean(Kidney_pixel_T1))**2))
        ss_tot_T2 = np.sum(np.nan_to_num((Kidney_pixel_T2-np.nanmean(Kidney_pixel_T2))**2))
        r_squared_T1 = np.nan_to_num(1 - (ss_res_T1 / ss_tot_T1))
        r_squared_T2 = np.nan_to_num(1 - (ss_res_T2 / ss_tot_T2))
    except:
        T1 = T2 = M_eq = FA_Eff = Eff = r_squared_T1 = r_squared_T2 = 0
    return x, y, T1, T2, M_eq, FA_Eff, Eff, r_squared_T1, r_squared_T2


def main(T1_images_to_be_fitted, T2_images_to_be_fitted, sequenceParam, GUI_object=None):
    """ main function that performs the joint T1 & T2 model-fit with shared parameters at single pixel level. 

    Args
    ----
    T1_images_to_be_fitted (numpy.ndarray) (x,y,z,TI): pixel value for time-series (i.e. at each TI time) with shape [x,:]
    T2_images_to_be_fitted (numpy.ndarray) (x,y,z,TE): pixel value for time-series (i.e. at each T2 prep time) with shape [x,:]
    
    sequenceParam (list): [TI,Tprep]


    Returns
    -------
    fitted_parameters: Map with signal model fitted parameters: 'S0', 'T1','T2','Flip Efficency','180 Efficency'.  
    """
    x1 = np.array(sequenceParam[0])
    x2 = np.array(sequenceParam[1])

    #Combine TI and TE for the joint T1 & T2 Fit
    comboX = np.append(x1, x2)

    # boundaries
    lb = [0  ,0     ,0   ,  0,  0  ]
    ub = [1  ,10000 ,5000,  1,  500]

    #prepare loop variables 
    T1map           = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    T2map           = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    M0map           = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    FA_Effmap       = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    Ref_Effmap      = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    T1_rsquare_map  = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))
    T2_rsquare_map  = np.zeros((np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1), np.size(T1_images_to_be_fitted,2)))

    for i in range(np.shape(T1_images_to_be_fitted)[2]):
        Kidney_pixel_T1 = np.squeeze(T1_images_to_be_fitted[...,i,:])
        Kidney_pixel_T2 = np.squeeze(T2_images_to_be_fitted[...,i,:])
        
        arguments = []
        pool = multiprocessing.Pool(processes=os.cpu_count()-1)
        for (x, y), _ in np.ndenumerate(Kidney_pixel_T1[..., 0]):
            t1_value = Kidney_pixel_T1[x, y, :]
            t2_value = Kidney_pixel_T2[x, y, :]
            #comboY = np.append(t1_value, t2_value)
            #combine T1 and T2 pixel signal intensity for joint T1 & T2 fit
            initialParameters = np.array([1, np.amax(t2_value), 1400, 1, 80])# initial parameters [180 Efficency, Signal at equilibrium, T1 value,Flip Angle Efficency,T2 value]
            arguments.append((x1, x2, x, y, comboFunc, comboX, t1_value, t2_value, initialParameters, lb, ub, 'trf', 5000))
        results = list(tqdm(pool.imap(parallel_curve_fit, arguments), total=len(arguments), desc='Processing pixels of slice ' + str(i)))

        #store the fitted parameters
        #T1map[..., i]          = np.reshape(np.nan_to_num(T1), (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))
        #T2map[..., i]          = np.reshape(np.nan_to_num(T2), (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))
        #M0map[..., i]          = np.reshape(np.nan_to_num(M_eq), (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))
        #FA_Effmap[..., i]  = np.reshape(np.nan_to_num(FA_Eff), (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))
        #Ref_Effmap[..., i]     = np.reshape(np.nan_to_num(Eff), (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))
        #T1_rsquare_map[..., i]  = np.reshape(r_squared_T1, (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))
        #T2_rsquare_map[..., i]  = np.reshape(r_squared_T2, (np.size(T1_images_to_be_fitted,0), np.size(T1_images_to_be_fitted,1)))

        for result in results:
            xi = result[0]
            yi = result[1]
            T1 = result[2]
            T2 = result[3]
            M_eq = result[4]
            FA_Eff = result[5]
            Eff = result[6]
            r_squared_T1 = result[7]
            r_squared_T2 = result[8]
            T1map[xi,yi,i]          = T1
            T2map[xi,yi,i]          = T2
            M0map[xi,yi,i]          = M_eq
            FA_Effmap[xi,yi,i]      = FA_Eff
            Ref_Effmap[xi,yi,i]     = Eff
            T1_rsquare_map[xi,yi,i] = r_squared_T1
            T2_rsquare_map[xi,yi,i] = r_squared_T2

    fittedMaps = T1map, T2map, M0map, FA_Effmap, Ref_Effmap,T1_rsquare_map, T2_rsquare_map

    return fittedMaps
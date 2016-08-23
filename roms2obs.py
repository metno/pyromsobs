'''
Given a roms OBS file (or OBSstruct object, 
return model value at observation location.

On input:

OBS - obsfile
romsfile - roms results

On output

MOD - a OBSstruct object similar to OBS, but with model values in MOD.values 

'''
from netCDF4 import Dataset
from .OBSstruct import OBSstruct
from scipy.interpolate import griddata
import numpy as np
from extract_modval import extract_modval
from multiprocessing import Pool
from datetime import datetime, timedelta

def multi_run_wrapper(args):
    return extract_modval(*args)

def roms2obs(S, romsfile):
    # A dictionary relating OBS.type with romsfile variable names
    varnames = {1:'zeta', 2:'ubar', 3:'vbar', 4:'u', 5:'v', 6:'temp', 7:'salt'}
    
    if not isinstance(S,OBSstruct):
       fid = Dataset(S)
       OBS = OBSstruct(fid)
    else:
       OBS = OBSstruct(S)
    fid = Dataset(romsfile)
    try:    
        time = fid.variables['ocean_time'][:]/86400.
    except:
        try:
            time = fid.variables['time'][:]/86400.
        except:
            try:
                time = fid.variables['clim_time']
                if "seconds" in time.units:
                    time = fid.variables['clim_time'][:]/86400.
                else:
                    # Assume days:
                    time = fid.variables['clim_time'][:]
            except:
                print 'Not able to find time variable, exiting'
                exit()
    fid.close()

    # First calculate fractional time Index. Do this for every survey time
    # If more than one day (24h) from obstime to model time, set Tgrid to None
    
    Tgrid = np.empty(len(OBS.survey_time))
    Terror = np.empty(len(OBS.survey_time))
    for n in range(0,len(OBS.survey_time)):
        dt = OBS.survey_time[n] - time
        if min(np.abs(dt)) >= 1:
            Tgrid[n] = None
        else:
            first= np.argmin(np.abs(dt))
            if OBS.survey_time[n] <= time[0]:
                Tgrid[n]=first
            elif OBS.survey_time[n] >= time[-1]:
                Tgrid[n]=first
            elif (np.floor(dt[first]) == np.ceil(dt[first])):
                Tgrid[n]=first
            else:
                if first == 0:
                    second = first + 1
                elif first == (len(time)-1):
                    second = first - 1
                elif np.abs(dt[first-1]) < np.abs(dt[first+1]):
                    second = first -1
                elif np.abs(dt[first-1]) > np.abs(dt[first+1]):
                    second = first + 1
                Tgrid[n] = min(first,second)+np.abs(OBS.survey_time[n]-np.abs(time)[min(first,second)])/np.abs(time[first]-time[second])
                Terror[n] = np.min(np.abs(dt))
                    
 
    MOD = OBSstruct(OBS); MOD.toarray()
    # First set all elements more than 1 day apart from model time to nan
    for n in np.where(np.isnan(Tgrid))[0]:
        MOD.value[np.where(OBS.time==OBS.survey_time[n])] = np.nan
    
    arguments=[]; indices=[]
    
    for n in np.where(np.isfinite(Tgrid))[0]: 
        O = OBS[np.where(OBS.time ==  OBS.survey_time[n])]
        index=np.where(OBS.time ==  OBS.survey_time[n])[0]
        for o in range(0,O.Ndatum):
            arguments.append([romsfile, Tgrid[n],O.Zgrid[o],O.Ygrid[o],O.Xgrid[o],O.type[o]])
            indices.append([index[o],Terror[n]])
    #pool=Pool(6)
    allresults = map(multi_run_wrapper,arguments)
    print 'Length of results from multi_run_wrapper: ', len(allresults),  len(indices)
    print 'Number of observations on OBS object: ', OBS.Ndatum
    T=OBS[np.where(np.isnan(MOD.value))]
    print 'Number of observations to far away in time to do calculations: ', T.Ndatum
    # Try to put results in MOD:
    for n in range (0,len(allresults)): 
        MOD.value[indices[n][0].astype(int)] = allresults[n]
        MOD.error[indices[n][0].astype(int)] = indices[n][1]
    return MOD
    

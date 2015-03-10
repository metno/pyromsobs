from .helpers import setDimensions, popEntries
from netCDF4 import Dataset
from .OBSstruct import OBSstruct
import numpy as np
def time_constraint(S,mintime=None,maxtime=None):
    '''
    This function removes all observations that fall out side the period
    of time defined by mintime, maxtime. If no maxtime is given on input, 
    the time period will not have an upper bound.  
 
    Input:
    
    OBS - OBSstruct object or observation netcdf file     
    mintime - Lower bound of time period, on same format as obs_time
    maxtime - Upper bound of time period, on same format as obs_time

    Output:
    OBS  - observation object
    '''
    if not isinstance(S,OBSstruct):
       fid = Dataset(S)
       OBS = OBSstruct(fid)
    else:
       OBS=OBSstruct(S)
       
    if mintime is None and maxtime is None:
       print 'No time limits provided, no observations removed'
       return OBS
    OBS.toarray()
    if mintime:
       popindex=np.argwhere(OBS.time<mintime).squeeze()
       OBS=popEntries(popindex,OBS)
       OBS.toarray()
    if maxtime:
       popindex=np.argwhere(OBS.time>maxtime).squeeze()
       OBS=popEntries(popindex,OBS)
       OBS.toarray()

    OBS=setDimensions(OBS)
    return OBS


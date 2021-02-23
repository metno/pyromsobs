import numpy as np
from netCDF4 import Dataset
from .utils import popEntries,setDimensions
from .OBSstruct import OBSstruct
def remove_duplicates(S):
    '''
    This function identifies duplicated observations
    and makes sure all observation on output are unique.

    Input:

    OBS - OBSstruct object or observation netcdf file

    OBS  - observation object
    '''
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)
    # New method

    OBSout = OBSstruct()
    OBSout.variance = OBS.variance
    OBSout.Nstate = OBS.Nstate
    OBSout.spherical = OBS.spherical
    OBSout.globalatts = OBS.globalatts

    unique_obs= set()
    ntypes = np.unique(OBS.type)
    for typ in ntypes:
        OBST = OBS[np.where(OBS.type == typ)]

        for n in range(0,OBST.Ndatum):
            unique_obs.add(( np.round(OBST.time[n],3), np.round(OBST.Xgrid[n],3),np.round(OBST.Ygrid[n],3), np.round(OBST.Zgrid[n],3), np.round(OBST.value[n],4)))
        if len(unique_obs) == OBST.Ndatum:
            OBSout.append(OBST)
            continue
        for instance in unique_obs:
            TS = OBST[np.where( (np.round(OBST.time,3) == np.round(instance[0],3)) & (np.round(OBST.Xgrid,3) == np.round(instance[1],3)) & (np.round(OBST.Ygrid,3) == np.round(instance[2],3)) & (np.round(OBST.Zgrid,3) == np.round(instance[3],3)) &(np.round(OBST.value,4) == np.round(instance[4],4)))]
            OBSout.append(TS[0])
    OBSout = setDimensions(OBSout)
    return OBSout

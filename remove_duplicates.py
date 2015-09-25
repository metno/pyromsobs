import numpy as np
from netCDF4 import Dataset
from .helpers import popEntries,setDimensions
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
    '''
    # Loop over observation type:    
    OBS.toarray()
    field_list=OBS.getfieldlist()
    ntypes=np.unique(OBS.type)
    popindex=[]
    for n in ntypes:

        typeind=np.argwhere(OBS.type==n).squeeze()
        # Find unique observation values:
        nvals=np.unique(OBS.value[typeind])
        if (len(nvals) == len(OBS.value[typeind])):
           continue
        # Loop over them and check if they have the same location in 
        # time and space
        # Round to 4 decimal places for value, 3 for time/space
        for val in nvals:
            valind=np.argwhere(np.round(OBS.value[typeind],4)==np.round(val,4))
            if len(valind) < 2:
               continue
            for i in range(1,len(valind)):
                tbool=np.round(OBS.time[typeind[valind[0]]],3) == np.round(OBS.time[typeind[valind[i]]],3)
                xbool=np.round(OBS.Xgrid[typeind[valind[0]]],3) ==np.round(OBS.Xgrid[typeind[valind[i]]],3)
                ybool=np.round(OBS.Ygrid[typeind[valind[0]]],3) ==np.round(OBS.Ygrid[typeind[valind[i]]],3)  
                zbool=np.round(OBS.Zgrid[typeind[valind[0]]],3) == np.round(OBS.Zgrid[typeind[valind[i]]],3)
                if all([tbool,xbool,ybool,zbool]):
                   popindex.append(typeind[valind[i]])

    OBS.toarray()
    OBS=popEntries(popindex,OBS)
  
    OBS=setDimensions(OBS)
    return OBS
    '''

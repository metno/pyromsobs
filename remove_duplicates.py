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

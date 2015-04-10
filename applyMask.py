import numpy as np
from netCDF4 import Dataset
from .helpers import popEntries, setDimensions
from .OBSstruct import OBSstruct
from scipy.interpolate import griddata

def applyMask(S,romsfile):
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)
        
    mask=Dataset(romsfile).variables['mask_rho'][:,:]
    popindex=[]
    for o in range(0,OBS.Ndatum):
        # set up grids for griddata interpolation
        if (np.floor(OBS.Xgrid[o]) == np.ceil(OBS.Xgrid[o])):
            xind = [OBS.Xgrid[o].astype(int)]
        else:
            xind = [np.floor(OBS.Xgrid[o]).astype(int), np.ceil(OBS.Xgrid[o]).astype(int)]
        
        if (np.floor(OBS.Ygrid[o]) == np.ceil(OBS.Ygrid[o])):
            yind = [OBS.Ygrid[o].astype(int)]
        else:
            yind = [np.floor(OBS.Ygrid[o]).astype(int), np.ceil(OBS.Ygrid[o]).astype(int)]
        
        var=mask[yind[0]:yind[1]+1,xind[0]:xind[1]+1]
            
        if len(yind) > 1:
            y = np.zeros_like(var)
        if len(yind) > 1:            
            x = np.zeros_like(var)
        for c in range(0,len(yind)):
            for d in range(0,len(xind)):
                y[c,d] = yind[c]
                x[c,d] = xind[d]
                    
        var = griddata((y.flatten(),x.flatten()),var.flatten(), (OBS.Ygrid[o],OBS.Xgrid[o]))
        if var < 0.5:
            popindex.append(o)
            
    OBS=popEntries(popindex,OBS)
    OBS=setDimensions(OBS)
    return OBS
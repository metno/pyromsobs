import numpy as np
from netCDF4 import Dataset
from .helpers import popEntries, setDimensions
from .OBSstruct import OBSstruct
from scipy.interpolate import griddata,interp1d

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

        if ( (len(yind) == 2) & (len(xind) == 2) ):
            var = mask[yind[0]:yind[0]+2, xind[0]:xind[0]+2]
            y = np.zeros_like(var)
            x = np.zeros_like(var)
            for c in range(0,len(yind)):
                for d in range(0,len(xind)):
                    y[c,d] = yind[c]
                    x[c,d] = xind[d]
            var = griddata((y.flatten(),x.flatten()),var.flatten(), (OBS.Ygrid[o],OBS.Xgrid[o]))

        elif  ( (len(yind) == 1) & (len(xind) == 1) ):
            var = mask[yind[0], xind[0]]
        elif  ( (len(yind) == 2) & (len(xind) == 1) ):
            var = mask[yind[0]:yind[0]+2 , xind[0]]
            w = 1 - np.abs(yind - OBS.Ygrid[o])
            var = np.dot(w, var)

        elif  ( (len(yind) == 1) & (len(xind) == 2) ):
            var = mask[yind[0], xind[0]:xind[0]+2]
            w = 1 - np.abs(xind - OBS.Xgrid[o])
            var = np.dot(w, var)

        '''
        print(var)
        #var=mask[yind[0]:yind[1]+1,xind[0]:xind[1]+1]
        print(OBS.Ygrid[o], OBS.Xgrid[o], len(yind), len(xind)))
        print(var.shape)
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
        print(var)
        '''
        if (var < 0.25):
            popindex.append(o)

    OBS=popEntries(popindex,OBS)
    OBS=setDimensions(OBS)
    return OBS

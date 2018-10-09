from .OBSstruct import OBSstruct
from .helpers import setDimensions
from netCDF4 import Dataset
import numpy as np

def inds(ps, qs):
    if (np.floor(ps) == np.ceil(ps)):
        ind = [ps.astype(int)]
    else:
        ind = [np.floor(ps).astype(int), np.ceil(ps).astype(int)]
    return ind

def masked(var):
    if np.ma.is_masked(var):
        nans = var.mask
    else:
        nans = np.isnan(var)
    notnans = np.logical_not(nans)
    return nans, notnans

def extraCoastMask(S, hisfile, ngrdpts=0):

    '''
    This function apply an extra check to filter out observations close to the coast.
    ngrdpts sets the number of grid points away from the observations where we
    can tolerate land
    '''
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)

    fid = Dataset(hisfile)
    mask = fid.variables['mask_rho'][:]
    J, I = mask.shape
    fid.close()


    for n in range(OBS.Ndatum):
        i = inds(OBS.Xgrid[n])
        j = inds(OBS.Ygrid[n])
        i.extend([min(i) - ngrdpts, max(i) + ngrdpts])
        j.extend([min(j) - ngrdpts, max(j) + ngrdpts])

        varval = mask[max(0,min(j)): min(J, max(j)+1),max(0,min(i)): min(I, max(i)+1) ]
        varval = np.ma.array(varval, mask = varval-1) # This will mask values of 0
        nans, notnans = masked(varval)
        if any(nans.ravel()):
            # if any masked grid in search area, set value to nan
            OBS.value[n] = np.nan

    # Return only finite OBS.values
    return OBS[np.isfinte(OBS.value))]

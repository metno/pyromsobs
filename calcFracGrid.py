from scipy.interpolate import griddata
import numpy as np
from netCDF4 import Dataset
from roppy import SGrid
from .obs_ijpos import obs_ijpos
from .helpers import setDimensions, popEntries
from .OBSstruct import OBSstruct

def calcFracGrid(S,hisfile,onlyVertical=False,method='cubic'):
    '''
    This function finds the fractional grid coordinates. 
    hisfile needs to contain information about grid vertical structure.
    For computational efficency, it should also contain projection information.
    (Not necessary for regular lat/lon grids)
    '''
    if not isinstance(S,OBSstruct):
       fid = Dataset(S)
       OBS = OBSstruct(fid)
    else:
       OBS=OBSstruct(S)
    OBS.toarray()
    # Make sure OBS has Zgrid of same size and type as depth
    OBS.Zgrid=np.ones_like(OBS.depth)
    
    grid=SGrid(Dataset(hisfile))
    Adepth=grid.z_r
    if  not onlyVertical:
        print 'calculating horizontal grid fractions'
        OBS.Xgrid,OBS.Ygrid=obs_ijpos(hisfile,OBS.lon,OBS.lat,'r')
    
    popindex=np.unique(np.concatenate((np.argwhere(OBS.Xgrid<0),np.argwhere(OBS.Ygrid<0))))
    OBS=popEntries(list(popindex),OBS)
    # If all observations were outside the model domain, return OBS now
    if not len(OBS.lon):
        return OBS
    del popindex
    OBS=setDimensions(OBS)

    OBS.toarray()
    popindex=np.unique(np.array([np.argwhere(np.isnan(OBS.Xgrid)),np.argwhere(np.isnan(OBS.Ygrid))]).flatten())
    OBS=popEntries(list(popindex),OBS)
    del popindex
    OBS=setDimensions(OBS)

    # Find weights to calculate depth at position
    # Must handle points that fall on 
    nipos=np.zeros([4,len(OBS.Xgrid)]); njpos=np.zeros([4,len(OBS.Ygrid)])
    nipos[0,:]=np.floor(OBS.Xgrid); njpos[0,:]=np.floor(OBS.Ygrid)
    nipos[1,:]=np.floor(OBS.Xgrid); njpos[1,:]=np.ceil(OBS.Ygrid)
    nipos[2,:]=np.ceil(OBS.Xgrid); njpos[2,:]=np.floor(OBS.Ygrid)
    nipos[3,:]=np.ceil(OBS.Xgrid); njpos[3,:]=np.ceil(OBS.Ygrid)
    nmask=np.zeros_like(nipos)
    for n in range(0,OBS.Ndatum):
       #print njpos[:,n], nipos[:,n], grid.z_r.shape, OBS.Ygrid[n], describe(OBS.Ygrid), describe(OBS.Xgrid)
       nmask[0,n]=grid.mask_rho[njpos[0,n],nipos[0,n]]
       nmask[1,n]=grid.mask_rho[njpos[1,n],nipos[1,n]]
       nmask[2,n]=grid.mask_rho[njpos[2,n],nipos[2,n]]
       nmask[3,n]=grid.mask_rho[njpos[3,n],nipos[3,n]]

    ndist=np.sqrt((OBS.Xgrid-nipos)**2 + (OBS.Ygrid-njpos)**2)
    # If the observation is exactly on a grid point, ndist will be zero,
    # and the weights will come out as nan. This is handled by setting all
    # nan's to 0.25. 
    with np.errstate(invalid='ignore',divide='ignore'):
        weights=(ndist**-2)/np.sum(ndist**-2,axis=0)
    weights[np.where(np.isnan(weights))]=0.25
    weights=weights*nmask
    Adepth=np.zeros([grid.z_r.shape[0]+1,grid.z_r.shape[1],grid.z_r.shape[2]])
    Adepth[0,:,:]=grid.h[:,:]*-1.
    Adepth[1::,:,:]=grid.z_r[:,:,:]
    ZatOBS=np.sum(Adepth[:,njpos.astype(int),nipos.astype(int)]*weights,axis=1)
    mzi=np.arange(0,Adepth.shape[0])

    for n in range(0,OBS.Ndatum):
        if  (OBS.depth[n]<=ZatOBS[0,n]) : 
           OBS.Zgrid[n]=mzi[0]          
        elif (OBS.depth[n]>=ZatOBS[-1,n]):
		   OBS.Zgrid[n]=mzi[-1]
        else:
           OBS.Zgrid[n]=griddata(ZatOBS[:,n],mzi,OBS.depth[n],method='linear')

	
    return OBS


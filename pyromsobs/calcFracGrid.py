from scipy.interpolate import interp1d
import numpy as np
from netCDF4 import Dataset
from roppy import SGrid
from .obs_ijpos import obs_ijpos
from .helpers import setDimensions, popEntries
from .applyMask import applyMask
from .OBSstruct import OBSstruct
from multiprocessing import Pool
from datetime import datetime,timedelta

def fracZ(depth,ZatOBS,mzi):
    if  (depth<=ZatOBS[0]) :
        z=mzi[0]
    elif (depth>=ZatOBS[-1]):
        z=mzi[-1]
    else:
        f=interp1d(ZatOBS,mzi)
        z=f(depth)
    return z

def multi_run_wrapper(args):
    return fracZ(*args)
def calcFracGrid(S,hisfile,onlyVertical=False,onlyHorizontal=False,multi=False):

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


    if  not onlyVertical:
        OBS.Xgrid = np.empty_like(OBS.lon)
        OBS.Ygrid = np.empty_like(OBS.lon)

        lons=np.unique(OBS.lon)
        sendlon=[]
        sendlat=[]
        putind=[]

        for lon in lons:
            index=np.where(OBS.lon == lon)[0]
            lat_at_ind = OBS.lat[index]
            lats = np.unique(lat_at_ind)

            for lat in lats:
                ind = np.where(lat_at_ind == lat)[0]
                sendlon.append(lon)
                sendlat.append(lat)
                putind.append(index[ind])


        x, y = obs_ijpos(hisfile, np.array(sendlon), np.array(sendlat),'r')

        #print('x,y, lat, lon: ', len(x),len(y), len(OBS.lon),len(OBS.lat))
        for n in range(0,len(sendlat)):
            OBS.Xgrid[putind[n]] = x[n]
            OBS.Ygrid[putind[n]] = y[n]
        x = None
        y=None
        OBS = OBS[np.where( (OBS.Xgrid >= 0) | (OBS.Ygrid >= 0)) ]


        # If all observations were outside the model domain, return OBS now
        if not len(OBS.lon):
            return OBS
        OBS = OBS[np.where((np.isfinite(OBS.Xgrid)) | ( np.isfinite(OBS.Ygrid)))]
        #OBS = setDimensions(OBS)
        if OBS.Ndatum != 0:
            OBS=applyMask(OBS,hisfile)

        if onlyHorizontal:
            OBS=setDimensions(OBS)
            return OBS

    # Make sure OBS has Zgrid of same size and type as depth
    OBS.Zgrid=np.ones_like(OBS.depth)
    fid = Dataset(hisfile)
    grid=SGrid(fid)
    #fid.close()
    #fid = None
    # Find weights to calculate depth at position
    # Must handle points that fall on
    nipos=np.zeros([4,len(OBS.Xgrid)]).astype(int); njpos=np.zeros([4,len(OBS.Ygrid)]).astype(int)
    nipos[0,:]=np.floor(OBS.Xgrid).astype(int); njpos[0,:]=np.floor(OBS.Ygrid).astype(int)
    nipos[1,:]=np.floor(OBS.Xgrid).astype(int); njpos[1,:]=np.ceil(OBS.Ygrid).astype(int)
    nipos[2,:]=np.ceil(OBS.Xgrid).astype(int); njpos[2,:]=np.floor(OBS.Ygrid).astype(int)
    nipos[3,:]=np.ceil(OBS.Xgrid).astype(int); njpos[3,:]=np.ceil(OBS.Ygrid).astype(int)
    nmask=np.zeros_like(nipos)
    for n in range(0,len(OBS.depth)):
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
    arguments=[]
    for n in range(0,len(OBS.depth)):
        arguments.append([OBS.depth[n],ZatOBS[:,n],mzi])
        '''
        if  (OBS.depth[n]<=ZatOBS[0,n]) :
           OBS.Zgrid[n]=mzi[0]
        elif (OBS.depth[n]>=ZatOBS[-1,n]):
		   OBS.Zgrid[n]=mzi[-1]
        else:
           OBS.Zgrid[n]=griddata(ZatOBS[:,n],mzi,OBS.depth[n],method='linear')
        '''
    if multi:
        pool=Pool()
        results = list(pool.map(multi_run_wrapper,arguments))
    else:
        results = list(map(multi_run_wrapper, arguments))
    for n in range(0,len(OBS.depth)):
        OBS.Zgrid[n] = results[n]
    OBS = OBS[np.where(np.isfinite(OBS.Zgrid))]
    results = None
    mzi = None
    arguments = None
    ZatOBS = None
    Adepth = None
    weights = None
    nmask = None
    nipos = None
    njpos = None
    ndist= None
    grid = None
    sendlon = None
    sendlat = None
    putind = None
    ind = None
    index =None
    lat_at_ind = None
    fid.close()
    OBS = setDimensions(OBS)
    return OBS

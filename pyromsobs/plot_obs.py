import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
from roppy import SGrid
from .OBSstruct import OBSstruct

def plot_obs(S,hisfile,vartype=6,depthmin=None, depthmax=None,timemin=None,timemax=None,Vmin=None,Vmax=None,fileout=None):
    # Let depthmin be closest to surface, depthmax deepest
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)

    obstypes={1:{'name':'zeta','cmap': plt.cm.ocean}, 2:{'name':'ubar', 'cmap':plt.cm.seismic},
              3:{'name':'vbar', 'cmap':plt.cm.seismic}, 4:{'name':'u', 'cmap':plt.cm.seismic},
              5:{'name':'v', 'cmap':plt.cm.seismic}, 6:{'name':'temperature', 'cmap':plt.cm.plasma},
              7:{'name':'salinity', 'cmap':plt.cm.viridis}, 20:{'name':'radial velocity', 'cmap':plt.cm.seismic}}
    grid=SGrid(Dataset(hisfile))

    OBS=OBS[np.where(OBS.type==vartype)]
    if not OBS.Ndatum:
        print('No observations of type ',vartype,' in dataset')
        return


    if timemin is not None:
        OBS=OBS[np.where(OBS.time>timemin)]
        if not OBS.Ndatum:
            print('No observations of type ',vartype,' in specified time range')
            return

    if timemax is not None:
        OBS=OBS[np.where(OBS.time<timemax)]
        if not OBS.Ndatum:
            print('No observations of type ',vartype,' in specified time range')
            return

    if depthmin is not None:
        depthmin=np.abs(depthmin)*-1.
        OBS=OBS[np.where((OBS.depth<depthmin))]
        if not OBS.Ndatum:
            print('No observations of type ',vartype,' in specified depth range')
            return
    if depthmax is not None:
        depthmax=np.abs(depthmax)*-1.
        OBS=OBS[np.where((OBS.depth>depthmax))]
        if not OBS.Ndatum:
            print('No observations of type ',vartype,' in specified depth range')
            return
    fig=plt.figure(figsize=(12,7))

    ax = fig.add_axes([0.1, 0.15, 0.8, 0.8])
    plt.pcolormesh(grid.Xb,grid.Yb,grid.mask_rho, cmap='Greys_r')
    im=plt.scatter(OBS.Xgrid,OBS.Ygrid,c=OBS.value,edgecolor='None',cmap=obstypes[vartype]['cmap'])

    plt.axis('image')

    if len(grid.Xb) > len(grid.Yb):
        cbar=plt.colorbar(im, orientation='horizontal')
    else:
        cbar=plt.colorbar(im, orientation='vertical')

    if (Vmin and Vmax):
        im.set_clim(vmin=Vmin,vmax=Vmax)

    #obstypes=['zeta', 'ubar', 'vbar', 'u' ,'v', 'temperature', 'salinity','','','','','','','','','','','','','radial velocity']
    plt.title(str(len(OBS.value))+' observations of '+obstypes[vartype]['name'])
    if fileout:
        plt.savefig(fileout, bbox_inches='tight',dpi=fig.dpi)
    else:
        plt.show()

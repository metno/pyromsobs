'''
Given a roms OBS file (or OBSstruct object, 
return model value at observation location.

On input:

OBS - obsfile
romsfile - roms results

On output

MOD - a OBSstruct object similar to OBS, but with model values in MOD.values 

'''

from netCDF4 import Dataset
from .OBSstruct import OBSstruct
from scipy.interpolate import griddata
import numpy as np
from gwibber.microblog.util import first

def roms2obs(S, romsfile):
    # A dictionary relating OBS.type with romsfile variable names
    varnames = {1:'zeta', 2:'ubar', 3:'vbar', 4:'u', 5:'v', 6:'temp', 7:'salt'}
    
    if not isinstance(S,OBSstruct):
       fid = Dataset(S)
       OBS = OBSstruct(fid)
    else:
       OBS = OBSstruct(S)
    OBS.toarray()
    
    time = Dataset(romsfile).variables['ocean_time'][:]/86400.

    # First calculate fractional time Index. Do this for every survey time
    # If more than one day (24h) from obstime to model time, set Tgrid to None
    
    Tgrid = np.empty(len(OBS.survey_time))
    for n in range(0,len(OBS.survey_time)):
        dt = OBS.survey_time[n] - time
        if min(np.abs(dt)) >= 1:
            Tgrid[n] = None
        else:
            first= np.argmin(np.abs(dt))
            if OBS.survey_time[n] <= time[0]:
                Tgrid[n]=first
            elif OBS.survey_time[n] >= time[-1]:
                Tgrid[n]=first
            else:
                if first == 0:
                    second = first + 1
                elif first == (len(time)-1):
                    second == first - 1
                elif np.abs(dt[first-1]) < np.abs(dt[first+1]):
                    second = first -1
                elif np.abs(dt[first-1]) > np.abs(dt[first+1]):
                    second = first + 1
                Tgrid[n]=min(first,second)+np.abs(OBS.survey_time[n]-np.abs(time)[min(first,second)])/np.abs(time[first]-time[second])
                    
                    
 
    MOD = OBSstruct(OBS); MOD.toarray()
    # First set all elements more than 1 day apart from model time to nan
    for n in np.where(np.isnan(Tgrid))[0]:
        MOD.value[np.where(OBS.time==OBS.survey_time[n])] = np.nan
    
    
    # Now process all observations for which a finite value of Tgrid was found
    for n in np.where(np.isfinite(Tgrid))[0]:
        S = OBS[np.where(OBS.time ==  OBS.survey_time[n])]
        if (np.floor(Tgrid[n]) == np.ceil(Tgrid[n])):
            tind = [Tgrid[n].astype(int)]
        else:
            tind = [np.floor(Tgrid[n]).astype(int), np.ceil(Tgrid[n]).astype(int)]
            
        for o in range(0,S.Ndatum):
            
            if (np.floor(S.Xgrid[o]) == np.ceil(S.Xgrid[o])):
                xind = [S.Xgrid[o].astype(int)]
            else:
                xind = [np.floor(S.Xgrid[o]).astype(int), np.ceil(S.Xgrid[o]).astype(int)]
                
            if (np.floor(S.Ygrid[o]) == np.ceil(S.Ygrid[o])):
                yind = [S.Ygrid[o].astype(int)]
            else:
                yind = [np.floor(S.Ygrid[o]).astype(int), np.ceil(S.Ygrid[o]).astype(int)]
                
                
            
            # retrive model result at given indices
            if S.type[o] in [1,2,3]:
                
                var=Dataset(romsfile).variables[varnames[S.type[o]]][tind,yind,xind]
                
                # set up grids for griddata interpolation
                t = np.zeros_like(var)
                y = np.zeros_like(var)
                x = np.zeros_like(var)

                for a in range(0,len(tind)):
                        for c in range(0,len(yind)):
                            for d in range(0,len(xind)):
                                t[a,c,d] = tind[a]
                                y[a,c,d] = yind[c]
                                x[a,c,d] = xind[d]
                                
                MOD.value[o] = griddata((t.flatten(),y.flatten(),x.flatten()),var.flatten(), (Tgrid[22],S.Ygrid[o],S.Xgrid[o]))
                  
            elif S.type[o] in [4,5,6]:
                 
                if (np.floor(S.Zgrid[o]) == np.ceil(S.Zgrid[o])):
                    zind = [S.Zgrid[o].astype(int)]
                else:
                    zind = [np.floor(S.Zgrid[o]).astype(int), np.ceil(S.Zgrid[o]).astype(int)]
                
                var=Dataset(romsfile).variables[varnames[S.type[o]]][tind,zind,yind,xind]
                
                t = np.zeros_like(var)
                z = np.zeros_like(var)
                y = np.zeros_like(var)
                x = np.zeros_like(var)

                for a in range(0,len(tind)):
                    for b in range(0,len(zind)):
                        for c in range(0,len(yind)):
                            for d in range(0,len(xind)):
                                t[a,b,c,d] = tind[a]
                                z[a,b,c,d] = zind[b]
                                y[a,b,c,d] = yind[c]
                                x[a,b,c,d] = xind[d]
                                
                MOD.value[o] = griddata((t.flatten(),z.flatten(),y.flatten(),x.flatten()),var.flatten(), (Tgrid[22],S.Zgrid[o],S.Ygrid[o],S.Xgrid[o]))
                                

  
    
            
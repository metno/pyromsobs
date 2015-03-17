from netCDF4 import Dataset
import numpy as np
from scipy.interpolate import griddata

def extract_modval(romsfile, Tgrid, Zgrid, Ygrid, Xgrid, otype):
    # remember that Zgrid is one-based, this is not the case for python. 
    # Subtract 1 from Zgrid to get correct layer
    Zgrid = Zgrid - 1.
    if Zgrid < 0:
        Zgrid = np.array(0)
    varnames = {1:'zeta', 2:'ubar', 3:'vbar', 4:'u', 5:'v', 6:'temp', 7:'salt'}
    if (np.floor(Tgrid) == np.ceil(Tgrid)):
        tind = [Tgrid.astype(int)]
    else:
        tind = [np.floor(Tgrid).astype(int), np.ceil(Tgrid).astype(int)]
        
        
    if (np.floor(Xgrid) == np.ceil(Xgrid)):
        xind = [Xgrid.astype(int)]
    else:
        xind = [np.floor(Xgrid).astype(int), np.ceil(Xgrid).astype(int)]
        
    if (np.floor(Ygrid) == np.ceil(Ygrid)):
        yind = [Ygrid.astype(int)]
    else:
        yind = [np.floor(Ygrid).astype(int), np.ceil(Ygrid).astype(int)]

    if otype in [1,2,3]:
    
        var=Dataset(romsfile).variables[varnames[otype]][tind,yind,xind]
    
        # set up grids for griddata interpolation
        if len(tind) > 1 :
            t = np.zeros_like(var)
        if len(yind) > 1:
            y = np.zeros_like(var)
        if len(yind) > 1:            
            x = np.zeros_like(var)

        if len(var.shape) == 3:
            for a in range(0,len(tind)):
                for c in range(0,len(yind)):
                    for d in range(0,len(xind)):
                        t[a,c,d] = tind[a]
                        y[a,c,d] = yind[c]
                        x[a,c,d] = xind[d]
                    
                        return griddata((t.flatten(),y.flatten(),x.flatten()),var.flatten(), (Tgrid,Ygrid,Xgrid))
        
        if len(var.shape) == 2:
            # Determine which dimensions to use, set pointers to appropriate variables
            if 't' in locals():
                first = t; ind1 = tind; grid1 = Tgrid 
                if 'y' in locals():
                    second = y; ind2 = yind; grid2 = Ygrid
                else:
                    second = x; ind2 = xind; grid2 = Xgrid
            
            elif 'y' in locals():
                first = y; ind1 = yind; grid1= Ygrid
                second = x; ind2 = xind; grid2 = Xgrid
                
            for a in range(0,len(ind1)):
                for b in range(0,len(ind2)):
                    first[a,b] = ind1[a]
                    second[a,b] = ind2[b]
            return griddata((first.flatten(),second.flatten()),var.flatten(), (grid1,grid2))
        
      
    elif otype in [4,5,6,7]:
     
        if (np.floor(Zgrid) == np.ceil(Zgrid)):
            zind = [Zgrid.astype(int)]
        else:
            zind = [np.floor(Zgrid).astype(int), np.ceil(Zgrid).astype(int)]
        
        var=Dataset(romsfile).variables[varnames[otype]][tind,zind,yind,xind].squeeze()

        if len(tind) > 1 :
            t = np.zeros_like(var)
        if len(zind) > 1:
            z = np.zeros_like(var)
        if len(yind) > 1:
            y = np.zeros_like(var)
        if len(yind) > 1:            
            x = np.zeros_like(var)
        #if ['t','z','y','x'] in locals():
        if len(var.shape) == 4:
            for a in range(0,len(tind)):
                for b in range(0,len(zind)):
                    for c in range(0,len(yind)):
                        for d in range(0,len(xind)):                            
                            t[a,b,c,d] = tind[a]
                            z[a,b,c,d] = zind[b]
                            y[a,b,c,d] = yind[c]
                            x[a,b,c,d] = xind[d]
                        
            return griddata((t.flatten(),z.flatten(),y.flatten(),x.flatten()),var.flatten(), (Tgrid,Zgrid,Ygrid,Xgrid))
        if len(var.shape) == 3:
            # Determine which dimensions to use, set pointers to appropriate variables
            if 't' in locals():
                first = t; ind1 = tind; grid1 = Tgrid 
                if 'z' in locals():
                    second = z; ind2 = zind; grid2 = Zgrid
                    if 'y' in locals():
                        third = y; ind3 = yind; grid3 = Ygrid
                    else:
                        third = x; ind3 = xind; grid3 = Xgrid
                elif 'y' in locals():
                    second = y; ind2 = yind; grid2= Ygrid
                    third = x; ind3 = xind; grid3 = Xgrid
                    
                    
            else: 
                first = z; ind1 = zind; grid1 = Zgrid
                second = y; ind2 = yind; grid2= Ygrid
                third = x; ind3 = xind; grid3 = Xgrid
                
            for a in range(0,len(ind1)):
                for b in range(0,len(ind2)):
                    for c in range(0,len(ind3)):
                        first[a,b,c] = ind1[a]
                        second[a,b,c] = ind2[b]
                        third[a,b,c] = ind3[c]
            return griddata((first.flatten(),second.flatten(),third.flatten()),var.flatten(), (grid1,grid2,grid3))
        
        if len(var.shape) == 2:
            # Determine which dimensions to use, set pointers to appropriate variables
            if 't' in locals():
                first = t; ind1 = tind; grid1 = Tgrid 
                if 'z' in locals():
                    second = z; ind2 = zind; grid2 = Zgrid
                elif 'y' in locals():
                    second = y; ind2 = yind; grid2 = Ygrid
                else:
                    second = x; ind2 = xind; grid2 = Xgrid
                    
            elif 'z' in locals():
                first = z; ind1 = zind; grid1= Zgrid
                if 'y' in locals():
                    second = y; ind2 = yind; grid2 = Ygrid
                else:
                    second = x; ind2 = xind; grid2 = Xgrid
            
            elif 'y' in locals():
                first = y; ind1 = yind; grid1= Ygrid
                second = x; ind2 = xind; grid2 = Xgrid
                
            for a in range(0,len(ind1)):
                for b in range(0,len(ind2)):
                    first[a,b] = ind1[a]
                    second[a,b] = ind2[b]
            return griddata((first.flatten(),second.flatten()),var.flatten(), (grid1,grid2))
        
        
        if len(var.shape) == 1 and var.shape[0] > 1 :
            # Determine which dimensions to use, set pointers to appropriate variables
            if 't' in locals():
                first = t; ind1 = tind; grid1 = Tgrid                  
            elif 'z' in locals():
                first = z; ind1 = zind; grid1= Zgrid
            elif 'y' in locals():
                first = y; ind1 = yind; grid1= Ygrid
            else:
                first = x; ind1 = xind; grid1 = Xgrid
                
            for a in range(0,len(ind1)):
                first[a] = ind1[a]
            return griddata((first.flatten()),var.flatten(), (grid1))
        elif len(var.shape) == 1 and var.shape[0] == 1 :
            return var
                    
    
    
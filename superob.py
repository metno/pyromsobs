import numpy as np
from .helpers import setDimensions,accum_np
from .OBSstruct import OBSstruct
from netCDF4 import Dataset
from roppy import SGrid

def superob(S,hisfile):
    '''
    This function checks the provided observation data and creates
    super observations when there are more than one meassurement of
    the same state variable per grid cell. 
    
    This is basically a python version of super_obs.m, distributed 
    through myroms.org
    '''
    if not isinstance(S,OBSstruct):
       fid = Dataset(S)
       OBS = OBSstruct(fid)
    else:
       OBS=OBSstruct(S)
    
    field_list=OBS.getfieldlist()
    
    binfields=OBS.getfieldlist(); binfields.remove('time'); binfields.remove('type')
    grid = SGrid(Dataset(hisfile))
    Lm=grid.i1
    Mm=grid.j1
    N=grid.N
    '''
    Lm=OBS.grid_Lm_Mm_N[0]
    Mm=OBS.grid_Lm_Mm_N[1]
    N=OBS.grid_Lm_Mm_N[2]
    '''
    # Find observations associated with the same state variable
    state_vars=np.unique(OBS.type)    
    Nstate=len(np.unique(OBS.type))
    
    Sout=OBSstruct()
    Sout.globalatts=OBS.globalatts
    Sout.Nsurvey=OBS.Nsurvey
    Sout.Nstate = len(OBS.variance)
    Sout.spherical=OBS.spherical
    Sout.survey_time=OBS.survey_time
    Sout.variance = OBS.variance
    Sout.Nobs = np.zeros_like(OBS.Nobs).tolist()
    Sout_std=[]
    # Compute super observations when needed
    
    for m in range(0, OBS.Nsurvey):
        T=OBSstruct()
        # Extract observations with the same survey time
        OBS.toarray()
        ind_t = np.where(OBS.time == OBS.survey_time[m])[0]
        for names in field_list:
           T.__dict__[names]=OBS.__dict__[names][ind_t]
        '''
        T.type=OBS.type[ind_t]
        T.time=OBS.time[ind_t]
        T.Xgrid=OBS.Xgrid[ind_t]
        T.Ygrid=OBS.Ygrid[ind_t]
        T.Zgrid=OBS.Zgrid[ind_t]
        T.depth=OBS.depth[ind_t]
        T.value=OBS.value[ind_t]
        T.error=OBS.error[ind_t]
        if (hasattr(OBS,'meta')): 
           T.meta=OBS.meta[ind_t]
        else:
           T.meta=np.zeros_like(T.value)

        if OBS.lat is not None:
           T.lat=OBS.lat[ind_t]
    
        if OBS.lon is not None:
           T.lon=OBS.lon[ind_t]
    
        if OBS.provenance is not None:
           T.provenance=OBS.provenance[ind_t]
        '''
        t_std=np.zeros_like(ind_t)
        std=OBS.error[ind_t]
      
        for n in range (0,Nstate):
            # Now extract observations associated with the same state variable
            ind_v = np.where(T.type == state_vars[n])[0]
            if (len(ind_v)==0):
                continue
            V=OBSstruct()
            for names in field_list:
                V.__dict__[names]=T.__dict__[names][ind_v]
            '''
            V.type=T.type[ind_v]
            V.time=T.time[ind_v]
            V.Xgrid=T.Xgrid[ind_v]
            V.Ygrid=T.Ygrid[ind_v]
            V.Zgrid=T.Zgrid[ind_v]
            V.depth=T.depth[ind_v]
            V.value=T.value[ind_v]
            V.error=T.error[ind_v]
            V.meta=T.meta[ind_v]
   
            if OBS.lat is not None:
               V.lat=T.lat[ind_v]
    
            if OBS.lon is not None:
               V.lon=T.lon[ind_v]
    
            if OBS.provenance is not None:
               V.provenance=T.provenance[ind_v]
            '''
            v_std=np.zeros_like(ind_v)
            vstd=T.error[ind_v]       
 
            # Set binning parameters. The processing is done in 
            #fractional (x,y,z) grid locations

            Xmin=np.min(V.Xgrid)
            Xmax=np.max(V.Xgrid)

            Ymin=np.min(V.Ygrid)
            Ymax=np.max(V.Ygrid)

            Zmin=np.min(V.Zgrid)
            Zmax=np.max(V.Zgrid)

            dx=1.; dy=1.; dz=1.
            minObs=1
 
            # Compute the index in each dimension of the grid cell in which the 
            # observation is located

            Xbin = 1.0 + np.floor((V.Xgrid -Xmin)/dx)
            Ybin = 1.0 + np.floor((V.Ygrid -Ymin)/dy)
            Zbin = 1.0 + np.floor((V.Zgrid -Zmin)/dz)

            # Similarly, compute the maximum averaging grid size

            Xsize = 1.0 + np.floor((Xmax - Xmin)/dx)
            Ysize = 1.0 + np.floor((Ymax - Ymin)/dy)
            Zsize = 1.0 + np.floor((Zmax - Zmin)/dz)
            A=np.ones([Ysize,Xsize,Zsize])
            # Combine the indices in each dimension into one index. 
            # It is like stacking all the matrix in one column vector
            varInd= Ybin + (Xbin-1)*A.shape[0] + (Zbin-1)*A.shape[0]*A.shape[1]
            onesCol=np.ones_like(varInd)
            maxVarInd=np.max(varInd)
            # Accumulate values in bins usig accum_np function. 
            # Count how many observations fall in each bin
            #count=accum_np(varInd,onesCol)
            count=np.bincount(varInd.astype(int),onesCol)

            # Bins with no observations are not kept. Index vector "isdata"
            # will be used in the conversion from the sparse output 
            # from accumarray to the corresponding full vector assigned to 
            # Sout
            isdata = np.where(count != 0)[0]
            Nsuper = len(isdata)
            Sout.tolist()
            # bin all fields
            # remove time and type from field_list used in this loop:
            
            for names in binfields:
                binned=np.bincount(varInd.astype(int),V.__dict__[names])
                binned=binned[isdata]/count[isdata]
                Sout.__dict__[names].extend(binned[:])
                if names =='value':
                    Vmean=binned
            '''   
            binned=np.bincount(varInd.astype(int),V.Xgrid)
            binned=binned[isdata]/count[isdata]
            Sout.Xgrid.extend(binned[:])
            binned=np.bincount(varInd.astype(int),V.Ygrid)
            binned=binned[isdata]/count[isdata]
            Sout.Ygrid.extend(binned[:])
            binned=np.bincount(varInd.astype(int),V.Zgrid)
            binned=binned[isdata]/count[isdata]
            Sout.Zgrid.extend(binned[:])
            binned=np.bincount(varInd.astype(int),V.depth)
            binned=binned[isdata]/count[isdata]
            Sout.depth.extend(binned[:])
            binned=np.bincount(varInd.astype(int),V.error)
            binned=binned[isdata]/count[isdata]
            Sout.error.extend(binned[:])
            binned=np.bincount(varInd.astype(int),V.value)
            binned=binned[isdata]/count[isdata]
            Sout.value.extend(binned[:])
            Vmean=binned
            binned=np.bincount(varInd.astype(int),V.meta)
            binned=binned[isdata]/count[isdata]
            Sout.meta.extend(binned[:])

            if OBS.lat is not None:
               binned=np.bincount(varInd.astype(int),V.lat)
               binned=binned[isdata]/count[isdata]
               Sout.lat.extend(binned[:])

            if OBS.lon is not None:
               binned=np.bincount(varInd.astype(int),V.lon)
               binned=binned[isdata]/count[isdata]
               Sout.lon.extend(binned[:])

            if OBS.provenance is not None:
               binned=np.bincount(varInd.astype(int),V.provenance)
               binned=binned[isdata]/count[isdata]
               Sout.provenance.extend(binned[:])
            '''
            binned = np.bincount(varInd.astype(int),V.value**2)
            binned=binned[isdata]/count[isdata] - Vmean**2
            #Sout.std.extend(np.sqrt(binned))
   
            Sout.type.extend(np.ones([Nsuper])*state_vars[n])
            Sout.time.extend(np.ones([Nsuper])*OBS.survey_time[m])
            Sout.Nobs[m] =  Sout.Nobs[m]+Nsuper
 
            if OBS.provenance is not None:
               Sout.provenance = np.floor(Sout.provenance).tolist()

    Sout=setDimensions(Sout)
    return Sout


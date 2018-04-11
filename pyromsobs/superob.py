import numpy as np
from .helpers import setDimensions,accum_np
from .OBSstruct import OBSstruct
from netCDF4 import Dataset
from roppy import SGrid

def superob(S,hisfile,superprov=77):
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

            Xsize = int(1.0 + np.floor((Xmax - Xmin)/dx))
            Ysize = int(1.0 + np.floor((Ymax - Ymin)/dy))
            Zsize = int(1.0 + np.floor((Zmax - Zmin)/dz))

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

                if names =='provenance':
                    for s in range(len(binned)):
                        if not binned[s] in set(V.provenance):
                            binned[s] = superprov + state_vars[n]

                Sout.__dict__[names].extend(binned[:])

                if names =='value':
                    Vmean=binned
            binned = np.bincount(varInd.astype(int),V.value**2)
            binned=binned[isdata]/count[isdata] - Vmean**2
            #Sout.std.extend(np.sqrt(binned))

            Sout.type.extend(np.ones([Nsuper])*state_vars[n])
            Sout.time.extend(np.ones([Nsuper])*OBS.survey_time[m])
            Sout.Nobs[m] =  Sout.Nobs[m]+Nsuper

            if hasattr(OBS,'provenance'):
               if len(OBS.provenance):
                    Sout.provenance = np.floor(Sout.provenance).tolist()

    Sout=setDimensions(Sout)
    Sout.toarray()
    return Sout

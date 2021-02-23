from netCDF4 import Dataset
import numpy as np
from .utils import setDimensions, sort_ascending
from .OBSstruct import OBSstruct

def add_fields(tmpS, field_list):
    for name in field_list:
        if (not hasattr(tmpS, name)) or (hasattr(tmpS, name) and len(getattr(tmpS, name)) != tmpS.Ndatum ):
            setattr(tmpS, name, np.ones(tmpS.Ndatum)*np.nan)
    return tmpS


def merge(files):
    '''
    Merges data from several ROMS observation NetCDF files

    Input:

    files - list containing file names or OBSstruct instances
    Output:

    S  - observation object

    '''


    Nfiles = len(files)

    # initialize object with first file
    if not isinstance(files[0],OBSstruct):
       fid = Dataset(files[0])
       S = OBSstruct(fid)
    else:
       S=OBSstruct(files[0])
    field_list = set(S.getfieldlist())
    S.toarray()

    try:
        if not any(getattr(S, 'variance')):
            S.variance = np.zeros(7)
    except:
        if not getattr(S, 'variance'):
            S.variance = np.zeros(7)

    # Process remaining files/objects
    for m in range(1,Nfiles):
        if not isinstance(files[m],OBSstruct):
           fid = Dataset(files[m])
           N = OBSstruct(fid)
        else:
           N=OBSstruct(files[m])

        # Make sure S and N have the same fields
        for name in N.getfieldlist():
            field_list.add(name)


        S = add_fields(S, field_list)


        N = add_fields(N, field_list)

        try:
            if not any(getattr(N, 'variance')):
                N.variance = np.zeros(7)
        except:
            if not getattr(N, 'variance'):
                N.variance = np.zeros(7)

        # Ensure the same dimension of variance across objects
        # The shorter variance will be appended 0 at the end of array to match the length of the longest variance
        if len(S.variance) != len(N.variance) :
            maxlen = max(len(S.variance),len(N.variance)  )
            for var in [S, N]:
                if len(getattr(var, 'variance')) < maxlen:
                    setattr(var, 'variance', np.append(getattr(var, 'variance'), np.zeros(maxlen - len(getattr(var, 'variance' )))))
        S.variance = (np.array( S.variance) +np.array( N.variance) ) / 2.


        N.tolist()
        S.tolist()
        for names in field_list:
            S.__dict__[names].extend(N.__dict__[names])

        # Ensure that observations are sorted according to ascending time,
        # and that survey_time, Nobs, Ndatum are up to date:
        S = sort_ascending(S)

    S=setDimensions(S)

    return S

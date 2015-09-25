from netCDF4 import Dataset
import numpy as np
from .helpers import setDimensions
from .OBSstruct import OBSstruct

def merge(files):
    '''
    Merges data from several ROMS observation NetCDF files
    
    Input:
    
    files - list containing file names or OBSstruct instances    
    Output:

    S  - observation object

    '''
    #field_list = ['time','type','depth','Xgrid','Ygrid','Zgrid','error','value']
 
    Nfiles = len(files)
    
    # initialize object with first file 
    if not isinstance(files[0],OBSstruct):
       fid = Dataset(files[0])
       S = OBSstruct(fid)
    else:
       S=OBSstruct(files[0])
    field_list=S.getfieldlist()
    S.toarray() 
    if (hasattr(S,'lon') and hasattr(S,'lat')):
       if( len(S.lat) and len(S.lon)):
           field_list.extend(['lon','lat'])
    if (hasattr(S,'provenance')): 
       if (len(S.provenance)):
           field_list.append('provenance')
    if (hasattr(S,'meta')): 
       if (len(S.meta)):
           field_list.append('meta')

    # Process remaining files/objects
    S.tolist()
    for m in range(1,Nfiles): 
        S.toarray()
        S.tolist()
        if not isinstance(files[m],OBSstruct):
           fid = Dataset(files[m])
           N = OBSstruct(fid)
        else:
           N=OBSstruct(files[m])
        N.tolist()
        for names in field_list:
            S.__dict__[names].extend(N.__dict__[names])
        S.survey_time.extend(N.survey_time)
        S.Nobs.extend(N.Nobs)
        S.variance = (np.array( S.variance) +np.array( N.variance) ) / 2.

        # order according to ascending survey_time
        tmplist = zip(*[S.survey_time, S.Nobs])
        tmplist.sort()
        tmplist = zip(*tmplist)
        S.survey_time=tmplist[:][0]
        S.Nobs=tmplist[:][1]
        S.Nsurvey=len(S.Nobs)

        # order according to ascending obs_time
        
        tmplist = zip(*[getattr(S,names) for names in field_list])
        tmplist.sort()
        tmplist = zip(*tmplist)
        
        for n in range(0,len(field_list)): 
            setattr(S,field_list[n],tmplist[n])

    S=setDimensions(S)
    S.toarray()
    return S




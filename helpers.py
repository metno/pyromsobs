import numpy as np



def setDimensions(OBS):
    '''
    Takes an observation structure, calculate unique survey_times
    and number of observations within each survey.
    Returns OBS
    '''
    OBS.toarray()
    OBS.survey_time=np.unique(OBS.time)
    '''
    OBS.Nsurvey=len(OBS.survey_time)
    OBS.Ndatum=len(OBS.time)
    '''
    OBS.Nsurvey=len(OBS.survey_time)
    OBS.Ndatum=len(OBS.time)
    Nobs=np.ones_like(OBS.survey_time)*float('nan')
    for item in enumerate(OBS.survey_time):
        Nobs[item[0]] = len(np.array(np.argwhere(OBS.time==item[1])))
    OBS.Nobs=Nobs
    return OBS
    
def accum_np(accmap, a, func=np.sum):
    indices = np.where(np.ediff1d(accmap, to_begin=[1],to_end=[1]))[0]     
    vals = np.zeros(len(indices) - 1)
    for i in xrange(len(indices) - 1):
        vals[i] = func(a[indices[i]:indices[i+1]])
    return vals


def popEntries(popindex, OBS):
    field_list=OBS.getfieldlist()
    '''
    field_list = ['time','type','depth','Xgrid','Ygrid','Zgrid','error','value']
    if (hasattr(OBS,'lon') and hasattr(OBS,'lat')):
       if ( OBS.lon.size and OBS.lat.size) :
           field_list.extend(['lon','lat'])
    if (hasattr(OBS,'provenance')): 
       if (OBS.provenance.size):
           field_list.append('provenance')
    if (hasattr(OBS,'meta')): 
       if (np.array(OBS.meta).size):
           field_list.append('meta')
    '''
    OBS.tolist()   

    popindex=np.array(popindex).squeeze()
    if popindex.size>1:
       indices=sorted(popindex.tolist(),reverse=True)
       for index in indices:
           for names in field_list:
                del OBS.__dict__[names][index]
    elif (popindex.size<2) & (popindex.size>0): 
       index=popindex
       for names in field_list:
           del OBS.__dict__[names][index]
    return OBS

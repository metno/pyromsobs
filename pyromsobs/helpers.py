import numpy as np
import re

def setDimensions(OBS):
    '''
    Takes an observation structure, calculate unique survey_times
    and number of observations within each survey.
    Returns OBS
    '''
    OBS.toarray()
    OBS.survey_time=np.unique(OBS.time)

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

def sort_ascending(OBS):
    '''
    Takes an observation structure and sorts the observations
    according to ascending time'
    '''
    field_list=OBS.getfieldlist()
    OBS.tolist()
    # order according to ascending obs_time

    tmplist = sorted(zip(*[getattr(OBS,names) for names in field_list]))
    #tmplist.sort()
    tmplist = list(zip(*tmplist))

    for n in range(0,len(field_list)):
        if (len(OBS.__dict__[field_list[n]])):
            setattr(OBS,field_list[n],tmplist[n])
    OBS.toarray()
    OBS=setDimensions(OBS)

    return OBS
def popEntries(popindex, OBS):
    field_list=OBS.getfieldlist()
    OBS.tolist()

    popindex=np.array(popindex).squeeze()
    if popindex.size>1:
       indices=sorted(popindex.tolist(),reverse=True)
       for index in indices:
           for names in field_list:
                if (len(OBS.__dict__[names])):
                    del OBS.__dict__[names][index]
    elif (popindex.size<2) & (popindex.size>0):
        index=popindex
        for names in field_list:
            if (len(OBS.__dict__[names])):
                del OBS.__dict__[names][index]
    return OBS
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
def extract_number(string):
    '''
    Function that can help sort filelist with datestring in filename
    '''
    r = re.compile(r'(\d+)')
    return int(r.findall(string)[0])

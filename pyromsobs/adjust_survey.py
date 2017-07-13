from netCDF4 import Dataset
import numpy as np
from .OBSstruct import OBSstruct
from .helpers import setDimensions
def adjust_survey(S,dt):
    '''
    This function spaces the survey_times evenely,
    and assigns observations to the closest survey.

    Input:

    OBS - OBSstruct object or observation netcdf file
    dt - interval between each survey_time in hours
    Output:

    OBS  - observation object
    '''

    if not isinstance(S,OBSstruct):
       fid = Dataset(S)
       OBS = OBSstruct(fid)
    else:
       OBS=OBSstruct(S)
    # let's assume survey_time/obs_time are given in decimal days.
    # Now define a new set of survey_times, based on the value given for dt

    survey_time=np.round(np.arange(np.floor(np.min(OBS.time)),np.ceil(np.max(OBS.time))+dt/24.,dt/24.),4)

    # The next step should allocate a given observation to the survey_time closest in time to the actual observation time.
    trydt=list(zip(*[abs(OBS.time - stamp) for stamp in survey_time]))
    uniquelength=np.array([len(np.unique(sample)) for sample in trydt])
    # If no observations are taken exactly 1/2 dt away from a survey_time
    # it is straight forward to assign observations to surveys. In this case
    # all elements of uniquelength will be equal, and hence np.unique(uniquelength)
    # will contain only one element.

    if not (len(np.unique(uniquelength)) > 1):
       otime=[survey_time[np.argmin(item[1])] for item in enumerate(trydt)]
    else:
       otime=np.ones_like(OBS.time)*float('nan')

       # Locate unproblematic observations and assign observation time
       ind = np.array(np.argwhere(uniquelength==len(survey_time))).squeeze()
       otime[ind]=[survey_time[np.argmin(item[1])] for item in enumerate(np.take(trydt,ind,axis=0))]

       # Now, locate problematic observations.
       ind = np.array(np.argwhere(uniquelength!=len(survey_time))).squeeze()


       # If a observation is taken exactly at the survey_time, there might be
       # timedeltas that are symmetric around 0, but containing zero. No need
       # to treat them any way special.

       check=[item[1] for item in enumerate(np.take(trydt,ind,axis=0))]

       popindex=[]
       trydt=np.array(trydt)
       for n in range(0,len(check)):
           if (0 in check[n]):
               popindex.append(n)
               otime[ind[n]]=survey_time[np.argmin(trydt[ind[n]])]


       # Now get rid of indicies that we assigned values for:
       newind = np.array([i for j, i in enumerate(ind) if j not in popindex]).squeeze()
       # Only continue if there are any observations left to handle:
       if (newind.size != 0):
           # Loop over unique observation times
           probtimes=np.array(np.unique(np.take(OBS.time,newind))).squeeze()

           #probtimes=np.array(np.unique(np.array(OBS.time)[newind])).squeeze()
           #for n in range(0,probtimes.size):
           if probtimes.size == 1:
               n=probtimes
               # Locate variables with coinciding observation time
               #tmpind=newind[np.take(OBS.time,newind)==probtimes[n]]
               #tmpind=newind[np.array(OBS.time)[newind]==probtimes[n]]

               tmpind=newind[np.array(OBS.time)[newind]== n]
               if (tmpind.size==1):
                  otime[tmpind]=survey_time[np.argmin(trydt[tmpind])]
               else:
                  # For each observation type, assign half of values to lower
                  # survey_time, other half to higher survey_time
                  # If only one observation of given type, assign it to the lower.
                  ntypes=np.array(np.unique(np.take(OBS.type,tmpind))).squeeze()
                  if not (ntypes.size>1):
                      # First half gets first mintime
                      np.put(otime,tmpind[0:int(np.floor(len(tmpind)/2.))],[survey_time[np.argmin(item[1])] for item in enumerate(np.take(trydt,tmpind[0:int(np.floor(len(tmpind)/2.))]))])
                      # Second half gets last mintime
                      np.put(otime,tmpind[int(np.floor(len(tmpind)/2.)):],[survey_time[np.argmin(item[1])+1] for item in enumerate(np.take(trydt,tmpind[int(np.floor(len(tmpind)/2.)):]))])
                  else:

                      for t in range(0,ntypes.size):
                          typeind=tmpind[np.take(OBS.type,tmpind)==ntypes[t]]
                          if (typeind.size == 1):
                             otime[typeind]=survey_time[np.argmin(trydt[typeind])]
                          else:
                             # First half gets first mintime
                             np.put(otime,typeind[0:int(np.floor(len(typeind)/2.))],[survey_time[np.argmin(item[1])] for item in enumerate(np.take(trydt,typeind[0:int(np.floor(len(typeind)/2.))]))])
                             # Second half gets last mintime
                             np.put(otime,typeind[int(np.floor(len(typeind)/2.)):],[survey_time[np.argmin(item[1])+1] for item in enumerate(np.take(trydt,typeind[int(np.floor(len(typeind)/2.)):]))])

           else:
               for n in probtimes:

                   # Locate variables with coinciding observation time
                   #tmpind=newind[np.take(OBS.time,newind)==probtimes[n]]
                   #tmpind=newind[np.array(OBS.time)[newind]==probtimes[n]]

                   tmpind=newind[np.array(OBS.time)[newind]== n]
                   if (tmpind.size==1):
                      otime[tmpind]=survey_time[np.argmin(trydt[tmpind])]
                   else:
                      # For each observation type, assign half of values to lower
                      # survey_time, other half to higher survey_time
                      # If only one observation of given type, assign it to the lower.
                      ntypes=np.array(np.unique(np.take(OBS.type,tmpind))).squeeze()
                      if not (ntypes.size>1):
                          # First half gets first mintime
                          np.put(otime,tmpind[0:int(np.floor(len(tmpind)/2.))],[survey_time[np.argmin(item[1])] for item in enumerate(np.take(trydt,tmpind[0:int(np.floor(len(tmpind)/2.))]))])
                          # Second half gets last mintime
                          np.put(otime,tmpind[int(np.floor(len(tmpind)/2.)):],[survey_time[np.argmin(item[1])+1] for item in enumerate(np.take(trydt,tmpind[int(np.floor(len(tmpind)/2.)):]))])
                      else:

                          for t in range(0,ntypes.size):
                              typeind=tmpind[np.take(OBS.type,tmpind)==ntypes[t]]
                              if (typeind.size == 1):
                                 otime[typeind]=survey_time[np.argmin(trydt[typeind])]
                              else:
                                 # First half gets first mintime
                                 np.put(otime,typeind[0:int(np.floor(len(typeind)/2.))],[survey_time[np.argmin(item[1])] for item in enumerate(np.take(trydt,typeind[0:int(np.floor(len(typeind)/2.))]))])
                                 # Second half gets last mintime
                                 np.put(otime,typeind[int(np.floor(len(typeind)/2.)):],[survey_time[np.argmin(item[1])+1] for item in enumerate(np.take(trydt,typeind[int(np.floor(len(typeind)/2.)):]))])

    # OK, that should have done the job!
    # Now we need to find number of observations within each survey_time,
    # and delete surveys that does not contain  observations
    OBS.time=otime
    OBS=setDimensions(OBS)

    '''
    OBS.survey_time=survey_time
    Nobs=np.ones_like(OBS.survey_time)*float('nan')
    for item in enumerate(OBS.survey_time):
        Nobs[item[0]] = int(len(np.array(np.argwhere(otime==item[1]))))
    OBS.Nobs=Nobs
    ind=np.argwhere(OBS.Nobs!=0).squeeze()
    OBS.survey_time=OBS.survey_time[ind]
    OBS.Nobs=OBS.Nobs[ind]
    OBS.Nsurvey=len(OBS.survey_time)

    OBS.time=otime
    '''
    OBS.toarray()
    return OBS

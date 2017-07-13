import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
from .OBSstruct import OBSstruct
from datetime import datetime,timedelta
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
def plot_datum(S,ref):
    # Plot number of observations as function of survey time
    # for all observation types
    
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)
        
    OBS.toarray()
    
    otype=np.unique(OBS.type)

    '''
    onum = np.ones([len(otype),OBS.Nsurvey]) * np.nan
    xdates=[]
    for n in range(0,len(otype)):
        for t in range(0, OBS.Nsurvey):
            onum[n,t] = OBS[np.where(OBS.type[np.where(OBS.time == OBS.survey_time[t])] == otype[n] )].Ndatum
            if not onum[n,t]:
                onum[n,t]=np.nan 
            if (n == 0) :
                xdates.append(ref + timedelta(days=OBS.survey_time[t])) 
    '''
    
    #xdates=np.array(xdates)
    obstypes=['zeta', 'ubar', 'vbar', 'u' ,'v', 'temperature', 'salinity','','','','','','','','','','','','','radial velocity']
    omark=['.','|','_','5','6','x','+','','','','','','','','','','','','','2']
    #print onum.shape, len(xdates)
    fig, ax = plt.subplots()
    count=0
    for n in otype:
        TS=OBS[np.where(OBS.type==n)]
        xdates=[]
        for t in range(0,len(TS.survey_time)):
            xdates.append(ref + timedelta(days=TS.survey_time[t]))  
        
        ax.semilogy(np.array(xdates),TS.Nobs,linestyle='None', marker=omark[int(n)-1], label=obstypes[int(n)-1], markersize=10)
       
        #ax.plot(np.array(xdates),onum[count,:],linestyle='None', marker=omark[int(n)-1], label=obstypes[int(n)-1])
        count += 1
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()
    
    import matplotlib.dates as mdates
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    # The hour locator takes the hour or sequence of hours you want to
    # tick, not the base multiple
    
    #a#x.xaxis.set_major_locator( DayLocator() )
    #ax.xaxis.set_minor_locator( HourLocator(arange(0,25,6)) )
    #ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d') )
    
    #ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
    #fig.autofmt_xdate()
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=len(otype), mode="expand", borderaxespad=0.)

    plt.ylabel('Nobs', fontsize=16)
    plt.show()
    return
    
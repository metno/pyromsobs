from netCDF4 import Dataset
import numpy as np
from .helpers import setDimensions, natural_keys
from subprocess import call
from glob import glob
import re
def fast_merge(files, outputfile):
    '''
    An alternative to the standard merge function for large observation files.
    This function makes use of nco tools, and will generate temporary nc-files
    in the working directory.
    For this function to work properly the observations within the files must already be
    sorted according to time in ascending order. The list of files given to this function
    should also be sorted.


    Input:
    files - list containing file names
    outputfile - filepath/filename of observation file to be generated

    Output:
    None, a new observation file file be created and written
    '''
    Nfiles = len(files)
    for n in range(Nfiles):
        try:
            call('ncks -O -x -v Nobs,survey_time --mk_rec_dmn datum '+files[n]+' '+'.tmp_obsfile_'+str(n)+'.nc', shell = True)
        except:
            pass
    tmpfiles = glob('.tmp_obsfile_*.nc')
    tmpfiles.sort(key=natural_keys)
    call('ncrcat -O '+' '.join(tmpfiles) + ' ' + outputfile, shell=True)
    fid = Dataset(outputfile, 'r+')
    time = fid.variables['obs_time'][:]
    stime = np.unique(time)
    Nsurvey = len(stime)
    Nobs = np.ones_like(stime)*float('nan')
    Ndatum=len(time)
    for item in enumerate(stime):
        Nobs[item[0]] = len(np.array(np.argwhere(time == item[1])))

    fid.createDimension('survey', Nsurvey)
    var = fid.createVariable('Nobs','i4',('survey',))
    var.long_name='number of observations with the same survey time'
    var[:]=Nobs[:]
    time = fid.variables['obs_time']

    var = fid.createVariable('survey_time','f8',('survey',))
    var.long_name='survey time'
    var.units= time.units
    var.calendar = "gregorian"
    var[:] = stime[:]
    fid.close()

    return None


from netCDF4 import Dataset
import pyromsobs
import numpy as np
from datetime import datetime, timedelta

def main():
    en4file = 'EN.4.2.1.f.profiles.g10.201704.nc'
    gridfile = 'http://thredds.met.no/thredds/dodsC/sea_norshelf_3hr_agg'

    reftime = datetime(1970, 1, 1)
    variables = { 'POTM_CORRECTED': {'key': 'POTM_CORRECTED', 'type': 6, 'provenance': 13, 'error': 0.25**2},
                  'PSAL_CORRECTED': {'key': 'PSAL_CORRECTED', 'type': 7, 'provenance': 14, 'error': 0.1**2}}

    obs = EN4_to_ROMSobs(variables['PSAL_CORRECTED'], en4file, reftime, gridfile)
    obs.writeOBS('test.nc')

    return
    
def EN4_to_ROMSobs(var, insitufile, reftime, gridfile):
    expected_format = "days since %Y-%m-%d %H:%M:%S utc"
    fid = Dataset(insitufile, 'r')
    # Create empty observation object
    obs = pyromsobs.OBSstruct()

    if (not (var['key'] in fid.variables)):
        print('No observations of {} on {}'.format(var['key'], insitufile))
        return None
    try:
        obs.time = fid.variables['JULD'][:]
        timeunit = str(fid.variables['JULD'].units)
        obsref = datetime.strptime(timeunit,expected_format)
        for n in range(0,len(obs.time)):
            obs.time[n]=(obsref + timedelta(days=obs.time[n])-reftime).total_seconds()/86400.

        # JULD has dimension N_PROF, but we want a time value for every observation value
        # (dimensions (N_PROF, N_LEVELS))
        # Thus, repeat JULD N_LEVELS times, make sure we get an array with dimension (N_PROF, N_LEVELS).,
        # Ravel array so we end up with a vector
        obs.time = np.transpose(np.tile(obs.time, (len(fid.dimensions['N_LEVELS']), 1))).ravel()

    except KeyError:
        print('No time variable on file ' + insitufile)
        return None
    try:
        obs.lon = np.transpose(np.tile(fid.variables['LONGITUDE'][:], (len(fid.dimensions['N_LEVELS']), 1))).ravel()
        obs.lat = np.transpose(np.tile(fid.variables['LATITUDE'][:], (len(fid.dimensions['N_LEVELS']), 1))).ravel()
        # Use meta for temporal storage of position quality flag
        obs.meta = np.transpose(np.tile(fid.variables['POSITION_QC'][:], (len(fid.dimensions['N_LEVELS']), 1))).ravel()
    except KeyError:
        print('No position data on ' + insitufile)
        return None

    try:
        obs.depth = -1* (fid.variables['DEPH_CORRECTED'][:,:]).ravel()
    except KeyError:
        print('No DEPH variable on ' + insitufile)
        return None
    try:
        obs.value = fid.variables[var['key']][:,:].ravel()
        # Use error as temporary storage of quality flag
        obs.error = fid.variables[var['key'] + '_QC'][:,:].ravel()
        # Use type as temporary storage of quality flag
        obs.type = np.transpose(np.tile(fid.variables['PROFILE_{}_QC'.format(var['key'].split('_')[0])][:],(len(fid.dimensions['N_LEVELS']), 1))).ravel()
    except KeyError:
        print('No {} data on {}'.format(var['key'], insitufile))
        return None

    fid.close()
    '''
    From https://www.metoffice.gov.uk/hadobs/en4/download-en4-2-0.html:
    Quality control information
    To make correct use of the profile data, the quality control flags must be read and applied.
    There are two ways to do this:
    Use the POSITION_QC, PROFILE_POTM_QC, PROFILE_PSAL_QC, POTM_CORRECTED_QC and PSAL_CORRECTED_QC variables.
    These have values of either '1' (accept) or '4' (reject)
    (or '0' where there were no data and hence no quality control was performed).
    '''

    # Get rid of bad observations (keep only observations with QC equal to '1':,

    obs = obs[np.where( obs.type == b'1')]
    obs = obs[np.where( obs.meta == b'1')]
    obs = obs[np.where( obs.error == b'1')]

    # Give type and error reasonable values, empty meta\n",
    obs.type = np.ones_like(obs.lon)*var['type']
    obs.error = np.ones_like(obs.lon)*var['error']
    obs.provenance = np.ones_like(obs.lon)*var['provenance']
    obs.meta = np.empty_like(obs.lon)

    obs.spherical = 1,
    obs.Nstate = 7
    obs.variance = np.zeros(obs.Nstate)
    obs = pyromsobs.helpers.setDimensions(obs)
    obs = pyromsobs.calcFracGrid(obs,gridfile, onlyHorizontal = False)

    obs.Zgrid = obs.depth

    obs.true_depth = np.empty_like(obs.lon)
    obs.true_time = np.empty_like(obs.lon)
    obs.instrumental_error = np.empty_like(obs.lon)
    obs.scale = np.empty_like(obs.lon)
    obs.NLmodel_value = np.empty_like(obs.lon)
    return obs

if __name__ == "__main__":
    main()

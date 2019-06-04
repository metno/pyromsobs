#! /usr/bin/env python
import numpy as np
#import matplotlib
#matplotlib.use('Agg')
import pyromsobs
from datetime import datetime, timedelta
from glob import glob
from subprocess import call
import os.path
# Script to read csvfiles from the CastAway CTD and convert them to ROMS observation files
ref = datetime(1970,1,1)
castawaydir = '/home/annks/work/pyromsobs_devel/example/'
castawayfiles = glob(castawaydir+'CC*.csv')

uncertainty = {'salt': 0.15*0.15, 'temp': 0.1*0.1}
provenance = {'salt':157, 'temp': 156}
#gridfile ='/lustre/storeB/project/fou/hi/opera/obs_configfiles/norshelf_2.4_vert_grd.nc'
latkey = 'End latitude'
lonkey = 'End longitude'
timekey = 'UTC'
expected_format = '%Y-%m-%d %H:%M:%S'

for castawayfile in castawayfiles:
    if os.path.exists('{}_obs.nc'.format(castawayfile.split('.')[0])):
        continue
    lat = np.nan
    lon = np.nan
    timestamp = np.nan
    gotpos = False
    # Get position and time from file header
    with open(castawayfile) as f:
        while not gotpos:
            line = f.readline()
            if latkey in line:
                lat = float(line.split(',')[-1])
            elif lonkey in line:
                lon = float(line.split(',')[-1])
            elif timekey in line:
                print(line, line.split(',')[-1])
                timestamp = (datetime.strptime(line.split(',')[-1].strip(), expected_format) - ref).total_seconds()/86400.
            if all(np.isfinite([lat,lon, timestamp])):
                gotpos = True
    print(lat,lon, timestamp)

    # read file body
    data = np.genfromtxt(castawayfile, delimiter=',', comments='#', skip_header = 29, dtype = (float, float, float, float, float, float, float, float),\
                             names='pressure, depth, temp, conductivity, specific_conductance, salinity, sound_velocitiy, density')

    # Create roms observation object and fill in information
    salt = pyromsobs.OBSstruct()
    salt.Nstate = 7
    salt.spherical = 1
    salt.variance = np.zeros(salt.Nstate)

    salt.variance[5] = 0.5*0.5
    salt.variance[6] = 0.05*0.05
    salt.value = data['salinity']
    salt.depth = np.abs(data['depth'])*-1.
    salt.lon = np.ones_like(salt.value)*lon
    salt.lat = np.ones_like(salt.value)*lat
    salt.time = np.ones_like(salt.value)*timestamp
    salt.type = np.ones(len(salt.value))*7

    us = [salt.__dict__]
    variables = ['Xgrid', 'Ygrid', 'Zgrid', 'meta', 'true_time', 'true_depth', 'instrumental_error',  'scale', 'NLmodel_value', 'NLmodel_initial', 'error', 'provenance' ]

    for me in us:
        for var in variables:
            try:
                me[var] = np.zeros_like(me['value'])
            except:
                pass

    salt = pyromsobs.helpers.setDimensions(salt)
    print(salt.Ndatum)
    #salt = pyromsobs.calcFracGrid(salt, gridfile)
    if not salt.Ndatum:
        # No observations within model grid
        # Create empty netcdf so we don't have to bother with this file later on
        call('touch {}_obs.nc'.format( castawayfile.split('.')[0]), shell = True)
        continue

    temp = pyromsobs.OBSstruct(salt)
    temp.value = data['temp']
    temp.type[:] = 6
    temp.provenance[:] = provenance['temp']
    temp.error[:] = uncertainty['temp']
    salt.provenance[:] = provenance['salt']
    salt.error[:] = uncertainty['salt']
    print(salt.Ndatum, temp.Ndatum)
    obs = pyromsobs.merge([salt, temp])
    obs.writeOBS('{}_obs.nc'.format(castawayfile.split('.')[0]) , attfile='/home/annks/work/pyromsobs_devel/pyromsobs/METattributes.att')
exit()

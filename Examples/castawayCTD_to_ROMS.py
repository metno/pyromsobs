#! /usr/bin/env python
import numpy as np
import pyromsobs
from datetime import datetime, timedelta
from glob import glob
from subprocess import call
import os.path
# Script to read csvfiles from the CastAway CTD and convert them to ROMS observation files
# Test file included in the repository is CC1747002_20180606_165416.csv

ref = datetime(1970,1,1)
castawaydir = ''
castawayfiles = glob(castawaydir+'CC*.csv')

uncertainty = {'salt': 0.15*0.15, 'temp': 0.1*0.1}
provenance = {'salt':157, 'temp': 156}


latkey = 'End latitude'
lonkey = 'End longitude'
timekey = 'UTC'
expected_format = '%Y-%m-%d %H:%M:%S'

for castawayfile in castawayfiles:
    if os.path.exists('{}_obs.nc'.format(castawayfile.split('.')[0])):
        call('rm {}_obs.nc'.format(castawayfile.split('.')[0]) , shell = True)
    lat = np.nan
    lon = np.nan
    timestamp = np.nan
    gotpos = False
    # Get position and time from file header
    # Will read csv file line by line, looking for the keys that identifies
    # that position information is on the current line.
    # When both lat, lon, and time is read gotpos will be set to True
    with open(castawayfile) as f:
        while not gotpos:
            line = f.readline()
            if latkey in line:
                lat = float(line.split(',')[-1])
            elif lonkey in line:
                lon = float(line.split(',')[-1])
            elif timekey in line:
                timestamp = (datetime.strptime(line.split(',')[-1].strip(), expected_format) - ref).total_seconds()/86400.
            if all(np.isfinite([lat,lon, timestamp])):
                gotpos = True
    print('\n Latitude: {}\n Longitude: {}\n Time: {}\n'.format(lat,lon, ref + timedelta(days=timestamp)))

    # read file body
    data = np.genfromtxt(castawayfile, delimiter=',', comments='#', skip_header = 29, dtype = (float, float, float, float, float, float, float, float),\
                             names='pressure, depth, temp, conductivity, specific_conductance, salinity, sound_velocitiy, density')

    # Create roms observation object and fill in information
    salt = pyromsobs.OBSstruct()
    salt.Nstate = 7  # Set the state dimension
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

    salt = pyromsobs.helpers.setDimensions(salt) # Setting the dimensions correctly (including Nobs and survey_time variables)
    print('Number of salinity observations read: {}'.format(salt.Ndatum))
    #salt = pyromsobs.calcFracGrid(salt, gridfile) # If calculating fractional grid coordinates, the call would look like this

    # calcFracGrid will also remove observations that fall outside the grid.
    # Thus, we could end up with zero observations.
    if not salt.Ndatum:
        # No observations within model grid
        continue

    # For the file type we are currently working on, there is a Temperature observation at
    # the same location as the salinities. Thus, we need only make a copy of the salinity
    # observation object, and change observation values and type.

    temp = pyromsobs.OBSstruct(salt)  # Creating a copy of salt
    temp.value = data['temp']        # Overwriting salinity values with Temperature
    temp.type[:] = 6                   # Setting the observation type

    # Finally, use the provenance and errors specified at the beginnig of the script.
    temp.provenance[:] = provenance['temp']

    temp.error[:] = uncertainty['temp']
    salt.provenance[:] = provenance['salt']
    salt.error[:] = uncertainty['salt']

    obs = pyromsobs.merge([salt, temp])  # Merge the two observation objects into one

    # The merge function also handles sorting according to ascending time
    print('Total number of observations to be saved to file: {}\n'.format(obs.Ndatum))


    obs.writeOBS('{}_obs.nc'.format(castawayfile.split('.')[0]) , attfile='../METattributes.att')
exit()

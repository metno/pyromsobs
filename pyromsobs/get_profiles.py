import numpy as np
from .utils import sort_ascending
from .OBSstruct import OBSstruct
from netCDF4 import Dataset

def get_profiles(S, obstype = None, provtype = None, ndepths = 2):
    '''
    This function identifies observations that constitute a vertical
    profile

    Input:

    OBS - OBSstruct object or observation netcdf file
    obstype     -   if defined it should point to one or more of the
                    state variables. Can be scalar or list
    ndepths     -   minimum number of unique depths in a profile

    Output:

    OBS         -   observation object, with only observations that belong to a profile
    NPROF       -   The number of unique profiles on OBS
    profileID   -   An array of length OBS.Ndatum. Will contain a number linking the observation
                    to the profile of which it is a part.
    '''
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)

    if obstype:
        if not type(obstype) in [list, int, float]:
            print('ERROR: Vartype argument must be either scalar or list of integer values')
            return

        if type(obstype) in [int,float]:
            obstype = [obstype]

        # Subsample OBS to only hold observation of the requested obstype
        OBS = OBS[np.where(np.in1d(OBS.type, obstype))]
        # Subsample OBS to only hold observation of the requested obstype
        if not OBS.Ndatum:
            print('ERROR: No observations matching the requested variable type')
            return

    if provtype:
        if not type(provtype) in [list, int, float]:
            print('ERROR: Vartype argument must be either scalar or list of integer values')
            return

        if type(provtype) in [int, float]:
            obstype = [obstype]

        # Subsample OBS to only hold observation of the requested provenance
        OBS = OBS[np.where(np.in1d(OBS.provenance, provtype))]
        if not OBS.Ndatum:
            print('ERROR: No observations matching the requested provenance')
            return


    # Make sure the observations are sorted:
    OBS = sort_ascending(OBS)

    # Observations that constitute a vertical profile
    # will have the same values for
    # - Time (taken ~simultaneusly)
    # - observation type  (same state variable)
    # - provenance (taken by the same instrument)
    # - longitude
    # - latitude   (same location)

    # Create a list of unique positions
    positions = set()

    for n in range(OBS.Ndatum):
        positions.add( (OBS.time[n], OBS.type[n], OBS.provenance[n], OBS.lon[n], OBS.lat[n]) )


    positions = list(positions)

    # Now identify unique positions with more than one unique depth value
    depths = []
    for n in range(len(positions)):
        depths.append(len(np.unique(OBS.depth[np.argwhere( (OBS.time == positions[n][0]) & (OBS.type == positions[n][1])
                             & (OBS.provenance == positions[n][2]) & (OBS.lon == positions[n][3])
                             & (OBS.lat == positions[n][4]) )])))

    # Filter positions. Keep only positions where there are more than ndepths unique depths
    positions = np.array([positions[n] for n in range(len(positions)) if depths[n] >=  ndepths ])

    # Now we need to strip down the observation object
    index =  np.squeeze(np.argwhere( (np.in1d(OBS.time,positions[:,0])) & (np.in1d(OBS.type ,positions[:,1]))
                         & (np.in1d(OBS.provenance, positions[:,2])) & (np.in1d(OBS.lon ,positions[:,3]))
                         & (np.in1d(OBS.lat,positions[:,4])) ))
    OBS = OBS[index]



    NPROF = positions.shape[0]  # Number of unique profiles
    profileID = np.zeros_like(OBS.time)

    # Loop over the unique profile locations
    for n in range(NPROF):
        index =  np.squeeze(np.argwhere( (OBS.time == positions[n,0]) & (OBS.type == positions[n,1])
                             & (OBS.provenance == positions[n,2]) & (OBS.lon == positions[n,3])
                             & (OBS.lat == positions[n,4]) ))
        profileID[index] = n



    return OBS, NPROF, profileID

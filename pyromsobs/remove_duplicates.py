import numpy as np
from netCDF4 import Dataset
from .utils import popEntries,setDimensions
from .OBSstruct import OBSstruct
import pandas as pd
def remove_duplicates(S, coordinate = 'fractional'):
    '''
    This function identifies duplicated observations
    and makes sure all observation on output are unique.

    Input:

    OBS - OBSstruct object or observation netcdf file
    coordinate - Whether to base method on fractional grid coordinates (default)
                or  use lon/lat/depth  'geographical'
    '''
    if not isinstance(S,OBSstruct):
        fid = Dataset(S)
        OBS = OBSstruct(fid)
    else:
        OBS=OBSstruct(S)
    # New method

    OBSout = OBSstruct()
    OBSout.variance = OBS.variance
    OBSout.Nstate = OBS.Nstate
    OBSout.spherical = OBS.spherical
    OBSout.globalatts = OBS.globalatts


    #  Create a pandas dataframe from the observation object:
    data = {}
    for name in OBS.getfieldlist():
        data[name] = getattr(OBS, name)

    if coordinate == 'fractional':
        identifyers = {'X' : 'Xgrid', 'Y':'Ygrid', 'Z':'Zgrid'}
    elif coordinate == 'geographical':
        identifyers = {'X' : 'lon', 'Y':'lat', 'Z':'depth'}
    identifyers['T'] = 'time'
    identifyers['V'] = 'value'

    # expand data with rounded values that will be used to test uniqueness
    for name in identifyers.keys():
        data[name] = np.round(getattr(OBS, identifyers[name]), 3)

    # Finally, the dataframe:
    df = pd.DataFrame(data)
    df=df.drop_duplicates(subset = ["T","X","Y","Z","V","type"])

    # Convert the reduced data set back to observation object
    for name in OBS.getfieldlist():
        setattr(OBSout, name, df[name].values)

    OBSout = setDimensions(OBSout)
    return OBSout

# -*- coding: utf-8 -*-
import operator
import numpy as np
from netCDF4 import Dataset
from .utils import setDimensions
class OBSstruct(object):
    """ Simple ROMS observation file object

    Typical usage: :
    Initializing from existing ROMS observation file

    >>> fid = Dataset(OBSfile)
    >>> OBS = OBSstruct(fid)

    or directly from file:
    >>> OBS = OBSstruct('OBSfile')

    Intializing an empty object, e.g. when reading raw observations
    or when super-obing/merging observation objects

    >>> OBS = OBSstruct()

    Copy existing object to new object
    >>> newOBS=OBSstruct(OBS)

    The array entries of the OBS object should always(!) be numpy arrays outside
    of the functions specific to the class.

    They may, however, be transformed to lists by
    OBS.tolist()

    and then back to arrays by:
    OBS.toarray()
    """

    def __init__(self, ifile = None):
        if ifile:
            if not isinstance(ifile,OBSstruct):
                # Check if ifile is string, if not we assume it is file id
                # for netcdf file opened with fid=Dataset('netcdf_file.nc')
                if isinstance(ifile, str):
                    ifile = Dataset(ifile)

                # Read info from file

                # first the dimensions, must be present on file
                self.Nsurvey = len(ifile.dimensions['survey'])
                try:
                    self.Nstate  = len(ifile.dimensions['state_variable'])
                except KeyError:
                    self.Nstate = len(ifile.dimensions['state_var'])

                self.Ndatum  = len(ifile.dimensions['datum'])

                # Now load Nobs and survey_time, must be present on file
                self.Nobs        = ifile.variables['Nobs'][:]
                self.survey_time = ifile.variables['survey_time'][:]

                # some information on the data set, not critical if not present
                try:
                    self.spherical   = ifile.variables['spherical'][0]
                except:
                    print("Variable spherical is not present on input file, consider adding information")
                    print("OBS.spherical = 1 if grid is spherical")
                    print("OBS.spherical = 0 if grid is cartesian")
                    self.spherical = None

                try:
                    self.variance    = ifile.variables['obs_variance'][:]
                except:
                    self.variance= []

                # A dictionary of possible variables which could be present on the
                # file, all of length Ndatum
                obsvars = self.allvarnames()

                for varname in obsvars:
                    try:
                        if len(ifile.variables[obsvars[varname][1]].dimensions) > 1:
                            self.__dict__[varname] = ifile.variables[obsvars[varname][1]][-1,:]
                        else:
                            self.__dict__[varname] = ifile.variables[obsvars[varname][1]][:]
                    except:
                        pass

                for varname in obsvars:
                    if not hasattr(self, varname):
                        setattr(self, varname, np.array([]))

                # The global attributes, stored in a dictionary
                self.globalatts = {}
                try:
                    for name in ifile.ncattrs():
                        exec('self.globalatts["%s"] = """%s"""' % (name, getattr(ifile,name)))
                except:
                    print("No global attributes on file")
                ifile.close()

            elif isinstance(ifile,OBSstruct):
                # Create an empty OBSstruct
                #first the dimension

                self.Nsurvey = np.int(ifile.Nsurvey)
                self.Ndatum  = np.int(ifile.Ndatum)

                self.Nobs        = np.array(ifile.Nobs)
                self.survey_time = np.array(ifile.survey_time)
                # Allow for the possibilty of statevars and variance not being defined yet
                try:
                    self.Nstate  = np.int(ifile.Nstate)
                except:
                    self.Nstate = None
                try:
                    self.variance    = np.array(ifile.variance)
                except:
                    self.variance = None
                try:
                    self.spherical = int(ifile.spherical)
                except:
                    self.spherical = None
                obsvars = self.allvarnames()
                for varname in obsvars:
                    try:
                        self.__dict__[varname] = np.array(ifile.__dict__[varname])
                    except:
                        pass
                self.globalatts = dict(ifile.globalatts)
        else:
            # Create an empty OBSstruct
            #first the dimension
            self.Nsurvey = 0
            self.Nstate  = 7
            self.Ndatum  = 0

            # some information on the data set
            self.spherical   = None
            self.Nobs        = np.array([])
            self.survey_time = np.array([])
            self.variance    = None

            obsvars = self.allvarnames()

            for varname in obsvars:
                self.__dict__[varname] = np.array([])
            # The global attributes, stored in a dictionary
            self.globalatts = {}

    def allvarnames(self):
        # The numbers in the dictionary entries determines how data will be sorted in other functions/methods.
        # Sorting observation will thus first order all observations after time.
        # Secondly, if there are more observation types for a given time, these will be sorted according to type.
        # Thirdly, if at a given time there are more observations of a given type, they will be sorted according to
        # their depth

        obsvars = {'time' : [1,'obs_time'], 'type' : [2,'obs_type'],
		           'depth' : [6,'obs_depth'],'Xgrid' : [4,'obs_Xgrid'],
				   'Ygrid' : [5,'obs_Ygrid'], 'Zgrid' : [7,'obs_Zgrid'],
				   'error' : [8,'obs_error'] , 'value' :[9,'obs_value'],
				   'lon' : [10,'obs_lon'],'lat' : [11,'obs_lat'] ,
				   'provenance' : [3,'obs_provenance'],'meta' : [12,'obs_meta'],
				   'true_time' : [13,'obs_true_time'] ,'true_depth' : [14,'obs_true_depth'],
				   'instrumental_error' :[ 15,'instrumental_error'], 'scale' : [16, 'obs_scale'],
                   'NLmodel_value': [17, 'NLmodel_value'], 'NLmodel_initial': [18, 'NLmodel_initial'],
                   'BgError_value': [19, 'BgError_value'], 'BgThresh_value': [20, 'BgThresh_value'],
                   'innovation': [21, 'innovation'], 'increment': [22, 'increment'],
                   'residual': [23, 'residual'], 'TLmodel_value': [24, 'TLmodel_value'],
                   'misfit_initial': [25, 'misfit_initial'], 'misfit_final': [26, 'misfit_final']
                   }

        return obsvars


    def getfieldlist(self):
        field_list = []
        obsvars = sorted(self.allvarnames().items(), key = operator.itemgetter(1))
        for varname in obsvars:
            if (hasattr(self,varname[0])):
                if (len(getattr(self, varname[0]))):
                    field_list.append(varname[0])
        return field_list

    def __getitem__(self,index):
        field_list = self.getfieldlist()
        self.toarray()
        S = OBSstruct()
        if isinstance(index, (int)):
            if index < 0:
                index = len(getattr(self, field_list[0])) + index
            index = slice(index, index+1, None)
        if isinstance(index, slice):

            if index.start < 0:
                index = slice(len(getattr(self, field_list[0])) + index.start, index.stop, None)
            if index.stop < 0:
                index = slice(index.start, len(getattr(self, field_list[0])) + index.stop, None )

        for names in field_list:
            if (len(self.__dict__[names])):
                S.__dict__[names] = self.__dict__[names][index]
        S = setDimensions(S)
        if hasattr(self,'spherical'):
            S.spherical = self.spherical
        S.Nstate = self.Nstate
        if hasattr(self,'variance'):
            S.variance = self.variance
        return S

    def put(self, obs_dict, fill_value = np.nan):
        '''
        obs_dict should be a dictionary with field names as keys (e.g. value, lon, lat, time) and the corresponding values as elements

        '''
        if len([obs_dict['value']]) > 1:
            print('ERROR message: self.put method is intended for single observation only')
            return

        if self.Ndatum: #(No point in the below if obs object is empty)
            field_list = self.getfieldlist()
            for key in obs_dict.keys():
                if not len(getattr(self, key)):
                    # Check if object has field indicated by key, if not create it
                    setattr(self, key, np.ones_like(getattr(self, field_list[0]))*fill_value)

            # Now the object is ready for appending the information provided in obs_dict.
            # To ensure that we add to all elements, loop over field_list.
            field_list = self.getfieldlist()
            for name in field_list:
                if name in obs_dict.keys():
                    setattr(self, name, np.append(getattr(self, name), obs_dict[name]))
                else:
                    setattr(self, name, np.append(getattr(self, name),fill_value))
            self = setDimensions(self)
        else: # special treatment for empty obs object
            for name in obs_dict.keys():
                setattr(self, name, np.append(getattr(self, name), obs_dict[name]))
            self = setDimensions(self)

    def append(self,S):
        field_list = S.getfieldlist()

        if (type(S.time) == np.ndarray ):
            returnarray = True
        else:
            returnarray = False
        for names in field_list:
            if (S.Ndatum > 0):
                self.__dict__[names] = np.append(self.__dict__[names] ,S.__dict__[names])

        self = setDimensions(self)
        if returnarray:
            self.toarray()
        else:
            self.tolist()


    def tolist(self):
        '''
        Convert all variables to list (to enable sorting and deleting entries)
        '''
        field_list = self.getfieldlist()

        field_list.extend(['Nobs','survey_time'])

        for names in field_list:
            if not type(self.__dict__[names]) == list:
                self.__dict__[names] = self.__dict__[names].tolist()
    def toarray(self):
        '''
        Convert all variables to array (to ease calculations)
        '''
        field_list = self.getfieldlist()
        field_list.extend(['Nobs','survey_time'])

        for names in field_list:
            if not type(self.__dict__[names]) == np.ndarray:
                self.__dict__[names]=np.array(self.__dict__[names])


    def writeOBS(self, output, reftime = None, timeunits = None,attributes = None, mode  =  'default', exclude_list = []):
        ''' write OBSstruct to netcdf file
            output - name
            reftime - string  (e.g. 1970-01-01 00:00:00 (set as default))
            timeunits - string (days)

            For global attributes, either a dictionary ({attributename: attributevalue, attributename2: attributevalue2}), or
            a text file containing the desired global attributes may be provided
            An globalatts.txt example:
            author = "annks@met.no"
            state_variables = "\n",
                  "1: free-surface (m) \n",
                  "2: vertically integrated u-momentum component (m/s) \n",
                  "3: vertically integrated v-momentum component (m/s) \n",
                  "4: u-momentum component (m/s) \n",
                  "5: v-momentum component (m/s) \n",
                  "6: potential temperature (Celsius) \n",
                  "7: salinity (nondimensional)" ;

            mode - default behaviour (mode = 'default') is to create an observation file defined variables
                   if mode = 'modfile', additional variables read in from a modfile is written as well.
            exclude_list - list containing names of fields NOT to be written to file, e.g. to save space
                        exclude_list = ['lat', 'lon'] would prevent these variables from being written to file, even if present on the observation object

        '''

        if attributes:
            if type(attributes) == dict:
                self.globalatts = attributes
            else:

                self.provenance_atts = {}
                rem = '";,\n'

                f = open(attributes)
                for line in f:
                    if '=' in line:
                        name = line.split('=')[0].strip()
                        cont = ''.join(x for x in line.split('=')[1].split('\n')[0] if x not in rem).strip()
                    else:
                        cont = ' '.join([cont,''.join(x for x in line if x not in rem).strip()])
                    if name=='flag_values' or name=='flag_meanings':
                       self.provenance_atts[name] = cont
                    else:
                       self.globalatts[name] = cont.replace('\\n','\n')
                f.close()
        if not reftime:
            reftime = '1970-01-01 00:00:00'
        if not timeunits:
            timeunits='days'
        # Create file:
        oncid = Dataset(output,'w',format = 'NETCDF4')

        # Add the global attributes if any:
        oncid.setncatts(self.globalatts)
        # Set dimensions:
        oncid.createDimension('survey',self.Nsurvey)
        if np.isscalar(self.Nstate):
            oncid.createDimension('state_variable',self.Nstate)
            oncid.createDimension('datum',self.Ndatum)
        else:
            print("Nstate is not properly set")
            print("Please add information (e.g. Nstate = 7)")
            print("variance should also be provided, this should be an array of length Nstate")

        var = oncid.createVariable('Nobs','i4',('survey',))
        var.long_name = 'number of observations with the same survey time'
        var[:] = self.Nobs[:]

        var = oncid.createVariable('survey_time','f8',('survey',))
        var.long_name = 'survey time'
        var.units =  timeunits+" since "+reftime+" GMT"
        var.calendar = "gregorian"
        var[:] = self.survey_time[:]

        # Now add the variables:
        if hasattr(self,'spherical') and np.isscalar(self.spherical):
            var = oncid.createVariable('spherical','i4')
            var.long_name = 'grid type logical switch'
            var.flag_values = '0, 1'
            var.flag_meanings = 'Cartesian, spherical'
            var[:] = self.spherical
        else:
            print("No information on grid type (spherical = 0 ,spherical= 1)")
            print("Consider adding this information!")

        if hasattr(self,'variance') and np.any(self.variance):
            var = oncid.createVariable('obs_variance','f4',('state_variable',))
            var.long_name = 'global temporal and spatial observation variance'
            var[:] = self.variance[:]

        ncvars = define_vars_and_attributes()
        try:
            ncvars['provenance']['flag_values'] = self.provenance_atts['flag_values']
            ncvars['provenance']['flag_meanings'] = self.provenance_atts['flag_meanings']
        except:
            print('No provenance attributes available')
            pass
        for var in ['time', 'true_time']:
            ncvars[var]['units'] = timeunits+" since "+reftime+" GMT"


        for variable in ncvars.keys():
            if (ncvars[variable]['mode'] == 'modfile') & (mode != 'modfile') :
                continue
            if hasattr(self, variable):
                if (len(getattr(self, variable)) == self.Ndatum) & (variable not in exclude_list):
                    if not 'varname' in ncvars[variable].keys():
                        ncvars[variable]['varname'] = variable

                    var = oncid.createVariable(ncvars[variable]['varname'],ncvars[variable]['dtype'],('datum',), fill_value = ncvars[variable]['fill_value'])
                    for key in ncvars[variable]:
                        if key not in ['varname', 'fill_value', 'dtype', 'mode']:
                            var.setncattr(key, ncvars[variable][key])
                    var[:] = getattr(self, variable)

                else:
                    if variable in ['time', 'value', 'error', 'Xgrid', 'Ygrid', 'Zgrid', 'depth', 'type', 'provenance', 'meta', 'lon', 'lat']:
                        print('Skipping {}'.format(variable))
        oncid.close()

def define_vars_and_attributes():
    ncattrs = {'type' :
            {'varname' : 'obs_type',
            'dtype' : 'f4',
            'fill_value': None,
            'mode': 'default',
            'long_name' :"model state variable associated with observations",
            'flag_values':  "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20",
            'flag_meanings': "zeta ubar vbar u v temperature salinity dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy radvelocity"},
            'provenance':
            {'varname' : 'obs_provenance',
            'dtype' : 'i4',
            'mode': 'default',
            'fill_value': None,
            'long_name': 'observation origin'},
            'time':
            {'varname' : 'obs_time',
            'long_name': 'time of observation',
            'calendar': 'gregorian',
            'fill_value': None,
            'mode': 'default',
            'dtype' : 'f8'},
            'true_time':
            {'varname' : 'true_time',
            'long_name': 'true time of observation',
            'calendar': 'gregorian',
            'fill_value': 1.e+37,
            'mode': 'default',
            'dtype' : 'f8'},
            'lon':
            {'varname' : 'obs_lon',
            'long_name': 'observation longitude',
            'units': 'degrees_east',
            'fill_value': None,
            'mode': 'default',
            'dtype' : 'f4'},
            'lat':
            {'varname' : 'obs_lat',
            'long_name': 'observation latitude',
            'dtype' : 'f4',
            'fill_value': None,
            'mode': 'default',
            'units': 'degrees_north'},
            'depth':
            {'varname' : 'obs_depth',
            'long_name': 'depth of observation',
            'units': 'meters',
            'dtype' : 'f4',
            'fill_value': None,
            'mode': 'default',
            'negative': 'downwards'},
            'true_depth':
            {'long_name': 'true depth of observation',
            'units': 'meters',
            'dtype' : 'f4',
            'fill_value': 1.e+37,
            'mode': 'default',
            'negative': 'downwards'},
            'Xgrid':
            {'varname' : 'obs_Xgrid',
            'dtype' : 'f4',
            'fill_value': None,
            'mode': 'default',
            'long_name': 'observation fractional x-grid location'},
            'Ygrid':
            {'varname' : 'obs_Ygrid',
            'dtype' : 'f4',
            'fill_value': None,
            'mode': 'default',
            'long_name': 'observation fractional y-grid location'},
            'Zgrid':
            {'varname' : 'obs_Zgrid',
            'long_name': 'observation fractional z-grid location',
            'fill_value': None,
            'mode': 'default',
            'dtype' : 'f4'},
            'error':
            {'varname' : 'obs_error',
            'long_name': 'observation error covariance',
            'fill_value': None,
            'mode': 'default',
            'dtype' : 'f4'},
            'instrumental_error':
            {'long_name': 'observation error covariance from instrument',
            'fill_value': 1.e+37,
            'mode': 'default',
            'dtype' : 'f4'},
            'value':
            {'varname' : 'obs_value',
            'long_name': 'observation value',
            'fill_value': None,
            'mode': 'default',
            'dtype' : 'f4'},
            'meta':
            {'varname' : 'obs_meta',
            'long_name': 'observation meta value',
            'units': 'nondimensional',
            'fill_value': None,
            'mode': 'default',
            'dtype' : 'f4'},
            'scale':
            {'varname' : 'obs_scale',
            'long_name': "observation screening/normalization scale",
            'fill_value': 0,
            'mode': 'modfile',
            'dtype' : 'i4'},
            'NLmodel_value':
            {'long_name': "model at observation locations",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'NLmodel_initial':
            {'long_name': "initial nonlinear model at observation locations",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'BgError_value':
            {'long_name': "Background error at observation locations",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'units': 'nulvar',
            'dtype' : 'f4'},
            'innovation':
            {'long_name': "4D-Var innovation: observation minus background, d_b = y - H(x_b)",
            'units': 'state variable units',
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'increment':
            {'long_name': "4D-Var increment: analysis minus background, dx_a = H(x_a) - H(x_b)",
            'units': 'state variable units',
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'residual':
            {'long_name': "4D-Var residual: observation minus analysis, d_a = y - H(x_b + dx_a)",
            'units': 'state variable units',
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'BgThresh_value':
            {'long_name':"Threshold for background quality control check of observations",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'TLmodel_value':
            {'long_name' :  "tangent linear model at observation locations",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4'},
            'misfit_initial':
            {'long_name':"initial model-observation misfit",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4' },
            'misfit_final':
            {'long_name':"final model-observation misfit",
            'fill_value': 1.e+37,
            'mode': 'modfile',
            'dtype' : 'f4' }

            }


    return ncattrs

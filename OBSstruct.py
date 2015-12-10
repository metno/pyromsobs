# -*- coding: utf-8 -*-
import operator
import numpy as np
from netCDF4 import Dataset
from .helpers import setDimensions
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
    
    def __init__(self, ifile=None):
        if ifile:
            if not isinstance(ifile,OBSstruct):
                # Check if ifile is string, if not we assume it is file id  
                # for netcdf file opened with fid=Dataset('netcdf_file.nc')
                if isinstance(ifile, str):
                    ifile=Dataset(ifile)
                
                # Read info from file
        
                # first the dimensions, must be present on file
                self.Nsurvey = len(ifile.dimensions['survey'])
                self.Nstate  = len(ifile.dimensions['state_variable'])
                self.Ndatum  = len(ifile.dimensions['datum'])
                
                # Now load Nobs and survey_time, must be present on fil
                self.Nobs        = ifile.variables['Nobs'][:]
                self.survey_time = ifile.variables['survey_time'][:]
  
                # some information on the data set, not critical if not present
                try:
                    self.spherical   = ifile.variables['spherical'][0]
                except:
                    print "Variable spherical is not present on input file, consider adding information"
                    print "OBS.spherical = 1 if grid is spherical"
                    print "OBS.spherical = 0 if grid is cartesian"
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
                        self.__dict__[varname] = ifile.variables[obsvars[varname][1]][:]
                    except:
                        pass
                    
                # The global attributes, stored in a dictionary
                self.globalatts={}
                try:
                    for name in ifile.ncattrs():
                        exec('self.globalatts["%s"] = """%s"""' % (name, getattr(ifile,name)))
                except:
                    print "No global attributes on file"
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
                self.globalatts=dict(ifile.globalatts)
        else: 
            # Create an empty OBSstruct
            #first the dimension
            self.Nsurvey = None
            self.Nstate  = None
            self.Ndatum  = None
  
            # some information on the data set
            self.spherical   = None
            self.Nobs        = np.array([])
            self.survey_time = np.array([])
            self.variance    = None

            obsvars = self.allvarnames()
            
            for varname in obsvars:
                self.__dict__[varname] = np.array([])
            # The global attributes, stored in a dictionary
            self.globalatts={}
            
    def allvarnames(self):
        obsvars = {'time' : [1,'obs_time'], 'type' : [2,'obs_type'], 
		           'depth' : [4,'obs_depth'],'Xgrid' : [5,'obs_Xgrid'], 
				   'Ygrid' : [6,'obs_Ygrid'], 'Zgrid' : [7,'obs_Zgrid'],
				   'error' : [8,'obs_error'] , 'value' :[9,'obs_value'], 
				   'lon' : [10,'obs_lon'],'lat' : [11,'obs_lat'] , 
				   'provenance' : [3,'obs_provenance'],'meta' : [12,'obs_meta'], 
				   'true_time' : [13,'obs_true_time'] ,'true_depth' : [14,'obs_true_depth'],
				   'instrumental_error' :[ 15,'instrumental_error']}

        return obsvars
    
     
    def getfieldlist(self):
        field_list = []
        obsvars = sorted(self.allvarnames().items(), key=operator.itemgetter(1))
        for varname in obsvars:
            if (hasattr(self,varname[0]) ):
                field_list.append(varname[0])
        return field_list
    
    def __getitem__(self,index):
        field_list = self.getfieldlist()
        self.toarray()
        S=OBSstruct()
        if isinstance(index, (int, long)):
            index = slice(index, index+1, None)
        for names in field_list:
            if (len(self.__dict__[names])):
                S.__dict__[names]=self.__dict__[names][index]
        S=setDimensions(S)
        if hasattr(self,'spherical'):
            S.spherical=self.spherical
        S.Nstate=self.Nstate
        if hasattr(self,'variance'):
            S.variance=self.variance
        return S
    def put(self,time,lon,lat,depth,otype,value, error = None, provenance = None, Xgrid = None, Ygrid = None, Zgrid = None, meta = None, true_time = None, true_depth = None, instrumental_error = None):
        try:
           if len(time) > 1:
               print 'ERROR message: self.put method is intended for single observation only'
               return
        except:
           self.tolist()
           self.time.append(time)
           self.lon.append(lon)
           self.lat.append(lat)
           self.depth.append(depth)
           self.type.append(otype)
           self.value.append(value)
           if error:
              self.error.append(error)
           else:
              self.error.append(-99999)
           if provenance:
              self.provenance.append(provenance)
           else:
              self.provenance.append(-99999)

           if Xgrid:
              self.Xgrid.append(Xgrid)
           else:
              self.Xgrid.append(-99999)
           if Ygrid:
              self.Ygrid.append(Ygrid)
           else:
              self.Ygrid.append(-99999)
           if Zgrid:
              self.Zgrid.append(Zgrid)
           else:
              self.Zgrid.append(-99999)
           if meta:
              self.meta.append(meta)
           else:
              self.meta.append(-99999)
           if true_time:
              self.true_time.append(true_time)
           else:
              self.true_time.append(-99999)
           if true_depth:
              self.true_depth.append(true_depth)
           else:
              self.true_depth.append(-99999)
           if instrumental_error:
              self.instrumental_error.append(instrumental_error)
           else:
              self.instrumental_error.append(-99999)
           self.toarray()
           self = setDimensions(self)

    def append(self,S):
        field_list = self.getfieldlist()
        
        if (type(S.time) == np.ndarray ):
            returnarray = True
        else:
            returnarray = False
        self.tolist()
        for names in field_list:
            if (S.Ndatum > 0):
                self.__dict__[names].extend(S.__dict__[names])
                
        self=setDimensions(self)
        if returnarray:
            self.toarray()
    
    def tolist(self):
        '''
        Convert all variables to list (to enable sorting and deleting entries)
        '''
        field_list = self.getfieldlist()
        field_list.extend(['Nobs','survey_time'])

        for names in field_list:
            if not type(self.__dict__[names]) == list:
                self.__dict__[names]=self.__dict__[names].tolist()
    def toarray(self):
        '''
        Convert all variables to array (to ease calculations)
        '''
        field_list = self.getfieldlist()
        field_list.extend(['Nobs','survey_time'])

        for names in field_list:
            if not type(self.__dict__[names]) == np.ndarray:
                self.__dict__[names]=np.array(self.__dict__[names])
    
    

    
        
    def writeOBS(self, output, reftime=None, timeunits=None,glbattfile=None):
        ''' write OBSstruct to netcdf file
            default time units is days, default time reference is 1970-01-01 00:00:00
            A text file containing the desired global attributes may be provided
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
        '''
        
        if glbattfile:
        
            rem='";,\n'
            f = open(glbattfile) 
            for line in f:
                if '=' in line:
                    name = line.split('=')[0].strip()
                    cont = ''.join(x for x in line.split('=')[1].split('\n')[0] if x not in rem).strip()
                else:                        
                    cont = ' '.join([cont,''.join(x for x in line if x not in rem).strip()])
                self.globalatts[name] = cont.replace('\\n','\n')
            f.close()
        if not reftime:
            reftime='1970-01-01 00:00:00'
        if not timeunits:
            timeunits='days'
        # Create file:
        oncid = Dataset(output,'w',format='NETCDF3_CLASSIC')
        
        # Add the global attributes if any:
        oncid.setncatts(self.globalatts)
        # Set dimensions:
        oncid.createDimension('survey',self.Nsurvey)
        if np.isscalar(self.Nstate):
            oncid.createDimension('state_variable',self.Nstate)
            oncid.createDimension('datum',self.Ndatum)
        else:
            print "Nstate is not properly set"
            print "Please add information (e.g. Nstate=7)"
            print "variance should also be provided, this should be an array of length Nstate"

        var=oncid.createVariable('Nobs','i4',('survey',))
        var.long_name='number of observations with the same survey time'
        var[:]=self.Nobs[:]  

        var=oncid.createVariable('survey_time','f8',('survey',))
        var.long_name='survey time'
        var.units= timeunits+" since "+reftime+" GMT"
        var.calendar = "gregorian" 
        var[:]=self.survey_time[:]
        
        # Now add the variables:
        if hasattr(self,'spherical') and np.isscalar(self.spherical):             
            var=oncid.createVariable('spherical','i4')
            var.long_name='grid type logical switch'
            var.flag_values='0, 1'
            var.flag_meanings='Cartesian, spherical'
            var[:]=self.spherical
        else:
            print "No information on grid type (spherical = 0 ,spherical= 1)"
            print "Consider adding this information!"
        
        if hasattr(self,'variance') and np.any(self.variance):
            var=oncid.createVariable('obs_variance','f8',('state_variable',))
            var.long_name = 'global temporal and spatial observation variance'
            var[:]=self.variance[:]
            
        if hasattr(self,'type'): 
            if len(self.type) == self.Ndatum:
                var=oncid.createVariable('obs_type','i4',('datum',))
                var.long_name = "model state variable associated with observations" 
                var.flag_values ="1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20"
                var.flag_meanings = "zeta ubar vbar u v temperature salinity dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy radvelocity" 
                var[:]=self.type[:]
            else:
                print 'dimension of type is inconsistent with Ndatum, skipping'
                 
        if hasattr(self,'provenance'): 
            if len(self.provenance) == self.Ndatum:
                var=oncid.createVariable('obs_provenance','i4',('datum',))
                var.long_name = "observation origin" 
                var[:]=self.provenance[:]
            else:
                print 'dimension of provenance is inconsistent with Ndatum, skipping'


        if hasattr(self,'time'): 
            if len(self.time) == self.Ndatum:
                var=oncid.createVariable('obs_time','f8',('datum',))
                var.long_name = "time of observation" 
                var.units =  timeunits+" since "+reftime+" GMT" 
                var.calendar = "gregorian" 
                var[:]=self.time[:]
            else:
                print 'dimension of obs_time is inconsistent with Ndatum, skipping'
         
        if hasattr(self,'true_time'): 
            if len(self.true_time) == self.Ndatum:
                var=oncid.createVariable('obs_true_time','f8',('datum',))
                var.long_name = "true time of observation" 
                var.units =  timeunits+" since "+reftime+" GMT" 
                var.calendar = "gregorian" 
                var[:]=self.true_time[:]
                
        if hasattr(self,'lon'): 
            if len(self.lon) == self.Ndatum:     
                var=oncid.createVariable('obs_lon','f8',('datum',))
                var.long_name='observation longitude'
                var.units='degrees_east'
                var[:]=self.lon[:]
            else:
                print 'dimension of obs_lon is inconsistent with Ndatum, skipping'
         
        if hasattr(self,'lat'): 
            if len(self.lat) == self.Ndatum:     
                var=oncid.createVariable('obs_lat','f8',('datum',))
                var.long_name='observation longitude'
                var.units ='degrees_north'
                var[:]=self.lat[:]
            else:
                print 'dimension of obs_lat is inconsistent with Ndatum, skipping'
         
         
        if hasattr(self,'depth'): 
            if len(self.depth) == self.Ndatum:            
                var=oncid.createVariable('obs_depth','f8',('datum',))
                var.long_name='depth of observation'
                var.units='meters'
                var.negative='downwards'
                var[:]=self.depth
            else:
                print 'dimension of obs_depth is inconsistent with Ndatum, skipping'
                
        if hasattr(self,'true_depth'): 
            if len(self.true_depth) == self.Ndatum:            
                var=oncid.createVariable('obs_true_depth','f8',('datum',))
                var.long_name='true depth of observation'
                var.units='meters'
                var.negative='downwards'
                var[:]=self.true_depth
                
        if hasattr(self,'Xgrid'): 
            if len(self.Xgrid) == self.Ndatum:       
                var=oncid.createVariable('obs_Xgrid','f8',('datum',))
                var.long_name='observation fractional x-grid location'
                var[:]=self.Xgrid[:]
            else:
                print 'dimension of obs_Xgrid is inconsistent with Ndatum, skipping'
        
        if hasattr(self,'Ygrid'): 
            if len(self.Ygrid) == self.Ndatum: 
                var=oncid.createVariable('obs_Ygrid','f8',('datum',))
                var.long_name='observation fractional y-grid location'
                var[:]=self.Ygrid[:]
            else:
                print 'dimension of obs_Ygrid is inconsistent with Ndatum, skipping'
                

        
        if hasattr(self,'Zgrid'): 
            if len(self.Zgrid) == self.Ndatum: 
                var=oncid.createVariable('obs_Zgrid','f8',('datum',))
                var.long_name='observation fractional z-grid location'
                var[:]=self.Zgrid[:]
            else:
                print 'dimension of obs_Zgrid is inconsistent with Ndatum, skipping'
                
        
        
        if hasattr(self,'error'): 
            if len(self.error) == self.Ndatum: 
                var=oncid.createVariable('obs_error','f8',('datum',))
                var.long_name='observation error covariance'
                var[:]=self.error[:]
            else:
                print 'dimension of obs_error is inconsistent with Ndatum, skipping'
               
        if hasattr(self,'instrumental_error'): 
            if len(self.instrumental_error) == self.Ndatum: 
                var=oncid.createVariable('instrumental_error','f8',('datum',))
                var.long_name='observation error covariance from instrument'
                var[:]=self.instrumental_error[:]

        if hasattr(self,'value'): 
            if len(self.value) == self.Ndatum: 
                var=oncid.createVariable('obs_value','f8',('datum',))
                var.long_name='observation value'
                var[:]=self.value[:]
            else:
                print 'dimension of obs_value is inconsistent with Ndatum, skipping'

        if (not hasattr(self,'meta')):
            self.meta=np.zeros_like(self.value).tolist()

        if not list(self.meta):
            self.meta=np.zeros_like(self.value).tolist()

        # Add meta whether it is initialized or not, as radial code requires it
        if not hasattr(self,'meta'): 
            self.meta=np.zeros_like(self.Ndatum)
            
        var=oncid.createVariable('obs_meta','f8',('datum',))
        var.long_name="observation meta value"
        var.units="nondimensional"
        var[:]=self.meta[:]


        oncid.close()

    
        

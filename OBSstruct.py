
import numpy as np
from netCDF4 import Dataset
from .helpers import setDimensions
class OBSstruct(object):
    """ Simple ROMS observation file object
     
    Typical usage: :
    Initializing from existing ROMS observation file

    >>> fid = Dataset(OBSfile)
    >>> OBS = OBSstruct(fid)
   
    Intializing an empty object, e.g. when reading raw observations
    or when super-obing/merging observation objects

    >>>> OBS = OBSstruct()
    
    Copy existing object to new object
    newOBS=OBSstruct(OBS)
   

    """

    def __init__(self, input=None):
        if input:
            if not isinstance(input,OBSstruct):
                # Read info from file
        
                # first the dimension
                self.Nsurvey = len(input.dimensions['survey'])
                self.Nstate  = len(input.dimensions['state_variable'])
                self.Ndatum  = len(input.dimensions['datum'])
  
                # some information on the data set
                self.spherical   = input.variables['spherical'][0]
                self.Nobs        = input.variables['Nobs'][:].tolist()
                self.survey_time = input.variables['survey_time'][:].tolist()

                self.variance    = input.variables['obs_variance'][:].tolist()

                # The observations themselves
                self.type        = input.variables['obs_type'][:].tolist()
                try:
                    self.provenance  = input.variables['obs_provenance'][:].tolist()
                except: 
                     "No provenance data on file"
                    #   self.provenance=None

                self.time        = input.variables['obs_time'][:].tolist()

                try:
                    self.lon         = input.variables['obs_lon'][:].tolist()
                except:
                    print "No longitude data on file"
                #   self.lon=None
                try:
                    self.lat         = input.variables['obs_lat'][:].tolist()
                except:
                    print "No latitude data on file"
                #   self.lat=None

                self.depth       = input.variables['obs_depth'][:].tolist()
                self.Xgrid       = input.variables['obs_Xgrid'][:].tolist()
                self.Ygrid       = input.variables['obs_Ygrid'][:].tolist()
                self.Zgrid       = input.variables['obs_Zgrid'][:].tolist()
                self.error       = input.variables['obs_error'][:].tolist()
                self.value       = input.variables['obs_value'][:].tolist()
                try: 
                    self.meta        = input.variables['obs_meta'][:].tolist()
                except:
                    self.meta=np.zeros_like(self.value).tolist()
                try:
                    self.grid_Lm_Mm_N = getattr(input,'grid_Lm_Mm_N')
                except:
                    pass
                # The global attributes, stored in a dictionary
                self.globalatts={}
 
                for name in input.ncattrs():
                    exec('self.globalatts["%s"] = """%s"""' % (name, getattr(input,name)))
            elif isinstance(input,OBSstruct):
                # Create an empty OBSstruct
                #first the dimension
                self.Nsurvey = np.int(input.Nsurvey)
                self.Nstate  = np.int(input.Nstate)
                self.Ndatum  = np.int(input.Ndatum)
  
                # some information on the data set
                self.spherical   = input.spherical
                self.Nobs        = np.array(input.Nobs)
                self.survey_time = np.array(input.survey_time)
                self.variance    = np.array(input.variance)
                
                # The observations themselves
                self.type        = np.array(input.type)
                if hasattr(input,'provenance'):
                    self.provenance  = np.array(input.provenance)
                self.time        = np.array(input.time)
                if (hasattr(input,'lon') and hasattr(input,'lat')):
                    self.lon         = np.array(input.lon)
                    self.lat         = np.array(input.lat)
                self.depth       = np.array(input.depth)
                self.Xgrid       = np.array(input.Xgrid)
                self.Ygrid       = np.array(input.Ygrid)
                self.Zgrid       = np.array(input.Zgrid)
                self.error       = np.array(input.error)
                self.value       = np.array(input.value)
                if hasattr(input,'meta'):
                    self.meta        = np.array(input.meta)

                # The global attributes, stored in a dictionary
                self.globalatts=input.globalatts
        else: 
            # Create an empty OBSstruct
            #first the dimension
            self.Nsurvey = None
            self.Nstate  = None
            self.Ndatum  = None
  
            # some information on the data set
            self.spherical   = None
            self.Nobs        = []
            self.survey_time = []
            self.variance    = None

            # The observations themselves
            self.type        = []
            self.provenance  = []
            self.time        = []
            self.lon         = []
            self.lat         = []
            self.depth       = []
            self.Xgrid       = []
            self.Ygrid       = []
            self.Zgrid       = []
            self.error       = []
            self.value       = []
            self.meta        = []

            # The global attributes, stored in a dictionary
            self.globalatts={}


    def __getitem__(self,index):
        field_list = self.getfieldlist()
        S=OBSstruct()
        if isinstance(index, (int, long)):
            index = slice(index, index+1, None)
        for names in field_list:
            S.__dict__[names]=self.__dict__[names][index]
            S=setDimensions(S)
            S.spherical=self.spherical
            S.Nstate=self.Nstate
            S.variance=self.variance
        return S
    
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
        Convert all variables to list (to ease calculations)
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
        
    def getfieldlist(self):
        #ield_list = ['time','type','depth','Xgrid','Ygrid','Zgrid','error','value']
        field_list = []
        # Consider that it is possible that the field is an empty list    
        if (hasattr(self,'time')):
            if (list(self.time) and len(self.time)) or len(self.time) :
               field_list.append('time')
            
        if (hasattr(self,'type')):
            if (list(self.type) and len(self.type)) or len(self.type) :            
            #if len(self.type):
               field_list.append('type')
            
        if (hasattr(self,'depth')):
            if (list(self.depth) and len(self.depth)) or len(self.depth) :
            #if len(self.depth):
               field_list.append('depth')
            
        if (hasattr(self,'Xgrid')):
            if (list(self.Xgrid) and len(self.Xgrid)) or len(self.Xgrid) :        
            #if len(self.Xgrid):
               field_list.append('Xgrid')
            
        if (hasattr(self,'Ygrid')):
            if (list(self.Ygrid) and len(self.Ygrid)) or len(self.Ygrid) : 
              
            #if len(self.Ygrid):
               field_list.append('Ygrid')
            
        if (hasattr(self,'Zgrid')):
                           
            if (list(self.Zgrid) and len(self.Zgrid)) or len(self.Zgrid) : 
            #if len(self.Zgrid):
               field_list.append('Zgrid')
            
        if (hasattr(self,'value')):
            if (list(self.value) and len(self.value)) or len(self.value) :             
            #f len(self.value):
               field_list.append('value')
            
        if (hasattr(self,'error')):
            if (list(self.error) and len(self.error)) or len(self.error) :        
                           
            #f len(self.error):
               field_list.append('error')

        if (hasattr(self,'lon') and hasattr(self,'lat')):                     
            if ( ( (list(self.lon) and len(self.lon)) or len(self.lon) ) and ( ( list([self.lat]) and len(self.lon)) or len(self.lon)) ): 
                field_list.extend(['lon','lat'])
            
        if (hasattr(self,'provenance')):
              
            #if len(self.provenance):
            if (list(self.provenance) and len(self.provenance)) or len(self.provenance) :  
               field_list.append('provenance')
            
        if (hasattr(self,'meta')):
            if (list(self.meta) and len(self.meta)) or len(self.meta) :  
                           
            #if len(self.meta):
               field_list.append('meta')
            
        return field_list
    

    def writeOBS(self, output, reftime=None, timeunits=None):
        ''' write OBSstruct to netcdf file
        '''
        self.tolist()
        if not reftime:
           reftime='1970-01-01 00:00:00'
        if not timeunits:
           timeunits='days'
        # Create file:
        oncid = Dataset(output,'w',format='NETCDF3_CLASSIC')
        # Set dimensions:
        oncid.createDimension('survey',self.Nsurvey)
        oncid.createDimension('state_variable',self.Nstate)
        oncid.createDimension('datum',self.Ndatum)

        # Add the global attributes, if any:
        for key in self.globalatts.keys():
            exec('oncid.%s  = """%s"""' %(key, self.globalatts[key]))

        # Now add the variables:
        var=oncid.createVariable('spherical','i4')
        var.long_name='grid type logical switch'
        var.flag_values='0, 1'
        var.flag_meanings='Cartesian, spherical'
        var[:]=self.spherical

        var=oncid.createVariable('Nobs','i4',('survey',))
        var.long_name='number of observations with the same survey time'
        var[:]=self.Nobs[:]  

        var=oncid.createVariable('survey_time','f8',('survey',))
        var.long_name='survey time'
        var.units= timeunits+" since "+reftime+" GMT"
        var.calendar = "gregorian" 
        var[:]=self.survey_time[:]

        var=oncid.createVariable('obs_variance','f8',('state_variable',))
        var.long_name = 'global temporal and spatial observation variance'
        var[:]=self.variance[:]
 
        var=oncid.createVariable('obs_type','i4',('datum',))
        var.long_name = "model state variable associated with observations" 
        var.flag_values ="1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20"
        var.flag_meanings = "zeta ubar vbar u v temperature salinity dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy dummy radvelocity" 
        var[:]=self.type[:]

        if self.provenance is not None:
            var=oncid.createVariable('obs_provenance','i4',('datum',))
            var.long_name = "observation origin" 
            var.flag_values ="1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 13 14 20"
            var.flag_meanings = """
2   CODAR u (rotated to grid), MET
3:  CODAR v (rotated to grid), MET
4:  CTD temperature from IMR
5:  CTD salinity from IMR
6:  Thermosalinograph temperature from IMR
7:  Thermosalinograph salinity from IMR
8:  OSI-SAF SST (1.5km res) from metop02 
9:  OSI-SAF SST (1.5km res) from noaa18 
10: OSI-SAF SST (1.5km res) from noaa19
11: InSitu temperature from MyOcean
12: InSitu salinity from MyOcean
13: InSitu temperature from the Hadley Centre
14: InSitu salinity from the Hadley Centre
20: CODAR radial current"""
            var[:]=self.provenance[:]


        var=oncid.createVariable('obs_time','f8',('datum',))
        var.long_name = "time of observation" 
        var.units =  timeunits+" since "+reftime+" GMT" 
        var.calendar = "gregorian" 
        var[:]=self.time[:]

        if self.lon is not None:
            var=oncid.createVariable('obs_lon','f8',('datum',))
            var.long_name='observation longitude'
            var.units='degrees_east'
            var[:]=self.lon[:]
    
        if self.lat is not None:
            var=oncid.createVariable('obs_lat','f8',('datum',))
            var.long_name='observation longitude'
            var.units ='degrees_north'
            var[:]=self.lat[:]
        
        var=oncid.createVariable('obs_depth','f8',('datum',))
        var.long_name='depth of observation'
        var.units='meters'
        var.negative='downwards'
        var[:]=self.depth

        var=oncid.createVariable('obs_Xgrid','f8',('datum',))
        var.long_name='observation fractional x-grid location'
        var[:]=self.Xgrid[:]

        var=oncid.createVariable('obs_Ygrid','f8',('datum',))
        var.long_name='observation fractional y-grid location'
        var[:]=self.Ygrid[:]

        var=oncid.createVariable('obs_Zgrid','f8',('datum',))
        var.long_name='observation fractional z-grid location'
        var[:]=self.Zgrid[:]

        var=oncid.createVariable('obs_error','f8',('datum',))
        var.long_name='observation error covariance'
        var[:]=self.error[:]

        var=oncid.createVariable('obs_value','f8',('datum',))
        var.long_name='observation value'
        var[:]=self.value[:]

        if (not hasattr(self,'meta')):
            self.meta=np.zeros_like(self.value).tolist()

        if not list(self.meta):
            self.meta=np.zeros_like(self.value).tolist()

        var=oncid.createVariable('obs_meta','f8',('datum',))
        var.long_name="observation meta value"
        var.units="nondimensional"
        var[:]=self.meta[:]


        oncid.close()

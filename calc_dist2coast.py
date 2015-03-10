import pickle
import netCDF4
import numpy as np    
import pyproj as proj

coor='v'
gridfile='/disk1/NOFO/Grid/nofo_crit30.nc'
gridfile='/disk1/cascade/wc12.0/wc12.0_coamps_woa_gls_v563_tave24_combo_01/20121022_20121028_is4dvar/ncfiles/wc12_grd.nc.0'
gfh= netCDF4.Dataset(gridfile,'r+',format='NETCDF3_CLASSIC')
g=proj.Geod("+proj=latlong +ellps=WGS84") 
if (coor == 'r'):
   lon=gfh.variables['lon_rho'][:,:]
   lat=gfh.variables['lat_rho'][:,:]
elif (coor == 'u'):
   lon=gfh.variables['lon_u'][:,:]
   lat=gfh.variables['lat_u'][:,:]
elif (coor == 'v'):
   lon=gfh.variables['lon_v'][:,:]
   lat=gfh.variables['lat_v'][:,:]


lon[np.where(lon>180.)]=lon[np.where(lon>180.)]-360.
ny,nx=lon.shape
dist = np.ones_like(lon)*-999999


data=pickle.load(open('wc12_dist2coast.dat'))
clon=data['lon']
clat=data['lat']
cdist=data['dist']


dum,dum,distance=g.inv(clon,clat,np.ones_like(clon)*lon[0,0],np.ones_like(clon)*lat[0,0])
print np.min(distance), np.max(distance), len(distance)
print distance[np.argmin(distance)]
print lon[0,0],lat[0,0]
print clon[np.argmin(distance)],clat[np.argmin(distance)],cdist[np.argmin(distance)]

for i in range(0,nx):
   for j in range(0,ny):
       dum,dum,distance=g.inv(clon,clat,np.ones_like(clon)*lon[j,i],np.ones_like(clon)*lat[j,i])
       dist[j,i] = cdist[np.argmin(distance)]

# create netcdf file:
oncid=netCDF4.Dataset('wc12_dist2coast.nc','w',format='NETCDF3_CLASSIC')
oncid.createDimension('ny',ny)
oncid.createDimension('nx',nx)
var=oncid.createVariable('dist2coast','f8',('ny' ,'nx',))
var[:,:]=dist[:,:]

oncid.close()

import matplotlib.pyplot as plt

plt.contourf(dist)
plt.show()
'''
j=0; i=0


dlat=np.abs(clat-lat[j,i])
latind=np.argmin(dlat)
dlon=np.abs(clon[latind]-lon[j,i])
lonind=np.argmin(dlon)
print latind

#print latind[lonind]
print lat[0,0], lon[0,0]
print clat[latind], clon[latind], cdist[latind]

#print clat[latind[lonind]], clon[latind[lonind]], cdist[latind[lonind]]
'''

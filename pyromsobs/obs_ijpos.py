import netCDF4
import pyproj as proj
#from matplotlib.mlab import griddata
from scipy.interpolate import griddata
import numpy as np
import scipy
import cartopy.crs as ccrs
from shapely.geometry import Polygon, Point

def obs_ijpos(gridfile,lons,lats,coor):
    """
    Finds fractional gridpoint locations of observation in a ROMS grid
    """

    gfh= netCDF4.Dataset(gridfile)
    cartesian=0
    if (coor=='r'):
        try:
            
            latr=gfh.variables['lat_rho'][:,:]
            lonr=gfh.variables['lon_rho'][:,:]
        except:
            latr=gfh.variables['latitude'][:,:]
            lonr=gfh.variables['longitude'][:,:]
            

        try:
            xr=gfh.variables['xi_rho'][:]
            yr=gfh.variables['eta_rho'][:]
        except:
            try:
                xr=gfh.variables['x_rho'][:]
                yr=gfh.variables['y_rho'][:]
            except:
                print('Neither xi_rho/eta_rho or x_rho/y_rho on file.')
                print('This might slow down the calculations')


    elif (coor=='u'):
        latr=gfh.variables['lat_u'][:,:]
        lonr=gfh.variables['lon_u'][:,:]
        try:
            xr=gfh.variables['xi_u'][:]
            yr=gfh.variables['eta_u'][:]
        except:
            xr=gfh.variables['x_u'][:]
            yr=gfh.variables['y_u'][:]
    elif (coor=='v'):
        latr=gfh.variables['lat_v'][:,:]
        lonr=gfh.variables['lon_v'][:,:]
        try:
            xr=gfh.variables['xi_v'][:]
            yr=gfh.variables['eta_v'][:]
        except:
            xr=gfh.variables['x_v'][:]
            yr=gfh.variables['y_v'][:]

    IN = point_in_polygon(lonr, latr, lons, lats)
    ind=np.where(IN)[0]
    
    if lats.size >1: 
        lons=lons[ind]; lats=lats[ind]
    try:
        try:
            mapstr=str(gfh.variables['h'].getncattr('mapping'))
        except:
            try:
                mapstr=str(gfh.variables['h'].getncattr('grid_mapping'))
            except:
                pass
        try:
            projstring=(gfh.variables[mapstr]).getncattr('proj4')
        except:
            try:
                projstring=(gfh.variables[mapstr]).getncattr('proj4string')
            except:
                pass
        try:
            projstring=(gfh.variables['grid_mapping']).getncattr('proj4')
        except:
            try:
                projstring=(gfh.variables['grid_mapping']).getncattr('proj4string')
            except:
                pass

        gridproj=proj.Proj(str(projstring))
        hasproj=1
    except:
        hasproj=0

        # Check if lat, lon spacing is uniform
        dx1=np.abs(lonr[0,1]-lonr[0,0])
        dx2=np.abs(lonr[0,-1]-lonr[0,-2])
        n=int(np.round(lonr.shape[1]/2))
        dx3=np.abs(lonr[0,n]-lonr[0,n-1])

        dy1=np.abs(latr[1,0]-latr[0,0])
        dy2=np.abs(latr[-1,0]-latr[-2,0])
        n=int(np.round(latr.shape[0]/2))
        dy3=np.abs(latr[n,0]-latr[n-1,0])

        if ( (dx1 == dx2) & (dx1==dx3) & (dx2==dx3) & (dy1 == dy2) & (dy1==dy3) & (dy2==dy3) ):
            cartesian=1
            gridproj=proj.Proj("+proj=latlong +datum=WGS84")
   

    
    if hasproj:
        dx=xr[1]-xr[0]
        dy=yr[1]-yr[0]
        [x,y]=gridproj(lons,lats)
        ipos=(x-xr[0])/dx
        jpos=(y-yr[0])/dy

    elif cartesian:
        [x1,y1]=gridproj(lonr[0,0],latr[0,0])
        [x2,y2]=gridproj(lonr[0,1],latr[0,1])
        dx=x2-x1
        [x2,y2]=gridproj(lonr[1,0],latr[1,0])
        dy=y2-y1
        [x,y]=gridproj(lons,lats)
        [x0,y0]=gridproj(lonr[0,0],latr[0,0])

        ipos=(x-x0)/dx
        jpos=(y-y0)/dy

    else:
        x=np.linspace(0,lonr.shape[1]-1,lonr.shape[1])
        y=np.linspace(0,lonr.shape[0]-1,lonr.shape[0])
        xi=np.zeros_like(lonr); yi=np.zeros([lonr.shape[1],lonr.shape[0]])
        xi[:,:]=x; yi[:,:]=y; yi=np.swapaxes(yi,1,0)
        zi=scipy.interpolate.griddata((lonr.flatten(),latr.flatten()),xi.flatten(),(lons,lats))
        ipos=zi
        zi=scipy.interpolate.griddata((lonr.flatten(),latr.flatten()),yi.flatten(),(lons,lats))
        jpos=zi
        
    if 'ind' in locals():
        oipos=np.ones(IN.shape)*-999.; ojpos=np.ones(IN.shape)*-999.
        oipos[ind]=ipos; ojpos[ind]=jpos
    else:
        oipos=ipos
        ojpos=jpos
        if not IN:
            oipos = np.array([-999.])
            ojpos = np.array([-999.])
    gfh.close()
    return oipos,ojpos

def xy_from_lonlat(proj, lon, lat):
    try:
        test = len(lon)
    except:
        lon = np.array([lon])
        lat = np.array([lat])
    transform = proj.transform_points(ccrs.PlateCarree(), lon, lat)
    x = transform[..., 0]
    y = transform[..., 1]
    return x[0], y[0]

def polygon_from_lonlat(lon, lat, proj= ccrs.LambertConformal(central_longitude = 0, central_latitude = 0, false_easting = 0.0, false_northing = 0.0)):
    coordinates = []
    geocoordinates = []
    l, m = lon.shape
    for i in range(0, l, int(l/10)):
        j = 0
        x, y = xy_from_lonlat(proj, lon[i,j], lat[i,j])
        coordinates.append([x,y])
        geocoordinates.append([lon[i,j], lat[i,j]])
    for j in range(0, m, int(m/10)):
        i = -1
        x, y = xy_from_lonlat(proj, lon[i,j], lat[i,j])
        coordinates.append([x,y])
        geocoordinates.append([lon[i,j], lat[i,j]])
    for i in range(l-1, 0, -int(l/10)):
        j = -1
        if i >= 0:
            x, y = xy_from_lonlat(proj, lon[i,j], lat[i,j])
            coordinates.append([x,y])
            geocoordinates.append([lon[i,j], lat[i,j]])
    for j in range(m-1, 0-int(m/10), -int(m/10)):
        i = 0
        if j >= 0:
            x, y = xy_from_lonlat(proj, lon[i,j], lat[i,j])
            coordinates.append([x,y])
            geocoordinates.append([lon[i,j], lat[i,j]])
    return Polygon(coordinates), Polygon(geocoordinates)

def point_in_polygon(mlon, mlat, olon, olat, proj = ccrs.LambertConformal(central_longitude = 0, central_latitude = 0, false_easting = 0.0, false_northing = 0.0)):
    poly, geopoly = polygon_from_lonlat(mlon, mlat , proj )
    IN = np.zeros_like(olat, dtype = object)

    for n in range(0, olat.size):
        IN[n] = poly.contains(Point(xy_from_lonlat(proj, olon[n], olat[n])))
    return IN
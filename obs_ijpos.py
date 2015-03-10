import netCDF4
import pyproj as proj
#from matplotlib.mlab import griddata
from scipy.interpolate import griddata
import numpy as np
import scipy
def obs_ijpos(gridfile,lons,lats,coor):
   """
   Finds fractional gridpoint locations of observation in a ROMS grid
   """

   gfh= netCDF4.Dataset(gridfile,'r',format='NETCDF3_CLASSIC')
   cartesian=0
   if (coor=='r'):
      latr=gfh.variables['lat_rho'][:,:]
      lonr=gfh.variables['lon_rho'][:,:]

      try:
        xr=gfh.variables['xi_rho'][:]
        yr=gfh.variables['eta_rho'][:]
      except:
        try:
           xr=gfh.variables['x_rho'][:]
           yr=gfh.variables['y_rho'][:]
        except:
           print 'Neither xi_rho/eta_rho or x_rho/y_rho on file.'
           print 'This might slow down the calculations'

      
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

   # Check if observations fall within polygon spanned by gridcorners
   #poly=[(lonr[0,0],latr[0,0]), (lonr[-1,0],latr[-1,0]),(lonr[-1,-1],latr[-1,-1]),(lonr[0,-1],latr[0,-1]),]
   #poly=[(lonr[0,0],latr[0,0]), (lonr[-1,0],latr[-1,0]),(lonr[-1,-1],latr[-1,-1]),(lonr[0,-1],latr[0,-1]),]
   edge=[]
   first=np.array([(lonr[:-1,0],latr[:-1,0])]).squeeze()
   second=np.array([(lonr[-1,:-1],latr[-1,:-1])]).squeeze()
   third=np.fliplr(np.array([(lonr[1:,-1],latr[1:,-1])]).squeeze())
   fourth=np.fliplr(np.array([(lonr[0,1:],latr[0,1:])]).squeeze())
   
   N=range(0,first.shape[1],10)
   N.append(first.shape[1]-1)
   for n in N:
        edge.append(tuple(first[:,n]))
        
   N=range(0,second.shape[1],10)
   N.append(second.shape[1]-1)

   for n in N:
        edge.append(tuple(second[:,n])) 
        
   N=range(0,third.shape[1],10)
   N.append(third.shape[1]-1)

   for n in N:
        edge.append(tuple(third[:,n]))
         
   N=range(0,fourth.shape[1],10)
   N.append(fourth.shape[1]-1)

   for n in N:
        edge.append(tuple(fourth[:,n]))

   poly=edge   

   if (lats.size>1):
      IN=np.zeros_like(lats)
      for n in range(0,lats.size):
         IN[n]=pip(lons[n],lats[n],poly)
      ind=np.where(IN)[0]
      lons=lons[ind]; lats=lats[ind]
   else:
       IN=pip(lons,lats,poly)

   #if (np.sum(IN>0):    
   # read the proj4 string from the netcdf file, it is used in all
   # necessary calculations
   
   try:
      mapstr=str(gfh.variables['h'].getncattr('mapping'))
      projstring=(gfh.variables[mapstr]).getncattr('proj4')
      gridproj=proj.Proj(str(projstring))
      hasproj=1
   except:
      hasproj=0

      # Check if lat, lon spacing is uniform
      dx1=np.abs(lonr[0,1]-lonr[0,0])
      dx2=np.abs(lonr[0,-1]-lonr[0,-2])
      n=np.round(lonr.shape[1]/2)
      dx3=np.abs(lonr[0,n]-lonr[0,n-1])

      dy1=np.abs(latr[1,0]-latr[0,0])
      dy2=np.abs(latr[-1,0]-latr[-2,0])
      n=np.round(latr.shape[0]/2)
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
      #dx=xr[0,3]-xr[0,2]
      #dy=yr[3,0]-yr[2,0]
      [x1,y1]=gridproj(lonr[0,0],latr[0,0])
      [x2,y2]=gridproj(lonr[0,1],latr[0,1])
      dx=x2-x1
      [x2,y2]=gridproj(lonr[1,0],latr[1,0])
      dy=y2-y1
      [x,y]=gridproj(lons,lats)
      [x0,y0]=gridproj(lonr[0,0],latr[0,0])
      #ipos=(x-xr[0,0])/dx
      #jpos=(y-yr[0,0])/dy

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
   return oipos,ojpos
'''
def pip(x,y,poly):
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

'''
def pip(x,y,poly):
   #print len(poly)
   # check if point is a vertex
   if (x,y) in poly: return True

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[-1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return True
												         
   n = len(poly)
   inside = False
   p1x,p1y = poly[0]
   for i in range(n+1):
       p2x,p2y = poly[i % n]
       if y > min(p1y,p2y):
          if y <= max(p1y,p2y):
             if x <= max(p1x,p2x):
                
               
                if p1y != p2y:
                    xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if not ( (x - p1x)*(p2y-p1y) >= (y-p1y)*(p2x-p1x)) :
                        inside=False
                        break
                   

                if  (p1x == p2x or x < xints):
                   inside = True
                
                
       p1x,p1y = p2x,p2y
   return inside





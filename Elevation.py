from mpl_toolkits.mplot3d import Axes3D
import requests
import json
import stateplane
import pyproj

#MSDN ELevation
def getElevation(lat1, long1, lat2, long2, rows, cols, heights):
    url = "http://dev.virtualearth.net/REST/v1/Elevation/Bounds?bounds={},{},{},{}&rows={}&cols={}&heights={}&key=ArQtm6kQdSgBJtGk63wfJiu7iR7lVwUzBeoXH6dlipaiGc-KNGLsnRpWNUwVbtqa".format(lat1, long1, lat2, long2, rows, cols, heights)
    r = requests.get(url)
    elevations = r.json()['resourceSets'][0]['resources'][0]['elevations']
    print(elevations[0])
    
    stateplaneTest = stateplane.to_latlon('2006327.03559019', '6231343.12187421', epsg='2230')
    
    state_plane = pyproj.Proj(init='EPSG:2230', preserve_units=True)
    wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84')
    lng, lat = pyproj.transform(state_plane, wgs, 6231343.12187421, 2006327.03559019)
    x, y = pyproj.transform(wgs, state_plane, -117.3294706444691, 33.16762412672104)
    
    print(x)
    print(y)
    
getElevation(33.074064, -117.207794, 33.074657, -117.206784, 5, 6, "sealevel")

#2500 per day
#def getElevation(lat, long):
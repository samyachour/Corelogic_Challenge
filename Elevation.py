from mpl_toolkits.mplot3d import Axes3D
import requests
import json
import stateplane
import pyproj
from matplotlib import cm
import matplotlib.pyplot as plt

def convertSPLL(x, y):
    state_plane = pyproj.Proj(init='EPSG:2230', preserve_units=True)
    wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84')
    lng, lat = pyproj.transform(state_plane, wgs, x, y)
    return lat, lng
    
def convertLLSP(lat, long):
    state_plane = pyproj.Proj(init='EPSG:2230', preserve_units=True)
    wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84')
    x, y = pyproj.transform(wgs, state_plane, long, lat)
    return x, y
    
#test = convertSPLL(6231343.12187421, 2006327.035590041)
#test = convertLLSP(33.167624126720625, -117.3294706444691)
#print(test)

googleBox = [(33.074657, -117.207794, 148.2841796875), (33.074657, -117.207794, 148.2841796875), (33.074657, -117.20799600000001, 147.4058227539062), (33.074657, -117.20819800000001, 147.7142791748047), (33.074657, -117.20840000000001, 146.1806335449219), (33.074657, -117.20860200000001, 142.0865325927734), (33.0745384, -117.207794, 147.398681640625), (33.0745384, -117.20799600000001, 146.9870300292969), (33.0745384, -117.20819800000001, 146.7901611328125), (33.0745384, -117.20840000000001, 145.4457702636719), (33.0745384, -117.20860200000001, 141.5194244384766), (33.0744198, -117.207794, 146.5807495117188), (33.0744198, -117.20799600000001, 146.2197875976562), (33.0744198, -117.20819800000001, 144.9052124023438), (33.0744198, -117.20840000000001, 143.4487609863281), (33.0744198, -117.20860200000001, 140.8649291992188), (33.0743012, -117.207794, 145.7697448730469), (33.0743012, -117.20799600000001, 144.6278228759766), (33.0743012, -117.20819800000001, 143.2326507568359), (33.0743012, -117.20840000000001, 142.426025390625), (33.0743012, -117.20860200000001, 141.0009155273438), (33.0741826, -117.207794, 144.79541015625), (33.0741826, -117.20799600000001, 143.2988433837891), (33.0741826, -117.20819800000001, 143.0630035400391), (33.0741826, -117.20840000000001, 142.8155212402344), (33.0741826, -117.20860200000001, 141.0392150878906)]
MSDNBox = [(33.074657, -117.207794, 150), (33.074657, -117.207794, 150), (33.074657, -117.20799600000001, 148), (33.074657, -117.20819800000001, 147), (33.074657, -117.20840000000001, 145), (33.074657, -117.20860200000001, 142), (33.0745384, -117.207794, 149), (33.0745384, -117.20799600000001, 148), (33.0745384, -117.20819800000001, 146), (33.0745384, -117.20840000000001, 145), (33.0745384, -117.20860200000001, 142), (33.0744198, -117.207794, 149), (33.0744198, -117.20799600000001, 147), (33.0744198, -117.20819800000001, 146), (33.0744198, -117.20840000000001, 144), (33.0744198, -117.20860200000001, 142), (33.0743012, -117.207794, 148), (33.0743012, -117.20799600000001, 147), (33.0743012, -117.20819800000001, 145), (33.0743012, -117.20840000000001, 144), (33.0743012, -117.20860200000001, 142), (33.0741826, -117.207794, 148), (33.0741826, -117.20799600000001, 146), (33.0741826, -117.20819800000001, 145), (33.0741826, -117.20840000000001, 143), (33.0741826, -117.20860200000001, 141)]

def Plot3DTriSurf(points):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x = []
    y = []
    z = []
    
    for coord in points:
        x.append(coord[0])
        y.append(coord[1])
        z.append(coord[2] * 3)
        
        
    ax.plot_trisurf(x, y, z, linewidth=0.2)
    plt.show()
    
#Plot3DTriSurf(googleBox)
    
def Plot3DScatter(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for coord in points:
        ax.scatter(coord[0], coord[1], coord[2])
        
    plt.show()

Plot3DScatter(googleBox)

def Plot3DScatterSP(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for coord in points:
        ax.scatter(convertLLSP(coord[0], coord[1])[0], convertLLSP(coord[0], coord[1])[1], coord[2])
        
    plt.show()
    
Plot3DScatterSP(googleBox)

#MSDN ELevation

def getElevationMSDN(lat, long):
    url = "http://dev.virtualearth.net/REST/v1/Elevation/List?points={},{}&heights=sealevel&key=ArQtm6kQdSgBJtGk63wfJiu7iR7lVwUzBeoXH6dlipaiGc-KNGLsnRpWNUwVbtqa".format(lat, long)
    r = requests.get(url)
    elevation = r.json()['resourceSets'][0]['resources'][0]['elevations'][0]
    return elevation
    
#getElevationMSDN(33.074065, -117.207147)

def getElevationMSDNBox(lat1, long1, lat2, long2, rows, cols):
    url = "http://dev.virtualearth.net/REST/v1/Elevation/Bounds?bounds={},{},{},{}&rows={}&cols={}&heights=sealevel&key=ArQtm6kQdSgBJtGk63wfJiu7iR7lVwUzBeoXH6dlipaiGc-KNGLsnRpWNUwVbtqa".format(lat1, long1, lat2, long2, rows, cols)
    r = requests.get(url)
    elevations = r.json()['resourceSets'][0]['resources'][0]['elevations']
    return elevations
    
#getElevationMSDNBox(33.074064, -117.207794, 33.074657, -117.206784, 5, 6)

def getElevationMSDNBoxManual(lat1, long1, lat2, long2, rows, cols):
    incrementX = (lat1-lat2)/cols
    incrementY = abs((long1-long2)/rows)
    
    x = lat1
    y = long1
    
    points = [(x, y, getElevationMSDN(x, y))]
              
    for i in range(rows):
        for j in range(cols):
            points.append((x, y, getElevationMSDN(x, y)))
            y = y - incrementY
        
        x = x - incrementX
        y = long1
    
    Plot3DScatter(points)

#getElevationMSDNBoxManual(33.074657, -117.207794, 33.074064, -117.206784, 15, 15)

#2500 per day
def getElevationGoogle(lat, long):
    url = "https://maps.googleapis.com/maps/api/elevation/json?locations={},{}&key=AIzaSyAJjZHwOgecHkrJ3d13FytDWHCQCTYvaM8".format(lat, long)
    r = requests.get(url)
    elevation = r.json()['results'][0]['elevation']
    return elevation
    
#getElevationGoogle(33.074065, -117.207147)

def getElevationGoogleBox(lat1, long1, lat2, long2, rows, cols):
    incrementX = (lat1-lat2)/cols
    incrementY = abs((long1-long2)/rows)
    
    x = lat1
    y = long1
    
    points = [(x, y, getElevationGoogle(x, y))]
              
    for i in range(rows):
        for j in range(cols):
            points.append((x, y, getElevationGoogle(x, y)))
            y = y - incrementY
        
        x = x - incrementX
        y = long1
    
    Plot3DScatter(points)
    
#getElevationGoogleBox(33.074657, -117.207794, 33.074064, -117.206784, 10, 10)
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
import pandas as pd

from figures import BLUE, BLACK, SIZE, plot_coords, color_isvalid
import gather

from shapely.geometry import Polygon, LineString, Point
from scipy import spatial
import numpy as np

from matplotlib import cm
from matplotlib.ticker import MaxNLocator
import mpl_toolkits.mplot3d.art3d as art3d
    
def getRatios(data):
    
    ratios = []
    totalBB = 0
    
    for index, row in data.iterrows():
        totalVal = row['Value'][0]
        landVal = row['Value'][1]
        observedFt = row['SqFtDelta'][0]
        expectedFt = row['SqFtDelta'][1]
        
        if expectedFt != 0 and len(row['House']) == 1:
            valRatio = (totalVal-landVal)/expectedFt
        else:
            valRatio = (totalVal-landVal)/observedFt    
        ftRatio = expectedFt/observedFt
        ratio = (ftRatio, valRatio, row['Bed/Bath'][0] + row['Bed/Bath'][1])
        ratios.append(ratio)
        
        totalBB += ratio[2]
        
    data['Ratios'] = pd.Series(ratios).values
    return (data, totalBB/data.shape[0])

def getFloors(data):
    
    data, avgBB = getRatios(data)
    #print(avgBB)
    floors = []    
    
    for index, row in data.iterrows():
        
        if type(row['Floors']) != float:
            floorNum = int(row['Floors'])
            if floorNum == 3:
                floorNum = 2
            floors.append(floorNum)
            continue
        
        elif row['Ratios'][2] >= 10:
            floors.append(2)
            continue
        
        elif row['Ratios'][1] < 0:
            floors.append(1)
            continue
        
        elif row['Ratios'][1] >= 250 and row['Ratios'][2] > avgBB:
            floors.append(2)
            continue
        
        elif row['Ratios'][0] >= 1 and row['Ratios'][1] >= 97:
            floors.append(2)
            continue
        
        elif (row['Ratios'][0] >= 1 or row['Ratios'][1] >= 100) and row['Ratios'][2] > avgBB:
            floors.append(2)
            continue
        
        elif row['Ratios'][0] >= 0.80 and row['Ratios'][1] >= 80 and row['Ratios'][2] > avgBB:
            floors.append(2)
            continue
        
        else:
            floors.append(1)
    
    data['Floors'] = pd.Series(floors).values
    return data


'''
I need to get all the polygons for parcels and houses. CHECK
Find the centroid. CHECK
FInd the nearest elevation point and use that as the z. CHECK
Convert all the polygons to patches and plot all the patches with the elevations CHECK
'''

def getHousePatches(surrHouses):
    #House Polygons
    
    housePolys = []
    for index, row in surrHouses.iterrows():
        shapes = row['House']
        centroids = []
        centroid = 0
        
        if len(shapes) > 2:
            for shape in shapes:
                centroid = shape.centroid
                centroids.append((centroid.x, centroid.y))
            centroid = Polygon(centroids).centroid
        
        elif len(shapes) > 1:
            centroid = LineString([(shapes[0].centroid.x, shapes[0].centroid.y), (shapes[1].centroid.x, shapes[1].centroid.y)]).centroid
            
        else:
            centroid = shapes[0].centroid
        
        housePolys.append([shapes, (centroid.x, centroid.y), row['Floors']])
    
    #print(housePolys)
    #print(surrElevation)
    
    chosenPoint = (0,0)
    idx = 0
    heights = []
    chosen = []
    for house in housePolys:
        houseHeight = 0
        if house[2] == 1:
            houseHeight = 15
        if house[2] == 2:
            houseHeight = 23
        
        for elevPoint in surrElevation:
            if (abs(elevPoint[0] - house[1][0]) + abs(elevPoint[1] - house[1][1])) < (abs(chosenPoint[0] - house[1][0]) + abs(chosenPoint[1] - house[1][1])):
                chosenPoint = (elevPoint[0], elevPoint[1])
                housePolys[idx] = [house[0], house[1], elevPoint[2] + houseHeight]
                if surrHouses['Chosen'].iloc[idx]: chosen = [elevPoint[2], house[2]]
        
        heights.append(housePolys[idx][2])
        chosenPoint = (0,0)
        idx += 1
    
    surrHouses['Heights'] = pd.Series(heights).values
    
    #print(housePolys)
    idx = 0
    max = 0
    for house in housePolys:
        if house[2] > max:
            max = house[2]
        
        
        patches = []
        for i in house[0]:
            # I took out the valid shape checker, to put back ie facecolor=color_isvalid(shape)
            if surrHouses['Chosen'].iloc[idx]:
                patch = PolygonPatch(i, facecolor=BLACK, edgecolor=BLACK, zorder=2)
                chosen.append(surrHouses['House'].iloc[idx]) 
                chosen.append(surrHouses['Parcel'].iloc[idx])
            else:
                patch = PolygonPatch(i, facecolor=BLUE, edgecolor=BLUE, zorder=2)
            patches.append(patch)
        
        housePolys[idx] = [patches, house[2]]
            
        idx += 1
    
    return (housePolys, max, surrHouses, chosen)

def elevationSurfaceDelta(point, surfacePts):        
        
        surfacePts2D = []
        point2D = (point[0], point[1])
        
        for i in surfacePts:
            surfacePts2D.append((i[0], i[1]))
            
        distances, indices = spatial.KDTree(surfacePts2D).query(point2D, k=3)
        
        p1 = np.array(surfacePts[indices[0]])
        p2 = np.array(surfacePts[indices[1]])
        p3 = np.array(surfacePts[indices[2]])
        
        v1 = p3 - p1
        v2 = p2 - p1
        
        # the cross product is a vector normal to the plane
        cp = np.cross(v1, v2)
        a, b, c = cp
        
        # This evaluates a * x3 + b * y3 + c * z3 which equals d
        d = np.dot(cp, p3)
        
        Z = (d - a * point[0] - b * point[1]) / c
        
        '''
        fig = plt.figure()
        ax = fig.add_subplot(212, projection='3d')
        
        ax.scatter(point[0], point[1], point[2])
        ax.scatter(p1[0], p1[1], p1[2])
        ax.scatter(p2[0], p2[1], p2[2])
        ax.scatter(p3[0], p3[1], p3[2])
            
        plt.show()
        '''
        
        if not Polygon([(p1[0], p1[1]), (p2[0], p2[1]), (p3[0], p3[1])]).contains(Point(point2D)):
            return None
        
        
        
        return Z - point[2]
   
def houseRoofDelta(point, housesDF):
            
        point2D = Point(point[0], point[1])
        
        for index, row in housesDF.iterrows():
            for i in row['House']:
                if i.contains(point2D):
                    #return delta, positive for roof above, negative for roof below
                    return row['Heights'] - point[2]
        
        return None    


surrHouses, surrElevation = gather.getData(0) # Numbers index - 2, 0,2,9
#plot.plotData2D(surrHouses)
surrHouses = getFloors(surrHouses)  
#surrHouses.to_csv('out.csv', index=False)
patches = getHousePatches(surrHouses)
surrHouses = patches[2]
#plot.Plot3DSurfaceWithPatches(surrElevation, patches[0], patches[1])

#print(elevationSurfaceDelta((6254423.823571282, 1899007.0645571742, 353.18389024367815), surrElevation))
#print(elevationSurfaceDelta((6254373.823571282, 1899057.0645571742, 353.18389024367815), surrElevation))

chosenHouseNParcel = patches[3]

surfacePts2D = []
for i in surrElevation:
    surfacePts2D.append((i[0], i[1]))
topRightElev = list(map(max, zip(*surfacePts2D)))
bottomLeftElev = list(map(min, zip(*surfacePts2D)))


def getSlopes(point_):
    pointX = point_[0]
    pointY = point_[1]
    deltas = []
    
    plotLine = []
    
    slopes = [0, 0.25, 1, 2, 3.5, 5.5,-0.25, -1, -2, -3.5, -5.5]
    
    for i in slopes:
        
        line = []
        deltasTemp = []
        
        for j in range (-500,500, 10):
            point = (pointX + j, pointY + j * i, point_[2])
            
            if chosenHouseNParcel[3].contains(Point(point[0], point[1])):
                continue

            #check if we're off the elevation map
            if point[0] > topRightElev[0] or point[1] > topRightElev[1]:
                continue
            if point[0] < bottomLeftElev[0] or point[1] < bottomLeftElev[1]:
                continue
            
            delta = houseRoofDelta(point, surrHouses)
            if delta == None:
                delta = elevationSurfaceDelta(point, surrElevation)
                if delta == None:
                    continue
            
            line.append((point[0], point[1], delta))
            deltasTemp.append(delta)
        
        plotLine.append(line)
        deltas.append(deltasTemp) 
    
    line = []
    deltasTemp = []
    
    for j in range (-500,500, 10):
        point = (pointX, pointY + j, point_[2])
        
        if chosenHouseNParcel[3].contains(Point(point[0], point[1])):
            continue
        
        #check if we're off the elevation map
        if point[0] > topRightElev[0] or point[1] > topRightElev[1]:
            continue
        if point[0] < bottomLeftElev[0] or point[1] < bottomLeftElev[1]:
            continue
        
        delta = houseRoofDelta(point, surrHouses)
        if delta == None:
            delta = elevationSurfaceDelta(point, surrElevation)
            if delta == None:
                continue
            
        line.append((point[0], point[1], delta))    
        deltasTemp.append(delta)
    
    plotLine.append(line)
    deltas.append(deltasTemp)

    # 2D array of lines of sight deltas
    return deltas, plotLine

# Find LOS
deltas = getSlopes((chosenHouseNParcel[3].centroid.x, chosenHouseNParcel[3].centroid.y, chosenHouseNParcel[0] + 5))

#if chosenHouseNParcel[1] == 2:
#    result += getSlopes((chosenHouseNParcel[2][0].centroid.x, chosenHouseNParcel[2][0].centroid.y, chosenHouseNParcel[0] + 15))[0]

#plot.plotLOS2D(chosenHouseNParcel[3], deltas[1])

#FINALLY, ANALYSIS, we have finalDeltas, -500-500 for each line so middle is closest

total = 0

for line in deltas[0]:
    center = len(line)/2 + 0.0001
    for index, delta in enumerate(line):
        weight = 1/abs(index - center)
        total += weight * (-delta)
    
print(total/len(deltas[0]))
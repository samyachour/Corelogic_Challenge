from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
import pandas as pd

from figures import BLUE, SIZE, plot_coords, color_isvalid
import gather

from shapely.geometry import Polygon, LineString, Point
from scipy import spatial
import numpy as np

from matplotlib import cm
from matplotlib.ticker import MaxNLocator
import mpl_toolkits.mplot3d.art3d as art3d

def plotMultiPolygon(shape):
    fig = plt.figure(1, figsize=SIZE, dpi=90)
    ax = fig.add_subplot(121)
    if str(type(shape)) == "<class 'shapely.geometry.multipolygon.MultiPolygon'>":
        for polygon in shape:
            plot_coords(ax, polygon.exterior, alpha=0)
            patch = PolygonPatch(polygon, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
            ax.add_patch(patch)
    
    if str(type(shape)) == "<class 'shapely.geometry.polygon.Polygon'>":
        plot_coords(ax, shape.exterior, alpha=0)
        patch = PolygonPatch(shape, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
        ax.add_patch(patch)
        
    ax.set_title('Polygon')

# TODO: deal with empty total_lvg area 45982 8

def plotData2D(data):
    
    for index, row in data.iterrows():
        plotMultiPolygon(row['Parcel'])
        for i in row['House']:
            plotMultiPolygon(i)
            
def Plot3DSurfaceWithPatches(points, patches, height):
    Xs, Ys, Zs = [], [], []
    
    for i in points:
        Xs.append(i[0])
        Ys.append(i[1])
        Zs.append(i[2])
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_trisurf(Xs, Ys, Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)
    
    for i in patches:
        for j in i[0]:
            ax.add_patch(j)
            art3d.pathpatch_2d_to_3d(j, z=i[1], zdir="z")
    
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))
    
    ax.set_zlim3d(0,height)
    
    #fig.tight_layout()
            
    plt.show() 

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
        
        if row['Ratios'][2] >= 10:
            floors.append(2)
            continue
        
        if row['Ratios'][1] >= 250 and row['Ratios'][2] > avgBB:
            floors.append(2)
            continue
        
        elif row['Ratios'][0] >= 1 and row['Ratios'][1] >= 97:
            floors.append(2)
            continue
        
        elif (row['Ratios'][0] >= 1 or row['Ratios'][1] >= 100) and row['Ratios'][2] > avgBB:
            floors.append(2)
            continue
        
        elif row['Ratios'][0] >= 0.75 and row['Ratios'][1] >= 50 and row['Ratios'][2] > avgBB:
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
            patch = PolygonPatch(i, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), zorder=2)
            patches.append(patch)
        
        housePolys[idx] = [patches, house[2]]
            
        idx += 1
    
    return (housePolys, max, surrHouses)

'''
convert point to 2d
find nearest elevation square, find the height delta
run through house polygons (in 2d) to see if the point is in any, if it is return the height delta
'''

def elevationSurfaceDelta(point, surfacePts):        
        
        surfacePts2D = []
        point2D = (point[0], point[1])
        
        for i in surfacePts:
            surfacePts2D.append((i[0], i[1]))
            
        distances, indices = spatial.KDTree(surfacePts2D).query(point2D, k=4)
        
        # square of elevation points right above our point
        elevSquare = []
        
        for i in indices:
            elevSquare.append(surfacePts[i])
        
        # Check which triangular plane to use
        
        distances, indices = spatial.KDTree(elevSquare).query(point2D, k=1)
        closest = elevSquare[indices[0]]
        distances, indices = spatial.KDTree(elevSquare).query(closest, k=2)
        triPoints = [closest, (elevSquare[indices[0]]), (elevSquare[indices[1]])]
        
        # calculate 2 planes for square
        
        p1 = np.array(triPoints[0])
        p2 = np.array(triPoints[1])
        p3 = np.array(triPoints[2])
        
        v1 = p3 - p1
        v2 = p2 - p1
        
        # the cross product is a vector normal to the plane
        cp = np.cross(v1, v2)
        a, b, c = cp
        
        # This evaluates a * x3 + b * y3 + c * z3 which equals d
        d = np.dot(cp, p3)
        
        Z = (d - a * point[0] - b * point[1]) / c
             
        return Z - point[2]
        
def houseRoofDelta(point, housesDF):
            
        point2D = Point(point[0], point[1])
        
        for index, row in housesDF.iterrows():
            for i in row['House']:
                if i.contains(point2D):
                    #return delta, positive for roof above, negative for roof below
                    return row['Heights'] - point[2]
        
        return None
    
    
    
    
    
#For live demo, uncomment the getElevation code in gather.py
surrHouses, surrElevation = gather.getData(45982)
#plotData2D(surrHouses)
#getFloors(surrHouses).to_csv('out1.csv', index=False)
surrHouses = getFloors(surrHouses)  
#print(housePolys)
patches = getHousePatches(surrHouses)
surrHouses = patches[2]
Plot3DSurfaceWithPatches(surrElevation, patches[0], patches[1])
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
import pandas as pd

from figures import BLUE, SIZE, plot_coords, color_isvalid
import gather

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
    
#For live demo, uncomment the getElevation code in gather.py
surrHouses, surrElevation = gather.getData(45982)

# deal with empty total_lvg area 45982 8

def plotData2D(data):
    
    for index, row in data.iterrows():
        plotMultiPolygon(row['Parcel'])
        for i in row['House']:
            plotMultiPolygon(i)
            
def Plot3DSurfaceWithPatch(points, patches):
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
        ax.add_patch(i[0])
        art3d.pathpatch_2d_to_3d(i[0], z=i[1], zdir="z")
    
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))
    
    fig.tight_layout()
            
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
    print(avgBB)
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

#plotData2D(surrHouses)
#getFloors(surrHouses).to_csv('out1.csv', index=False)

surrHouses = getFloors(surrHouses)  


#PolygonPatch(shape, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), zorder=2)
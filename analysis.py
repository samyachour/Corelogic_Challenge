from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
import pandas as pd

from figures import BLUE, SIZE, plot_coords, color_isvalid
import gather

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

# analyze dataframe to find floors, consider bed/bath # and home value (asr_total & tax_value)
# deal with empty rows, empty total_lvg area 45982 8, and add up polygons for condos or multi family

def plotData2D(data):
    
    for index, row in data.iterrows():
        plotMultiPolygon(row['Parcel'])
        for i in row['House']:
            plotMultiPolygon(i)

def getFloors(data):
    
    ratios = []    
    
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
        ratios.append((ftRatio, valRatio))
    
    se = pd.Series(ratios)
    data['Ratios'] = se.values
    return data

plotData2D(surrHouses)
getFloors(surrHouses).to_csv('out1.csv', index=False)
import pandas as pd
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch

from figures import BLUE, SIZE, plot_coords, color_isvalid
import gather
import Elevation as elev

def getElev():
    elevationPoints_ = elev.elevationPoints
    elevationPoints = []
    
    for point in elevationPoints_:
        sp = elev.convertLLSP(point[0], point[1])
        elevationPoints.append((sp[0], sp[1], point[2]))
    
    return elevationPoints

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
    
#For live demo, uncomment the getElevation code in gather.py and the following line
#surrHouses, surrElevation = gather.getData(0)

surrHouses = pd.read_csv("out.csv")
elevations = getElev()

# analyze dataframe to find floors, make sure to add up polygons for condos or multi family, consider bed/bath # and home value (asr_total & tax_value)
# deal with empty rows, empty total_lvg area 45982 8, and add up polygons for condos or multi family
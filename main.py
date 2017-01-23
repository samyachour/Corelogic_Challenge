import pandas as pd
from shapely.geometry import Polygon
from shapely import wkt
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from descartes.patch import PolygonPatch

from figures import BLUE, SIZE, plot_coords, color_isvalid
import mapsImages as mimg
import Elevation as elev
import pythonShapefilePostGIS as pgis
import numpy as np
np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_columns', 500)

from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults

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

coreLogic = pd.read_csv("../CorelogicResources/Corelogic_houses_csv.csv")
house = coreLogic.iloc[45982] # numbers loc - 2   0 is APN = 344-030-06-00    32.8721, -117.249 2425    2425 Ellentown rd, La Jolla, CA

latitude = house['PARCEL LEVEL LATITUDE']
longitude = house['PARCEL LEVEL LONGITUDE']
nearestParcelsData = pgis.findNearestParcels(house['FORMATTED APN'])

nearestParcels = mimg.getBuildingPolygons(latitude, longitude, 18, 640, 640, "parcels")
nearestParcelsDF = pd.DataFrame(index=range(0, len(nearestParcels)), columns=["Polygon"])
idx = 0

for i in nearestParcels:
    nearestParcelsDF.set_value(idx, "Polygon", Polygon(i))
    idx += 1
    
nearestParcelsDF['x_coord'] = 0.000000000
nearestParcelsDF['y_coord'] = 0.000000000
nearestParcelsDF['area'] = 0.000000000                

for index, row in nearestParcelsDF.iterrows():
    nearestParcelsDF.set_value(index, "x_coord", row['Polygon'].centroid.x)
    nearestParcelsDF.set_value(index, "y_coord", row['Polygon'].centroid.y)
    nearestParcelsDF.set_value(index, "area", row['Polygon'].area)    
    
    

#houseParcel = nearestParcels.loc[nearestParcels['apn'] == house['FORMATTED APN'].replace("-", "")]
# HOUSE LAT LONG we care about
#comes as SP, need to convert to polygons
nearestPolygons = mimg.getBuildingPolygons(latitude, longitude, 18, 640, 640, "houses")
nearestPolygonsDF = pd.DataFrame(index=range(0, len(nearestPolygons)), columns=["Polygon"])
idx = 0

for i in nearestPolygons:
    nearestPolygonsDF.set_value(idx, "Polygon", Polygon(i))
    idx += 1

nearestPolygonsDF['x_coord'] = 0.000000000
nearestPolygonsDF['y_coord'] = 0.000000000
nearestPolygonsDF['area'] = 0.000000000                

for index, row in nearestPolygonsDF.iterrows():
    nearestPolygonsDF.set_value(index, "x_coord", row['Polygon'].centroid.x)
    nearestPolygonsDF.set_value(index, "y_coord", row['Polygon'].centroid.y)
    nearestPolygonsDF.set_value(index, "area", row['Polygon'].area)

#print(nearestPolygonsDF)
#print(nearestPolygons)

#6.254550, 1.898823, 8485.24  7146
#6.255281 1.898643   3389.342628  3564


#Box: 32.873320, -117.250975 to 32.871759, -117.248062
#print(elev.getElevationGoogleBox(latitude + 0.0015, longitude + 0.0015, latitude - 0.0015, longitude - 0.0015, 25, 25))
#comes as lat long, need to convert to SP
elevationPoints_ = elev.elevationPoints
elevationPoints = []

for point in elevationPoints_:
    sp = elev.convertLLSP(point[0], point[1])
    elevationPoints.append((sp[0], sp[1], point[2]))

'''
so we have nearestParcelsDF, nearestParcelsData, house, lat/long, nearestPolygonsDF, and elevationPoints all in SP
'''
'''
for index, row in nearestParcelsDF.iterrows():
    shape = row['Polygon']
    plotMultiPolygon(shape)  

for index, row in nearestPolygonsDF.iterrows():
    shape = row['Polygon']
    plotMultiPolygon(shape)
'''
'''
for index, row in nearestParcelsData.iterrows():
    shape = wkt.loads(row['st_astext'])
    plotMultiPolygon(shape)
'''

# We want to compare the nearestPolygonsDF area with the TOTAL_LVG_ in nearestParcelsData to find height
# We want to grab the NearestPolygonsDF, and query the nearestParcelsData

# TODO: ignore weird small shapes 0 22, 0 7, 0 5 (better)
# TODO: ignore apartment buildings/condos 2742 0
# TODO: ignore shapes that don't overlap 45982 0-4
# TODO: deal with shapes touching 0 3
# TODO: deal with empty parcel data total_lvg 45982 8

test = nearestPolygonsDF.iloc[19]
areas = [test['area'], 0.0000, 0.0000]
shapes = [test['Polygon'], test['Polygon']]
address = ""
zipcode = 0
rooms = ""
x = test['x_coord']
y = test['y_coord']
x1 = 0
y1 = 0

for index, row in nearestParcelsData.iterrows():
    if (abs(row['x_coord'] - x) + abs(row['y_coord'] - y)) < (abs(x1 - x) + abs(y1 - y)):
        x1 = row['x_coord']
        y1 = row['y_coord']
        areas[1] = row['total_lvg_']
        areas[2] = row['usable_sq_']
        shapes[1] = wkt.loads(row['st_astext'])
        address = str(int(row['situs_addr'])) + " " + row['situs_stre'] + " " +  row['situs_suff']
        zipcode = row['own_zip']
        rooms = "Bedrooms: " + str(row['bedrooms']) + "Bathrooms: " + str(row['baths'])

print(areas)
print(address)
print(rooms)
plotMultiPolygon(shapes[1])
plotMultiPolygon(shapes[0])

# 45982
# 5: 2 floors 1039.788362172010, 1408.0
# 6: 1 floor 2064.6996684360101, 1162.0
# 7: 1/2 1 floor, 1/2 2 floors, 2587.0305508661154, 2196.0
# 13: 1 floor, 1078.0723589012371, 1031.0

# 15: 1 floor, 1123.2520837836387, 1044.0
# 16: 1 floor, 1676.7780576678415, 1496.0

zillow_data = ZillowWrapper("X1-ZWz1fm3nv90ft7_aovt1")
deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
result = GetDeepSearchResults(deep_search_response)
print(result.home_size)

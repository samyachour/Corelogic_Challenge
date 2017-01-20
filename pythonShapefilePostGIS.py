from sqlalchemy import create_engine
import pandas as pd
from shapely import wkt
from shapely.geometry import Polygon
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from descartes.patch import PolygonPatch
from figures import BLUE, SIZE, plot_coords, color_isvalid
# TODO: check for xy coords, exclude multi's?

import mapsImages as mimg
import Elevation as elev
import numpy as np
np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_columns', 500)

engine = create_engine('postgresql://@localhost:5432/parcels')

def getPolygon(geomCol, table, idCol, rowNum):
    sql = 'SELECT *, ST_AsText({}) FROM {} WHERE "{}" < {};'.format(geomCol, table, idCol, rowNum + 5)
    data = pd.read_sql(sql, engine)
    #print(data['st_astext'].iloc[rowNum])
    
    
    shape = wkt.loads(data['st_astext'].iloc[rowNum])
    plotMultiPolygon(shape)
        
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
    
#getPolygon("geom", "public.parcelterminal", "gid", 0)

# Adjust parcel radius to match with google maps static image
def findNearestParcels(APN):
    sql = 'SELECT * FROM public.parcelterminal WHERE "apn" = \'{}\';'.format(APN.replace("-", ""))
    parcel = pd.read_sql(sql, engine)
    
    x = parcel['x_coord'].iloc[0]
    y = parcel['y_coord'].iloc[0]
    x_bounds = (x + 400, x - 400)
    y_bounds = (y + 400, y - 400)
    
    # plotMultiPolygon(shape) MAKE DIFF COLOR
    
    sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal WHERE "x_coord" < {} AND "x_coord" > {} AND "y_coord" < {} AND "y_coord" > {};'.format(x_bounds[0], x_bounds[1], y_bounds[0], y_bounds[1])  
    surroundingParcels = pd.read_sql(sql, engine)
    
    #return surroundingParcels
    
    '''
    #plotMultiPolygon(wkt.loads(surroundingParcels['st_astext'].iloc[0]))
    nearestParcels = []
    
    for index, row in surroundingParcels.iterrows():
        shape = wkt.loads(row['st_astext'])
        plotMultiPolygon(shape)
        nearestParcels.append(shape)
            
    #surroundingParcels['shape'] = pd.Series(nearestParcels)
    '''
    return surroundingParcels
    

df = pd.read_csv("../CorelogicResources/Corelogic_houses_csv.csv")
house = df.iloc[0] # APN = 344-030-06-00    32.8721, -117.249 2425    2425 Ellentown rd, La Jolla, CA

nearestParcels = findNearestParcels(house['FORMATTED APN'])
#print(nearestParcels)


houseParcel = nearestParcels.loc[nearestParcels['apn'] == house['FORMATTED APN'].replace("-", "")]
# HOUSE LAT LONG we care about
latitude, longitude = elev.convertSPLL(float(houseParcel['x_coord']), float(houseParcel['y_coord']))
#comes as SP, need to convert to polygons
nearestPolygons_ = mimg.getBuildingPolygons(latitude, longitude, 18, 640, 640)
nearestPolygons = []
nearestPolygonsDF = pd.DataFrame(index=range(0, len(nearestPolygons_)), columns=["Polygon"])
idx = 0

for i in nearestPolygons_:
    nearestPolygons.append(Polygon(i))
    nearestPolygonsDF.set_value(idx, "Polygon", Polygon(i))
    idx += 1

#nearestPolygons = pd.DataFrame(nearestPolygons_, columns=["Polygon"])

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

#so we have nearestParcels, houseParcel, lat/long, nearestPolygons, and elevationPoints all in SP

for index, row in nearestParcels.iterrows():
    shape = wkt.loads(row['st_astext'])
    plotMultiPolygon(shape)   

for index, row in nearestPolygonsDF.iterrows():
    shape = row['Polygon']
    plotMultiPolygon(shape)









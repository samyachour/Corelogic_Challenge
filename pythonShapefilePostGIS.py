from sqlalchemy import create_engine
import pandas as pd
from shapely import wkt
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from descartes.patch import PolygonPatch
from figures import BLUE, SIZE, plot_coords, color_isvalid
# TODO: check for xy coords, exclude multi's?

import mapsImages as mimg
import Elevation as elev

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
    for polygon in shape:
        plot_coords(ax, polygon.exterior, alpha=0)
        patch = PolygonPatch(polygon, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
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
    
    #plotMultiPolygon(wkt.loads(surroundingParcels['st_astext'].iloc[0]))
    
    for index, row in surroundingParcels.iterrows():
        shape = wkt.loads(row['st_astext'])
        plotMultiPolygon(shape)

#findNearestParcels("344-030-06-00")
    
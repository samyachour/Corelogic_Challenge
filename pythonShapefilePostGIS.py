from sqlalchemy import create_engine
import pandas as pd
from shapely import geometry
from shapely import wkt
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
from figures import BLUE, GRAY, SIZE, set_limits, plot_coords, plot_bounds, plot_line, color_isvalid, color_issimple
# TODO: check for xy coords, exclude multi's?

engine = create_engine('postgresql://@localhost:5432/parcels')

def getPolygon(geomCol, table, idCol, rowNum, shapeType):
    sql = 'SELECT *, ST_AsText({}) FROM {} WHERE "{}" < {};'.format(geomCol, table, idCol, rowNum + 5)
    data = pd.read_sql(sql, engine)
    #print(data['st_astext'].iloc[rowNum])
    
    
    shape = wkt.loads(data['st_astext'].iloc[rowNum])
    
    if shapeType == "MP":
        plotMultiPolygon(shape)
    elif shapeType == "MLS":
        plotMultiLineString(shape)
        
def plotMultiPolygon(shape):
    fig = plt.figure(1, figsize=SIZE, dpi=90)
    ax = fig.add_subplot(121)
    for polygon in shape:
        plot_coords(ax, polygon.exterior, alpha=0)
        patch = PolygonPatch(polygon, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
        ax.add_patch(patch)
        
    ax.set_title('Polygon')
    
def plotMultiLineString(shape):
    fig = plt.figure(1, figsize=SIZE, dpi=90)
    ax = fig.add_subplot(121)
    
    color = color_issimple(shape)
    for line in shape:
        plot_coords(ax, line, alpha=0, zorder=1)
    plot_bounds(ax, shape, alpha=0)
    for line in shape:
        plot_line(ax, line, color=color, alpha=0.7, zorder=2)
    
    ax.set_title('Linestring')

#getPolygon("geom", "public.parcelterminal", "gid", 0, "MP")
getPolygon("geom", "public.topographical", "id", 0, "MLS")

def findNearestParcels(APN):
    sql = 'SELECT * FROM public.parcelterminal WHERE "apn" = \'{}\';'.format(APN.replace("-", ""))
    parcel = pd.read_sql(sql, engine)
    
    x = parcel['x_coord'].iloc[0]
    y = parcel['y_coord'].iloc[0]
    x_bounds = (x + 300, x - 300)
    y_bounds = (y + 300, y - 300)
    
    sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal WHERE "x_coord" < {} AND "x_coord" > {} AND "y_coord" < {} AND "y_coord" > {};'.format(x_bounds[0], x_bounds[1], y_bounds[0], y_bounds[1])  
    surroundingParcels = pd.read_sql(sql, engine)
    
    #plotMultiPolygon(wkt.loads(surroundingParcels['st_astext'].iloc[0]))
    
    for index, row in surroundingParcels.iterrows():
        shape = wkt.loads(row['st_astext'])
        plotMultiPolygon(shape)
    

#findNearestParcels("344-030-06-00")

# NOTE: When you find the topographical polygons, use the centroid column to plot them!!!!!
def findNearestTopography(APN):
    sql = 'SELECT * FROM public.parcelterminal WHERE "apn" = \'{}\';'.format(APN.replace("-", ""))
    parcel = pd.read_sql(sql, engine)
    
    x = parcel['x_coord'].iloc[0]
    y = parcel['y_coord'].iloc[0]
    x_bounds = (x + 300 , x - 300)
    y_bounds = (y + 300, y - 300)
    
    sql = 'SELECT *, ST_AsText("geom") FROM public.topographical WHERE "x_coord" < {} AND "x_coord" > {} AND "y_coord" < {} AND "y_coord" > {};'.format(x_bounds[0], x_bounds[1], y_bounds[0], y_bounds[1])  
    surroundingTopography = pd.read_sql(sql, engine)
    #print(surroundingTopography['st_astext'].iloc[6])
    
    #plotMultiPolygon(wkt.loads(surroundingParcels['st_astext'].iloc[0]))
    
    for index, row in surroundingTopography.iterrows():
        shape = wkt.loads(row['st_astext'])
        plotMultiLineString(shape)
    
#findNearestTopography("344-030-06-00")

def test(rowNum=0):
    #sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal;'
    sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal WHERE "gid" < 7'
    #sql = 'SELECT *, ST_AsText("centroid") FROM public.topographical WHERE "id" < 5'
    data = pd.read_sql(sql, engine)
    #print(data)
    #print(wkt.loads(data['st_astext'].iloc[rowNum]))
    #print(type(data['geom'].iloc[rowNum]))
    print(type(data['apn'].iloc[rowNum]))
    '''
    print(data['st_astext'].iloc[rowNum])
    
    inputString = data['st_astext'].iloc[rowNum][15:-3]
    inputString = inputString.split(",")
    points = []
    for coord in inputString:
        coords = geometry.Point(float(coord.split(" ")[0]), float(coord.split(" ")[1]))
        points.append(coords)
    
    poly = geometry.Polygon([[p.x, p.y] for p in points])
    
    x,y = poly.exterior.xy
    fig = plt.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)
    ax.plot(x, y, color='#6699cc', alpha=0.7,
        linewidth=3, solid_capstyle='round', zorder=2)
    ax.set_title('Polygon')
    
    print(data['total_lvg_'].iloc[rowNum])
    '''
    
#test(1)
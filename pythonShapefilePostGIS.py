from sqlalchemy import create_engine
import pandas as pd
from shapely import geometry
from shapely import wkt
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
from figures import BLUE, SIZE, set_limits, plot_coords, color_isvalid
# TODO: check for xy coords, exclude multi's?

def getPolygon(geomCol, table, idCol, rowNum):
    engine = create_engine('postgresql://@localhost:5432/parcels')
    sql = 'SELECT *, ST_AsText({}) FROM {} WHERE "{}" < {};'.format(geomCol, table, idCol, rowNum + 5)
    data = pd.read_sql(sql, engine)
    #print(data['st_astext'].iloc[rowNum])
    
    
    shape = wkt.loads(data['st_astext'].iloc[rowNum])
        
    fig = plt.figure(1, figsize=SIZE, dpi=90)
    ax = fig.add_subplot(121)
    for polygon in shape:
        plot_coords(ax, polygon.exterior)
        patch = PolygonPatch(polygon, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
        ax.add_patch(patch)
        
    ax.set_title('a) valid')
        
        

getPolygon("geom", "public.parcelterminal", "gid", 1)
#getPolygon("geom", "public.topographical", "id", 0)






def test(rowNum=0):
    engine = create_engine('postgresql://@localhost:5432/parcels')
    #sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal WHERE "multi" = \'Y\';'
    sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal WHERE "gid" < 7'
    data = pd.read_sql(sql, engine)
    print(type(wkt.loads(data['st_astext'].iloc[rowNum])))
    
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
    
#test(0)
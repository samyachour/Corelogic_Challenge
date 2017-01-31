from sqlalchemy import create_engine
import pandas as pd
from shapely import wkt

import numpy as np
np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_columns', 500)

engine = create_engine('postgresql://@localhost:5432/parcels')

def getPolygon(geomCol, table, idCol, rowNum):
    sql = 'SELECT *, ST_AsText({}) FROM {} WHERE "{}" < {};'.format(geomCol, table, idCol, rowNum + 5)
    data = pd.read_sql(sql, engine)
    
    shape = wkt.loads(data['st_astext'].iloc[rowNum])
    return shape
    
#getPolygon("geom", "public.parcelterminal", "gid", 0)

# Adjust parcel radius to match with google maps static image
def findNearestParcels(APN):
    sql = 'SELECT * FROM public.parcelterminal WHERE "apn" = \'{}\';'.format(APN.replace("-", ""))
    parcel = pd.read_sql(sql, engine)
    
    x = parcel['x_coord'].iloc[0]
    y = parcel['y_coord'].iloc[0]
    x_bounds = (x + 450, x - 450)
    y_bounds = (y + 450, y - 450)
        
    sql = 'SELECT *, ST_AsText("geom") FROM public.parcelterminal WHERE "x_coord" < {} AND "x_coord" > {} AND "y_coord" < {} AND "y_coord" > {};'.format(x_bounds[0], x_bounds[1], y_bounds[0], y_bounds[1])  
    surroundingParcels = pd.read_sql(sql, engine)
        
    return surroundingParcels
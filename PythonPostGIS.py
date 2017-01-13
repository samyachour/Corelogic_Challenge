import sys
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from shapely.wkt import loads as wkt_loads
from matplotlib.collections import LineCollection
from mpl_toolkits.basemap import Basemap
import stateplane

def db_connection():
    main_dt = {
        'db': 'parcels',  # name of your database
        'ip': 'localhost',  # ip of the database or 'localhost'
        'port': '5432'
        }
    return main_dt

def map_definition(main_dt):
    main_dt['parcelterminal'] = {}

    # Germany off-shore regions (ZNES)
    main_dt['parcelterminal']['parcels'] = {
        'table': 'parcelterminal',  # name of the table
        'geo_col': 'geom',  # name of the geometry column
        'id_col': 'parcelid',  # name of the geo-id column
        'schema': 'public',  # name of the schema
        'simp_tolerance': '0.01',  # simplification tolerance (1)
        'where_col': 'gid',  # column for the where-condition
        'where_cond': '< 10',  # condition for the where-condition
        'facecolor': '#a5bfdd'   # color of the polygon (blue)
        }
        
def execute_read_db(dic, db_string):
    '''
    Executes a sql-string and returns a tuple
    '''
    conn = psycopg2.connect(
        '''host={ip} dbname={db}
           port={port}
        '''.format(**main_dt))
    cur = conn.cursor()
    cur.execute(db_string)
    values = cur.fetchall()
    cur.close()
    conn.close()
    return values
    

def box_definition(main_dt):
    main_dt['x1'] = -117.418098  # longitude, east
    main_dt['x2'] = -116.997871  # longitude, east
    main_dt['y1'] = 33.243695  # latitude, north
    main_dt['y2'] = 33.092530  # latitude, north

    
def fetch_geometries(main_dt):
    '''
    Reads the geometry and the id of all given tables and
    writes it to the 'geom'-key of each branch.
    '''
    sql_str = '''
        SELECT {id_col}, ST_AsText(
            ST_SIMPLIFY({geo_col},{simp_tolerance}))
        FROM {schema}.{table}
        WHERE "{where_col}" {where_cond}
        ORDER BY {id_col} DESC;'''

    main_dt['parcelterminal']['parcels']['geom'] = execute_read_db(
        main_dt, sql_str.format(
            **main_dt['parcelterminal']['parcels']))



def create_plot(main_dt):
    'Creates the basic plot object.'
    main_dt['ax'] = plt.subplot(111)
    plt.box(on=None)

def create_basemap(main_dt):
    'Creates the basemap.'
    main_dt['m'] = Basemap(
        resolution='i', epsg=None, projection='merc',
        llcrnrlat=main_dt['y1'], urcrnrlat=main_dt['y2'],
        llcrnrlon=main_dt['x1'], urcrnrlon=main_dt['x2']
        #,lat_ts=(main_dt['x1'] + main_dt['x2']) / 2
                )
    main_dt['m'].drawcoastlines(linewidth=0)

def create_vectors_multipolygon(main_dt, multipolygon):
    'Create the vectors for MultiPolygons, given'
    '''
    (Decimal('86055'), 
    'MULTIPOLYGON(((6231408.67900001 2006327.18700001,6231364.956 
     2006254.02500001,6231267 2006308.999,6231293.689 2006354.17900001,6231311 2006384,
     6231408.67900001 2006327.18700001)))'
    '''
    vectors = []
    seg = []
    inputString = multipolygon[1][15:-3]
    inputString = inputString.split(",")
    for coord in inputString:
        coords = stateplane.to_latlon(float(coord.split(" ")[0]), float(coord.split(" ")[1]), epsg='2230')
        seg.append(main_dt['m'](coords[0], coords[1]))

    vectors.append(np.asarray(seg))
    return vectors
    
def create_geoplot(main_dt):
    ''
    '''
    for mp in main_dt['parcelterminal']['parcels']['geom']:
        vectors = create_vectors_multipolygon(main_dt, mp)
        lines = LineCollection(vectors, antialiaseds=(1, ))
        lines.set_facecolors(main_dt['parcelterminal']['parcels']['facecolor'])
        lines.set_edgecolors('white')
        lines.set_linewidth(1)
        main_dt['ax'].add_collection(lines)
    '''
    vectors = create_vectors_multipolygon(main_dt, main_dt['parcelterminal']['parcels']['geom'][2])
    lines = LineCollection(vectors, antialiaseds=(1, ))
    lines.set_facecolors(main_dt['parcelterminal']['parcels']['facecolor'])
    lines.set_edgecolors('white')
    lines.set_linewidth(1)
    main_dt['ax'].add_collection(lines)
    
main_dt = db_connection()
map_definition(main_dt)
box_definition(main_dt)
fetch_geometries(main_dt)
print(main_dt['parcelterminal']['parcels']['geom'][0])
create_plot(main_dt)
create_basemap(main_dt)
create_geoplot(main_dt)
plt.tight_layout()
plt.show()

    
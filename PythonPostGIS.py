import sys
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from shapely.wkt import loads as wkt_loads
from matplotlib.collections import LineCollection
from mpl_toolkits.basemap import Basemap

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
        'id_col': 'gid',  # name of the geo-id column
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
    
'''
def box_definition(main_dt):
    main_dt['x1'] = 3.  # longitude, east
    main_dt['x2'] = 16.  # longitude, east
    main_dt['y1'] = 47.  # latitude, north
    main_dt['y2'] = 56.  # latitude, north
'''
    
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

    for key in list(main_dt['parcelterminal'].keys()):
        main_dt['parcelterminal'][key]['geom'] = execute_read_db(
            main_dt, sql_str.format(
                **main_dt['parcelterminal'][key]))
        
main_dt = db_connection()
map_definition(main_dt)
fetch_geometries(main_dt)
print(main_dt['parcelterminal']['parcels']['geom'][0])
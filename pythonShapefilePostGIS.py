from sqlalchemy import create_engine
import pandas as pd
from shapely import geometry
from matplotlib import pyplot as plt

engine = create_engine('postgresql://@localhost:5432/parcels')
sql = """
SELECT *, ST_AsText(geom) FROM public.parcelterminal WHERE "gid" < 5;
"""
parcels = pd.read_sql(sql, engine)
print(parcels['st_astext'].iloc[0])



inputString = parcels['st_astext'].iloc[1][15:-3]
inputString = inputString.split(",")
points = []
for coord in inputString:
    coords = geometry.Point(float(coord.split(" ")[0]), float(coord.split(" ")[1]))
    points.append(coords)

poly = geometry.Polygon([[p.x, p.y] for p in points])
print(poly)

x,y = poly.exterior.xy
fig = plt.figure(1, figsize=(5,5), dpi=90)
ax = fig.add_subplot(111)
ax.plot(x, y, color='#6699cc', alpha=0.7,
    linewidth=3, solid_capstyle='round', zorder=2)
ax.set_title('Polygon')

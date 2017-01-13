from geoalchemy2.shape import to_shape
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://@localhost:5432/parcels')
sql = """
SELECT * FROM public.parcelterminal limit 5;
"""
parcels = pd.read_sql(sql, engine)
print(parcels)
import pandas
import shapefile

def getParcel():
    # df = pandas.read_csv("../CorelogicResources/Corelogic_houses_csv.csv")
    sf = shapefile.Reader("../CorelogicResources/Parcels/PARCELS.shp")
    # print(len(sf.records()))
    # print(sf.fields)
    
getParcel()
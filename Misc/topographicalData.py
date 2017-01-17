import pandas
import shapefile

def getParcel():
    # df = pandas.read_csv("../CorelogicResources/Corelogic_houses_csv.csv")
    sf = shapefile.Reader("../CorelogicResources/Topographical/Topo_2014_2Ft_LaJolla.shp")
    # print(len(sf.records()))
    # print(sf.fields)
    
getParcel()
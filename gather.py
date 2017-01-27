import pandas as pd
from shapely.geometry import Polygon
from shapely import wkt
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch

from figures import BLUE, SIZE, plot_coords, color_isvalid
import mapsImages as mimg
import Elevation as elev
import pythonShapefilePostGIS as pgis
import numpy as np
np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_columns', 500)

from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults, GetUpdatedPropertyDetails

def plotMultiPolygon(shape):
    fig = plt.figure(1, figsize=SIZE, dpi=90)
    ax = fig.add_subplot(121)
    if str(type(shape)) == "<class 'shapely.geometry.multipolygon.MultiPolygon'>":
        for polygon in shape:
            plot_coords(ax, polygon.exterior, alpha=0)
            patch = PolygonPatch(polygon, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
            ax.add_patch(patch)
    
    if str(type(shape)) == "<class 'shapely.geometry.polygon.Polygon'>":
        plot_coords(ax, shape.exterior, alpha=0)
        patch = PolygonPatch(shape, facecolor=color_isvalid(shape), edgecolor=color_isvalid(shape, valid=BLUE), alpha=0.5, zorder=2)
        ax.add_patch(patch)
        
    #ax.set_title('Polygon')

def getData(row):
    coreLogic = pd.read_csv("../CorelogicResources/Corelogic_houses_csv.csv")
    house = coreLogic.iloc[row] # numbers loc - 2   0 is APN = 344-030-06-00    32.8721, -117.249 2425    2425 Ellentown rd, La Jolla, CA
    
    latitude = house['PARCEL LEVEL LATITUDE']
    longitude = house['PARCEL LEVEL LONGITUDE']
    nearestParcelsData = pgis.findNearestParcels(house['FORMATTED APN'])
    
    nearestParcels = mimg.getBuildingPolygons(latitude, longitude, 18, 640, 640, "parcels")
    nearestParcelsDF = pd.DataFrame(index=range(0, len(nearestParcels)), columns=["Polygon", "x_coord", "y_coord", "area"])
    idx = 0
    
    for i in nearestParcels:
        nearestParcelsDF.set_value(idx, "Polygon", Polygon(i))
        idx += 1
        
    for index, row in nearestParcelsDF.iterrows():
        nearestParcelsDF.set_value(index, "x_coord", row['Polygon'].centroid.x)
        nearestParcelsDF.set_value(index, "y_coord", row['Polygon'].centroid.y)
        nearestParcelsDF.set_value(index, "area", row['Polygon'].area)    
        
        
    nearestPolygons = mimg.getBuildingPolygons(latitude, longitude, 18, 640, 640, "houses")
    nearestPolygonsDF = pd.DataFrame(index=range(0, len(nearestPolygons)), columns=["Polygon", "x_coord", "y_coord", "area"])
    idx = 0
    
    for i in nearestPolygons:
        nearestPolygonsDF.set_value(idx, "Polygon", Polygon(i))
        idx += 1            
    
    for index, row in nearestPolygonsDF.iterrows():
        nearestPolygonsDF.set_value(index, "x_coord", row['Polygon'].centroid.x)
        nearestPolygonsDF.set_value(index, "y_coord", row['Polygon'].centroid.y)
        nearestPolygonsDF.set_value(index, "area", row['Polygon'].area)
    
    
    #Box: 32.873320, -117.250975 to 32.871759, -117.248062
    elevationPoints_ = elev.getElevationGoogleBox(latitude + 0.002, longitude + 0.002, latitude - 0.002, longitude - 0.002, 15, 15)
    
    #comes as lat long, need to convert to SP
    #elevationPoints_ = elev.elevationPoints_
    elevationPoints = []
    
    for point in elevationPoints_:
        sp = elev.convertLLSP(point[0], point[1])
        elevationPoints.append((sp[0], sp[1], point[2] * 3.2808399))
    
    '''
    for index, row in nearestParcelsDF.iterrows():
        plotMultiPolygon(row['Polygon'])
    
    for index, row in nearestPolygonsDF.iterrows():
        plotMultiPolygon(row['Polygon'])
    '''
        
    # TODO: deal with shapes touching 0 3, 45982 25-26
    # TODO: deal with border houses that still barely touch a parcel (plot 45982), they don't matter cause they're far away fron chosen house
    
    """
    # Testing
    test = nearestPolygonsDF.iloc[11]
    areas = [test['area'], 0.0000, 0.0000]
    shapes = [test['Polygon'], test['Polygon']]
    address = ""
    zipcode = 0
    rooms = ""
    x = test['x_coord']
    y = test['y_coord']
    x1 = 0
    y1 = 0
    
    for index, row in nearestParcelsData.iterrows():
        if (abs(row['x_coord'] - x) + abs(row['y_coord'] - y)) < (abs(x1 - x) + abs(y1 - y)):
            x1 = row['x_coord']
            y1 = row['y_coord']
            areas[1] = row['total_lvg_']
            areas[2] = row['usable_sq_']
            shapes[1] = wkt.loads(row['st_astext'])
            address = str(int(row['situs_addr'])) + " " + row['situs_stre'] + " " +  row['situs_suff']
            zipcode = row['own_zip']
            rooms = "Bedrooms: " + str(row['bedrooms']) + " Bathrooms: " + str(row['baths'])
    
    print(areas)
    print(address)
    print(rooms)
    plotMultiPolygon(shapes[1])
    plotMultiPolygon(shapes[0])
    """
    
    
    zillow_data = ZillowWrapper("X1-ZWz1fmczai5rm3_7c2wf")
    
    """
    try: 
        deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
        result = GetDeepSearchResults(deep_search_response)
        print("Home size: " + str(result.home_size) + " " + str(result.home_type) + " Bedrooms: " + str(result.bedrooms) + " Bathrooms: " + str(result.bathrooms))
    except:
        print("ZZillow couldn't find the house")
    """
    
    
    #so we have nearestParcelsDF, nearestParcelsData, house, lat/long, nearestPolygonsDF, and elevationPoints (all in SP)
    
    # Works around condos/multi family by adding polygons, works around small weird random polygons, works around non-intersecting house/parcel
    # Modular so the zillow api failing only affects the type column, ('SingleFamily', 10) to 10
    returnDF = pd.DataFrame(index=range(0, len(nearestParcels)), columns=["APN", "Parcel", "House", "Address", "SqFtDelta", "Bed/Bath", "Type", "Value", "ParcelSqFt","Chosen", "Floors"])
    
    for index, row in nearestPolygonsDF.iterrows():
        mapArea = row['area']
        mapShape = row['Polygon']
        
        x1 = 0
        y1 = 0
        apn = 0
            
        # make sure we don't have some small weird shape
        if mapArea < 150:
            continue
        
        for index1, row1 in nearestParcelsData.iterrows():
            if (abs(row1['x_coord'] - row['x_coord']) + abs(row1['y_coord'] - row['y_coord'])) < (abs(x1 - row['x_coord']) + abs(y1 - row['y_coord'])):
                apn = row1['apn']
                x1 = row1['x_coord']
                y1 = row1['y_coord']
                
        x1 = 0
        y1 = 0
        
        for index1, row1 in nearestParcelsDF.iterrows():
            if (abs(row1['x_coord'] - row['x_coord']) + abs(row1['y_coord'] - row['y_coord'])) < (abs(x1 - row['x_coord']) + abs(y1 - row['y_coord'])):
                x1 = row1['x_coord']
                y1 = row1['y_coord']
         
        parcelData = nearestParcelsData.loc[nearestParcelsData['apn'] == apn].iloc[0]
        
        # Make sure house polygon is on parcel polygon
        if not mapShape.intersects(wkt.loads(parcelData['st_astext'])):
            continue
        
        if not returnDF.loc[returnDF['APN'] == apn].empty:
                selectedRow = returnDF.loc[returnDF['APN'] == apn]
                index1 = selectedRow.index[0]
                selectedRow = selectedRow.iloc[0]
                # Adding up polygon area if they share a parcel
                returnDF.set_value(index1, "House", selectedRow['House'] + [mapShape]) 
                returnDF.set_value(index1, "SqFtDelta", [selectedRow['SqFtDelta'][0] + mapArea, selectedRow['SqFtDelta'][1]]) 
                continue
        
        #Only one polygon per parcel, also getting zillow data while catching for weird rows
        address = str(int(parcelData['situs_addr'])) + " " + parcelData['situs_stre'] + " " +  parcelData['situs_suff']
        zipcode = parcelData['own_zip']
        try:
            deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
            result = GetDeepSearchResults(deep_search_response)
        except:        
            # if zillow couldn't find the house
                
            returnDF.set_value(index, "APN", apn)
            returnDF.set_value(index, "Address", address)
            returnDF.set_value(index, "Value", (parcelData['asr_total'], parcelData['asr_land']))
            # usable_sq_ from parceldata and property_size from pyzillow are both too innacurate and inconsistent
            returnDF.set_value(index, "ParcelSqFt", (parcelData['shape_area']))
            if apn == house['FORMATTED APN'].replace("-", ""):
                returnDF.set_value(index, "Chosen", True)
            else:
                returnDF.set_value(index, "Chosen", False)
            
            nearestMapParcel = nearestParcelsDF.loc[nearestParcelsDF['x_coord'] == x1].iloc[0]
            returnDF.set_value(index, "Parcel", nearestMapParcel['Polygon'])
            returnDF.set_value(index, "House", [mapShape])
        
            returnDF.set_value(index, "Type", (parcelData['nucleus_zo']))
            returnDF.set_value(index, "Bed/Bath", (int(parcelData['bedrooms']), int(parcelData['baths'])/10))
            returnDF.set_value(index, "SqFtDelta", [mapArea, int(parcelData['total_lvg_'])])
            
        else:
            
            returnDF.set_value(index, "APN", apn)
            returnDF.set_value(index, "Address", address)
            returnDF.set_value(index, "Value", ((parcelData['asr_total'] + float(result.tax_value))/2, parcelData['asr_land']))
            # usable_sq_ from parceldata and property_size from pyzillow are both too innacurate and inconsistent
            returnDF.set_value(index, "ParcelSqFt", (parcelData['shape_area']))
            if apn == house['FORMATTED APN'].replace("-", ""):
                returnDF.set_value(index, "Chosen", True)
            else:
                returnDF.set_value(index, "Chosen", False)
        
            nearestMapParcel = nearestParcelsDF.loc[nearestParcelsDF['x_coord'] == x1].iloc[0]
            returnDF.set_value(index, "Parcel", nearestMapParcel['Polygon'])
        
            returnDF.set_value(index, "House", [mapShape])
    
            returnDF.set_value(index, "Type", (result.home_type, int(parcelData['nucleus_zo'])))
            
            bedbath = []
            if result.bedrooms == None:
                bedbath.append(int(parcelData['bedrooms']))
            elif int(result.bedrooms) == int(parcelData['bedrooms']):
                bedbath.append(int(result.bedrooms))
            else:
                bedbath.append(int(parcelData['bedrooms']))
            if result.bathrooms == None:
                bedbath.append(int(parcelData['baths'])/10)
            elif float(result.bathrooms) == int(parcelData['baths'])/10:
                bedbath.append(float(result.bathrooms))
            else:
                bedbath.append(int(parcelData['baths'])/10)
            returnDF.set_value(index, "Bed/Bath", (bedbath[0], bedbath[1]))
        
            zillowID = result.zillow_id
            try:
                updated_property_details_response = zillow_data.get_updated_property_details(zillowID)
                resultUp = GetUpdatedPropertyDetails(updated_property_details_response)
            except:
                #print("Zillow couldn't find floors, but could find everything else you wanted")
                pass
            else:
                if resultUp.num_floors != None:
                    returnDF.set_value(index, "Floors", resultUp.num_floors) 
               
            if result.home_size != None:
                returnDF.set_value(index, "SqFtDelta", [mapArea, max(int(result.home_size), int(parcelData['total_lvg_']))])
            else:
                returnDF.set_value(index, "SqFtDelta", [mapArea, parcelData['total_lvg_']])
         
        
        
    returnDF = returnDF.dropna(how='all')    
    #returnDF.to_csv('out.csv', index=False)
    return (returnDF, elevationPoints)
    
#getData(0)
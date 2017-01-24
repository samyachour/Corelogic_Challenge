import shutil
import requests
import pandas
from PIL import Image

import matplotlib.pyplot as plt

import numpy as np
#np.set_printoptions(threshold=np.nan)
from skimage.measure import find_contours, approximate_polygon
from skimage import io
from skimage import color
from skimage.util import crop

import MercatorProjection
import Elevation as elev

def getImage(latitude, longitude, zoom, size, tag):
    # WITH SCALE url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&scale=2&maptype=satellite&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    # WITH MARKER url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&maptype=satellite&markers=color:red%7Clabel:H%7C{0},{1}&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&maptype=roadmap&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    response = requests.get(url, stream=True)
    with open('img' + str(tag) + '.png', 'wb') as out_file:
        
        shutil.copyfileobj(response.raw, out_file)
    del response
    
#TEST getImage("33.796745", "-117.851196", "18", "400x400")
# Adjust resolution and zoom to match with nearest parcels function
def retrieveAerialImages(numRows):
    df = pandas.read_csv("../CorelogicResources/Corelogic_houses_csv.csv")
    tag = 0
    
    # Retreive aerial images using the google API
    for index, row in df.iterrows():
        getImage(row["PARCEL LEVEL LATITUDE"], row["PARCEL LEVEL LONGITUDE"], "18", "640x640", tag)
        tag += 1
        if tag >= numRows:
            break
        
    # Crop google watermark out of image
    for i in range(0, numRows):
        image = "img" + str(i) + ".png"
        original = Image.open(image)
        width, height = original.size
        cropped = original.crop((0, 0, width, height-22))
        cropped.save("img" + str(i) + ".png")
    
#retrieveAerialImages(3)

def getBuildingPolygons(lat, long, zoom, w, h, polys):
    if polys == "houses":    
        style = "feature:landscape.man_made%7Celement:geometry.stroke%7Cvisibility:on%7Ccolor:0xffffff%7Cweight:1&style=feature:road%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:administrative.land_parcel%7Cvisibility:off"
    if polys == "parcels":
        style = "feature:administrative.land_parcel%7Celement:geometry.stroke%7Cvisibility:on%7Ccolor:0xffffff%7Cweight:1&style=feature:road%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:landscape.man_made%7Cvisibility:off"
    urlBuildings = "https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom={}&format=png32&sensor=false&size={}&maptype=roadmap&style=".format(lat, long, zoom, str(w) + "x" + str(h)) + style + "&key=AIzaSyAT_hASGVJSp5KiEz3phNDtXij7kGd7m_A"                                                             
                                                                          
    imgBuildings = io.imread(urlBuildings)
    imgBuildings = crop(imgBuildings, ((0, 22), (0, 0), (0, 0)))
    gray_imgBuildings = color.rgb2gray(imgBuildings)
    binary_imageBuildings = np.where(gray_imgBuildings > np.mean(gray_imgBuildings), 0.0, 1.0)
    contoursBuildings = find_contours(binary_imageBuildings, 0.1)
       
    '''
    fig, ax = plt.subplots()
    ax.imshow(imgBuildings, interpolation='nearest', cmap=plt.cm.gray)
    '''
    
    surroundingPolygons = []
    
    for n, contour in enumerate(contoursBuildings):
        
        coords = approximate_polygon(contour, tolerance=3.5)
        if len(coords) >= 4:
            # TO make sure we don't get house polygons that are cut off
            if not any(0.0 in subl for subl in coords):
                if not any(639.0 in subl for subl in coords):
                    yValues = []
                    for i in coords:
                        yValues.append(i[0])
                    #because we cropped the image, 640-22 = 618
                    if 617.0 not in yValues:
                        #ax.plot(coords[:, 1], coords[:, 0], '-r', linewidth=2)
                        surroundingPolygons.append(coords)
    
    '''
    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()
    '''
    
    
    centerPoint = MercatorProjection.G_LatLng(lat, long)
    housePolygons = []
        
    for i in surroundingPolygons:
        coords = []
        for j in i:
            point = MercatorProjection.G_Point(j[1], j[0])
            point = MercatorProjection.point2LatLng(centerPoint, zoom, w, h, point)
            point = elev.convertLLSP(point[0], point[1])
            coords.append(point)
        housePolygons.append(coords)
            
    return housePolygons
    
#getBuildingPolygons(33.167624126720625, -117.3294706444691, 18, 640, 640, "houses")
#getBuildingPolygons(32.8721, -117.249, 18, 640, 640, "houses")

# https://maps.googleapis.com/maps/api/staticmap?
# size=512x512&zoom=15&center=Brooklyn
# &style=feature:road.local%7Celement:geometry%7Ccolor:0x00ff00&style=feature:landscape%7Celement:geometry.fill%7Ccolor:0x000000&style=element:labels%7Cinvert_lightness:true&style=feature:road.arterial%7Celement:labels%7Cinvert_lightness:false
# &key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A
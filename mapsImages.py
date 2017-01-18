import shutil
import requests
import pandas
from PIL import Image

import numpy as np
from requests.utils import quote
from skimage.measure import find_contours, points_in_poly, approximate_polygon
from skimage import io
from skimage import color
from threading import Thread

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

def getBuildingPolygons(lat, long, zoom, size):
    # Styled google maps url showing only the buildings
    style = "feature:landscape.man_made%7Celement:geometry.stroke%7Cvisibility:on%7Ccolor:0x000000%7Cweight:1&style=feature:road%7Cvisibility:off&style=feature:poi%7Cvisibility:off"
    urlBuildings = "https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom={}&format=png32&sensor=false&size={}&maptype=roadmap&style=".format(lat, long, zoom, size) + style + "&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A"
    print(urlBuildings)
    
    imgBuildings = io.imread(urlBuildings)
    gray_imgBuildings = color.rgb2gray(imgBuildings)
    binary_imageBuildings = np.where(gray_imgBuildings > np.mean(gray_imgBuildings), 0.0, 1.0)
    contoursBuildings = find_contours(binary_imageBuildings, 0.1)
    
    
getBuildingPolygons(33.167624126720625, -117.3294706444691, "18", "400x400")

# https://maps.googleapis.com/maps/api/staticmap?
# size=512x512&zoom=15&center=Brooklyn
# &style=feature:road.local%7Celement:geometry%7Ccolor:0x00ff00&style=feature:landscape%7Celement:geometry.fill%7Ccolor:0x000000&style=element:labels%7Cinvert_lightness:true&style=feature:road.arterial%7Celement:labels%7Cinvert_lightness:false
# &key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A
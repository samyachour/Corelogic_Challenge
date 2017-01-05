import shutil
import requests
import pandas
from PIL import Image

def getImage(latitude, longitude, zoom, size, tag):
    # WITH SCALE url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&scale=2&maptype=satellite&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&maptype=satellite&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    response = requests.get(url, stream=True)
    with open('img' + str(tag) + '.png', 'wb') as out_file:
        
        shutil.copyfileobj(response.raw, out_file)
    del response
    
#TEST getImage("33.796745", "-117.851196", "18", "400x400")

def retreiveAerialImages(numRows):
    df = pandas.read_csv("../Resources/Corelogic_houses.csv")
    STOP = 0
    
    # Retreive aerial images using the google API
    for index, row in df.iterrows():
        getImage(row["PARCEL LEVEL LATITUDE"], row["PARCEL LEVEL LONGITUDE"], "19", "400x400", STOP)
        STOP += 1
        if STOP >= numRows:
            break
        
    # Crop google watermark out of image
    for i in range(0, numRows):
        image = "img" + str(i) + ".png"
        original = Image.open(image)
        width, height = original.size
        cropped = original.crop((0, 0, width, height-22))
        cropped.save("img" + str(i) + ".png")
    
retreiveAerialImages(3)
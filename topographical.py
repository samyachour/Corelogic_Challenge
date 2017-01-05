import shutil
import requests
import pandas

def getImage(latitude, longitude, zoom, size, tag):
    # WITH SCALE url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&scale=2&maptype=satellite&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    url = 'https://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom={2}&size={3}&maptype=satellite&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A'.format(latitude, longitude, zoom, size)
    response = requests.get(url, stream=True)
    with open('img' + str(tag) + '.png', 'wb') as out_file:
        
        shutil.copyfileobj(response.raw, out_file)
    del response
    
#getImage("33.796745", "-117.851196", "18", "400x400")

df = pandas.read_csv("../Resources/Corelogic_houses.csv")
STOP = 0

for index, row in df.iterrows():
    getImage(row["PARCEL LEVEL LATITUDE"], row["PARCEL LEVEL LONGITUDE"], "19", "400x400", STOP)
    STOP += 1
    if STOP >= 10:
        break

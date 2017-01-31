import matplotlib.pyplot as plt

import numpy as np
#np.set_printoptions(threshold=np.nan)
from skimage.measure import find_contours, approximate_polygon
from skimage import io
from skimage import color
from skimage.util import crop

import MercatorProjection
import Elevation as elev

def getBuildingPolygons(lat, long, zoom, w, h, polys):
    if polys == "houses":    
        style = "feature:landscape.man_made%7Celement:geometry.stroke%7Cvisibility:on%7Ccolor:0xffffff%7Cweight:1&style=feature:road%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:administrative.land_parcel%7Cvisibility:off"
    if polys == "parcels":
        style = "feature:administrative.land_parcel%7Celement:geometry.stroke%7Cvisibility:on%7Ccolor:0xffffff%7Cweight:1&style=feature:road%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:landscape.man_made%7Cvisibility:off"
    urlBuildings = "https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom={}&format=png32&sensor=false&size={}&maptype=roadmap&style=".format(lat, long, zoom, str(w) + "x" + str(h)) + style + "&key=AIzaSyChqczf6qEYwqV7AxZlRvTYgMbnnpmoH6A"                                                             
                                                        
    imgBuildings = io.imread(urlBuildings)
    imgBuildings = crop(imgBuildings, ((0, 22), (0, 0), (0, 0)))
    gray_imgBuildings = color.rgb2gray(imgBuildings)
    binary_imageBuildings = np.where(gray_imgBuildings > np.mean(gray_imgBuildings), 0.0, 1.0)
    contoursBuildings = find_contours(binary_imageBuildings, 0.1)
       
    '''
    fig, ax = plt.subplots()
    ax.imshow(binary_imageBuildings, interpolation='nearest', cmap=plt.cm.gray)
    '''
    
    surroundingPolygons = []
    
    for n, contour in enumerate(contoursBuildings):
        
        coords = approximate_polygon(contour, tolerance=3.5)
        if len(coords) >= 4:
            # to make sure we don't get house polygons that are cut off
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
    
#getBuildingPolygons(32.872112, -117.249232, 18, 640, 640, "parcels")
#getBuildingPolygons(32.8721, -117.249, 18, 640, 640, "houses")
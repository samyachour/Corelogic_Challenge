library(ggmap)
library(RgoogleMaps)
library(rgdal)
library(ggplot2)

CenterOfMap <- geocode("32.805582, -117.078552")

SD <- get_map(c(lon=CenterOfMap$lon, lat=CenterOfMap$lat),zoom = 11, maptype = "satellite", source = "google")
SDMap <- ggmap(SD)
SDMap

setwd("/Users/samy/Documents/Programming_Stuff/Data_Science/CorelogicResources/Parcels")
Parcels <- readOGR(".","PARCELS")

Parcels <- spTransform(Parcels, CRS("+proj=longlat +datum=WGS84"))
Parcels <- fortify(Parcels)

SDMap <- SDMap + geom_polygon(aes(x=long, y=lat, group=group), fill='grey', size=.2,color='green', data=Parcels, alpha=0)
SDMap
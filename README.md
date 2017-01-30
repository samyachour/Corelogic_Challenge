# Corelogic Grand Challenge

## The problem
The Corlelogic Grand Challengs was a competition to solve a problem for [Corelogic](https://en.wikipedia.org/wiki/CoreLogic) - an Irvine based Data Analytics and Warehousing company, providing financial, property and consumer information, analytics and business intelligence.

The problem was as follows:
> Given a specific house, how can you calculate the view obstruction for the property in all directions?

*They also provided a dataset of ~65000 houses to analyze.

### The Given Data

Corelogic's data included columns such as:

* Formatted APN (property ID)
* Lat/Long
* Address
* Square footage

Corelogic's data did not include all surrounding homes for every property. Obviously the houses on the border of this giant list of homes don't have data on all surrounding houses.

So it was incomplete, and I went searching for more data.
## The solution
My goal was to output a single number that would rate the view obstruction as accurately as possible. Other solutions to the challenge included GUIs, webapps,
### The Found Data

I used four distinct sources to solve this problem...

#### *Google Elevation API*

The Google Elevation API takes in a lat long and returns an elevation. This means that we can easily map all the surrounding elevations with a grid of points. This also means lots of API calls, and the limit for a free subscription is 2500/day - meaning I can only do a few rows at a time.

So we take a lat long, and create a bounding box.
```python    
getElevationGoogleBox(latitude + 0.002, longitude + 0.002, latitude - 0.002, longitude - 0.002, 15, 15)
```
As you can see our bounding box is 0.004&deg; (latitude) by 0.004&deg; (longitude). We also passed in "15,15" which are our column and row count.
```python   
def getElevationGoogleBox(lat1, long1, lat2, long2, rows, cols):
    incrementX = abs((lat1-lat2)/cols)
    incrementY = abs((long1-long2)/rows)

    x = lat1
    y = long1

    points = []

    for i in range(rows):
        for j in range(cols):
            points.append((x, y, getElevationGoogle(x, y)))
            y = y - incrementY

        x = x - incrementX
        y = long1

    return points
```
Which gives us a nice grid of ColxRow points.
![Scatter](images/elevationPointsScatter.png)
Which we can then map, using [matplotlib](http://matplotlib.org), as a 3D surface.
![Surface](images/elevationSurface.png)

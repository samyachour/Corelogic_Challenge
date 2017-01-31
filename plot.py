import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib import cm
from matplotlib.ticker import MaxNLocator
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.patches import Circle, PathPatch
from matplotlib import pyplot as plt
from descartes.patch import PolygonPatch
from figures import BLUE, SIZE, plot_coords, color_isvalid
import Elevation as elev

def Plot3DTriSurf(points):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    x = []
    y = []
    z = []
    
    for coord in points:
        x.append(coord[0])
        y.append(coord[1])
        z.append(coord[2] * 3)
        
        
    ax.plot_trisurf(x, y, z, linewidth=0.2)
    plt.show()
    

def Plot3DSurface(points):
    Xs, Ys, Zs = [], [], []
    
    for i in points:
        Xs.append(i[0])
        Ys.append(i[1])
        Zs.append(i[2])
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_trisurf(Xs, Ys, Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)
    
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))
    
    fig.tight_layout()
            
    plt.show()
    
def Plot3DSurfaceWithPatch(points):
    Xs, Ys, Zs = [], [], []
    
    for i in points:
        Xs.append(i[0])
        Ys.append(i[1])
        Zs.append(i[2])
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_trisurf(Xs, Ys, Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)
    
    p = Circle((Xs[0], Ys[0]), 100)
    ax.add_patch(p)
    art3d.pathpatch_2d_to_3d(p, z=Zs[0], zdir="z")
    
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))
    
    fig.tight_layout()
            
    plt.show()    
    
def Plot3DScatter(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for coord in points:
        ax.scatter(coord[0], coord[1], coord[2])
        
    plt.show()
    
def Plot3DScatterSP(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    for coord in points:
        ax.scatter(elev.convertLLSP(coord[0], coord[1])[0], elev.convertLLSP(coord[0], coord[1])[1], coord[2])
        
    plt.show()
    
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
        
    ax.set_title('Polygon')
    
def plotData2D(data):
    
    for index, row in data.iterrows():
        plotMultiPolygon(row['Parcel'])
        for i in row['House']:
            plotMultiPolygon(i)
            
def plotLOS2D(poly, lines):
    fig = plt.figure(1, figsize=SIZE, dpi=90)
    ax = fig.add_subplot(121)
    
    plot_coords(ax, poly.exterior, alpha=0)
    patch = PolygonPatch(poly, facecolor=color_isvalid(poly), edgecolor=color_isvalid(poly, valid=BLUE), alpha=0.5, zorder=2)
    ax.add_patch(patch)
    
    annotateNum = 0
    for line in lines:
        for point in line:
            if annotateNum == 5:
                ax.scatter(point[0], point[1])
                ax.annotate(point[2], (point[0],point[1]))
        annotateNum += 1
            
    plt.show()
            
def Plot3DSurfaceWithPatches(points, patches, height, lines=[]):
    Xs, Ys, Zs = [], [], []
    
    for i in points:
        Xs.append(i[0])
        Ys.append(i[1])
        Zs.append(i[2])
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_trisurf(Xs, Ys, Zs, cmap=cm.jet, linewidth=0)
    fig.colorbar(surf)
    
    for i in patches:
        for j in i[0]:
            ax.add_patch(j)
            art3d.pathpatch_2d_to_3d(j, z=i[1], zdir="z")
    
    for line in lines:
        for point in line:
            ax.scatter(point[0], point[1], point[2])
            
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.zaxis.set_major_locator(MaxNLocator(5))
    
    ax.set_zlim3d(0,height)
    
    #fig.tight_layout()
            
    plt.show()
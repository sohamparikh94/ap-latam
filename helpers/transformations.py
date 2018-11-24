from shapely.geometry import box, shape, mapping
from rasterio.windows import Window
from functools import partial
import pyproj
from shapely.ops import transform

"""
Returns a ploygon object with the coordinates projected from source to destination CRS

Parameters
-------------------- 
shape : shapely.geometry.polygon.Polygon Object
src_crs : CRS of the source system
dst_crs : CRS of the destination system

"""
def reproject_shape(shape, src_crs, dst_crs):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init=src_crs['init']),
        pyproj.Proj(init=dst_crs['init']))
    return transform(project, shape)

"""
Given a raster file and a list of shapes, returns the list of shapes that intersect with the raster file

Parameters
-------------------- 
raster : Raster image. Rasterio object
shapes : Polygon shape files. Fiona object
returnCoord : If True, Returns only the geospatial coordinates of the transformed shapes
              Else, Returns the shape object, coordinates of polygon its CRS and 
                    the coordinates of the transformed shape in theraster system
window(Optional) : A window object specifying the specific window in the raster to taken intersection with.
                   If given:  Consider it, else take full raster object.

"""
def getOverlappingShapes(raster, shapes, returnCoord = False, window = None):    
    if window != None:
        fullBox = window
    else:
        fullBox = Window(0, 0, raster.width, raster.height)
    
    fullWindow = box(*raster.window_bounds(fullBox))
    
    matchingShapes = []
    for i in range(len(shapes)):

        t = reproject_shape(shape(shapes[i]['geometry']), shapes.crs, raster.crs)
        intersect = t.intersection(fullWindow)
        if intersect.area > 0 :
            matchingShapes.append([shapes[i], shape(shapes[i]['geometry']), t])
            
    if returnCoord == True:
        matchingShapes = [mapping(x[2]) for x in matchingShapes]
    
    return(matchingShapes)


"""
Given a Window based on a raster and a shape object, returns the ratio/total area of overlap between
the shape and the window

Parameters
-------------------- 
raster : Raster object
window : Rasterio Window object
shapeDict : Dict containing geospatial coordinates
ratio : If true, returns the ratio of intersection area to full window area, else returns intersection area

"""
def getIntersectionArea(raster, window, shapeDict, ratio = True):
    window_box = box( * raster.window_bounds(window))
    
    if(type(shapeDict)==list):
        shp = shape(shapeDict[0])
        
        for i in range(1,len(shapeDict)):
            shp = shp.union(shape(shapeDict[i]))            
    else:        
        shp = shape(shapeDict)
    
    intersection = shp.intersection(window_box)
    
    boxArea = window_box.area
    interArea = intersection.area
    
    if ratio == True:
        return ( interArea / float(boxArea) )
    else:

def generateWindowsWithMasks(window_width = 1000, window_height = 1000, step_size = 100):
    count = 0
    e = all_raster_files('asd')
    for k in range(len(e)):
        r = rasterio.open(e[k])
        shapes = getOverlappingShapes(r, vector, returnCoord=True)
        if len(shapes) == 0:
            continue
        mask = getBinaryMask(r, shapes)
        for i in range(0, r.width - window_width, step_size):
            for j in range(0,r.height - window_height, step_size):

                w = Window(i, j, window_width, window_height)
                wbox = box(*r.window_bounds(w))

                #Reads all 3 bands and concatenates them
                img = np.dstack([r.read(i,window=w) for i in range(1,4)])

                window_mask = mask[w.row_off:(w.row_off+w.height) , w.col_off:(w.col_off+w.width)]
                intersectionArea = 1 - np.sum(window_mask)/1000000;
                window_mask = window_mask*255  #Convert 0-1 array to 0-255
                if (intersectionArea > 0.05):
                    count += 1
                    name = e[k].split('/')[-1].split('.')[0] + str(i) + "_" + str(j)
                    print("{} {} Area : {} Name:{}".format(i,j,intersectionArea, name))
                    imsave("./Patches/" + name + "img.jpg", img)
                    imsave("./Patches/" + name + "mask.jpg", window_mask)
                    
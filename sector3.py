from shapely.geometry import Point, Polygon, MultiPolygon, mapping
import math
import numpy as np
#import matplotlib as mpl
import matplotlib.pyplot as plt
from descartes.patch import PolygonPatch
import geopandas as gpd
#import georasters as gr
from rasterstats import zonal_stats, raster_stats

import rasterio
import rasterio.plot
# read file
path="./data/LU_1985.tif"
src=rasterio.open(path)

def drawSectors(center,radius,sectors,start,steps):
	end = 360 + start # end of circle in degrees

	# prepare parameters
	if start > end:
		start = start - 360
	else:
		pass

	step_angle_width = (end-start) / steps
	sector_width = (end-start) / sectors
	steps_per_sector = int(math.ceil(steps / sectors))
	
	global features
	features = []
	for x in xrange(0,int(sectors)):
		segment_vertices = []

		# first the center and first point
		segment_vertices.append(polar_point(center, 0,0))
		segment_vertices.append(polar_point(center, start + x*sector_width,radius))

		# then the sector outline points
		for z in xrange(1, steps_per_sector):
			segment_vertices.append((polar_point(center, start + x * sector_width + z * step_angle_width,radius)))

		# then again the center point to finish the polygon
		segment_vertices.append(polar_point(center, start + x * sector_width+sector_width,radius))
		segment_vertices.append(polar_point(center, 0,0))

		# create feature
		features.append(Polygon(segment_vertices))

	polys2 = gpd.GeoSeries(features)
	global df2
	df2 = gpd.GeoDataFrame({'geometry':polys2,'id':range(sectors)})
	df2.to_file("./output/sectors3.shp")
	
	global res   #raster
	res= zonal_stats(df2, path)   #raster's path
        df_stat = gpd.GeoDataFrame(res)
	#print df_stat

	global res1   #raster
	res1= raster_stats(df2, path, stats="*", copy_properties=True)   #raster's path
        df_stat1 = gpd.GeoDataFrame(res1)
	print df_stat1

# helper function to calculate point from relative polar coordinates (degrees)
def polar_point(origin_point, angle,  distance):
	return [origin_point.x + math.sin(math.radians(angle)) * distance, origin_point.y + math.cos(math.radians(angle)) * distance]

def plotResult():
	plt.figure()
	ax = plt.axes()
	ax.set_aspect('equal')

	df2.plot(ax=ax, edgecolor="grey",facecolor="white", linewidth=0.25, alpha=.5)

	val=src.read()
	#msk=src.read_masks(1)
	msk1=val
	np.place(msk1,msk1!=1,0)
	rasterio.plot.show(msk1)
	rasterio.plot.show((src,1))
	rasterio.plot.show_hist(src,6)

	#ax=plt.gca()
	#patches=[PolygonPatch(x["geometry"],edgecolor="black",facecolor="none",linewidth=2) for x in df2]
	#ax.add_collection(mpl.collections.PatchCollection(patches, match_oringal=True))

	plt.show()

def main():
   	# initial parameters for segmentation
	bounds = src.bounds
	x0,y0 = (bounds[2]+bounds[0])/2, (bounds[3]+bounds[1])/2
	center = Point(x0,y0)
	
	radius = math.sqrt((bounds[0]-bounds[2])**2 + (bounds[1]-bounds[3])**2)
	sectors = 32 # number of sectors in the circle (12 means 30 degrees per sector)
	start = 22.5 # start of circle in degrees
	steps = 45 # subdivision of circle. The higher, the smoother it will be
	
	drawSectors(center,radius/3,sectors,start,steps)
	#drawSectors(center,radius/4,sectors,start,steps)
	plotResult()
	
if __name__ == "__main__":
	main()

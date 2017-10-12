from shapely.geometry import Point, Polygon, MultiPolygon, mapping
import math
import numpy as np
import matplotlib.pyplot as plt
from descartes.patch import PolygonPatch
import geopandas as gpd

# read file
df1 = gpd.GeoDataFrame.from_file("./data/bd.shp")
	
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
	df2.to_file("./output/sectors.shp")
	
	global res   #shapefile
	res=gpd.overlay(df2,df1,how='intersection')	 #res_union=gpd.overlay(df1,df2,how='union')
	res.to_file("./output/result.shp")

# helper function to calculate point from relative polar coordinates (degrees)
def polar_point(origin_point, angle,  distance):
	return [origin_point.x + math.sin(math.radians(angle)) * distance, origin_point.y + math.cos(math.radians(angle)) * distance]

def plotResult():
	plt.figure()
	ax = plt.axes()
	ax.set_aspect('equal')
	#ax=df1.plot(color="blue",alpha=0.1)
	df2.plot(ax=ax, color="green", alpha=0.45)
	res.plot(ax=ax, color="red", alpha=1)
	plt.show()

def main():
   	# initial parameters for segmentation
	bounds=df1.total_bounds
	x0,y0 = (bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2
	center = Point(x0,y0)
	
	radius = math.sqrt((bounds[0]-bounds[2])**2 + (bounds[1]-bounds[3])**2)
	sectors = 8 # number of sectors in the circle (12 means 30 degrees per sector)
	start = 0 # start of circle in degrees
	steps = 45 # subdivision of circle. The higher, the smoother it will be
	
	drawSectors(center,radius/2,sectors,start,steps)
	plotResult()
	print res
	
if __name__ == "__main__":
	main()

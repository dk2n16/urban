import os, shutil
from osgeo import gdal
import numpy as np 
import pandas as pd
import subprocess

class MosaicRasters:
	"""Class to copy binary rasters from folder by going through each iso in the folder. Mosaicks all rasters into global raster"""

	def __init__(self, parent_folder, prefix, year):

		self.parent_folder = parent_folder
		self.prefix = prefix
		self.year = year
		self.df = pd.read_csv('src/WPGP_ISO_Country_codes.csv')
		self.df = self.df['iso_id'].tolist()

	def make_list_of_folders_in_parent(self):
		"""List folders. return list of folders and ISOS"""
		folders_list = os.listdir(self.parent_folder)
		return folders_list


	def check_all_rasters_present_for_year(self, folders_list):
		"""Loop through all folders and check that all rasters for year are present. Print missing rasters and total number as well as countries' folders that are missing"""
		tiffs_present = []
		tiffs_missing = []
		for folder in folders_list:
			iso = folder[-3:]
			tiff_name = os.path.join(self.parent_folder, folder, '{0}{1}_{2}.tif'.format(self.prefix, iso, self.year))
			if os.path.exists(tiff_name):
				tiffs_present.append(tiff_name)
			else:
				tiffs_missing.append(tiff_name)
		return tiffs_present, tiffs_missing

	def check_for_missing_isos(self, folders_list, tiffs_missing):
		"""Folders in directory against countries in iso.csv"""
		isos = []
		for folder in folders_list:
			isos.append(folder[-3:])
		f = open('log/missing_isos/missing_countries_{0}.txt'.format(self.year), 'w')
		diff_isos = set(self.df) - set(isos)
		for iso in list(diff_isos):
			f.write(iso + ' \n')
		f.close()

	def check_for_missing_tiffs(self, tiffs_missing):
		"""Missing tiffs within each country"""
		if len(tiffs_missing) > 0:
			f = open('log/missing_tiffs/missing_tiffs_{0}.txt'.format(self.year), 'w')
			for tiff in tiffs_missing:
				f.write(tiff + ' \n')
			f.close()

	def make_tiff_list(self, tiffs_present):
		"""Make tiff list to use to make vrt"""
		if not os.path.exists('datain/{0}'.format(self.year)):
			os.mkdir('datain/{0}'.format(self.year))
		f = open('datain/{0}/tiff_list.txt'.format(self.year), 'w')
		for tiff in tiffs_present:
			f.write(tiff + '\n')
		#Write something to loop through tiffs missing and add the 2014 urban raster for those isos to the tiff list. ###################
		f.close()

	def make_vrt(self):
		"""List rasters and make VRT on local folder relative to location of rasters --> C:/OSGeo4W64/bin/gdalbuildvrt.exe"""
		mosaic_folder = 'datain/{0}'.format(self.year)
		# GLOBAL EXTENT gdal_command = 'C:/OSGeo4W64/bin/gdalbuildvrt.exe -tr 0.00083333333 0.00083333333 -te -180.001249265 -72.0004161771 180.001249294 84.0020831987 -input_file_list {0} {1}'.format(os.path.join(mosaic_folder, 'tiff_list.txt'), os.path.join(mosaic_folder, 'urban_{0}_VRT.vrt'.format(self.year)))
		gdal_command = 'gdalbuildvrt -tr 0.00083333333 0.00083333333 -input_file_list {0} {1}'.format(os.path.join(mosaic_folder, 'tiff_list.txt'), 'urban_{0}_VRT.vrt'.format(self.year))
		subprocess.call(gdal_command, shell=True)


	def mosaic_rasters(self):
		"""Mosaic rasters in local folder ----> C:/OSGeo4W64/bin/gdal_translate.exe"""
		# if not os.path.exists('dataout/{0}'.format(self.year)):
		# 	os.mkdir('dataout/{0}'.format(self.year))
		if not os.path.exists('dataout/{0}'.format(self.year)):
			os.mkdir('dataout/{0}'.format(self.year))
		vrt_file = 'urban_{0}_VRT.vrt'.format(self.year)
		#GLOBAL EXTENT #gdal_command = 'C:/OSGeo4W64/bin/gdal_translate.exe -ot Byte \
		#-of GTIFF -tr 0.00083333333 0.00083333333 CHECK THIS-projwin -180.001249265 -72.0004161771 180.001249294 84.0020831987 CHECK THIS \
		#-a_nodata 255 -co COMPRESS=LZW -co PREDICTOR=2 -co BIGTIFF=YES {0} dataout/{1}/urban_0_1_ND_{1}.tif'.format(vrt_file, self.year)
		gdal_command = 'gdal_translate -ot Byte \
		-of GTIFF -a_nodata 255 -co COMPRESS=LZW -co PREDICTOR=2 -co BIGTIFF=YES urban_2015_VRT.vrt dataout/{0}/urban_1_0_ND_{0}.tif'.format(self.year)
		#subprocess.call(['gdal_translate', 'urban_2015_VRT.vrt', 'dataout/{0}/urban_2015_1_0_ND.tif'], shell=True)
		#subprocess.call(gdal_command, shell=True)
		#gdal_command = "gdalwarp urban_2015_VRT.vrt dataout/2015/urban_2015_1_0_ND.tif"
		subprocess.call(gdal_command, shell=True)





class ReclassifyBinary:
	"""Class to reclassify 1_0_ND global raster to 1_ND global raster"""

	def __init__(self, path_to_raster, year):

		self.path_to_raster = path_to_raster
		self.year = year

	def reclassify_raster(self):
		"""Reclassify raster at path_to_raster from 1_0_ND to 1_ND ----> C:/OSGeo4W64/bin/gdal_calc.py"""
		gdal_command = "gdal_calc.py -A {1} --outfile='dataout/{0}/urban_1_ND_{0}.tif' \
		--calc='1*(A==1) + 255*(A==0)' --NoDataValue=255 --type=Byte --co=COMPRESS=LZW --co PREDICTOR=2 --co BIGTIFF=YES".format(self.year, self.path_to_raster)
		subprocess.call(gdal_command, shell=True)

if __name__ == "__main__":
	#years = range(2015, 2021)
	#for year in years:
	#	mosaic_urban = MosaicRasters()
	mosaic = MosaicRasters('tmp_data', 'BSGM_Extentsprj_2014-2020_', 2015)
	folders_list = mosaic.make_list_of_folders_in_parent()
	tiffs_present, tiffs_missing = mosaic.check_all_rasters_present_for_year(folders_list)
	mosaic.check_for_missing_isos(folders_list, tiffs_missing)
	mosaic.check_for_missing_tiffs(tiffs_missing)
	mosaic.make_tiff_list(tiffs_present)
	mosaic.make_vrt()
	mosaic.mosaic_rasters()
	reclassify = ReclassifyBinary('dataout/2015/urban_1_0_ND_2015.tif', 2015)
	reclassify.reclassify_raster()








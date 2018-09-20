import unittest, os

from mosaic_reclassify_binary import MosaicRasters


class MosaicReclassifyTest(unittest.TestCase):

	def setUp(self):
		self.mosaic_class_true = MosaicRasters('tmp_data', 'BSGM_Extentsprj_2014-2020_', 2015)
		self.mosaic_class_false = MosaicRasters('tmp_data', 'BSGM_Extentsprj_2014-2020_', 2021)

	def tearDown(self):
		del self.mosaic_class_true

	def test_object_instantiated(self):
		self.assertEqual(self.mosaic_class_true.parent_folder, 'tmp_data')
		self.assertEqual(self.mosaic_class_true.prefix, 'BSGM_Extentsprj_2014-2020_')
		self.assertEqual(self.mosaic_class_true.year, 2015)

	def test_all_folders_listed(self):
		folder_list = self.mosaic_class_true.make_list_of_folders_in_parent()
		self.assertTrue(len(folder_list) == 4)
		self.assertEqual(folder_list, ['prj_2014-2020_AGO','prj_2014-2020_BWA','prj_2014-2020_NAM','prj_2014-2020_ZMB'])

	def test_rasters_are_all_accounted_for(self):
		folder_list = self.mosaic_class_true.make_list_of_folders_in_parent()
		tiffs_present, tiffs_missing = self.mosaic_class_true.check_all_rasters_present_for_year(folder_list)
		self.assertTrue(len(tiffs_present) == 4)
		self.assertTrue(len(tiffs_missing) == 0)

	def test_log_is_made_for_missing_countries(self):
		folder_list = self.mosaic_class_true.make_list_of_folders_in_parent()
		isos = []
		for folder in folder_list:
			isos.append(folder[-3:])
		tiffs_present, tiffs_missing = self.mosaic_class_true.check_all_rasters_present_for_year(folder_list)
		self.mosaic_class_true.check_for_missing_isos(folder_list, tiffs_missing)
		log_loc = os.path.join('log/missing_isos/missing_countries_{0}.txt'.format(self.mosaic_class_true.year))
		self.assertTrue(os.path.exists(log_loc))
		with open(log_loc) as f:
			content = f.readlines()
		content = [x.strip() for x in content]
		df = self.mosaic_class_true.df
		self.assertEqual(list(set(df) - set(isos)), content)
		self.assertEqual(len(content), 245)
		self.assertFalse('BWA' in content)
		os.remove(log_loc)

	def test_log_is_made_for_missing_tiffs(self):
		folder_list = self.mosaic_class_true.make_list_of_folders_in_parent()
		log_loc = 'log/missing_tiffs/missing_tiffs_{0}.txt'.format(self.mosaic_class_true.year)
		tiffs_present, tiffs_missing = self.mosaic_class_true.check_all_rasters_present_for_year(folder_list)
		if len(tiffs_missing) > 0:
			self.mosaic_class_true.check_for_missing_tiffs(tiffs_missing)
			self.assertTrue(os.path.exists(log_loc))
			with open(log_loc) as f:
				content = f.readlines()
			content = [x.strip() for x in content]
			self.assertEqual(content, tiffs_missing)
			os.remove(log_loc)

	def test_tiff_list_is_made(self):
		folder_list = self.mosaic_class_true.make_list_of_folders_in_parent()
		tiffs_present, tiffs_missing = self.mosaic_class_true.check_all_rasters_present_for_year(folder_list)
		self.mosaic_class_true.check_for_missing_tiffs(tiffs_missing)
		self.mosaic_class_true.make_tiff_list(tiffs_present)
		self.assertTrue(os.path.exists('datain/{0}/tiff_list.txt'.format(self.mosaic_class_true.year)))

	def test_vrt_is_made(self):
		vrt_path = 'urban_{0}_VRT.vrt'.format(self.mosaic_class_true.year)
		self.mosaic_class_true.make_vrt()
		self.assertTrue(os.path.exists(vrt_path))

	def test_rasters_are_mosaicked(self):
		tiff_path = 'dataout/{0}/urban_0_1_ND_{0}.tif'.format(self.mosaic_class_true.year)
		self.mosaic_class_true.mosaic_rasters()
		self.assertTrue(os.path.exists(tiff_path))













if __name__ == "__main__":
	unittest.main()
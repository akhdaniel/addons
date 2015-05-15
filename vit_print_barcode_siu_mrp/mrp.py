import time
import math
import datetime
import calendar
import tempfile
import win32api
import win32print
import csv
import os
import shutil
import platform
from openerp.osv import osv, fields

class MaterialRequirement(osv.osv):
	_name = 'material.requirement'
	_inherit  = 'material.requirement'
	homedir = os.path.expanduser('~')

	def print_barcode(self, cr, uid, ids, context={}):
		self.process_csv(cr,uid,ids,context={})

	####################################################################################
	####################################################################################
	def process_csv(self, cr, uid, ids, context=None):
		# self.cek_folder_move(cr, uid, context)
		# with open("%s/move"%self.homedir + '/move.csv', 'wb') as f:
		with open("%s"%self.homedir + '/barcode.txt', 'wb') as f:
			writer = csv.writer(f)
			mr_obj 	= self.pool.get('material.requirement')
			for mr in mr_obj.browse(cr,uid, ids, context):
				pl_obj = self.pool.get('production.plan').browse(cr,uid,mr.plan_id.id,context)
				for plan_line in pl_obj.plan_line:
					tmpfile = writer.writerow([
						plan_line.product_id.name,
						plan_line.product_id.ean13
						])

		# import pdb;pdb.set_trace()

		# filename = tempfile.mktemp (".txt")
		filename = self.homedir + '/barcode.txt'
		win32api.ShellExecute (0,"printto",filename,'"%s"' % win32print.GetDefaultPrinter (),".",0)

	####################################################################################
	#Cek Folder dan Buat bila tidak ada
	####################################################################################
	def cek_folder_move(self, cr, uid, context=None):
		if platform.system() == 'Linux' or platform.system() == 'Windows':
			if not os.path.exists('%s/barcode' % self.homedir):
				os.mkdir('%s/barcode' % self.homedir)
				return True

MaterialRequirement()
from osv import osv, fields
import base64
import zipfile
import platform
import os
import csv

class vit_sync_master_attach(osv.osv):
	_name = "vit.sync.master.attach"
	homedir = os.path.expanduser('~')

	#################################################################################
	# Cron proses unzip 
	#################################################################################
	def cron_process_unzip_sync(self, cr, uid, context=None):
		# import pdb;pdb.set_trace()
		##############################################################################
		# Cek Dahulu Folder homedir.move_zip folder bila tidak ada akan membuat dahulu
		# Di linux /home/user/move_zip
		##############################################################################
		self.cek_folder(cr, uid, context)

		##############################################################################
		# Akses Objek mail_message dan lalukan pencarian ids berdasarkan subjec/is_imported
		##############################################################################
		mail_message_obj 	= self.pool.get('mail.message')
		mail_message_obj_ids = mail_message_obj.search(cr,uid,[('subject','=','move.csv.zip'),('is_imported','=',False)], limit=1)
		# import pdb;pdb.set_trace()
		##############################################################################
		# Cek List ids. Bila tidak kosong, Next ambil attachment_id  
		##############################################################################
		if mail_message_obj_ids != []:
			for mail_message_obj_id in mail_message_obj_ids:
				attachment_id = cr.execute('SELECT attachment_id FROM message_attachment_rel WHERE message_id = %i' % (mail_message_obj_id,))
				attachment_id = cr.fetchone()
				attachment = self.pool.get('ir.attachment').browse(cr, uid, attachment_id[0], context=context)

				#decode datas yang diperoleh
				file_data = base64.b64decode(attachment.datas)
				
				#buat file zip nya di path ex: /home/../move_zip/
				open('%s/move_zip/move.csv.zip' % self.homedir,'wb').write(file_data)

				#Proses Unzip File di folder /home/user/move_zip
				with zipfile.ZipFile('%s/move_zip/move.csv.zip' % self.homedir, "r") as z:
					z.extractall("%s/move_zip/" % self.homedir)

				#Baca csv dan kirim param mail_message_obj_id
				self.read_csv(cr, uid, mail_message_obj_id, context)


	#################################################################################
	# Read Csv 
	#################################################################################
	def read_csv(self, cr, uid, mail_message_obj_id, context=None):
		# import pdb;pdb.set_trace()
		csvfile = open('%s/move_zip/move.csv' % self.homedir,'r')
		##############################################################################
		# Simpan Di base_import_import
		##############################################################################
		base_import_pool = self.pool.get('base_import.import')
		base_id = base_import_pool.create(cr, uid, {
			'file_type' : "text/csv",
            'file': csvfile.read(),
            'file_name': "move.csv",
            'res_model': 'account.move',
            })

		##############################################################################
		# params fields dan options untuk import csvnya
		##############################################################################
		# fields = ['name', 'journal_id/.id', 'period_id/.id', 'ref', 'date', 'to_check', 'line_id/name']
		# Jika dari csv misalnya Header -- > Journal dan nilai Row Valuenya --> Non id ,
		# Maka penulisan nilai fieldsnya cukup gunakan 'journal_id' , bila nilai row nya id
		# Tambahkan /.id seperti shop_id ('shop_id' : fields.many2one('sale.shop', 'Shop'),)
		# pada csv nya berupa id ex: 1 , maka untuk validasinya fields nya --> 'shop_id/.id'
		fields = ['name', 'journal_id', 'period_id', 'ref', 'date', 'to_check','shop_id/.id', 'state', 'line_id/name', 'line_id/quantity',
				  False, False, 'line_id/debit', 'line_id/credit', 'line_id/account_id', False, 'line_id/ref',
				  False, 'line_id/reconcile_id', False, False, False, False, False, 'line_id/journal_id', False, 'line_id/partner_id',
				  False, False, False, False, 'line_id/centralisation', False, False, False, False, False, False, False,
				  'line_id/name']

		options = {'headers': True, 'quoting': '"', 'separator': ',', 'encoding': 'utf-8'}
		
		##############################################################################
		# Import Csv
		##############################################################################
		import_csv = base_import_pool.do(cr, uid, int(base_id) , fields, options, dryrun=False, context=None)
		
		##############################################################################
		# Cek import_csv jika list atau [] next ke set is_imported ke True
		##############################################################################
		if isinstance(import_csv, list) or import_csv == []:
			self.set_imported(cr,uid,mail_message_obj_id,context)
		



	####################################################################################
	# update to true 
	####################################################################################
	def set_imported(self, cr, uid, mail_message_obj_id, context=None):
		#update record jadi is_processed = True
		cr.execute("UPDATE mail_message set is_imported='t' where id = %s" % (mail_message_obj_id))


				
	####################################################################################
	#Cek Folder dan Buat bila tidak ada
	####################################################################################
	def cek_folder(self, cr, uid, context=None):
		if platform.system() == 'Linux':
			if not os.path.exists('%s/move_zip' % self.homedir):
				os.mkdir('%s/move_zip' % self.homedir)
				return True



	#################################################################################
	# Cron proses unzip 
	#################################################################################
	def cron_process_unzip_sync_stock(self, cr, uid, context=None):
		##############################################################################
		# Cek Dahulu Folder homedir.move_zip folder bila tidak ada akan membuat dahulu
		# Di linux /home/user/move_zip
		##############################################################################
		self.cek_folder_stock(cr, uid, context)

		##############################################################################
		# Akses Objek mail_message dan lalukan pencarian ids berdasarkan subjec/is_imported
		##############################################################################
		mail_message_obj 	= self.pool.get('mail.message')
		mail_message_obj_ids = mail_message_obj.search(cr,uid,[('subject','=','stock.csv.zip'),('is_imported','=',False)], limit=1)
		# import pdb;pdb.set_trace()
		##############################################################################
		# Cek List ids. Bila tidak kosong, Next ambil attachment_id  
		##############################################################################
		if mail_message_obj_ids != []:
			for mail_message_obj_id in mail_message_obj_ids:
				attachment_id = cr.execute('SELECT attachment_id FROM message_attachment_rel WHERE message_id = %i' % (mail_message_obj_id,))
				attachment_id = cr.fetchone()
				attachment = self.pool.get('ir.attachment').browse(cr, uid, attachment_id[0], context=context)

				#decode datas yang diperoleh
				file_data = base64.b64decode(attachment.datas)
				
				#buat file zip nya di path ex: /home/../move_zip/
				open('%s/stock_zip/stock.csv.zip' % self.homedir,'wb').write(file_data)

				#Proses Unzip File di folder /home/user/move_zip
				with zipfile.ZipFile('%s/stock_zip/stock.csv.zip' % self.homedir, "r") as z:
					z.extractall("%s/stock_zip/" % self.homedir)

				#Baca csv dan kirim param mail_message_obj_id
				self.read_csv_stock(cr, uid, mail_message_obj_id, context)


	#################################################################################
	# Read Csv 
	#################################################################################
	def read_csv_stock(self, cr, uid, mail_message_obj_id, context=None):
		# import pdb;pdb.set_trace()
		csvfile = open('%s/stock_zip/stock.csv' % self.homedir,'r')
		##############################################################################
		# Simpan Di base_import_import
		##############################################################################
		base_import_pool = self.pool.get('base_import.import')
		base_id = base_import_pool.create(cr, uid, {
			'file_type' : "text/csv",
            'file': csvfile.read(),
            'file_name': "stock.csv",
            'res_model': 'stock.move',
            })

		##############################################################################
		# params fields dan options untuk import csvnya
		##############################################################################
		# fields = ['name', 'journal_id/.id', 'period_id/.id', 'ref', 'date', 'to_check', 'line_id/name']
		# Jika dari csv misalnya Header -- > Journal dan nilai Row Valuenya --> Non id ,
		# Maka penulisan nilai fieldsnya cukup gunakan 'journal_id' , bila nilai row nya id
		# Tambahkan /.id seperti shop_id ('shop_id' : fields.many2one('sale.shop', 'Shop'),)
		# pada csv nya berupa id ex: 1 , maka untuk validasinya fields nya --> 'shop_id/.id'
		fields = ['name', 'picking_id', 'origin', 'product_id', 'product_qty', 'product_uom','product_uos','location_id', 'location_dest_id', 'date','date_expected','shop_id']
		options = {'headers': True, 'quoting': '"', 'separator': ',', 'encoding': 'utf-8'}
		
		##############################################################################
		# Import Csv
		##############################################################################
		import_csv = base_import_pool.do(cr, uid, int(base_id) , fields, options, dryrun=False, context=None)
		
		##############################################################################
		# Cek import_csv jika list atau [] next ke set is_imported ke True
		##############################################################################
		if isinstance(import_csv, list) or import_csv == []:
			self.set_imported_stock(cr,uid,mail_message_obj_id,context)
		



	####################################################################################
	# update to true 
	####################################################################################
	def set_imported_stock(self, cr, uid, mail_message_obj_id, context=None):
		#update record jadi is_processed = True
		cr.execute("UPDATE mail_message set is_imported='t' where id = %s" % (mail_message_obj_id))


				
	####################################################################################
	#Cek Folder dan Buat bila tidak ada
	####################################################################################
	def cek_folder_stock(self, cr, uid, context=None):
		if platform.system() == 'Linux':
			if not os.path.exists('%s/stock_zip' % self.homedir):
				os.mkdir('%s/stock_zip' % self.homedir)
				return True
	



	
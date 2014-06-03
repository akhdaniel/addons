import logging
from osv import osv, fields
import time
import datetime
from openerp import netsvc
import openerp.tools
from openerp.tools.translate import _
import csv
import os
import zipfile
from shutil import make_archive
import shutil
import base64
import platform


_logger = logging.getLogger(__name__)

class vit_sync_slave_uploader(osv.osv):
	_name = "vit.sync.slave.uploader"
	homedir = os.path.expanduser('~')
	# path = '/home/wn/papua'


	####################################################################################
	# proses import dari menu More..
	####################################################################################
	def menu_process_am_export(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		# import pdb;pdb.set_trace()
		active_ids 		= context['active_ids']
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_process_am_export(cr, uid, active_ids, context)

	####################################################################################
	# proses import dari menu More  stok move
	####################################################################################
	def menu_process_sm_export(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		import pdb;pdb.set_trace()
		active_ids 		= context['active_ids']

		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_process_sm_export(cr, uid, active_ids, context)


	####################################################################################
	# proses import dari Cron Job, puilih yang masih is_processed = False
	# limit records
	# panggil dari cron job (lihat di xml)
	####################################################################################
	def cron_process_export(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		# import pdb;pdb.set_trace()
		move_obj = self.pool.get('account.move')
		active_ids 	= move_obj.search(cr,uid,[('is_exported','=',False),('state','=','posted')], limit=10)
		_logger.info('CRON --> processing move_obj from cron. active_ids=%s' % (active_ids))
		
		if active_ids != []:
		 	for active_id in active_ids:
		 		self.actual_process_am_export(cr, uid, [active_id], context)
		 	# else:
		 	# 	_logger.info('CRON --> Tidak Ada Id yang akan di export = %s' % (active_ids))
		# active_ids 	= stock_move_obj.search(cr,uid,[('is_exported','=',False)], limit=10)
		# _logger.info('processing stock_move_obj from cron. active_ids=%s' % (active_ids)) 
		# self.actual_process_sm_export(cr, uid, active_ids, context)

	####################################################################################
	# actual process
	#	1. create move.csv from account.move
	#	2. create stock_picking.csv from stock.picking.in
	#	3. zip file csvs
	#	4. upload ke server via FTP/HTTP
	####################################################################################
	def actual_process_am_export(self, cr, uid, active_ids, context=None):
		# import pdb;pdb.set_trace()
		# self.update_shop_id(cr,uid,active_ids,context)
		# self.get_shop_id(cr,uid,active_ids,context)
		self.process_move(cr, uid, active_ids, context)
		self.zip_files_move(cr, uid, context)
		
		# self.send_email (cr, uid, context)
		return True

	####################################################################################
	# actual process
	#	1. create stock.csv from account.move
	#	2. create stock_picking.csv from stock.picking.in
	#	3. zip file csvs
	#	4. upload ke server via FTP/HTTP
	####################################################################################
	def actual_process_sm_export(self, cr, uid, active_ids, context=None):
		
		self.process_stock_picking(cr, uid, active_ids, context)

		self.zip_files_stock(cr, uid, context)
		return True
	

	##############################################################################
	# Fungsi untuk mengambil shop_id dari config parameter, sebelumnya harus di setting 
	# terlebih dahulu untuk value id shopnya. ex : MMK Budi Utomo > id : 11 harus sama di server.
	##############################################################################
	def get_shop_id(self, cr, uid, context=None):
		ir_config_pool = self.pool.get('ir.config_parameter')
		ir_config_pool_id = ir_config_pool.search(cr,uid,[('key','=','key.pos')],context =context)
		shop_id = self.pool.get('ir.config_parameter').browse(cr, uid, ir_config_pool_id[0], context=context)
		return shop_id.value
		
	####################################################################################
	# Fungsi update shop id
	####################################################################################
	def update_shop_id(self,cr,uid,active_ids,context=None):
		# import pdb;pdb.set_trace()
		move_obj = self.pool.get('account.move')
		pos_session_pool = self.pool.get('pos.session')
		pos_config_pool = self.pool.get('pos.config')
		
		for move in move_obj.browse(cr,uid, active_ids, context):
			#Dapat move.ref yang bisa direlasikan dengan pos.session untuk diperoleh config_id
			pos_session_id = pos_session_pool.search(cr,uid,[('name','=',move.ref)],context=context)
			for session in pos_session_pool.browse(cr,uid, pos_session_id, context):
				cr.execute("UPDATE account_move set shop_id=%s where id = %s" % (str(session.config_id.id), active_ids[0]))
				return True
	
	####################################################################################
	#	1. cari account_move dan account_move_line yang exported = false
	#	2. tulis ke file account_move.csv
	####################################################################################
	def process_move(self, cr, uid, active_ids,context=None):
		#########################################################################
		# open file csv and process account move
		#########################################################################
		self.cek_folder_move(cr, uid, context)
		with open("%s/move"%self.homedir + '/move.csv', 'wb') as f:
			writer = csv.writer(f)
	
			#########################################################################
			# 1. process account move
			#########################################################################
			_logger.info('processing from cron. active_ids=%s' % (active_ids)) 
			writer.writerow([
				'name',
				'journal_id',
				'period_id',
				'ref',
				'date',
				'to_check',
				'shop_id',
				'state',
				'line.name',
				'line.quantity',
				'line.product_uom_id.name',
				'line.product_id.name',
				'line.debit',
				'line.credit',
				'line.account_id.code',
				#'line.move_id.name',
				'line.narration',
				'line.ref',
				'line.statement_id.name',
				'line.reconcile_id.name',
				'line.reconcile_partial_id.name',
				#'line.reconcile',
				'line.amount_currency',
				'line.amount_residual_currency',
				'line.amount_residual',
				'line.currency_id.code',
				'line.journal_id.code',
				#'line.period_id. ',
				'line.blocked',
				'line.partner_id.name',
				'line.date_maturity',
				'line.date',
				'line.date_created',
				'line.analytic_lines',
				'line.centralisation',
				'line.balance',
				'line.state',
				'line.tax_code_id.code',
				'line.tax_amount',
				'line.invoice',
				'line.account_tax_id.name',
				'line.analytic_account_id.code',
				'line.company_id.name'
			
				])

			move_obj 	= self.pool.get('account.move')
			for move in move_obj.browse(cr,uid, active_ids, context):
				
				###############################################################
				# skip if already exported
				###############################################################
				if move.is_exported == True:
					continue

				###############################################################
				# write account.move row
				###############################################################
				move_header = [
					move.name,
					move.journal_id.name,
					move.period_id.code ,
					move.ref,
					move.date,
					move.to_check,
					self.get_shop_id(cr, uid,context),
					move.state
				]
				i = 0

				for line in move.line_id:
					if i==0:
						header = move_header
					else:
						header = ["","","","","","","",""]
					writer.writerow( header + [
						line.name,
						line.quantity,
						line.product_uom_id.name ,
						line.product_id.name,
						line.debit,
						line.credit,
						line.account_id.code,
						#line.move_id.name,
						line.narration,
						line.ref,
						line.statement_id.name ,
						line.reconcile_id.name ,
						line.reconcile_partial_id.name ,
						#line.reconcile,
						line.amount_currency,
						line.amount_residual_currency,
						line.amount_residual,
						line.currency_id.code ,
						line.journal_id.code ,
						#line.period_id. ,
						line.blocked,
						line.partner_id.name,
						line.date_maturity,
						line.date,
						line.date_created,
						line.analytic_lines,
						line.centralisation,
						line.balance,
						line.state,
						line.tax_code_id.code,
						line.tax_amount,
						line.invoice.name,
						line.account_tax_id.name,
						line.analytic_account_id.code,
						line.company_id.name 
					])
					i= i +1 

				###############################################################
				# set is_processed = True 
				###############################################################
				cr.execute("UPDATE account_move set is_exported='t', exported_date='%s' where id = %s" % 
					(datetime.datetime.now(), move.id))

	####################################################################################
	#	1. cari stock.picking.out dan move_lines yang exported = false
	#	2. tulis ke file stock.csv
	####################################################################################
	def process_stock_picking(self, cr, uid, active_ids, context=None):
		self.cek_folder_stock(cr, uid, context)
		with open("%s/stock"%self.homedir  + '/stock.csv', 'wb') as f:
			writer = csv.writer(f)
	
			#########################################################################
			# 1. process stock picking out 
			#########################################################################
			_logger.info('processing from cron. active_ids=%s' % (active_ids)) 
			writer.writerow([
				'name',
				'picking_id',
				'origin',
				'product_id',
				'product_qty',
				'product_uom',
				'product_uos',
				'location_id',
				'location_dest_id',
				'date',
				'date_expected',
				'shop_id'
				])

			stock_obj 	= self.pool.get('stock.move')
			for stock in stock_obj.browse(cr,uid, active_ids, context):
				
				###############################################################
				# skip if already exported
				###############################################################
				if stock.is_exported == True:
					continue

				###############################################################
				# write stock.move row
				###############################################################
				writer.writerow([
					stock.name,
					stock.picking_id.name,
					stock.origin,
					stock.product_id.name,
					stock.product_qty,
					stock.product_uom.name,
					stock.product_uos.name,
					stock.location_id.name,
					stock.location_dest_id.name,
					stock.date,
					stock.date_expected,
					self.get_shop_id(cr, uid,context)
					
					])

				###############################################################
				# set is_processed = True 
				###############################################################
				cr.execute("UPDATE stock_move set is_exported='t', exported_date='%s' where id = %s" % 
					(datetime.datetime.now(), stock.id))
	####################################################################################
	# zip move.csv dan stock.csv
	####################################################################################
	def zip_files_move(self, cr, uid, context=None):
		##Cek folder dan buat folder bila belum ada##
		# import pdb;pdb.set_trace()
		self.cek_folder_move(cr, uid, context)
		#Cari Root File
		for root, dirs, files in os.walk('%s/move' % self.homedir):
			for file in files:
				#Buat Zip Saat
				my_archive = make_archive(file,'zip',"%s/move" % self.homedir)
				_logger.info('CRON --> Proses Zip file %s done di root=%s' % (file,self.homedir))

				zipfile = open('%s/move.csv.zip' % self.homedir,'r')
				attachment_pool = self.pool.get('ir.attachment')

				#Simpan Di ir.attachment
				attachment_id = attachment_pool.create(cr, uid, {
				  	'name': "move.csv.zip",
            		'datas': base64.encodestring(zipfile.read()),
            		'datas_fname': "move.csv.zip",
            		'res_model': 'account.move',
            		})
				# import pdb;pdb.set_trace()
				thread_pool = self.pool.get('mail.thread')
				
				#Cari Id untuk email master.kokarfi@gmail.com
				partner_obj = self.pool.get('res.partner')
				partner_id_server = partner_obj.search(cr,uid,[('name','=','master.kokarfi@gmail.com')])

				#Buat String waktu untuk label 
				t = datetime.datetime.now()
				date_str = t.strftime('%m/%d/%Y')
				subject = t.strftime('%m/%d/%Y %X')

				#Kirim Variable dengan message_post()
				# post_vars = {'subject': "Client move.csv.zip per %s" % subject,'body': "Ini adalah Pesan dari Clien per tanggal %s" % subject,'partner_ids': partner_id_server,'attachment_ids':[attachment_id],}
				post_vars = {'subject': "move.csv.zip",'body': "Ini adalah Pesan dari Clien per tanggal %s" % subject,'partner_ids': partner_id_server,'attachment_ids':[attachment_id],}

				thread_pool.message_post(cr, uid, False,type="comment",subtype="mt_comment",context=context,**post_vars)
				_logger.info('CRON --> Proses Pengirimiman move.zip ke master.kokarfi@gmail.com .. Done!! ' )
				
				return attachment_id
	


	def zip_files_stock(self, cr, uid, context=None):
		##Cek folder dan buat folder bila belum ada##
		import pdb;pdb.set_trace()
		self.cek_folder_stock(cr, uid, context)
		#Cari Root File
		for root, dirs, files in os.walk('%s/stock' % self.homedir):
			for file in files:
				#Buat Zip Saat
				my_archive = make_archive(file,'zip',"%s/stock" % self.homedir)
				_logger.info('CRON --> Proses Zip file %s done di root=%s' % (file,self.homedir))

				zipfile = open('%s/stock.csv.zip' % self.homedir,'r')
				attachment_pool = self.pool.get('ir.attachment')

				#Simpan Di ir.attachment
				attachment_id = attachment_pool.create(cr, uid, {
				  	'name': "stock.csv.zip",
            		'datas': base64.encodestring(zipfile.read()),
            		'datas_fname': "stock.csv.zip",
            		'res_model': 'stock.move',
            		})
				# import pdb;pdb.set_trace()
				thread_pool = self.pool.get('mail.thread')
				
				#Cari Id untuk email master.kokarfi@gmail.com
				partner_obj = self.pool.get('res.partner')
				partner_id_server = partner_obj.search(cr,uid,[('name','=','master.kokarfi@gmail.com')])

				#Buat String waktu untuk label 
				t = datetime.datetime.now()
				date_str = t.strftime('%m/%d/%Y')
				subject = t.strftime('%m/%d/%Y %X')

				#Kirim Variable dengan message_post()
				# post_vars = {'subject': "Client move.csv.zip per %s" % subject,'body': "Ini adalah Pesan dari Clien per tanggal %s" % subject,'partner_ids': partner_id_server,'attachment_ids':[attachment_id],}
				post_vars = {'subject': "stock.csv.zip",'body': "Ini adalah Pesan dari Clien per tanggal %s" % subject,'partner_ids': partner_id_server,'attachment_ids':[attachment_id],}

				thread_pool.message_post(cr, uid, False,type="comment",subtype="mt_comment",context=context,**post_vars)
				_logger.info('CRON --> Proses Pengirimiman stock.zip ke master.kokarfi@gmail.com .. Done!! ' )
				
				return attachment_id

	####################################################################################
	#Cek Folder dan Buat bila tidak ada
	####################################################################################
	def cek_folder_move(self, cr, uid, context=None):
		if platform.system() == 'Linux' or platform.system() == 'Windows':
			if not os.path.exists('%s/move' % self.homedir):
				os.mkdir('%s/move' % self.homedir)
				return True
	

	####################################################################################
	#Cek Folder dan Buat bila tidak ada
	####################################################################################
	def cek_folder_stock(self, cr, uid, context=None):
		if platform.system() == 'Linux' or platform.system() == 'Windows':
			if not os.path.exists('%s/stock' % self.homedir):
				os.mkdir('%s/stock' % self.homedir)
				return True
	

vit_sync_slave_uploader()
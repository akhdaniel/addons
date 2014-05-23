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

_logger = logging.getLogger(__name__)

class vit_sync_slave_uploader(osv.osv):
	_name = "vit.sync.slave.uploader"
	path = '/home/wn/papua'


	####################################################################################
	# proses import dari menu More..
	####################################################################################
	def menu_process_am_export(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		
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
		active_ids 	= move_obj.search(cr,uid,[('is_exported','=',False)], limit=10)
		_logger.info('processing move_obj from cron. active_ids=%s' % (active_ids)) 
		self.actual_process_am_export(cr, uid, active_ids, context)

		active_ids 	= stock_move_obj.search(cr,uid,[('is_exported','=',False)], limit=10)
		_logger.info('processing stock_move_obj from cron. active_ids=%s' % (active_ids)) 
		self.actual_process_sm_export(cr, uid, active_ids, context)

	####################################################################################
	# actual process
	#	1. create move.csv from account.move
	#	2. create stock_picking.csv from stock.picking.in
	#	3. zip file csvs
	#	4. upload ke server via FTP/HTTP
	####################################################################################
	def actual_process_am_export(self, cr, uid, active_ids, context=None):
		self.process_move(cr, uid, active_ids, context)
		self.zip_files(cr, uid, context)
		
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
		process_stock_picking(cr, uid, active_ids, context)

		zip_files(cr, uid, context)
		return True
	
	####################################################################################
	#	1. cari account_move dan account_move_line yang exported = false
	#	2. tulis ke file account_move.csv
	####################################################################################
	def process_move(self, cr, uid, active_ids, context=None):
		#########################################################################
		# open file csv and process account move
		#########################################################################
		with open(self.path + '/move.csv', 'wb') as f:
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
					move.to_check
				]
				i = 0

				for line in move.line_id:
					if i==0:
						header = move_header
					else:
						header = ["","","","","",""]
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
	def process_stock_picking(self, cr, uid, context=None):
		with open(path + '/move.csv', 'wb') as f:
			writer = csv.writer(f)
	
			#########################################################################
			# 1. process stock picking out 
			#########################################################################
			_logger.info('processing from cron. active_ids=%s' % (active_ids)) 
			move_obj 	= self.pool.get('account.move')
			writer.writerow([
				'name',
				'line.company_id.name'
				])
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
					move.to_check
				]
				i = 0

				for line in move.line_id:
					if i==0:
						header = move_header
					else:
						header = ["","","","","",""]
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
	# zip move.csv dan stock.csv
	####################################################################################
	def zip_files(self, cr, uid, context=None):
		#Cari Root File
		for root, dirs, files in os.walk(self.path):
			for file in files:
				#Buat Zip Saat
				my_archive = make_archive(file,'zip',"%s" % self.path)
				_logger.info('Proses Zip file %s done di root=%s' % (file,self.path))

				zipfile = open('/home/wn/move.csv.zip','r')
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
				
				return attachment_id
	
	def unzip_import(self, cr, uid, context=None):
		import pdb;pdb.set_trace()
		print "HELLO unzip_import"
		_logger.info('Proses Unzip')
		# return True

		#unzip
		#import : account_move account_move_line.
		#import : stock_picking stock_picking_line
vit_sync_slave_uploader()

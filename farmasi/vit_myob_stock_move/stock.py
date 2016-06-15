from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import datetime
import logging
import os
from openerp.tools.translate import _
import openerp
import csv

_logger = logging.getLogger(__name__)

class stock_move(osv.osv):
	_name 		= "stock.move"
	_inherit 	= "stock.move"

	def action_export_myob(self, cr, uid, context=None):
		##########################################################
		# id line product_request_line yang diselect
		##########################################################
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_process(cr, uid, active_ids, context=context)

	_columns 	= {
		'is_myob_export': fields.boolean("Exported to MYOB?")
	}

	def cron_export_myob(self, cr, uid, context=None):
		active_ids = self.search(cr, uid, [
			'|',('location_id','=','GBA/Stock'),('location_dest_id','=','GOJ/Stock'),
			('is_myob_export','=', False),
			('state','=','done')], context=context)
		if active_ids:
			self.actual_process(cr, uid, active_ids, context=context)
		else:
			print "no stock move to export"
		return True

	def actual_process(self, cr, uid, ids, context=None):
		headers=[
			"no_batch"			,
			"tgl_pengambilan"	,
			"nomor_mo"			,
			"kode_barang"		,
			"lokasi"			,
			"quantity"			,
			"harga_per_unit"	,
			"statis"			,
			"no_akun"			,
			"statis"			,
			"statis"			,
			"statis"			,
		]

		myob_export = self.pool.get('stock.myob_export')
		i = 0

		mpath = openerp.modules.get_module_path('vit_myob_stock_move')

		dtim = time.strftime("%Y-%m-%d %H:%M:%S")
		dbname = cr.dbname
		
		csvfile = open(mpath + '/static/'+dbname+'-stock-'+ dtim +'.csv', 'wb')
		csvwriter = csv.writer(csvfile, delimiter ='	')
		csvwriter.writerow( [ h.upper() for h in headers ])
		
		cr.execute("delete from stock_myob_export")

		j = 0

		for stock_move in self.browse(cr, uid, ids, context=context):

			if stock_move.is_myob_export == False:
				i = i +1
				self.write(cr, uid, stock_move.id, {'is_myob_export':True}, context=context)

				x = time.strptime(stock_move.date, "%Y-%m-%d %H:%M:%S")
				tgl_pengambilan = time.strftime("%d/%m/%Y", x)

				kode_barang = ""
				if stock_move.product_id.default_code:
					kode_barang = stock_move.product_id.default_code[:6]

				data = {
					"no_batch"			: stock_move.name,
					"tgl_pengambilan"	: tgl_pengambilan,
					"nomor_mo"			: stock_move.origin,
					"kode_barang"		: kode_barang,
					"lokasi"			: stock_move.location_id.name,
					"quantity"			: stock_move.product_uom_qty,
					"harga_per_unit"	: stock_move.product_id.standard_price,
					"statis"			: "STATIS",
					"no_akun"			: stock_move.product_id.categ_id.property_stock_valuation_account_id.code,
					"statis"			: "STATIS",
					"statis"			: "STATIS",
					"statis"			: "STATIS",
				}
				myob_export.create(cr, uid, data, context=context)

				csvwriter.writerow( [data[v] for v in headers  ] )

				# data = {'nama_perusahaan':''}
				myob_export.create(cr, uid, data, context=context)
				csvwriter.writerow([])

		csvfile.close()
		cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s Stock Move to Export ' % (i) )			

class stock_myob_export(osv.osv):
	_name 		= "stock.myob_export"
	_columns 	= {
		"no_batch"			:	fields.char("No Batch"),
		"tgl_pengambilan"	:	fields.char("Tgl Pengambilan"),
		"nomor_mo"			:	fields.char("Nomor MO"),
		"kode_barang"		:	fields.char("Kode Barang"),
		"lokasi"			:	fields.char("Lokasi"),
		"quantity"			:	fields.char("Quantity"),
		"harga_per_unit"	:	fields.char("Harga per unit"),
		"statis"			:	fields.char("Statis"),
		"no_akun"			:	fields.char("No akun"),
		"statis"			:	fields.char("Statis"),
		"statis"			:	fields.char("Statis"),
		"statis"			:	fields.char("Statis"),
	}

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

class purchase_order(osv.osv):
	_name 		= "purchase.order"
	_inherit 	= "purchase.order"

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
		active_ids = self.search(cr, uid, [('is_myob_export','=', False),('state','=','approved')], context=context)
		if active_ids:
			self.actual_process(cr, uid, active_ids, context=context)
		else:
			print "no po to export"
		return True

	def actual_process(self, cr, uid, ids, context=None):
		headers=[
			'nama_perusahaan' 	,
			'statis1' 			,
			'statis2' 			,
			'statis3' 			,
			'statis4' 			,
			'statis5' 			,
			'statis6' 			,
			'statis7' 			,
			'no_po' 			,
			'tgl' 				,
			'no_pr' 			,
			'statis8' 			,
			'statis9' 			,
			'kode_barang' 		,
			'qty' 				,
			'nama_barang' 		,
			'harga_unit' 		,
			'statis10' 			,
			'statis11' 			,
			'harga_x_qty' 		,
			'statis12' 			,
			'statis13' 			,
			'statis14' 			,
			'statis15' 			,
			'statis16' 			,
			'kode_pajak' 		,
			'statis17' 			,
			'nilai_ppn' 		,
			'statis18' 			,
			'statis19' 			,
			'statis20' 			,
			'statis21' 			,
			'statis22' 			,
			'statis23' 			,
			'statis24' 			,
			'statis25' 			,
			'kode_currency' 	,
			'nilai_kurs'		,
			'statis26' 			,
			'statis27' 			,
			'statis28' 			,
			'statis29' 			,
			'statis30' 			,
			'statis31' 			,
			'order' 			,
			'statis32' 			,
			'statis33' 			,
			'location_id' 		,
			'statis34' 			,
			'statis35' 			,
		]

		myob_export = self.pool.get('purchase.myob_export')
		i = 0

		mpath = openerp.modules.get_module_path('vit_myob_po')

		dtim = time.strftime("%Y-%m-%d %H:%M:%S")
		csvfile = open(mpath + '/static/po-'+ dtim +'.csv', 'wb')
		csvwriter = csv.writer(csvfile)
		csvwriter.writerow( [ h.upper() for h in headers ])
		
		cr.execute("delete from purchase_myob_export")

		for po in self.browse(cr, uid, ids, context=context):
			if po.is_myob_export == False:
				i = i +1
				self.write(cr, uid, po.id, {'is_myob_export':True}, context=context)
				if po.currency_id.name == 'IDR':
					kurs = 1
				else:
					kurs = po.currency_id.rate_silent

				x = time.strptime(po.date_order, "%Y-%m-%d %H:%M:%S")
				po_date = time.strftime("%d/%m/%Y", x)

				j = 0

				for po_line in po.order_line:
					# if po_line.taxes_id:
					# 	kode_pajak = ",".join(po_line.taxes_id.name)
					# else:
					# 	kode_pajak = ""
					nama_perusahaan = po.partner_id.ref
					po_name = po.name
					data = {
						'nama_perusahaan' 	: nama_perusahaan,
						'statis1' 			: "",
						'statis2' 			: "",
						'statis3' 			: "",
						'statis4' 			: "",
						'statis5' 			: "",
						'statis6' 			: "",
						'statis7' 			: "",
						'no_po' 			: po_name,
						'tgl' 				: po_date,
						'no_pr' 			: po.requisition_id.name,
						'statis8' 			: "",
						'statis9' 			: "",
						'kode_barang' 		: po_line.product_id.default_code[:6],
						'qty' 				: po_line.product_qty,
						'nama_barang' 		: po_line.product_id.name,
						'harga_unit' 		: po_line.price_unit,
						'statis10' 			: "",
						'statis11' 			: "0",
						'harga_x_qty' 		: po_line.product_qty * po_line.price_unit,
						'statis12' 			: "",
						'statis13' 			: "",
						'statis14' 			: "",
						'statis15' 			: "",
						'statis16' 			: "",
						'kode_pajak' 		: po_line.taxes_id.name,
						'statis17' 			: "0",
						'nilai_ppn' 		: po_line.product_qty * po_line.price_unit - po_line.price_subtotal,
						'statis18' 			: "0",
						'statis19' 			: "",
						'statis20' 			: "",
						'statis21' 			: "N-T",
						'statis22' 			: "0",
						'statis23' 			: "0",
						'statis24' 			: "0",
						'statis25' 			: "O",
						'kode_currency' 	: po.currency_id.name,
						'nilai_kurs'		: kurs,
						'statis26' 			: "2",
						'statis27' 			: "0",
						'statis28' 			: "0",
						'statis29' 			: "0",
						'statis30' 			: "0",
						'statis31' 			: "",
						'order' 			: po_line.product_qty,
						'statis32' 			: "0",
						'statis33' 			: "",
						'location_id' 		: po.picking_type_id.default_location_dest_id.location_id.name,
						'statis34' 			: po.partner_id.ref,
						'statis35' 			: "",
					}
					myob_export.create(cr, uid, data, context=context)

					csvwriter.writerow( [data[v] for v in headers  ] )

					# blank line if different po

					j += 1

				data = {'nama_perusahaan':''}
				myob_export.create(cr, uid, data, context=context)
				csvwriter.writerow([])

		csvfile.close()
		cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s Approved PO to Export ' % (i) )			

class myob_export(osv.osv):
	_name 		= "purchase.myob_export"
	_columns 	= {
		'nama_perusahaan' 	: fields.char("NAMA PERUSAHAAN"),
		'statis1' 			: fields.char("STATIS"),
		'statis2' 			: fields.char("STATIS"),
		'statis3' 			: fields.char("STATIS"),
		'statis4' 			: fields.char("STATIS"),
		'statis5' 			: fields.char("STATIS"),
		'statis6' 			: fields.char("STATIS"),
		'statis7' 			: fields.char("STATIS"),
		'no_po' 			: fields.char("NO PO (DARI OPEN ERP)"),
		'tgl' 				: fields.char("TGL"),
		'no_pr' 			: fields.char("NO PR (DARI OPEN ERP)"),
		'statis8' 			: fields.char("STATIS"),
		'statis9' 			: fields.char("STATIS"),
		'kode_barang' 		: fields.char("KODE BARANG"),
		'qty' 				: fields.char("QTY"),
		'nama_barang' 		: fields.char("NAMA BARANG"),
		'harga_unit' 		: fields.char("HARGA/UNIT"),
		'statis10' 			: fields.char("STATIS"),
		'statis11' 			: fields.char("STATIS"),
		'harga_x_qty' 		: fields.char("HARGA X QTY"),
		'statis12' 			: fields.char("STATIS"),
		'statis13' 			: fields.char("STATIS"),
		'statis14' 			: fields.char("STATIS"),
		'statis15' 			: fields.char("STATIS"),
		'statis16' 			: fields.char("STATIS"),
		'kode_pajak' 		: fields.char("KODE PAJAK"),
		'statis17' 			: fields.char("STATIS"),
		'nilai_ppn' 		: fields.char("NILAI PPN"),
		'statis18' 			: fields.char("STATIS"),
		'statis19' 			: fields.char("STATIS"),
		'statis20' 			: fields.char("STATIS"),
		'statis21' 			: fields.char("STATIS"),
		'statis22' 			: fields.char("STATIS"),
		'statis23' 			: fields.char("STATIS"),
		'statis24' 			: fields.char("STATIS"),
		'statis25' 			: fields.char("STATIS"),
		'kode_currency' 	: fields.char("KODE CURRENCY"),
		'nilai_kurs' 		: fields.char("NILAI KURS"),
		'statis26' 			: fields.char("STATIS"),
		'statis27' 			: fields.char("STATIS"),
		'statis28' 			: fields.char("STATIS"),
		'statis29' 			: fields.char("STATIS"),
		'statis30' 			: fields.char("STATIS"),
		'statis31' 			: fields.char("STATIS"),
		'order' 			: fields.char("Order"),
		'statis32' 			: fields.char("STATIS"),
		'statis33' 			: fields.char("STATIS"),
		'location_id' 		: fields.char("Location ID"),
		'statis34' 			: fields.char("STATIS"),
		'statis35' 			: fields.char("STATIS"),
	}

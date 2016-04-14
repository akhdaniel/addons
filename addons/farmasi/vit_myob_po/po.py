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
			'nama_perusahaan' 	, #a
			'statis1' 			, #b
			'statis2' 			, #c
			'statis3' 			, #d
			'statis4' 			, #e
			'statis5' 			, #f
			'statis6' 			, #g
			'statis7' 			, #h
			'no_po' 			, #i
			'tgl' 				, #j
			'no_pr' 			, #k
			'statis8' 			, #l
			'statis9' 			, #m
			'kode_barang' 		, #n
			'qty' 				, #o
			'nama_barang' 		, #p
			'harga_unit' 		, #q
			'statis10' 			, #r
			'statis11' 			, #s
			'harga_x_qty' 		, #t
			'statis12' 			, #u
			'statis13' 			, #v
			'statis14' 			, #w
			'statis15' 			, #x
			'statis16' 			, #y
			'kode_pajak' 		, #z
			'statis17' 			, #aa
			'nilai_ppn' 		, #ab
			'statis18' 			, #ac
			'statis19' 			, #ad
			'statis20' 			, #ae
			'statis21' 			, #af
			'statis22' 			, #ag
			'statis23' 			, #ah
			'statis24' 			, #ai
			'statis25' 			, #aj
			'kode_currency' 	, #ak
			'nilai_kurs'		, #al
			'statis26' 			, #am
			'statis27' 			, #an
			'statis28' 			, #ao
			'statis29' 			, #ap
			'statis30' 			, #aq
			'statis31' 			, #ar
			'order' 			, #as
			'statis32' 			, #at
			'statis33' 			, #au
			'location_id' 		, #av
			'statis34' 			, #aw
			'statis35' 			, #ax
		]

		myob_export = self.pool.get('purchase.myob_export')
		i = 0

		mpath = openerp.modules.get_module_path('vit_myob_po')

		dtim = time.strftime("%Y-%m-%d %H:%M:%S")
		dbname = cr.dbname
		
		csvfile = open(mpath + '/static/'+dbname+'-po-'+ dtim +'.csv', 'wb')
		csvwriter = csv.writer(csvfile, delimiter ='	')
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

					#  konversi tax ke PPN dan N-T
					taxes=""
					# import pdb;pdb.set_trace()
					for tx in po_line.taxes_id:
						amt = tx.amount or 0.0
						if tx.type == 'percent' and amt == 0.1 : taxes="PPN"
						elif (tx.type == 'fixed' and amt == 0.0) or (tx.type == 'percent' and amt == 0.0) : taxes="N-T"
						else : taxes = "N-T"


					kode_barang = ""
					if po_line.product_id.default_code:
						kode_barang = po_line.product_id.default_code[:6]

					data = {
						'nama_perusahaan' 	: "",
						'statis1' 			: "",
						'statis2' 			: "",
						'statis3' 			: "",
						'statis4' 			: "",
						'statis5' 			: "",
						'statis6' 			: "",
						'statis7' 			: "",
						'no_po' 			: po_name,
						'tgl' 				: po_date,
						'no_pr' 			: po.requisition_id.origin or "",
						'statis8' 			: "",
						'statis9' 			: "",
						'kode_barang' 		: kode_barang,
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
						'kode_pajak' 		: taxes,
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
						'statis34' 			: po.partner_id.comment or "",
						# 'statis34' 			: po.partner_id.ref or "",
						'statis35' 			: "",
					}
					myob_export.create(cr, uid, data, context=context)

					csvwriter.writerow( [data[v] for v in headers  ] )

					# blank line if different po

					j += 1

				# data = {'nama_perusahaan':''}
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

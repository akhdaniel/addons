from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time,datetime
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class order_line(osv.osv):
	_inherit 		= "purchase.order.line"


	#######################################################################
	# cari total qty yang sudah received, dari move_ids yg status = done
	#######################################################################
	def _get_total_received(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for po_line in self.browse(cr, uid, ids , context=context):
			total = 0.0
			results[po_line.id] = total

			for move_line in po_line.move_ids:
				if move_line.state == 'done':
					total += move_line.product_uom_qty 
			results[po_line.id] = total			

		return results	

	#######################################################################
	# cari total outstanding qty 
	#######################################################################
	def _get_outstanding(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for po_line in self.browse(cr, uid, ids , context=context):
			total = 0.0
			results[po_line.id] = po_line.product_qty

			for move_line in po_line.move_ids:
				if move_line.state == 'done':
					total += move_line.product_uom_qty
			results[po_line.id] = po_line.product_qty - total			

		return results	

	#######################################################################
	# PR related function 
	#######################################################################
	def _pr_get_date(self, cr, uid, ids, field_names, arg=None, context=None):
		res={}
		for line in self.browse(cr,uid,ids,context) :
			res[line.id] = line.order_id.requisition_id.line_ids and  line.order_id.requisition_id.line_ids[0].schedule_date and datetime.datetime.strptime(line.order_id.requisition_id.line_ids[0].schedule_date, '%Y-%m-%d').strftime("%m/%d/%Y")  or ''
		return res

	def _pr_get_date_appr(self, cr, uid, ids, field_names, arg=None, context=None):
		res={}
		for line in self.browse(cr,uid,ids,context) :
			res[line.id]= line.order_id.requisition_id and line.order_id.requisition_id.approved_date and datetime.datetime.strptime(line.order_id.requisition_id.approved_date, '%Y-%m-%d').strftime("%m/%d/%Y")  or False
		return res
		
	def _pr_get_appr(self, cr, uid, ids, field_names, arg=None, context=None):
		res={}
		for line in self.browse(cr,uid,ids,context) :
			res[line.id]=line.order_id.requisition_id and line.order_id.requisition_id.user_id and line.order_id.requisition_id.user_id.id or False
		return res

	_columns 	= {
		'total_qty_received' 	: fields.function(_get_total_received, type='float', string="Received Qty"),
		'outstanding_qty' 		: fields.function(_get_outstanding, type='float', string="Outstanding Qty"),
		'bid_no' 	: fields.related('order_id','requisition_id',type='many2one',relation='purchase.requisition',string='BID',readonly=True),
		'bid_src' 	: fields.related('bid_no','origin',type='char',string='BID Source',readonly=True),
		'notes2' 	: fields.related('order_id','notes2',type='text',string='Terms & Condition',readonly=True),
		'pr_date' 	: fields.function(_pr_get_date, type='char', string="PR Date", ),
		'pr_date_appr' : fields.function(_pr_get_date_appr, type='char', string="PR Approved", ),
		'pr_approver' 	: fields.function(_pr_get_appr, type='many2one', relation='res.users', string="PR Responsibility", ),
		'invo_id' 	: fields.related('invoice_lines','invoice_id',type='many2one',relation='account.invoice',string='Invoice',readonly=True),
		'invo_date' 	: fields.related('invo_id','date_invoice',type='date',string='Invoice Date',readonly=True),
		'invo_user_id' 	: fields.related('invo_id','user_id',type='many2one',relation='res.users', string='Invoice Responsible',readonly=True),
	}
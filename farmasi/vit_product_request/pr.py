from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class purchase_requisition_line(osv.osv):
	_name 		= "purchase.requisition.line"
	_inherit 	= "purchase.requisition.line"

	def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, parent_analytic_account, analytic_account, parent_date, date, context=None):
		""" Changes UoM and name if product_id changes.
		@param name: Name of the field
		@param product_id: Changed product_id
		@return:  Dictionary of changed values
		"""
		value = {'product_uom_id': ''}
		if product_id: 
			prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			value = {'product_uom_id': prod.uom_id.id}
		if not analytic_account:
			value.update({'account_analytic_id': parent_analytic_account})
		if not date:
			value.update({'schedule_date': parent_date})
		return {'value': value}

	_columns 	= {
		'description' : fields.char('Description'),
	}


class purchase_requisition(osv.osv):
	_name 		= "purchase.requisition"
	_inherit 	= "purchase.requisition"

	def _product_names(self, cr, uid, ids, field, arg, context=None):
		results = {}
		# return harus berupa dictionary dengan key id session
		# contoh kalau 3 records:
		# {
		#      1 : 50.8,
		#      2 : 25.5,
		#      3 : 10.0
		# }

		for pr in self.browse(cr, uid, ids, context=context):
			product_names = []
			for line in pr.line_ids:
				product_names.append( "%s/%s" % (line.product_id.name , line.description) )
			results[pr.id] = ",".join(product_names)
		return results	

	def tender_in_progress(self, cr, uid, ids, context=None):
		header=[]
		for line in self.browse(cr,uid,ids,context)[0].line_ids:
			if line.product_id.is_header and line.product_id.categ_id.display_name.find('Non Starting Material')==-1:
				# since inly 1 id, and return value is [(id,name)]
				header.append(line.product_id.name_get()[0][1]) 
		if header:
			raise osv.except_osv(_('Warning!'), _('Produk berikut harus diganti menjadi produk dengan serial no 10 digit \n%s.') % '\n'.join(header))
		self.write(cr,uid,ids,{'approved_date': time.strftime('%Y-%m-%d')})
		return super(purchase_requisition,self).tender_in_progress( cr, uid, ids, context=None)

	def _get_confirmed_po(self, cr, uid, ids, fields, arg, context=None):
		res = {}
		# {
		#	1: po1,
		#	2: po2,
		#	3: po3
		# }

		# list of record object: [ob1, ob2, ob3]
		prs = self.browse(cr, uid, ids, context=context)

		for pr in prs:
			res[pr.id] = False
			
			for po in pr.purchase_ids:
				if po.state == 'approved':
					res[pr.id] = po
		return res
	
	_columns 	= {
		'product_names' : fields.function(_product_names, type='char', string="Products"),
		'approved_date' : fields.date(string="approved date" , readonly=True,),
		'confirmed_po_id': fields.function(_get_confirmed_po,
								 method=True,
								 string='Confirmed PO',
								 type='many2one',
								 relation="purchase.order",
								 store=False,
								 help = 'Confirmed PO'),
	}
		
	_defaults = {
		'approved_date': lambda *a: time.strftime('%Y-%m-%d'),
		}

	def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
		department_id = False
		res = super(purchase_requisition, self)._prepare_purchase_order(cr, uid, requisition, supplier, context=context)
		b = self.pool.get('vit.product.request').search(cr, uid, [('name','=', requisition.origin)])
		pr = self.pool.get('vit.product.request').browse(cr, uid, b)
		department_id = pr[0].department_id.id
		res.update({'department_id': department_id})
		return res 
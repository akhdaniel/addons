from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.product.product
import openerp.addons.decimal_precision as dp
import time

class lph(osv.osv):
	_name 		= "vit_dist_payment.lph"
	_columns 	= {
		'name'			: fields.char('Number'),
		'date'			: fields.date('Date'),
        'user_id'		: fields.many2one('res.users', 'Salesman', select=True, ),
        'based_route_id'  : fields.many2one('master.based.route','Route'),		
        'lph_line_ids'    : fields.many2many(
			'account.invoice',   	# 'other.object.name' dengan siapa dia many2many
			'lph_invoice',          # 'relation object'
			'lph_id',               # 'actual.object.id' in relation table
			'invoice_id',           # 'other.object.id' in relation table
			'Invoice',              # 'Field Name'
			domain="[('state','=','open')]",
			required=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'On Progress'),
            ('done', 'Done'),
            ], 'Status', readonly=True, 
            help="Gives the status of the quotation or sales order.", 
            select=True),

	}

	def create(self, cr, uid, vals, context=None):
		ctx = None
		new_name= self.pool.get('ir.sequence').get(cr, uid, 'lph', context=ctx) or '/'
		vals.update({'name' : new_name}) 
		return super(lph, self).create(cr, uid, vals, context=context)

	_defaults = {
		'state' : 'draft',
		'date'  : lambda *a : time.strftime("%Y-%m-%d") ,
	}

	def action_confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'open'},context=context)

	def action_done(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'done'},context=context)

	def action_draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'},context=context)


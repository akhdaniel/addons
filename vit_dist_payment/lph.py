from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.product.product
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _

class lph(osv.osv):
	_name 		= "vit_dist_payment.lph"
	_order = 'name desc'

	def hitung_total(self,lph_line_ids):
		total = 0.0
		for lphl in lph_line_ids:
			total = total + lphl.amount_total 
		return total 

	def hitung_balance(self,lph_line_ids):
		total = 0.0
		for lphl in lph_line_ids:
			total = total + lphl.residual 
		return total 

	def hitung_paid(self,lph_line_ids):
		total = 0.0
		for lphl in lph_line_ids:
			total = total + ( lphl.amount_total - lphl.residual )
		return total 

	def _calc_total(self, cr, uid, ids, field, arg, context=None):
		results = {}
		lphs = self.browse(cr, uid, ids, context=context) 
		for lph in lphs:
			results[lph.id] = self.hitung_total(lph.lph_line_ids)
		return results

	def _calc_balance(self, cr, uid, ids, field, arg, context=None):
		results = {}
		lphs = self.browse(cr, uid, ids, context=context)
		for lph in lphs:
			results[lph.id] = self.hitung_balance(lph.lph_line_ids)
		return results

	def _calc_paid(self, cr, uid, ids, field, arg, context=None):
		results = {}
		lphs = self.browse(cr, uid, ids, context=context)
		for lph in lphs:
			results[lph.id] = self.hitung_paid(lph.lph_line_ids)
		return results

	_columns 	= {
		'name'			  : fields.char('Number'),
		'date'			  : fields.date('Date'),
		'user_id'		  : fields.many2one('res.users', 'Salesman', select=True,required=True),
		'based_route_id'  : fields.many2one('master.based.route','Route',required=True),		
		'lph_line_ids'    : fields.many2many(
			'account.invoice',   	# 'other.object.name' dengan siapa dia many2many
			'lph_invoice',          # 'relation object'
			'lph_id',               # 'actual.object.id' in relation table
			'invoice_id',           # 'other.object.id' in relation table
			'Invoice',              # 'Field Name'
			domain="[('state','=','open'),\
			('user_id','=',user_id),\
			('is_draft_lph','=',False),\
			('based_route_id','=',based_route_id)]",
			#('is_cn','=',False),\
			required=True),
		'total'           : fields.function(_calc_total, type="float", string="Total"),
		'balance'         : fields.function(_calc_balance, type="float", string="Balance"),
		'total_paid'      : fields.function(_calc_paid, type="float", string="Total Paid"),
		'state'           : fields.selection([
			('draft', 'Draft'),
			('open', 'On Progress'),
			('done', 'Done'),
			], 'Status', readonly=True, 
			select=True),
		'voucher_id'	  : fields.many2one('vit_dist_payment.voucher', 'Voucher'),
		'voucher_total'	  : fields.related('voucher_id', 'total' , type="float", 
			relation="vit_dist_payment.voucher", string="Voucher Total", store=True)
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

	def onchange_based_route(self, cr, uid, ids, date, user_id, based_route_id, context=None):

		results = {}
		if not based_route_id:
			return results

		##############################################################################
		# 
		##############################################################################
		inv_obj = self.pool.get('account.invoice')
		inv_ids = inv_obj.search(cr, uid, [
			('state','=','open'),
			('type','in',('out_invoice','out_refund')),
			('is_cn','=',False),
			('is_draft_lph','=',False),
			('user_id','=',user_id),
			('based_route_id','=',based_route_id) ], context=context)

		#insert many2many records
		lph_line_ids = [(6,0,inv_ids)]
		results = {
			'value' : {
				'lph_line_ids' : lph_line_ids
			}
		}
		return results

	def onchange_voucher_id(self, cr, uid, ids, user_id, voucher_id, voucher_total, context=None):
		results = {}
		if not voucher_id:
			return results
		voc_obj = self.pool.get('vit_dist_payment.voucher')
		tot_get = voc_obj.search(cr,uid,[('id','=',voucher_id),('received_from','=',user_id)],context=context)
		v_tot = voc_obj.browse(cr,uid,tot_get)[0].total

		results =  {'value' :{'voucher_total': v_tot}}
		return results

	def action_confirm(self,cr,uid,ids,context=None):
		inv_obj = self.pool.get('account.invoice')
		pic = self.browse(cr,uid,ids[0])
		inv = pic.lph_line_ids
		for x in inv :
			idd = x.id
			inv_src = inv_obj.search(cr,uid,[('id','=',idd)])
			if inv_src != []:
				inv_br = inv_obj.browse(cr,uid,inv_src)[0]
				id_inv = inv_br.id
				id_st = inv_br.state
				if id_st == 'open' :
					inv_obj.write(cr,uid,id_inv,{'is_draft_lph':True},context=context)
		self.write(cr,uid,ids,{'state':'open'},context=context)
		#return True
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_dist_payment', 'view_lph_tree')
		view_id = view_ref and view_ref[1] or False,		
		return {
			'name' : _('Temporary View'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'vit_dist_payment.lph',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'domain' : "[('state','=','draft')]",
			#'context': "{'default_state':'open'}",#
			'nodestroy': False,
			}


	def action_done(self,cr,uid,ids,context=None):
		lph = self.browse(cr, uid, ids[0], context=context )
		if lph.voucher_id.total != lph.total_paid:
			raise osv.except_osv(_('Validate Error'),_("Nominal Voucher tidak sama dengan total pembayaran ") ) 
		inv_obj = self.pool.get('account.invoice')
		pic = self.browse(cr,uid,ids[0])
		inv = pic.lph_line_ids
		for x in inv :
			idd = x.id
			inv_src = inv_obj.search(cr,uid,[('id','=',idd)])
			if inv_src != []:
				inv_br = inv_obj.browse(cr,uid,inv_src)[0]
				id_inv = inv_br.id
				id_st = inv_br.state
				if id_st == 'open' :
					inv_obj.write(cr,uid,id_inv,{'is_draft_lph':False},context=context)

		v_id = lph.voucher_id.id
		if v_id :
			self.pool.get('vit_dist_payment.voucher').write(cr,uid,v_id,{'state':'done'},context=context)
					
		self.write(cr,uid,ids,{'state':'done'},context=context)
		return True

	def action_draft(self,cr,uid,ids,context=None):
		inv_obj = self.pool.get('account.invoice')
		pic = self.browse(cr,uid,ids[0])
		inv = pic.lph_line_ids
		for x in inv :
			idd = x.id
			inv_src = inv_obj.search(cr,uid,[('id','=',idd)])
			if inv_src != []:
				inv_br = inv_obj.browse(cr,uid,inv_src)[0].id
				inv_obj.write(cr,uid,inv_br,{'is_draft_lph':False},context=context)		
		return self.write(cr,uid,ids,{'state':'draft'},context=context)

class account_journal(osv.osv):
	_inherit = "account.journal"
	_name = "account.journal"

	_columns = {'is_cn' : fields.boolean('CN Confirmation'),}

account_journal()	
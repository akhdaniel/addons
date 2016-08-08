from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from collections import defaultdict

_logger = logging.getLogger(__name__)
PR_STATES =[('draft','Draft'),
	('pending','Pending Approval'), 
	('open','Confirmed'), 
	('onprogress','On Progress'), 
	('done','Done'),
	('reject','Rejected')]
PR_LINE_STATES =[('draft','Draft'),
	('pending','Pending Approval'), 
	('open','Confirmed'), 
	('onprogress','On Progress'), # Call for Bids in progress
	('done','Done'),# Call for Bids = PO created / done
	('reject','Rejected')]

class product_request(osv.osv):
	_name 		= "vit.product.request"
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	def _product_request_lines(self, cr, uid, ids, field, arg, context=None):
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
			for line in pr.product_request_line_ids:
				if line.product_id.name:
					product_names.append(line.product_id.name)
			results[pr.id] = ",".join(product_names)
		return results	

	_columns 	= {
		'name'	: fields.char("Number" , readonly=True),
		'date'	: fields.date("Request Date", 
			required=True, 
			readonly=True,
			states={'draft':[('readonly',False)]},
		),
		'user_id': fields.many2one('res.users', 'Requester',
			required=True, 
			readonly=True,
			states={'draft':[('readonly',False)]},
		),
		'product_request_line_ids': fields.one2many('vit.product.request.line',
			'product_request_id','Product Lines', 
			ondelete="cascade",
			readonly=True,
			states={'draft':[('readonly',False)]},
			),

		'product_request_lines': fields.function(_product_request_lines, type='char', 
			string="Product Request Lines"),

		'department_id' : fields.many2one('hr.department', 'Department',
			required=True, 
			readonly=True,
			states={'draft':[('readonly',False)]},
			),
		'category_id' : fields.many2one('product.category', 'Product Category',
			required=True, 
			readonly=True,
			states={'draft':[('readonly',False)]},
			),
		'notes'		: fields.text("Request Notes",
			readonly=True,
			states={'draft':[('readonly',False)]},
			),
		'state' : fields.selection(PR_STATES,'Status',readonly=True,required=True),
	}

	_defaults = {
		'state'				: 'draft',
		'date'	 			: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'			: lambda obj, cr, uid, context: uid,
		'name'				: '/',
	}

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		# if vals.get('name', '/') == '/':
		dept = self.pool.get('hr.department').browse(cr, uid, vals['department_id'], context=context)
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.product.request') + '/' + dept.name or '/'

		new_id = super(product_request, self).create(cr, uid, vals, context=context)

		#add followers to managers
		partner_id=dept.manager_id.user_id.partner_id.id if dept.manager_id else False
		if partner_id:
			self.write(cr, uid, new_id, {'message_follower_ids': [(4, partner_id)]})

		return new_id

	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		body = _("PR set to draft")
		self.send_followers(cr, uid, ids, body, context=context)

		self.update_line_state(cr, uid, ids, PR_STATES[0][0], context)
		return self.write(cr,uid,ids,{'state':PR_STATES[0][0]},context=context)
	
	def action_send_approval(self,cr,uid,ids,context=None):

		#set to "pending" state
		# post message
		body = _("PR sent for approval")
		self.send_followers(cr, uid, ids, body, context=context)

		self.update_line_state(cr, uid, ids, PR_STATES[1][0], context)
		return self.write(cr,uid,ids,{'state':PR_STATES[1][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "open" approved state
		body = _("PR confirmed")
		self.send_followers(cr, uid, ids, body, context=context)
		self.update_line_state(cr, uid, ids, PR_STATES[2][0], context)
		return self.write(cr,uid,ids,{'state':PR_STATES[2][0]},context=context)

	def action_onprogress(self,cr,uid,ids,context=None):
		#set to "onprogress" state
		body = _("PR on progress")
		self.send_followers(cr, uid, ids, body, context=context)
		self.update_line_state(cr, uid, ids, PR_STATES[3][0], context)
		return self.write(cr,uid,ids,{'state':PR_STATES[3][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		body = _("PR done")
		self.send_followers(cr, uid, ids, body, context=context)
		self.update_line_state(cr, uid, ids, PR_STATES[4][0], context)
		return self.write(cr,uid,ids,{'state':PR_STATES[4][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "reject" state
		body = _("PR reject")
		self.send_followers(cr, uid, ids, body, context=context)
		self.update_line_state(cr, uid, ids, PR_STATES[5][0], context)
		return self.write(cr,uid,ids,{'state':PR_STATES[5][0]},context=context)

	def update_line_state(self, cr, uid, ids, state , context=None):
		for request in self.browse(cr, uid, ids, context=context):
			line_obj = self.pool.get('vit.product.request.line')
			for line in request.product_request_line_ids:
				line_obj.write(cr, uid, line.id, {'state':state}, context=context)


	# create pr sekaligus dari product request
	def action_create_pr(self, cr, uid, ids, context=None):
		purchase_requisition  		= self.pool.get('purchase.requisition')
		purchase_requisition_line  	= self.pool.get('purchase.requisition.line')

		for prd_req in self.browse(cr, uid, ids, context=context):
			pr_line_ids = []
			for lines in prd_req.product_request_line_ids:
				pr_line_ids.append( (0,0,{
					'product_id'	: lines.product_id.id,
					'description'	: lines.name,
					'product_qty'	: lines.product_qty,
					'product_uom_id': lines.product_uom_id.id,
					'schedule_date'	: lines.date_required,
				}) )

			pr_id = purchase_requisition.create(cr, uid, {
				'name'			: self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.requisition'),
				'exclusive'		: 'exclusive',
				'warehouse_id'  : 2 ,
				'line_ids' 		: pr_line_ids,
				'origin'  		: prd_req.name
			})
			#update state dan pr_id di line product request asli
			cr.execute("update vit_product_request_line set state=%s, purchase_requisition_id=%s where product_request_id = %s",
			 ( 'onprogress', pr_id,  prd_req.id  ))

			self.write(cr, uid, prd_req.id, {'state':'onprogress'}, context=context)

			body = _("PR bid created")
			self.send_followers(cr, uid, ids, body, context=context)

			return pr_id			

	def send_followers(self, cr, uid, ids, body, context=None):
		records = self._get_followers(cr, uid, ids, None, None, context=context)
		followers = records[ids[0]]['message_follower_ids']
		self.message_post(cr, uid, ids, body=body,
						  subtype='mt_comment',
						  partner_ids=followers,
						  context=context)

class product_request_line(osv.osv):
	_name 		= "vit.product.request.line"
	_columns 	= {
		'product_request_id': fields.many2one('vit.product.request', 'Product Request'),
		'product_id' 		: fields.many2one('product.product', 'Product'),
		'name'				: fields.char("Description"),
		'product_qty' 		: fields.float('Quantity'),
		'product_qty_hand'	: fields.related('product_id', 'detail_qty_available' ,
			type="float", relation="product.product", string="Quantity On Hand",
			store=False),
		'product_qty_incoming'	: fields.related('product_id', 'detail_incoming_qty' ,
			type="float", relation="product.product", string="Incoming Quantity",
			store=False),
		'product_qty_outgoing'	: fields.related('product_id', 'detail_outgoing_qty' ,
			type="float", relation="product.product", string="Outgoing Quantity",
			store=False),
		'product_qty_avail' : fields.related('product_id', 'detail_available' , 
			type="float", relation="product.product", string="Quantity Available", 
			store=False),

		# 'product_qty_avail' : fields.float('Quantity Available' ),
		# 'product_uom_id' 	: fields.many2one('product.uom', 'Product UOM', readonly=True),
		'product_uom_id' 	: fields.many2one('product.uom', 'Product UOM' ),
		'date_required'  	: fields.date('Required Date'),
		'state' 			: fields.selection(PR_LINE_STATES,'Status',readonly=True,required=True),
		'purchase_requisition_id' : fields.many2one('purchase.requisition', 'Call for Bid',readonly=True),
		'purchase_order_id' : fields.related('purchase_requisition_id', 'confirmed_po_id',
			type="many2one", relation="purchase.order", string="RFQ/PO", store=False),
	}
	_defaults = {
		'state'				: 'draft',
	}	

	def onchange_product_id(self, cr, uid, ids, product_id, context=None):
		res = {'value': {'product_uom_id' : False, 'name':'', 'product_qty_avail':0.0}}
		product_product = self.pool.get('product.product')		
		product = product_product.browse(cr, uid, product_id, context=context)
		product_uom_po_id = product.uom_po_id.id
		res['value'].update({'product_uom_id': product_uom_po_id, 
			'name': "%s/%s" % (product.name, product.description_purchase ),
			'product_qty_avail': product.virtual_available
			})
		return res 

	
	def action_create_pr(self, cr, uid, context=None):
		##########################################################
		# id line product_request_line yang diselect
		##########################################################
		active_ids = context and context.get('active_ids', False)

		if not context:
			context = {}



		##########################################################
		# untuk setiap partner , create PO dari line PR
		##########################################################
		# prs = defaultdict(list)
		# import pdb; pdb.set_trace()
		prs = {}
		origins = []
		line_ids = []
		# import pdb; pdb.set_trace()

		for line_id in self.browse(cr, uid, active_ids, context):
			product_qty = 0.0

			if line_id.state == 'open' and line_id.purchase_requisition_id.id == False:
				
				hasil = prs.get(line_id.product_id.id, False)
				if hasil:
					product_qty =  hasil.get('product_qty',0) +  line_id.product_qty
					origins.append(line_id.product_request_id.name)
					line_ids.append(line_id.id)
				else:
					product_qty =  line_id.product_qty
					origins = [line_id.product_request_id.name]
					line_ids = [line_id.id]

				prs[ line_id.product_id.id ] = { 
					'product_qty'	 : product_qty ,
					'product_uom_id' : line_id.product_uom_id.id,
					'schedule_date'  : line_id.date_required ,
					'origins'		 : origins,
					'line_ids'		 : line_ids,
					'description'	 : line_id.name,
				}

		##########################################################
		#create PR per produk diatas
		##########################################################
		i = 0 
		# import pdb; pdb.set_trace()
		for product_id in prs.keys():
			pr_id = self.create_pr(cr, uid, product_id, prs[product_id] )
			i = i + 1

		cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s Call for Bid(s) ' % (i) )		


	def create_pr(self, cr, uid, product_id, request_line, context=None):
		purchase_requisition  		= self.pool.get('purchase.requisition')
		purchase_requisition_line  	= self.pool.get('purchase.requisition.line')

		pr_line_ids = [(0,0,{
			'product_id': product_id,
			'product_qty': request_line['product_qty'],
			'product_uom_id': request_line['product_uom_id'],
			'schedule_date': request_line['schedule_date'],
			'description': request_line['description'],
		})]

		pr_id = purchase_requisition.create(cr, uid, {
			'name': self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.requisition'),
			'exclusive'	: 'exclusive',
			'warehouse_id'  : 2 ,
			'line_ids' : pr_line_ids,
			'origin'  : ",".join(request_line['origins'])
		})


		#update state dan pr_id di line product request asli
		cr.execute("update vit_product_request_line set state=%s, purchase_requisition_id=%s where id in %s",
		 ( 'onprogress', pr_id, tuple(request_line['line_ids'])))

		return pr_id



class purchase_requisition(osv.osv):
	_name = 'purchase.requisition'
	_inherit = 'purchase.requisition'

	def unlink(self, cr, uid, ids, context=None):
		cr.execute("update vit_product_request_line set state=%s where purchase_requisition_id in %s ", ('open', tuple(ids))  )
		return super(purchase_requisition, self).unlink(cr, uid, ids, context=context)	

	def tender_done(self, cr, uid, ids, context=None):
		cr.execute("update vit_product_request_line set state=%s where purchase_requisition_id in %s ", ('done', tuple(ids))  )
		return super(purchase_requisition, self).tender_done(cr, uid, ids, context=context)	
   
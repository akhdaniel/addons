from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

####################################################################
#partner_bonus:
#
#Terisi ketika ada konfirmasi pendaftaran member baru (on aktivate partner).
#
#Proses nya:
#1. cek bisnis plan yg aktiv
#2. dari dan isikan bonus sponsor ke sponsor_id
#3. cari dan isikan bonus level ke upline_id
#4. dari dan isikan bonus pasangan ke upline_id dan sponsor_id
#
####################################################################
BONUS_SPONSOR_CODE   = 1
BONUS_PASANGAN_CODE  = 2
BONUS_LEVEL_CODE     = 3
BONUS_BELANJA	     = 4

class member_bonus(osv.osv):
	_name 		= "mlm.member_bonus"
	_columns 	= {
		'member_id' 		: fields.many2one('res.partner', 'Member'),
		'new_member_id' 	: fields.many2one('res.partner', 'Activated New Member', 
			help="Activated Member that trigger the bonus"),
			# help="Member yang diaktivasi yang menyebabkan terjadinya bonus"),
		'match_member_id'	: fields.many2one('res.partner', 'Matched Member', 
			help="Paired Member"),
			# help="Member pasangan"),
		'level' 			: fields.integer('At Level'),
		'amount'			: fields.float('Bonus Amount'),
		'trans_date'		: fields.datetime('Transaction Date'),
		'bonus_id'			: fields.many2one('mlm.bonus', 'Bonus Type'),
		'is_transfered'		: fields.boolean('Is Transfered'),	
		'description' 		: fields.char('Description'),
	}

	def addSponsor(self, cr, uid, new_member_id, sponsor_id, amount, description, context=None):

		bonus_sponsor = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_SPONSOR_CODE)], context=context)
		if not bonus_sponsor:
			raise osv.except_osv(_('Error'),_("Bonus sponsor not defined, code = 1") ) 

		data = {
			'member_id' 		: sponsor_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'level' 			: False, # pada level berapa
			'amount'			: amount,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_sponsor[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)


	def addBonusLevel(self, cr, uid, new_member_id, member_id, level, amount, description, context=None):

		bonus_sponsor = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_LEVEL_CODE)], context=context)
		if not bonus_sponsor:
			raise osv.except_osv(_('Error'),_("Bonus Level not defined, code = 3") ) 

		data = {
			'member_id' 		: member_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'level' 			: level, # pada level berapa
			'amount'			: amount,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_sponsor[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)


	def addBonusPairing(self, cr, uid, new_member_id, match_member_id, member_id, level, amount, description, context=None):
		#import pdb;pdb.set_trace()
		bonus_pasangan = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_PASANGAN_CODE)], context=context)
		if not bonus_pasangan:
			raise osv.except_osv(_('Error'),_("Bonus Pairing not defined, code = 2") ) 

		data = {
			'member_id' 		: member_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'match_member_id' 	: match_member_id, # sumber member 
			'level' 			: level, # pada level berapa
			'amount'			: amount,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_pasangan[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)

	####################################################################################
	# make invoice dari menu More..
	####################################################################################
	def action_make_invoice(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_make_invoice(cr, uid, active_ids, context)

		# res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_stock_return_picking_form')
		# res_id = res and res[1] or False
		# picking_id = self.browse(cr, uid, ids[0], context=context).picking_id.id
		# #assert len(ids) == 1, 'This option should only be used for a single id at a time'
		# return {
		# 	'name': _('Return lines'),
		# 	'view_type': 'form',
		# 	'view_mode': 'form',
		# 	'view_id': [res_id],
		# 	'res_model': 'stock.return.picking',
		# 	'type': 'ir.actions.act_window',
		# 	'target': 'current',
		# 	'context':context
		# }

	####################################################################################
	# make invoice dari Cron Job, pilih yang masih is_processed = False
	# limit records
	# panggil dari cron job (lihat di xml)
	####################################################################################
	def cron_make_invoice(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids = self.search(cr,uid, [('is_transfered','=',False)], limit=100)
		_logger.info('processing from cron. active_ids=%s' % (active_ids)) 
		self.actual_make_invoice(cr, uid, active_ids, context)

	####################################################################################
	# mulai make invoice, bisa dari menu atau dari cron job
	####################################################################################
	def actual_make_invoice(self, cr, uid, ids, context=None):

		##################################################################################
		# loop setiap record member_bonus yang id nya ids 
		# kelompokkan berdasarkan member_id, setiap 1 member => 1 invoice
		# dengan detail dari member_bonus tsb
		##################################################################################
		i = 0
		old_member_id = 0
		lines = []

		# import pdb; pdb.set_trace()

		for member_bonus in self.browse(cr,uid, ids, context):

			partner_id = member_bonus.member_id.id

			if old_member_id!=partner_id:
				if old_member_id != 0:
					self.create_supplier_invoice(cr, uid, member_bonus, old_member_id, lines, context)
					lines = []
	
			lines = self.add_invoice_lines(cr, uid, member_bonus, lines, context)
			cr.execute("UPDATE mlm_member_bonus set is_transfered='t' where id = %s" % (member_bonus.id))

			old_member_id = partner_id
			i = i + 1

		self.create_supplier_invoice(cr, uid, member_bonus, old_member_id, lines, context)

		#cr.commit()

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_mlm', 'view_member_bonus_tree')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s import(s) member_bonus' % (i) )}, 
			'name' : _('List Member Bonus'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'mlm.member_bonus',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{'search_default_sponsor': 1,'search_default_not_transfered':1, 'search_default_not_null': 1,'search_default_group_by_member':1,}",
			'nodestroy': False,
		}

	####################################################################################
	# add_invoice_lines
	####################################################################################
	def add_invoice_lines(self, cr,uid, member_bonus, lines, context):

		################################################################################
		# common variabels
		################################################################################
		partner_id 		= member_bonus.member_id

		################################################################################
		# check COA of the bonus expense
		################################################################################
		coa = member_bonus.bonus_id.coa_id
		if not coa:
			raise osv.except_osv(_('Warning'), "Please set expense COA for this bonus type: %s" %(member_bonus.bonus_id) ) 
		coa_id = coa.id

		################################################################################
		#  product line
		################################################################################
		lines.append(
			(0,0,{
				'name'			:  "%s: %s-%s" % (member_bonus.description, 
					member_bonus.new_member_id.name or '', member_bonus.match_member_id.name or '' ) ,
				'origin'		:  '%s' % (member_bonus.bonus_id.name),
				'sequence'		:  '',
				'uos_id'		:  False,
				'product_id'	:  False,
				'account_id'	:  coa_id, 
				'price_unit'	:  member_bonus.amount,
				'quantity'		:  1 , 
				'price_subtotal':  member_bonus.amount,  
				'discount'		:  0,
				'partner_id'	:  partner_id.id
			})
		)

		return lines 

	####################################################################################
	#create supplier invoice
	####################################################################################
	def create_supplier_invoice(self, cr, uid, member_bonus, partner_id, lines, context=None):

		################################################################################
		# prepare common variable
		################################################################################
		company_id 		= self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
		ap_coa_id 		= company_id.ap_coa_id
		if not ap_coa_id:
			raise osv.except_osv(_('Warning'),_("Please set AP COA for the Company") ) 


		################################################################################
		# purchase journal
		################################################################################
		journal_ids 			= self.pool.get('account.journal').search(cr, uid,[('type', '=', 'purchase'), 
								('company_id', '=', company_id.id)],limit=1)
		if not journal_ids:
			raise osv.except_osv(_('Error!'),_('Please define purchase journal for this company.')  )
		purchase_journal_id = journal_ids[0]

		################################################################################
		# cari periode_id
		################################################################################
		date_invoice 	= time.strftime("%Y-%m-%d %H:%M:%S") 
		if context==None:
			context={}
		context['account_period_prefer_normal']= True
		period_id 	= self.pool.get('account.period').find(cr,uid, date_invoice, context)[0]

		################################################################################
		# cari COA hutang bonus
		################################################################################
		ap_coa_id = company_id.ap_coa_id

		################################################################################
		# invoice data
		################################################################################
		invoice_id = self.pool.get('account.invoice').create(cr,uid,{
		    'date_invoice' 	: date_invoice,
		    'partner_id' 	: partner_id,
		    'account_id' 	: ap_coa_id.id,
		    'invoice_line'	: lines,
		    'type'			: 'in_invoice',
		    'origin'		: member_bonus.bonus_id.name,
		    'name'			: '/',
		    'period_id' 	: period_id,
		    'date_due'		: date_invoice,
		    'journal_id'	: purchase_journal_id,
		    'company_id'	: company_id.id
		    })
		_logger.info("   created supplier invoice id:%d" % (invoice_id) )

		################################################################################
		# post supplier invoice  
		################################################################################
		self.invoice_confirm(cr, uid, invoice_id, context)		

		return invoice_id

	####################################################################################
	#set open/validate
	####################################################################################
	def invoice_confirm(self, cr, uid, id, context=None):
		wf_service = netsvc.LocalService('workflow')
		wf_service.trg_validate(uid, 'account.invoice', id , 'invoice_open', cr)
		_logger.info("   validated invoice id:%d" % (id) )
		return True

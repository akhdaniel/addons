from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
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
		'new_member_id' 	: fields.many2one('res.partner', 'New Member'),
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
			raise osv.except_osv(_('Error'),_("Belum ada definisi Bonus sponsor, code = 1") ) 

		data = {
			'member_id' 		: sponsor_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'amount'			: amount,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_sponsor[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)


	def addBonusLevel(self, cr, uid, new_member_id, sponsor_id, level, amount, description, context=None):

		bonus_sponsor = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_LEVEL_CODE)], context=context)
		if not bonus_sponsor:
			raise osv.except_osv(_('Error'),_("Belum ada definisi Bonus Level, code = 3") ) 

		data = {
			'member_id' 		: sponsor_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'level' 			: level, # pada level berapa
			'amount'			: amount,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_sponsor[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)


	def addBonusPasangan(self, cr, uid, new_member_id, sponsor_id, level, amount, description, context=None):

		bonus_sponsor = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_PASANGAN_CODE)], context=context)
		if not bonus_sponsor:
			raise osv.except_osv(_('Error'),_("Belum ada definisi Bonus Level, code = 3") ) 

		data = {
			'member_id' 		: sponsor_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'level' 			: level, # pada level berapa
			'amount'			: amount,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_sponsor[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)


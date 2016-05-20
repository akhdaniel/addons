from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _


# model partner

_logger = logging.getLogger(__name__)

class partner(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"
	_columns 	= {
		'ls_client_id' 			: fields.char('LS Client ID', select=1),
		'ls_client_sid' 		: fields.char('LS SID', select=1),
		'ls_id_card_type' 		: fields.char('LS ID Card Type', select=1),

		'partner_cash_ids'		: fields.one2many('reliance.partner_cash','partner_id','LS Cash', ondelete="cascade"),
		'partner_stock_ids'		: fields.one2many('reliance.partner_stock','partner_id','LS Stock', ondelete="cascade"),
	}
	
	def get_ls_cash(self, cr, uid, ls_client_id, context=None):

		pid = self.search(cr, uid, [('ls_client_id','=',ls_client_id)], context=context)
		partner_cash = self.pool.get('reliance.partner_cash')
		_logger.warning('pid=%s' % pid)
		if pid:
			cashs = partner_cash.search_read(cr,uid,[('partner_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with ls_client_id=%s' % ls_client_id)
		return cashs 


	def get_ls_stock(self, cr, uid, ls_client_id, context=None):
		stocks = []
		pid = self.search(cr, uid, [('ls_client_id','=',ls_client_id)], context=context)
		partner_stock = self.pool.get('reliance.partner_stock')
		_logger.warning('pid=%s' % pid)
		if pid:
			stocks = partner_stock.search_read(cr,uid,[('partner_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with ls_client_id=%s' % ls_client_id)
		return stocks

	def get_ls_stock2(self, cr, uid, ls_client_sid, ls_client_id=False, context=None):
		stocks = []
		if ls_client_id:
			pid = self.search(cr, uid, [('ls_client_sid','=',ls_client_sid),('ls_client_id','=',ls_client_id)], context=context)
		else:	
			pid = self.search(cr, uid, [('ls_client_sid','=',ls_client_sid)], context=context)

		partner_stock = self.pool.get('reliance.partner_stock')
		_logger.warning('ls_client_sid=%s ls_client_id=%s' % (ls_client_sid, ls_client_id))
		if pid:
			stocks = partner_stock.search_read(cr,uid,[('partner_id','in',pid)],context=context)
		else:
			raise osv.except_osv(_('error'), 'no partner with ls_client_sid=%s ls_client_id=%s ' % (ls_client_sid, ls_client_id) ) 

		return stocks

	def get_ls_cash2(self, cr, uid, ls_client_sid, ls_client_id=False, context=None):
		cashs = []
		if ls_client_id:
			pid = self.search(cr, uid, [('ls_client_sid','=',ls_client_sid),('ls_client_id','=',ls_client_id)], context=context)
		else:	
			pid = self.search(cr, uid, [('ls_client_sid','=',ls_client_sid)], context=context)

		partner_cash = self.pool.get('reliance.partner_cash')
		_logger.warning('ls_client_sid=%s ls_client_id=%s' % (ls_client_sid, ls_client_id))
		if pid:
			cashs = partner_cash.search_read(cr,uid,[('partner_id','in',pid)],context=context)
		else:
			raise osv.except_osv(_('error'), 'no partner with ls_client_sid=%s ls_client_id=%s ' % (ls_client_sid, ls_client_id) ) 

		return cashs


class partner_cash(osv.osv):
	_name 		= "reliance.partner_cash"
	_rec_name 	= "partner_id"
	_columns 	= {
		"partner_id"	: fields.many2one('res.partner', 'Partner', select=1),
		"client_id"		: fields.related('partner_id', 'ls_client_id' , type="char", 
							relation="res.partner", string="Client ID" ),
		"date"			: fields.date("Date"),
		"cash_on_hand"	: fields.float("Cash on Hand"),
		"saldo_t1"		: fields.float("SaldoT1"),
		"saldo_t2"		: fields.float("SaldoT2"),
	}

class partner_stock(osv.osv):
	_name 		= "reliance.partner_stock"
	_rec_name 	= "stock_id"
	_columns 	= {
		"partner_id"		: fields.many2one('res.partner', 'Partner', select=1),
		"date"				: fields.date("Date", select=1),
		"client_id"			: fields.related('partner_id', 'ls_client_id' , type="char", 
								relation="res.partner", string="Client ID" ),
		"stock_id"			: fields.char("Stock ID", select=1),
		"stock_name"		: fields.char("Stock Name", select=1),
		"avg_price"			: fields.float("Avg Price"),
		"close_price"		: fields.float("Close Price"),
		"balance"			: fields.float("Balance"),
		"lpp"				: fields.float("LPP"),
		"stock_avg_value"	: fields.float("Stock Avg Value"),
		"market_value"		: fields.float("Market Value"),
		"stock_type"		: fields.char("Stock Type"),
		"sharesperlot"		: fields.char("Shares per Lot"),
	}


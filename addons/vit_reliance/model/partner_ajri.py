from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class partner(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"
	_columns = {
		'partner_ajri_product_ids'	: fields.one2many('reliance.partner_ajri_product','partner_id','Products', ondelete="cascade"),
	}

	
	def get_ajri_participant(self, cr, uid, nomor_polis, context=None):
		participants = False
		pid = self.search(cr, uid, [('nomor_polis','=',nomor_polis)], context=context)
		_logger.warning('nomor_polis=%s' % nomor_polis)

		if pid:
			participants = self.search_read(cr,uid,[('parent_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with nomor_polis=%s' % nomor_polis)
		return participants 


	def get_ajri_pemegang(self, cr, uid, nomor_partisipan, context=None):
		pemegang = False
		participant = self.search_read(cr, uid, [('nomor_partisipan','=',nomor_partisipan)], context=context)
		_logger.warning('participant=%s' % participant)

		if pid:
			pemegang = self.search_read(cr,uid,[('id','=',participant[0].parent_id.id)],context=context)
		else:
			_logger.error('no partner with nomor_partisipan=%s' % nomor_partisipan)
		return pemegang


class partner_ajri_product(osv.osv):
	_name = "reliance.partner_ajri_product"
	_columns = {
		'partner_id'		: fields.many2one('res.partner', 'Partner'),
		'product_id'		: fields.many2one('product.product', 'Product'),
		'start_date'		: fields.date('Tanggal Mulai'),
		'end_date'			: fields.date('Tanggal Selesai'),
		'status'			: fields.char('Status'),
		'up'				: fields.float('UP'),
		"total_premi"		: fields.float('Total Premi'),
		"status_klaim"		: fields.char('Status Klaim'),
		"status_bayar"		: fields.char('Status Bayar'),
		"tgl_bayar"			: fields.date('Tanggal Bayar'),
		"klaim_disetujui" 	: fields.char('Klaim Disetujui'),
	}
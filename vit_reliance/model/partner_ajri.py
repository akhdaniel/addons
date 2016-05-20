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
		'ajri_nomor_partisipan' 	: fields.char('AJRI Nomor Partisipan', select=1),
		'ajri_nomor_polis' 			: fields.char('AJRI Nomor Polis', select=1),
		'ajri_parent_id' 			: fields.many2one('res.partner','AJRI Pemegang Polis', select=1),
		'partner_ajri_product_ids'	: fields.one2many('reliance.partner_ajri_product','partner_id','AJRI Products', ondelete="cascade"),
	}

	
	def get_ajri_all_participant(self, cr, uid, nomor_polis, context=None):
		participants = False
		pid = self.search(cr, uid, [('ajri_nomor_polis','=',nomor_polis)], context=context)
		_logger.warning('ajri_nomor_polis=%s' % nomor_polis)

		if pid:
			participants = self.search_read(cr,uid,[('ajri_parent_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with nomor_polis=%s' % nomor_polis)
		return participants 

	def get_ajri_pemegang(self, cr, uid, nomor_partisipan, context=None):
		pemegang = False
		pid = self.search_read(cr, uid, [('ajri_nomor_partisipan','=',nomor_partisipan)], context=context)
		_logger.warning('participant=%s' % pid)

		if pid:
			if not pid[0]['ajri_parent_id']:
				raise osv.except_osv(_('error'),_("not linked to any ajri_parent_id") ) 
			pemegang = self.search_read(cr,uid,[('id','=',pid[0]['ajri_parent_id'][0])],context=context)
		else:
			raise osv.except_osv(_('error'),'no partner with nomor_partisipan=%s' % nomor_partisipan) 
		return pemegang

	def get_ajri_product(self, cr, uid, nomor_partisipan, context=None):
		products = False
		partner_ajri_product = self.pool.get('reliance.partner_ajri_product')
		pid = self.search(cr, uid, [('ajri_nomor_partisipan','=',nomor_partisipan)], context=context)
		_logger.warning('participant=%s' % pid)

		if pid:
			products = partner_ajri_product.search_read(cr,uid,[('partner_id','=',pid[0])],context=context)
		else:
			_logger.error('no partner with nomor_partisipan=%s' % nomor_partisipan)
		return products


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

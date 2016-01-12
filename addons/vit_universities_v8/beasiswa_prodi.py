from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class beasiswa_prodi(osv.Model):
	_name = 'beasiswa.prodi'


	_columns = {
		'name'				: fields.char('Kode',required=True,size=32),
		'date'				: fields.datetime('Tanggal ',required=True),
		'tahun_ajaran_id'	: fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'fakultas_id'		: fields.many2one('master.fakultas', 'Fakultas'),
		'prodi_id'			: fields.many2one('master.prodi', 'Prodi'),
		'product_id'		: fields.many2one('product.product', 'Discount Product', domain=[('categ_id','=','Discount Beasiswa')], help="Produk services yang memiliki tag Discount Beasiswa"),
		'limit_ipk'			: fields.float('Batas Minimal IPK',required=True,help='Batas Lolos IPK semester sebelumnya untuk mendapatkan beasiswa'),
		'amount'			: fields.float('Besarnya Beasiswa',required=True,help='Nilai potongan beasiswa'),
		'is_active'			: fields.boolean('Aktif?',size=128),
		'user_id'			: fields.many2one('res.users','User',readonly=True),
	}
	_defaults = {  
		'is_active'	:True,
		'user_id'	: lambda obj, cr, uid, context: uid,
		'date'		: lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	}

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in active state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.is_active:
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non active'))
		return super(beasiswa_prodi, self).unlink(cr, uid, ids, context=context)
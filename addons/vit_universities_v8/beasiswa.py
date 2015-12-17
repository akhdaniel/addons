from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class beasiswa_mahasiswa(osv.Model):
	_name = 'beasiswa.mahasiswa'


	_columns = {
		'name': fields.char('Kode',required=True,size=32),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'date':fields.datetime('Tanggal ',required=True),
		'is_active':fields.boolean('Aktif?',size=128),
		'limit_nilai_sma':fields.float('Batas Nilai SMA/Sederajat',required=True,help='Batas Lolos penerimaan untuk mendapatkan beasiswa'),
		'user_id':fields.many2one('res.users','User',readonly=True),
	}
	_defaults = {  
		'is_active':True,
		'user_id': lambda obj, cr, uid, context: uid,
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
				}

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in active state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.is_active:
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non active'))
		return super(beasiswa_mahasiswa, self).unlink(cr, uid, ids, context=context)
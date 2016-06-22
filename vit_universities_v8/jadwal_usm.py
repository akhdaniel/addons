from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class jadwal_usm(osv.Model):
	_name = 'jadwal.usm'

	_columns = {
		'name'				: fields.char('Kode',required=True,size=32),
		'tahun_ajaran_id'	: fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'date_start'		: fields.date('Tanggal Mulai',required=True),
		'date_end'			: fields.date('Tanggal Akhir',required=True),
		'date'				: fields.date('Tanggal Ujian',required=True),
		'is_active'			: fields.boolean('Aktif?',size=128),
		'limit'				: fields.float('Batas Maximum',required=True,help='Quota Tes'),
		'user_id'			: fields.many2one('res.users','User',readonly=True),
		'calon_mhs_ids'		: fields.one2many('res.partner','jadwal_usm_id','Calon MHS', ondelete="cascade"),
		'state'				: fields.selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],'Status',readonly=True),
		'discount'			: fields.float('Potongan Gelombang (%)'),
		'discount_tunai'	: fields.float('Potongan Tunai (%)'),
		'discount_alumni'	: fields.float('Potongan Alumni ISTN (%)'),
		'discount_lembaga'	: fields.float('Potongan Ulang Tahun Lembaga (%)'),
		'discount_karyawan'	: fields.float('Potongan Karyawan (%)'),
		'discount_ranking1'	: fields.float('Potongan Ranking 1 (%)'),
		'discount_ranking2'	: fields.float('Potongan Ranking 2 (%)'),
		'discount_ranking3'	: fields.float('Potongan Ranking 3 (%)'),
		'discount_non_ranking'	: fields.float('Potongan Non Ranking (%)'),
		'type_pendaftaran'  : fields.selection([('ganjil','Ganjil'),('genap','Genap'),('pendek','Pendek')],'Type Pendaftaran'),
	}

	_defaults = {  
		'is_active':True,
		'user_id': lambda obj, cr, uid, context: uid,
		'date_start': lambda *a: time.strftime('%Y-%m-%d'),
		'date_end': lambda *a: time.strftime('%Y-%m-%d'),
		'date': lambda *a: time.strftime('%Y-%m-%d'),
		'state': 'draft',
	}

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in active state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.is_active:
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non active'))
		return super(jadwal_usm, self).unlink(cr, uid, ids, context=context)

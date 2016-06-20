from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class beasiswa_prodi(osv.Model):
	_name = 'beasiswa.prodi'

	def _get_default_produk_beasiswa(self, cr, uid, context=None):
		product_ids = []
		#import pdb;pdb.set_trace()
		prod_obj = self.pool.get('product.product')
		product = prod_obj.search(cr,uid,[('name_template','ilike','Beasiswa')])
		if product:
			name = 'Potongan Prodi'			
			seq = -1
			code = 4
				
			product_ids.append((0,0,{'product_id':product[0],'name':name,'sequence':seq,'code':code}))
		return product_ids

	_columns = {
		'name'				: fields.char('Kode',required=True,size=32),
		'date'				: fields.datetime('Tanggal ',required=True),
		'tahun_ajaran_id'	: fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'fakultas_id'		: fields.many2one('master.fakultas', 'Fakultas',required=True),
		'prodi_id'			: fields.many2one('master.prodi', 'Prodi',required=True),

		'product_id1'		: fields.many2one('product.product', 'Potongan USM', domain=[('type','=','service')], help="Produk services"),
		'limit_nilai_sma'	:fields.float('Batas Nilai SMA/Sederajat',help='Batas Lolos penerimaan untuk mendapatkan beasiswa'),
		'amount1'			: fields.float('Besarnya Beasiswa',help='Nilai potongan beasiswa'),
		'usm_sequence'		: fields.integer('Sequence',help='Urutan proses dengan disc yang mempunyai sequence, lebih kecil itu yg diproses'),

		'product_id2'		: fields.many2one('product.product', 'Potongan Prodi', domain=[('type','=','service')], help="Produk services"),
		'limit_ipk'			: fields.float('Batas Minimal IPK',help='Batas Lolos IPK semester sebelumnya untuk mendapatkan beasiswa'),
		'amount2'			: fields.float('Besarnya Beasiswa',help='Nilai potongan beasiswa prestasi'),

		'product_id3'		: fields.many2one('product.product', 'Potongan Alumni', domain=[('type','=','service')], help="Produk services"),
		'amount3'			: fields.float('Besarnya Beasiswa',help='Nilai potongan beasiswa jika punya kerabat alumni'),		
		'alumni_sequence'	: fields.integer('Sequence',help='Urutan proses dengan disc yang mempunyai sequence, lebih kecil itu yg diproses'),

		'product_id4'		: fields.many2one('product.product', 'Potongan Karyawan', domain=[('type','=','service')], help="Produk services"),
		'amount4'			: fields.float('Besarnya Beasiswa',help='Nilai potongan beasiswa jika karyawan internal'),		
		'karyawan_sequence'	: fields.integer('Sequence',help='Urutan proses dengan disc yang mempunyai sequence, lebih kecil itu yg diproses'),

		'product_id5'		: fields.many2one('product.product', 'Potongan Ulang Tahun Lembaga', domain=[('type','=','service')], help="Produk services"),
		'amount5'			: fields.float('Besarnya Beasiswa',help='Nilai potongan beasiswa jika ulang tahun lembaga/universitas'),		
		'ultah_sequence'	: fields.integer('Sequence',help='Urutan proses dengan disc yang mempunyai sequence, lebih kecil itu yg diproses'),

		'beasiswa_prodi_detail_ids' : fields.one2many('beasiswa.prodi.detail','beasiswa_prodi_id','Beasiswa Detail'),
		'is_active'			: fields.boolean('Aktif?',size=128),
		'user_id'			: fields.many2one('res.users','User',readonly=True),
	}
	_defaults = {  
		'is_active'	: True,
		'user_id'	: lambda obj, cr, uid, context: uid,
		'date'		: lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'beasiswa_prodi_detail_ids' : _get_default_produk_beasiswa, 
	}

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in active state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.is_active:
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non active'))
		return super(beasiswa_prodi, self).unlink(cr, uid, ids, context=context)


class beasiswa_prodi_detail(osv.osv):
	_name = "beasiswa.prodi.detail"

	_columns = {
		'beasiswa_prodi_id' : fields.many2one('beasiswa.prodi','Beasiswa'),
		'name'				: fields.char('Deskripsi',required=True),
		'code'				: fields.char('Kode',required=True),
		'product_id'		: fields.many2one('product.product', 'Product', domain=[('type','=','service')],required=True, help="Produk services"),
		'limit_nilai'		: fields.float('Batas Nilai Min',help='Batas Lolos penerimaan untuk mendapatkan beasiswa'),
		'amount'			: fields.float('%',help='Nilai persentase potongan beasiswa'),
		'sequence'			: fields.integer('Sequence',required=True,help='Urutan proses dengan disc yang mempunyai sequence, lebih kecil itu yang lebih dulu diproses (jika diisi minus sequence akan diabaikan)'),
		'from_smt_id'		: fields.many2one('master.semester','Dari Smt'),
		'to_smt_id'			: fields.many2one('master.semester','Sampai Smt'),
		'uang_bangunan'		: fields.boolean('SPP'),
		'limit_nilai_max'	: fields.float('Batas Nilai Max',),
	}
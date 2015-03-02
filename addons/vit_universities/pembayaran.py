from openerp import tools
from openerp.osv import fields,osv
import datetime
import time
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class master_pembayaran(osv.Model):
	_name = "master.pembayaran"

	def create(self, cr, uid, vals, context=None):
		
		ta = vals['tahun_ajaran_id']
		t_idd = self.pool.get('academic.year').browse(cr,uid,ta,context=context).date_start				
		ta_tuple =  tuple(t_idd)
		ta_id = ta_tuple[2]+ta_tuple[3]#ambil 2 digit paling belakang dari tahun saja		

		fak = vals['fakultas_id']
		fak_id = self.pool.get('master.fakultas').browse(cr,uid,fak,context=context).kode

		jur = vals['jurusan_id']
		jur_id = self.pool.get('master.jurusan').browse(cr,uid,jur,context=context).kode

		pro = vals['prodi_id']
		pro_id = self.pool.get('master.prodi').browse(cr,uid,pro,context=context).kode

		no = fak_id+jur_id+pro_id+ta_id
		vals['name'] = no
		
		return super(master_pembayaran, self).create(cr, uid, vals, context=context)

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non aktif'))
		return super(master_pembayaran, self).unlink(cr, uid, ids, context=context)

	def _total(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for x in self.browse(cr,uid,ids,context=context):
			tot = 0.00
			for t in x.detail_product_ids:
				harga = t.total
				tot += harga
			res[x.id] = tot

		return res

	_columns = {
		'name': fields.char('Kode',size=64,readonly=True), 
		'date': fields.datetime('Tanggal',readonly=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('jurusan_id','=',jurusan_id)]",required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True), 
		'state':fields.selection([('draft','Non Aktif'),('confirm','Aktif')],'Status'),
		'detail_product_ids':fields.one2many('master.pembayaran.detail','pembayaran_id',string='Pembayaran',required=True),		
		'type': fields.selection([('flat','Flat'),('paket','Paket SKS')],'Type Pembayaran',required=True),
		'sks_plus' : fields.boolean('Bayar jika tambah SKS'),
		'total': fields.function(_total,type='char',string='Total'),
	}
	_defaults = {
		'type':'flat',
		'name': '/',
		'state':'draft',
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode template pembayaran tidak boleh sama')]

	def confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirm'},context=context)

	def draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'},context=context)

master_pembayaran()  

class master_pembayaran_detail(osv.Model):
	_name = "master.pembayaran.detail"

	def _sub_total(self, cr, uid, ids, field_name, arg, context=None):
		#import pdb;pdb.set_trace()
		res = {}
		for x in self.browse(cr,uid,ids,context=context):
			tot = 0.00
			for t in x.product_ids:
				harga = t.list_price
				tot += harga
			res[x.id] = tot

		return res

	_columns ={
		'pembayaran_id' : fields.many2one('master.pembayaran','Pembayaran ID'),
		'semester_id' : fields.many2one('master.semester','Semester',required=True),
		'product_ids':fields.many2many(
			'product.product',   	# 'other.object.name' dengan siapa dia many2many
			'product_pembayaran_detail_rel',          # 'relation object'
			'pembayaran_detail_id',               # 'actual.object.id' in relation table
			'product_id',           # 'other.object.id' in relation table
			'Pembayaran',              # 'Field Name'
			domain="[('type','=','service')]",
			required=True),
		'total': fields.function(_sub_total,type='char',string='Sub Total'),
	}
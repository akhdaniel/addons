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

		pro = vals['prodi_id']
		pro_id = self.pool.get('master.prodi').browse(cr,uid,pro,context=context).kode

		#tambah kode lokasi
		loc = vals['lokasi_kampus_id']
		loc_id = self.pool.get('master.alamat.kampus').browse(cr,uid,loc,context=context).kode

		#tambah kode reguler/ paralel
		type_mhs = vals['type_mhs_id']
		type_mhs_id = self.pool.get('master.type.mahasiswa').browse(cr,uid,type_mhs,context=context).name

		# no = fak_id+jur_id+pro_id+ta_id
		no = fak_id+pro_id+ta_id+loc_id+type_mhs_id
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
		tot = 0.00
		for x in self.browse(cr,uid,ids,context=context):	
			for t in x.detail_product_ids:
				harga = float(t.total)
				tot += harga
			res[x.id] = tot

		return res

	_columns = {
		'name': fields.char('Kode',size=64,readonly=True), 
		'date': fields.datetime('Tanggal',readonly=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		# 'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True), 
		'state':fields.selection([('draft','Non Aktif'),('confirm','Aktif')],'Status'),
		'detail_product_ids':fields.one2many('master.pembayaran.detail','pembayaran_id',string='Pembayaran'),		
		'type': fields.selection([('flat','Flat'),('paket','Paket SKS')],'Type Pembayaran',required=True),
		'sks_plus' : fields.boolean('Bayar jika tambah SKS'),
		#'total': fields.function(_total,type='char',string='Total', digits_compute=dp.get_precision('Account')),
		'total': fields.float('Total', digits_compute=dp.get_precision('Account')),
		'type_mhs_id'	: fields.many2one('master.type.mahasiswa','Type Mahasiswa'),
		'lokasi_kampus_id' : fields.many2one('master.alamat.kampus','Lokasi Kampus'),
		'uang_semester' : fields.float('Uang Semester'),
		'special_price' : fields.selection([('limited','Limited'),('unlimited','Unlimited')],string='Special Price ?',help="Limited = Uang kuliah berhenti dibayar jika total pembayaran kuliah sudah mencapai batas tertentu (Max Pembayaran), '\
											Unlimited = Uang kuliah harus terus dibayar kalau mahasiswa belum lulus"),
		'max_pembayaran' : fields.float('Max Pembayaran'),
		'is_special_price' : fields.boolean('Special Price ?',help="True jika uang kuliah dan uang semester flat perbulan"),
		'type_pendaftaran': fields.selection([('ganjil','Ganjil'),('genap','Genap'),('pendek','Pendek')],'Type Pendaftaran'),
		'is_urutan'	: fields.boolean('Special Sequence'),
		'urutan_ids':fields.one2many('master.urutan.pembayaran','pembayaran_id',string='Urutan'),
		'biaya_lainnya_ids':fields.one2many('master.biaya.lainnya','pembayaran_id',string='Biaya Lainnya'),
	}
	_defaults = {
		'type':'flat',
		'name': '/',
		'state':'draft',
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'type_pendaftaran':'ganjil',
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
			domain="[('type','=','service')]"),
		#'product_ids':fields.many2one('product.template','Pembayaran Detail',required=True,domain="[('type','=','service')]"),
		 # master price UP dan UK
		'date1'			: fields.date('Tgl Angs 1'),
        'angsuran1'		: fields.float('Angs 1'),
        'date2'			: fields.date('Tgl Angs 2'),
        'angsuran2'		: fields.float('Angs 2'),
   		'date3'			: fields.date('Tgl Angs 3'),
        'angsuran3'		: fields.float('Angs 3'),
        'date4'			: fields.date('Tgl Angs 4'),
        'angsuran4'		: fields.float('Angs 4'),
        'date5'			: fields.date('Tgl Angs 5'),
        'angsuran5'		: fields.float('Angs 5'),
        'date6'			: fields.date('Tgl Angs 6'),
        'angsuran6'		: fields.float('Angs 6'),
        'total'			: fields.float('Total'),		
		#'total': fields.function(_sub_total,type='char',string='Sub Total', digits_compute=dp.get_precision('Account')),
	}


class master_pembayaran_pendaftaran(osv.Model):
	_name = "master.pembayaran.pendaftaran"

	def create(self, cr, uid, vals, context=None):
		
		ta = vals['tahun_ajaran_id']
		t_idd = self.pool.get('academic.year').browse(cr,uid,ta,context=context).date_start				
		ta_tuple =  tuple(t_idd)
		ta_id = ta_tuple[2]+ta_tuple[3]#ambil 2 digit paling belakang dari tahun saja		

		fak = vals['fakultas_id']
		fak_id = self.pool.get('master.fakultas').browse(cr,uid,fak,context=context).kode

		pro = vals['prodi_id']
		pro_id = self.pool.get('master.prodi').browse(cr,uid,pro,context=context).kode

		#tambah kode lokasi
		loc = vals['lokasi_kampus_id']
		loc_id = self.pool.get('master.alamat.kampus').browse(cr,uid,loc,context=context).kode

		#tambah kode reguler/ paralel
		type_mhs = vals['type_mhs_id']
		type_mhs_id = self.pool.get('master.type.mahasiswa').browse(cr,uid,type_mhs,context=context).name

		# no = fak_id+jur_id+pro_id+ta_id
		no = fak_id+pro_id+ta_id+loc_id+type_mhs_id
		vals['name'] = no
		
		return super(master_pembayaran_pendaftaran, self).create(cr, uid, vals, context=context)

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non aktif'))
		return super(master_pembayaran_pendaftaran, self).unlink(cr, uid, ids, context=context)


	_columns = {
		'name': fields.char('Kode',size=64,readonly=True), 
		'date': fields.datetime('Tanggal',readonly=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		# 'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True), 
		'state':fields.selection([('draft','Non Aktif'),('confirm','Aktif')],'Status'),
		'detail_product_ids':fields.one2many('master.pembayaran.pendaftaran.detail','pembayaran_id2',string='Pembayaran'),	
		'type_mhs_id'	: fields.many2one('master.type.mahasiswa','Type Mahasiswa'),	
		'lokasi_kampus_id' : fields.many2one('master.alamat.kampus','Lokasi Kampus'),
	}
	_defaults = {
		'name': '/',
		'state':'draft',
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode template pembayaran tidak boleh sama')]

	def confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirm'},context=context)

	def draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'},context=context)

master_pembayaran_pendaftaran()  	

class master_pembayaran_pendaftaran_detail(osv.Model):
	_name = "master.pembayaran.pendaftaran.detail"


	_columns ={
		'pembayaran_id' : fields.many2one('master.pembayaran','Pembayaran ID'),
		'pembayaran_id2' : fields.many2one('master.pembayaran.pendaftaran','Pembayaran ID'),
		'product_id':fields.many2one('product.template','Pembayaran Detail',required=True,domain="[('type','=','service')]"),
		'public_price': fields.float('Harga', digits_compute=dp.get_precision('Account')),
	}


class master_pembayaran_bangunan(osv.Model):
	_name = "master.pembayaran.bangunan"

	def create(self, cr, uid, vals, context=None):
		
		ta = vals['tahun_ajaran_id']
		t_idd = self.pool.get('academic.year').browse(cr,uid,ta,context=context).date_start				
		ta_tuple =  tuple(t_idd)
		ta_id = ta_tuple[2]+ta_tuple[3]#ambil 2 digit paling belakang dari tahun saja		

		fak = vals['fakultas_id']
		fak_id = self.pool.get('master.fakultas').browse(cr,uid,fak,context=context).kode

		pro = vals['prodi_id']
		pro_id = self.pool.get('master.prodi').browse(cr,uid,pro,context=context).kode

		# no = fak_id+jur_id+pro_id+ta_id
		no = fak_id+pro_id+ta_id
		vals['name'] = no
		
		return super(master_pembayaran_bangunan, self).create(cr, uid, vals, context=context)

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus non aktif'))
		return super(master_pembayaran_bangunan, self).unlink(cr, uid, ids, context=context)


	_columns = {
		'name': fields.char('Kode',size=64,readonly=True), 
		'date': fields.datetime('Tanggal',readonly=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True), 
		'state':fields.selection([('draft','Non Aktif'),('confirm','Aktif')],'Status'),
		'detail_product_ids':fields.one2many('master.pembayaran.bangunan.detail','pembayaran_id',string='Pembayaran'),		
		'type_mhs_id'	: fields.many2one('master.type.mahasiswa','Type Mahasiswa'),
	}
	_defaults = {
		'name': '/',
		'state':'draft',
		'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode template pembayaran tidak boleh sama')]

	def confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirm'},context=context)

	def draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'},context=context)

master_pembayaran_bangunan()  	

class master_pembayaran_bangunan_detail(osv.Model):
	_name = "master.pembayaran.bangunan.detail"


	_columns ={
		'pembayaran_id' : fields.many2one('master.pembayaran.bangunan','Pembayaran ID'),
		'product_id':fields.many2one('product.product','Pembayaran Detail',required=True,domain="[('type','=','service')]"),
		'public_price': fields.float('Harga', digits_compute=dp.get_precision('Account')),
	}	


class master_urutan_pembayaran(osv.osv):
	_name = "master.urutan.pembayaran"


	_columns ={
		'pembayaran_id' 	: fields.many2one('master.pembayaran','Pembayaran ID'),
		'urutan_awal' 		: fields.integer('Urutan Awal'),
		'urutan_akhir' 		: fields.integer('Urutan Akhir'),
		'harga'				: fields.float('Harga', digits_compute=dp.get_precision('Account')),
	}


class master_biaya_lainnya(osv.osv):
	_name = "master.biaya.lainnya"

	_columns ={
		'pembayaran_id' 	: fields.many2one('master.pembayaran','Pembayaran ID'),
		'pola_bayar' 		: fields.selection([('bulan2','Bulan ke 2'),
												('praktek','Jika di KRS ada MK Praktek'),
												('seminar','Jika di KRS ada MK Seminar'),
												('ta','Jika di KRS ada MK Tugas Akhir atau sejenis'),
												('kemahasiswaan','Tiap semester 1 kali')],string='Pola Bayar'),
		'product_id'		: fields.many2one('product.product','Product',required=True,domain="[('type','=','service')]"),
		'harga'				: fields.float('Harga', digits_compute=dp.get_precision('Account')),
	}
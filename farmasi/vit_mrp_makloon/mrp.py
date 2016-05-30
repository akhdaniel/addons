from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import time
import datetime


class mrp_production(osv.osv):
	_inherit = 'mrp.production'

	_columns = {
		'is_makloon': fields.boolean("Is Makloon"),
		'makloon_partner_id': fields.many2one('res.partner', 
			'Makloon Partner', domain=[('category_id','ilike','makloon')],
			help="Partner with category makloon"),
	}


	def create_batch_number(self,cr,uid,production,context=None):
		if production.is_makloon:
			res = self.makloon_bath_number(cr, uid, production, context=context)
		else:
			res = super(mrp_production, self).create_batch_number(cr, uid, production, context=context)

		return res 

	def create(self, cr, uid, vals, context=None):	  
		mo_id = super(mrp_production, self).create(cr, uid, vals, context=context)  
		
		mrp = self.browse(cr, uid, mo_id,context=context)
		data = {
			'is_makloon'  : mrp.product_id.is_makloon,
			'makloon_partner_id' : mrp.product_id.makloon_partner_id.id
		}
		self.write(cr, uid, [mo_id], data, context=context)
		return mo_id

	def copy(self, cr, uid, id, defaults, context=None):
		
		prev_mrp = self.browse(cr, uid, id, context=context)
		# import pdb; pdb.set_trace()

		defaults['batch_number'] = False
		defaults['is_makloon'] = prev_mrp.is_makloon
		defaults['makloon_partner_id'] = prev_mrp.makloon_partner_id.id

		new_id = super(mrp_production,self).copy(cr, uid, id, defaults, context=context)
		return new_id		

	def makloon_bath_number(self, cr, uid, production, context=None):
		"""
		terdiri dari 8 digit, dengan ketentuan sebagai berikut :
		> digit 1,2 : Tahun produksi
		> digit 3	 : Bentuk sediaan produk (huruf)
		> digit 4,5 : Bulan produksi
		> dihit 6,7 : Tanggal produksi
		> digit 8	 : Urutan produksi

		Rincian kode sediaan produk	
		Kode	Sediaan
		T	Tablet
		C	Tablet hisap/kunyah
		E	Effervescent
			
		Contoh penulisan :	
		Holisticare Super Ester C Strip :	
		16T04163	
		> digit 16 : Tahun produksi	
		> huruf T  : Bentuk sediaan tablet	
		> digit 04  : Produksi bulan april	
		> digit 16  : Produksi tanggal 16	
		> digit 3	: Urutan produksi ke-3			
		"""

		# 2016-02-02 hh:mm:ss
		# 0123456789
		tahun = production.date_planned[2:4]
		bulan = production.date_planned[5:7]
		tanggal = production.date_planned[8:10]

		#Sediaan
		sediaan_code = '-'
		if production.product_id.categ_id.sediaan_id:				   
			sediaan_code =  production.product_id.categ_id.sediaan_id.code

		# jika belum punya batch number buat dari 001
		if production.batch_numbering_start == 'besar':
			new_batch_number = str(tahun+sediaan_code+bulan+tanggal+'500')
		else:
			new_batch_number = str(tahun+sediaan_code+bulan+tanggal+'001')

		batch_rule	   = str(tahun + sediaan_code + bulan +tanggal +'%')

		# 16T0416 3: SUBSTRING ( expression ,start , length )
		# 1234567 8
		cr.execute("SELECT batch_number,SUBSTRING(batch_number, 8, 1) AS Initial " \
			"FROM mrp_production " \
			"WHERE state NOT IN ('draft','cancel') " \
			"AND batch_number like %s and batch_numbering_start=%s ORDER BY Initial DESC" \
			, (batch_rule,production.batch_numbering_start))		 
		batch_ids = cr.fetchall()
		
		if batch_ids :
			seq_batch = int(batch_ids[0][1])+1
			new_seq_batch = str(seq_batch)
			new_batch_number = str(tahun+sediaan_code+bulan+tanggal+new_seq_batch) 

		return new_batch_number


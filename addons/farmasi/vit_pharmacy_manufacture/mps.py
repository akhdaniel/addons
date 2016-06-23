import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re



""" MPS (Master Production Schedule) """
class mps(osv.osv):
	_name = 'vit_pharmacy_manufacture.mps'
	_description = 'Master Production Schedule'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	_columns = {
		'name': fields.char('Name',
			readonly=True,
            states={'draft':[('readonly',False)]} ),
		'year': fields.integer('Year',
			readonly=True,
            states={'draft':[('readonly',False)]} ),
		'month' : fields.char('Month'),
		'month_id' : fields.integer('Month'),
		'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
		'created_date': fields.datetime('Created Date', required=True, readonly=True, select=True),




		'mps_detail_ids1':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Betalaktam',
			readonly=True,
			domain=[('sediaan_id','=','Betalaktam')],
            states={'draft':[('readonly',False)]} ),
		
		'mps_detail_ids2':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Syrup',
			readonly=True,
			domain=[('sediaan_id','=','Syrup')],
            states={'draft':[('readonly',False)]} ),
		
		'mps_detail_ids3':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Kapsul',
			readonly=True,
			domain=[('sediaan_id','=','Kapsul')],
            states={'draft':[('readonly',False)]} ),
		
		'mps_detail_ids4':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Soft Capsule',
			readonly=True,
			domain=[('sediaan_id','=','Soft Capsule')],
            states={'draft':[('readonly',False)]} ),
		
		'mps_detail_ids5':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Larutan',
			readonly=True,
			domain=[('sediaan_id','=','Larutan')],
            states={'draft':[('readonly',False)]} ),
		
		'mps_detail_ids6':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Injeksi',
			readonly=True,
			domain=[('sediaan_id','=','Injeksi')],
            states={'draft':[('readonly',False)]} ),





		'mps_detail_ids7':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Tablet Biasa',
			readonly=True,
			domain=[('sediaan_id','=','Tablet Biasa')],
            states={'draft':[('readonly',False)]} ),

		'mps_detail_ids8':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Tablet Coating',
			readonly=True,
			domain=[('sediaan_id','=','Tablet Coating')],
            states={'draft':[('readonly',False)]} ),

		'mps_detail_ids9':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Tablet Effervescent',
			readonly=True,
			domain=[('sediaan_id','=','Tablet Effervescent')],
            states={'draft':[('readonly',False)]} ),

		'mps_detail_ids10':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Semisolid',
			readonly=True,
			domain=[('sediaan_id','=','Semisolid')],
            states={'draft':[('readonly',False)]} ),

		'mps_detail_ids11':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Tablet (Makloon)',
			readonly=True,
			domain=[('sediaan_id','=','Tablet (Makloon)')],
            states={'draft':[('readonly',False)]} ),

		'mps_detail_ids12':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Tablet Hisap/ Kunyah (Makloon)',
			readonly=True,
			domain=[('sediaan_id','=','Tablet Hisap/ Kunyah (Makloon)')],
            states={'draft':[('readonly',False)]} ),

		'mps_detail_ids13':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_id','Forecast Details Effervescent (Makloon)',
			readonly=True,
			domain=[('sediaan_id','=','Effervescent (Makloon)')],
            states={'draft':[('readonly',False)]} ),


		
		'forecast_id': fields.many2one('vit_pharmacy_manufacture.forecast_product', 'Forecast',
			readonly=True,
            states={'draft':[('readonly',False)]} ),
		
		'state': fields.selection([
			('draft', 'Draft'),
			('open', 'Open'),
			('done', 'Done'),
			], 'Status', readonly=True, track_visibility='onchange',
			help="", select=True),

	}

	_defaults = {
				 'created_date': time.strftime('%Y-%m-%d %H:%M:%S'),
				 'state': 'draft',
	}

	def action_confirm(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'open'}, context=context)

	def action_cancel(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'draft'}, context=context)

	def action_create_wps(self, cr, uid, ids, context=None):
		""" Create Sejumlah WPS dari Urutan Week Paling Pertama """
		# import pdb; pdb.set_trace()
		sediaan_ids = self.pool.get('vit.sediaan').search(cr, uid, [], context=context)
		for sediaan in self.pool.get('vit.sediaan').browse(cr, uid, sediaan_ids, context=context):
			index = sediaan.index 
			fieldname = "self.browse(cr,uid,ids[0],).mps_detail_ids%s" % index
			for details_product in eval(fieldname):
				self.create_wps(cr,uid, ids, details_product, context=context)
		
		# self.write(cr, uid, ids, {'state':'done'}, context=context)

	def action_create_pr(self, cr, uid, ids, context=None):
		"""
		create product request jika stok bahan baku kurang di gudang
		"""
		self.create_pr(cr,uid, ids, context=context)

	def create_wps(self, cr, uid, ids, details_product, context=None):

		mps = self.browse(cr,uid,ids[0],)
		m = mps.month
		year = mps.year

		week_on_month = [1,2,3,4,5]
		week_on_year = self.get_no_week(cr,uid,ids,m)

		# import pdb;pdb.set_trace()

		batch = [details_product.w1,details_product.w2,details_product.w3,details_product.w4]
		for wm,wy,b in zip(week_on_month,week_on_year,batch):
			if b > 0.00:
				start_date  = self.get_start_date(cr, uid, ids, wy)
				end_date  = self.get_end_date(cr, uid, ids, wy)
				wps_obj = self.pool.get('vit_pharmacy_manufacture.wps').create(cr,uid,{
					'name' : 'WPS'+'/'+str(wm)+'/'+ m +'/'+ str(year) + '/' + details_product.product_id.name,
					'mps_id' : mps.id,
					'week_on_month' : wm,
					'week_on_year' : wy,
					'product_id' : details_product.product_id.id,
					'categ_id': details_product.product_id.categ_id.id,
					'batch' : b,
					'start_date' : start_date,
					'end_date' : end_date,
					'year'  : year,
					})

				""" Create MO Berdasarkan batch (b) """
				product_id = details_product.product_id.id
				batch_numbering_start = details_product.batch_numbering_start
				self.create_mo(cr,uid,ids,wm,b,wps_obj,product_id,start_date, batch_numbering_start)

	def create_pr(self, cr, uid, ids, context=None):
		"""
		loop mps details ini
		breakdown semua BOM produkc dan qty nya
		gabungkan per bahan baku plus total qty 
		for each bahan baku:
			cek stok current 
			jika kurang:
				create detail pr utk bahan baku tsb 

		create pr dengan line detail tadi
		date request = mundur 1 bulan dari tgl MPS 


		products = { 
			1: 100,
			2: 200,
			3: 300
		}

		"""

		# cari total produk yang harus diproduksi
		products = {}
		actives = {} # bahan awal aktif
		helpers = {} # bahn awal pembantu
		packages = {} # bahan pengemas
		origin  = False

		for mps in self.browse(cr, uid, ids, context=context):
			origin = mps 
			for i in range (1,6):
				fieldname = "mps.mps_detail_ids%s" % i
				for detail in eval(fieldname):
					product_id = detail.product_id.id 
					qty = products.get(product_id, 0 )
					products.update({product_id : qty + detail.production_order + detail.reminder_prev})


		# cari bahan baku produk2 tersebut
		bom_obj = self.pool.get('mrp.bom')
		product_obj = self.pool.get('product.product')
		for product_id in products.keys():

			product 	= product_obj.browse(cr, uid, product_id, context=context)
			bom_id 		= bom_obj._bom_find(cr, uid, product_id, [], context=context)
			bom 		= bom_obj.browse(cr, uid, bom_id, context=context)
			
			factor = products[product_id] 

			bom_lines, work_centers = bom_obj._bom_explode(cr, uid, bom, product, factor, [], context=context)

			print product_id, factor

			for line in bom_lines:
				product_id = line.get('product_id',0)
				product    = product_obj.browse(cr, uid, product_id, context=context)

				if product.categ_id.name == 'Bahan Awal Aktif' :
					qty = actives.get( product_id ,0)
					actives.update( { product_id : qty + line.get('product_qty',0) })

				elif product.categ_id.name == 'Bahan Awal Pembantu' :
					qty = helpers.get( product_id ,0)
					helpers.update( { product_id : qty + line.get('product_qty',0) })

				elif product.categ_id.name == 'Bahan Pengemas' :
					qty = packages.get( product_id ,0)
					packages.update( { product_id : qty + line.get('product_qty',0) })

		self.actual_create_pr(cr, uid, actives, "Bahan Awal Aktif", origin, context=context)
		self.actual_create_pr(cr, uid, helpers, "Bahan Awal Pembantu", origin, context=context)
		self.actual_create_pr(cr, uid, packages, "Bahan Pengemas", origin, context=context)

		return 

	def actual_create_pr(self, cr, uid, products, category, origin, context=None):
		product_obj = self.pool.get('product.product')
		pr_lines = []

		#req date mundur 1 bulan dari tgl MPS (origin)
		req_date = datetime.datetime(origin.year, origin.month_id, 1) - datetime.timedelta(days=60)

		for product_id in products.keys():
			
			# production order
			qty = products[product_id]
			
			# sedang di PR, in progress status
			qty_in_request = self.calculate_in_request(cr, uid, product_id, context=context)

			product = product_obj.browse(cr, uid, product_id, context=context)

			print product.name, qty, qty_in_request

			# qty yang sebenarnya diperlukan
			qty = qty - qty_in_request

			if qty > 0 and qty > product.virtual_available :
				pr_lines.append( (0,0,{
					'product_id'    : product_id,
					'name'		    : product.name,
					'description'   : product.name,
					'product_qty'   : qty - product.virtual_available,
					'product_uom_id': product.uom_id.id,
					'date_required' : req_date.strftime("%Y-%m-%d")
				}) )

		categ_id = self.pool.get('product.category').search(cr, uid, [('name','=', category)])
		if not categ_id:
			raise osv.except_osv(_('error'),_("no categ found") ) 

		# create purchase request 
		if pr_lines:
			
			department_id = self.pool.get('hr.department').search(cr, uid, [('name','=','Production')] , context=context)
			if not department_id:
				raise osv.except_osv(_('error'),_("no department Production") ) 

			pr_obj = self.pool.get('vit.product.request')
			data = {
				'date'          : req_date.strftime("%Y-%m-%d"),
				'user_id'       : uid, 
				'department_id' : department_id[0],
				'category_id'   : categ_id[0],
				'product_request_line_ids': pr_lines,
				'notes'			: 'Product request for %s' % origin.name 
			}
			pr_obj.create(cr, uid, data, context=context)

	def calculate_in_request(self, cr, uid, product_id, context=None):
		r = 0
		sql = "select sum(product_qty) from vit_product_request_line where product_id=%s and state in ('open', 'onprogress')" % product_id
		cr.execute(sql)
		hasil = cr.fetchone()
		if hasil and hasil[0]:
			r=hasil[0]
		return r 

	def get_start_date(self, cr, uid, ids, wy, context=None):
		""" Ambil Start Date Tiap Minggu nya"""
		mps = self.browse(cr,uid,ids[0],)
		year = mps.year
		y_w = str(year) +"-W"+str(wy)
		start_date_on_week = datetime.datetime.strptime(y_w + '-0',"%Y-W%W-%w")
		""" start_date_on_week di mulai dari hari minggu, bila ingin hari senin di mulai lakukan
			penambahan satu hari """
		start_date_on_week += datetime.timedelta(days=1)
		# import pdb;pdb.set_trace()
		return start_date_on_week

	def get_end_date(self, cr, uid, ids, wy, context=None):
		""" Ambil end Date Tiap Minggu nya"""
		mps = self.browse(cr,uid,ids[0],)
		year = mps.year
		y_w = str(year)+"-W"+str(wy)
		end_date_on_week = datetime.datetime.strptime(y_w + '-0',"%Y-W%W-%w") 
		""" end_date_on_week di mulai dari hari minggu, bila ingin hari 6 end di mulai lakukan
			penambahan 6 hari """
		end_date_on_week += datetime.timedelta(days=6)
		return end_date_on_week

	def get_no_week(self, cr, uid, ids, m, context=None):
		""" Ambil No Urutan Week Berdasarkan Bulannya """
		if m == "Jan":
			w = [0,1,2,3]
		if m == "Feb":
			w = [4,5,6,7]
		if m == "Mar":
			w = [8,9,10,11]
		if m == "Apr":
			w = [12,13,14,15]
		if m == "May":
			w = [16,17,18,19]
		if m == "Jun":
			w = [20,21,22,23]
		if m == "Jul":
			w = [26,27,28,29]
		if m == "Aug":
			w = [30,31,32,33]
		if m == "Sep":
			w = [34,35,36,37]
		if m == "Oct":
			w = [39,40,41,42]
		if m == "Nov":
			w = [43,44,45,46]
		if m == "Dec":
			w = [47,48,49,50]

		return w

	def create_mo(self,cr,uid,ids,wm,b,wps_obj,product_id,start_date,batch_numbering_start,context=None):
		for mo_w in range(0,int(b)):
			index_n = range(0,int(b)).index(mo_w)
			start_date2 = start_date + datetime.timedelta(days=index_n)
			# import pdb;pdb.set_trace()

			product_obj = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
			mrp_obj = self.pool.get('mrp.bom').search(cr, uid, [('product_tmpl_id','=',product_obj.product_tmpl_id.id)])
			mrp_bom = self.pool.get('mrp.bom').browse(cr, uid,mrp_obj[0])

			mo_obj = self.pool.get('mrp.production').create(cr,uid,{
					# 'name' : 'MO/W'+'/'+str(w)
					'product_id' : product_id,
					'product_qty' : mrp_bom.product_qty,
					'product_uom' : self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id,
					'wps_id' : wps_obj,
					'bom_id' : mrp_bom.id,
					'routing_id' : mrp_bom.routing_id.id,
					'date_planned' : start_date2,
					'batch_numbering_start': batch_numbering_start,


			})

			""" Update lagi wps id dan isi mrp_detail_id nya """
			# self.update_line_wps(cr,uid,ids,wps_obj,mo_obj)

	def update_line_wps(self,cr,uid,ids,wps_obj,mo_obj,context=None):
		data_line = {
			'mrp_id' : mo_obj,
		}
		mrp_detail_ids = [(0,0,data_line)]
		datas = {'mrp_detail_ids' : mrp_detail_ids,}
		self.pool.get('vit_pharmacy_manufacture.wps').write(cr,uid,wps_obj,datas)

	def check_available(self,cr,uid, qty,header_component_product_id, bom, component_type ,context=None):
		product_obj = self.pool.get('product.product')
		bom_line_obj = self.pool.get('mrp.bom.line')

		header_component_product    = product_obj.browse(cr, uid, header_component_product_id, context=context)

		print "    Header name " + header_component_product.name 


		component_product_ids = product_obj.search(cr, uid, 
			[('default_code','ilike',header_component_product.default_code),
			('is_header','=',False)], 
			context=context)

		total_available = 0.0
		for component_product in product_obj.browse(cr, uid, component_product_ids, context=context):
			print "    [%s]%s" % (header_component_product.code, header_component_product.name)
			print "        [%s]%s avail=%s qty=%s" % (component_product.code,component_product.name , component_product.virtual_available,qty)
			total_available = total_available + component_product.qty_available #onhand

		print "    total available %s = %s" % (component_type, total_available)

		if qty > 0 and total_available > qty:
			actives_avail = True 
		else:
			actives_avail = False 

		return actives_avail

	def check_material_available(self, cr, uid, detail, context=None):

		# cari info bahan mentah tersedia?
		products = {}
		actives_avail = False # bahan awal aktif
		kemas_primer_avail = False # bahn awal pembantu
		kemas_sekunder_avail = False  # bahan pengemas

		product_id = detail.product_id.id 
		# qty = products.get(product_id, 0 )


		# cari bahan baku produk2 tersebut
		bom_obj     = self.pool.get('mrp.bom')
		bom_line_obj  = self.pool.get('mrp.bom.line')
		product_obj = self.pool.get('product.product')

		product 	= product_obj.browse(cr, uid, product_id, context=context)
		bom_id 		= bom_obj._bom_find(cr, uid, product_id, [], context=context)
		bom 		= bom_obj.browse(cr, uid, bom_id, context=context)
		factor 		= detail.production_order


		print "\nProduct Jadi ----------------- [" + product.name + "] -----------------------"

		# bom breakdown sesuai order qty finish good
		# return daftar komponen berikut qty 
		bom_lines, work_centers = bom_obj._bom_explode(cr, uid, bom, product, factor, [], context=context)

		print "    BOM Lines"
		print bom_lines

		for line in bom_lines:

			qty = line.get('product_qty',0.0)

			header_component_product_id = line.get('product_id',0)
			bom_line_id = bom_line_obj.search(cr, uid, [('bom_id','=',bom.id),('product_id','=',header_component_product_id)], context=context)
			bom_line 	= bom_line_obj.browse(cr, uid, bom_line_id[0], context=context)

			if bom_line.component_type == 'raw_material':
				actives_avail = self.check_available(cr,uid, qty, header_component_product_id, bom, 'raw_material' ,context=context)
				print "        >>> actives_avail=%s" % (actives_avail)

			if bom_line.component_type == 'kemas_primer':
				kemas_primer_avail = self.check_available(cr,uid, qty, header_component_product_id, bom,'kemas_primer' ,context=context)
				print "        >>> kemas_primer=%s" % (kemas_primer_avail)

			if bom_line.component_type == 'kemas_sekunder':
				kemas_sekunder_avail = self.check_available(cr,uid, qty, header_component_product_id, bom,'kemas_sekunder' ,context=context)
				print "        >>> kemas_sekunder=%s" % (kemas_sekunder_avail)

		return actives_avail, kemas_primer_avail, kemas_sekunder_avail

	def action_recalculate(self, cr, uid, ids, context=None):

		for mps in self.browse(cr, uid, ids, context=context):

			sediaan_ids = self.pool.get('vit.sediaan').search(cr, uid, [], context=context)
			for sediaan in self.pool.get('vit.sediaan').browse(cr, uid, sediaan_ids, context=context):
				index = sediaan.index
				fieldname = "mps.mps_detail_ids%s" % index 
				for detail in eval(fieldname):
					self.update_detail(cr, uid, detail, 1, context=context)

	"""
	recalculate the w1..w5 details 
	"""
	def update_detail_old(self, cr, uid, detail, sediaan_index, context=None):
		detail_obj = self.pool.get('vit_pharmacy_manufacture.mps_detail')
		mps_obj = self.pool.get('vit_pharmacy_manufacture.mps')

		# production_order = detail.production_order
		production_order = self.get_total_production_order(cr, uid, detail, sediaan_index, context=context)
		reminder_prev = self.get_total_reminder_prev(cr, uid, detail, sediaan_index, context=context)
		total_products = self.get_total_product(cr, uid, detail, sediaan_index, context=context)
		reminder_per_product = detail.production_order + detail.reminder_prev

		sediaan = detail.sediaan_id 
		max_batch_per_week = math.ceil( sediaan.max_batch_per_week / total_products )

		w1=0;w2=0;w3=0;w4=0;w5=0

		mps = detail.mps_id 
		number_of_weeks = self.count_number_of_weeks(cr, uid, mps.year, mps.month_id)

		# reminder this month
		# reminder_prev = detail.reminder_prev
		reminder = production_order  + reminder_prev 

		# import pdb; pdb.set_trace()

		for i in range(1,6):
			if reminder_per_product > max_batch_per_week:

				reminder = reminder - max_batch_per_week
				reminder_per_product = reminder_per_product - max_batch_per_week

				if i==1:
					w1 = max_batch_per_week
				elif i==2:
					w2 = max_batch_per_week
				elif i==3:
					w3 = max_batch_per_week
				elif i==4:
					w4 = max_batch_per_week
					if number_of_weeks == 4 and reminder_per_product>0:
						self.create_new_line(cr, uid, detail, reminder_per_product, context=context)
				elif i==5:
					w5 = max_batch_per_week
					# import pdb; pdb.set_trace()
					if number_of_weeks == 5 and reminder_per_product>0:
						self.create_new_line(cr, uid, detail, reminder_per_product, context=context)
			else:
				w1 = reminder_per_product
				reminder_per_product = 0
				break 

		data = {
			'w1': w1,
			'w2': w2,
			'w3': w3,
			'w4': w4,
			'w5': w5,
			'reminder' : reminder_per_product,
		}

		if detail_obj.search(cr, uid, [('id','=',detail.id)], context=context):
			detail_obj.write(cr, uid, [detail.id], data, context=context)		


	"""
	recalculate the w1..w5 details 
	"""
	def update_detail(self, cr, uid, detail, sediaan_index, context=None):
		detail_obj = self.pool.get('vit_pharmacy_manufacture.mps_detail')
		mps_obj    = self.pool.get('vit_pharmacy_manufacture.mps')

		# production_order = detail.production_order
		production_order = self.get_total_production_order(cr, uid, detail, sediaan_index, context=context)
		reminder_prev = self.get_total_reminder_prev(cr, uid, detail, sediaan_index, context=context)
		total_products = self.get_total_product(cr, uid, detail, sediaan_index, context=context)
		reminder_per_product = detail.production_order + detail.reminder_prev

		sediaan = detail.sediaan_id 
		max_batch_per_shift= sediaan.max_batch_per_shift  
		max_batch_per_week = 0
		shift = 0


		w1=0;w2=0;w3=0;w4=0;w5=0

		mps = detail.mps_id 
		number_of_weeks = self.count_number_of_weeks(cr, uid, mps.year, mps.month_id)

		# import pdb; pdb.set_trace()

		for i in range(1,4): # shift 
			max_batch_per_week = math.ceil(max_batch_per_shift) * i * 7 
			shift = i
			if max_batch_per_week * number_of_weeks > reminder_per_product:
				break


		# reminder this month
		# reminder_prev = detail.reminder_prev
		reminder = production_order  + reminder_prev 


		for i in range(1,6): #weeks
			if reminder_per_product > max_batch_per_week:

				reminder = reminder - max_batch_per_week
				reminder_per_product = reminder_per_product - max_batch_per_week

				if i==1:
					w1 = max_batch_per_week
				elif i==2:
					w2 = max_batch_per_week
				elif i==3:
					w3 = max_batch_per_week
				elif i==4:
					w4 = max_batch_per_week
					if number_of_weeks == 4 and reminder_per_product>0:
						self.create_new_line(cr, uid, detail, reminder_per_product, context=context)
				elif i==5:
					w5 = max_batch_per_week
					# import pdb; pdb.set_trace()
					if number_of_weeks == 5 and reminder_per_product>0:
						self.create_new_line(cr, uid, detail, reminder_per_product, context=context)
			else:
				if i==1:
					w1 = reminder_per_product
				elif i==2:
					w2 = reminder_per_product
				elif i==3:
					w3 = reminder_per_product
				elif i==4:
					w4 = reminder_per_product
				elif i==5:
					w5 = reminder_per_product

				reminder_per_product = 0
				break 


		active_material_status,kemas_primer,kemas_sekunder = self.check_material_available(cr, uid, detail, context=context)

		data = {
			'active_material_status'    : active_material_status,
			'helper_material_status'    : kemas_primer,
			'packaging_material_status' : kemas_sekunder,
			'max_batch_per_shift'       : max_batch_per_shift,
			'shift': shift,
			'w1': w1,
			'w2': w2,
			'w3': w3,
			'w4': w4,
			'w5': w5,
			'reminder' : reminder_per_product,
		}

		if detail_obj.search(cr, uid, [('id','=',detail.id)], context=context):
			detail_obj.write(cr, uid, [detail.id], data, context=context)		

	def create_new_line(self, cr, uid, detail, reminder, context=None):
		"""
		simpan sisa bulan ini utk bulan depan 
		utk detail line yang sama dng ini dan sediaan_index ini
		jika tidak ada, create line MPS baru
		"""
		detail_obj = self.pool.get('vit_pharmacy_manufacture.mps_detail')
		mps_obj = self.pool.get('vit_pharmacy_manufacture.mps')

		#reminder next month
		reminder_next = 0 
		next_mps_id = detail.mps_id.id + 1
		next_mps_ids = mps_obj.search(cr, uid, [('id','=',next_mps_id)], context=context)
		if next_mps_ids:

			next_detail_id = detail_obj.search(cr, uid, [('mps_id','=',next_mps_id),('product_id','=',detail.product_id.id)], context=context)
			if not next_detail_id:
				next_data = {
					'mps_id' : next_mps_id,
					'reminder_prev': reminder,
					'product_id': detail.product_id.id,
					'product_uom': detail.product_uom.id
				}
				detail_obj.create(cr, uid, next_data, context=context)	
			else:
				next_data = {
					'reminder_prev': reminder,
				}
				detail_obj.write(cr, uid, next_detail_id,next_data, context=context)	

	def get_total_production_order(self, cr, uid, detail, sediaan_index, context=None):
		r = 0
		sql = "select sum(production_order) from vit_pharmacy_manufacture_mps_detail where mps_id = %s and sediaan_id=%s" % (detail.mps_id.id, sediaan_index)
		cr.execute(sql)
		hasil	= cr.fetchone()
		if hasil and hasil[0]:
			r= hasil[0]
		return r

	def get_total_reminder_prev(self, cr, uid, detail, sediaan_index, context=None):
		r = 0
		sql = "select sum(reminder_prev) from vit_pharmacy_manufacture_mps_detail where mps_id = %s and sediaan_id=%s" % (detail.mps_id.id, sediaan_index)
		cr.execute(sql)
		hasil	= cr.fetchone()

		if hasil and hasil[0]:
			r= hasil[0]
		return r

	def get_total_product(self, cr, uid, detail, sediaan_index, context=None):
		r = 0
		sql = "select count(*) from vit_pharmacy_manufacture_mps_detail where mps_id = %s and sediaan_id=%s" % (detail.mps_id.id, sediaan_index)
		cr.execute(sql)
		hasil	= cr.fetchone()
		if hasil and hasil[0]:
			r= hasil[0]
		return r

	def count_number_of_weeks(self, cr, uid, year, month, context=None):
		c = calendar.monthcalendar(2015, 9)
		return len(c)


""" Details MPS (Master Production Schedule) """
class mps_detail(osv.osv):
	_name = 'vit_pharmacy_manufacture.mps_detail'
	_description = 'Master Production Schedule Details'

	# if these fields are changed, call method
	@api.onchange('w1', 'w2','w3','w4','w5') 
	def on_change_plan(self):
		self.total_plan = self.w1 + self.w2 + self.w3 + self.w4 + self.w5

	# if these fields are changed, call method
	@api.onchange('w1a', 'w2a','w3a','w4a','w5a') 
	def on_change_actual(self):
		self.total_actual = self.w1a + self.w2a + self.w3a + self.w4a + self.w5a



	def _total_plan(self, cr, uid, ids, field, arg, context=None):
		res = {}
		for det in self.browse(cr, uid, ids, context=context):
			res[det.id] = det.w1 + det.w2 + det.w3 + det.w4 + det.w5 
		return res	

	def _total_actual(self, cr, uid, ids, field, arg, context=None):
		res  = {}
		for det in self.browse(cr, uid, ids, context=context):
			res[det.id] = det.w1a + det.w2a + det.w3a + det.w4a + det.w5a  
		return res 	
 
	_columns = {
		'mps_id' : fields.many2one('vit_pharmacy_manufacture.mps', 'MPS Reference',required=True, ondelete='cascade', select=True),
		'product_id': fields.many2one('product.product', 'Substance', required=True),

		'sediaan_id' : fields.related('product_id', 'categ_id' , 'sediaan_id', type="many2one", 
			relation="vit.sediaan", string="Sediaan", store=True),

		'production_order' : fields.integer('Order(s)' , help="Number of production order (batches)"), 
		'max_order' : fields.integer('Max' , help="Number of maximum production order (batches) ready to produce according to the available materials"), 
		'product_uom': fields.many2one('product.uom', 'Uom'),
		'max_batch_per_shift' : fields.float('Bat/Shf' , help='Max Number of batch per shift'),
		'shift' : fields.integer('Shf' , help='Number of shift(s) required'),
		'w1': fields.integer('W1p'),
		'w2': fields.integer('W2p'),
		'w3': fields.integer('W3p'),
		'w4': fields.integer('W4p'),
		'w5': fields.integer('W5p'),
		'w1a': fields.integer('W1a'),
		'w2a': fields.integer('W2a'),
		'w3a': fields.integer('W3a'),
		'w4a': fields.integer('W4a'),
		'w5a': fields.integer('W5a'),
		'total_plan': fields.function(_total_plan, type='integer', string='Tp', store=True ),
		'total_actual': fields.function(_total_actual, type='integer', string='Ta', store=True ),
		'reminder' : fields.integer('Next'),
		'reminder_prev' : fields.integer('Prev'),

		'active_material_status': fields.boolean('Active Material Available?'),
		'helper_material_status': fields.boolean('Helper Material Available?'),
		'packaging_material_status': fields.boolean('Packaging Material Available?'),

		'batch_numbering_start' : fields.selection([('kecil','K'),('besar','B')],'B/K'),

		'note'  : fields.char("Note"),
	}

	_defaults = {
		'batch_numbering_start' : 'kecil'
	}

	def on_change_product_id(self, cr, uid, ids, product_id, name, context=None):
		uom = self.pool.get('product.product').browse(cr, uid, product_id, context=context).uom_id.id
		# import pdb;pdb.set_trace()
 
		if product_id!=False:
			return {
				'value' : {
					'product_uom' : uom,
				}
			}
		else:
			return {
				'value' : {
					'product_uom' : '',
				} 
			}
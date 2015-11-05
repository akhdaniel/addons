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

	def action_create_wps(self, cr, uid, ids, context=None):
		""" Create Sejumlah WPS dari Urutan Week Paling Pertama """

		for details_product in self.browse(cr,uid,ids[0],).mps_detail_ids1:
			self.create_wps(cr,uid, ids, details_product, context=context)
		
		self.write(cr, uid, ids, {'state':'done'}, context=context)

	def create_wps(self, cr, uid, ids, details_product, context=None):

		mps = self.browse(cr,uid,ids[0],)
		m = mps.month
		year = mps.year

		week_on_month = [1,2,3,4,5]
		week_on_year = self.get_no_week(cr,uid,ids,m)

		batch = [details_product.w1,details_product.w2,details_product.w3,details_product.w4]
		for wm,wy,b in zip(week_on_month,week_on_year,batch):
			if b > 0.00:
				start_date  = self.get_start_date(cr, uid, ids, wy)
				end_date  = self.get_end_date(cr, uid, ids, wy)
				wps_obj = self.pool.get('vit_pharmacy_manufacture.wps').create(cr,uid,{
					'name' : 'WPS'+'/'+str(wm)+'/'+ m +'/'+ str(year),
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
				self.create_mo(cr,uid,ids,wm,b,wps_obj,product_id,start_date)

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

	def create_mo(self,cr,uid,ids,wm,b,wps_obj,product_id,start_date,context=None):
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

	def action_recalculate(self, cr, uid, ids, context=None):

		for mps in self.browse(cr, uid, ids, context=context):
			for detail in mps.mps_detail_ids1:
				self.update_detail(cr, uid, detail, context=context)
			for detail in mps.mps_detail_ids2:
				self.update_detail(cr, uid, detail, context=context)
			for detail in mps.mps_detail_ids3:
				self.update_detail(cr, uid, detail, context=context)
			for detail in mps.mps_detail_ids4:
				self.update_detail(cr, uid, detail, context=context)
			for detail in mps.mps_detail_ids5:
				self.update_detail(cr, uid, detail, context=context)
			for detail in mps.mps_detail_ids6:
				self.update_detail(cr, uid, detail, context=context)

	def update_detail(self, cr, uid, detail, context=None):
		detail_obj = self.pool.get('vit_pharmacy_manufacture.mps_detail')
		production_order = detail.production_order
		w1 = production_order / 4
		w2 = production_order / 4
		w3 = production_order / 4
		w4 = production_order / 4
		w5 = 0
		data= {'w1': w1,
			'w2': w2,
			'w3': w3,
			'w4': w4,
			'w5': w5,
		}
		detail_obj.write(cr, uid, [detail.id], data, context=context)		

""" Details MPS (Master Production Schedule) """
class mps_detail(osv.osv):
	_name = 'vit_pharmacy_manufacture.mps_detail'
	_description = 'Master Production Schedule Details'

	_columns = {
		'mps_id' : fields.many2one('vit_pharmacy_manufacture.mps', 'MPS Reference',required=True, ondelete='cascade', select=True),
		'product_id': fields.many2one('product.product', 'Substance', required=True),

		'sediaan_id' : fields.related('product_id', 'categ_id' , 'sediaan_id', type="many2one", 
			relation="vit.sediaan", string="Sediaan", store=True),

		'production_order' : fields.integer('Production Order (Batch)'), 
		'product_uom': fields.many2one('product.uom', 'Uom'),
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

		'note'  : fields.char("Note"),
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
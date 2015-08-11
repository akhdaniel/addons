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

	_columns = {
		'name': fields.char('Name'),
		'year': fields.char('Year'),
		'month' : fields.char('Month'),
		'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
		'created_date': fields.datetime('Created Date', required=True, readonly=True, select=True),
		'mps_detail_ids':fields.one2many('vit_pharmacy_manufacture.mps_detail','mps_detail_id','Forecast Details'),
		'state': fields.selection([
			('draft', 'Draft'),
			('done', 'Done'),
			], 'Status', readonly=True, track_visibility='onchange',
			help="", select=True),

	}

	_defaults = {
				 'created_date': time.strftime('%Y-%m-%d %H:%M:%S'),
				 'state': 'draft',
	}

	def action_confirm(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state':'done'}, context=context)

	def action_create_wps(self, cr, uid, ids, context=None):
		""" Create Sejumlah WPS dari Urutan Week Paling Pertama """
		m = self.browse(cr,uid,ids[0],).month
		year = self.browse(cr,uid,ids[0],).year
		for details_product in self.browse(cr,uid,ids[0],).mps_detail_ids:
			week_on_month = [1,2,3,4]
			week_on_year = self.get_no_week(cr,uid,ids,m)
			batch = [details_product.w1,details_product.w2,details_product.w3,details_product.w4]
			for wm,wy,b in zip(week_on_month,week_on_year,batch):
				if b > 0.00:
					start_date  = self.get_start_date(cr, uid, ids, wy)
					end_date  = self.get_end_date(cr, uid, ids, wy)
					wps_obj = self.pool.get('vit_pharmacy_manufacture.wps').create(cr,uid,{
						'name' : 'WPS'+'/'+str(wm)+'/'+self.browse(cr,uid,ids[0],).month+'/'+self.browse(cr,uid,ids[0],).year,
						'mps_id' : self.browse(cr,uid,ids[0],).id,
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
		year = self.browse(cr,uid,ids[0],).year
		y_w = year+"-W"+str(wy)
		start_date_on_week = datetime.datetime.strptime(y_w + '-0',"%Y-W%W-%w")
		""" start_date_on_week di mulai dari hari minggu, bila ingin hari senin di mulai lakukan
			penambahan satu hari """
		start_date_on_week += datetime.timedelta(days=1)
		# import pdb;pdb.set_trace()
		return start_date_on_week

	def get_end_date(self, cr, uid, ids, wy, context=None):
		""" Ambil end Date Tiap Minggu nya"""
		year = self.browse(cr,uid,ids[0],).year
		y_w = year+"-W"+str(wy)
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
					'product_qty' : 1,
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


""" Details MPS (Master Production Schedule) """
class mps_detail(osv.osv):
	_name = 'vit_pharmacy_manufacture.mps_detail'
	_description = 'Master Production Schedule Details'

	_columns = {
		'mps_detail_id' : fields.many2one('vit_pharmacy_manufacture.mps', 'MPS Reference',required=True, ondelete='cascade', select=True),
		'product_id': fields.many2one('product.product', 'Substance', required=True),
		'production_order' : fields.float('Production Order'), 
		'product_uom': fields.many2one('product.uom', 'Uom'),
		'w1': fields.float('W1'),
		'w2': fields.float('W2'),
		'w3': fields.float('W3'),
		'w4': fields.float('W4'),
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
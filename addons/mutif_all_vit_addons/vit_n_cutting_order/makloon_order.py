from osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.vit_upi_uang_persediaan import terbilang_func
import datetime 


_logger = logging.getLogger(__name__)

class vit_material_req_line(osv.osv):
	_name = "vit.material.req.line"
	_description = 'Material Requirements Lines'
	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',ondelete='cascade'),
		'material': fields.many2one('product.product', 'Material'),
		'type' : fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type'),
		'qty'  : fields.float('Quantity'),         
	}

class vit_accessories_req_line(osv.osv):
	_name = "vit.accessories.req.line"
	_description = 'Accessories Requirements Lines'
	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',ondelete='cascade'),
		'material': fields.many2one('product.product', 'Material'),
		'type' : fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type'),
		'qty'  : fields.float('Quantity'),
		'uom_id' : fields.many2one('product.uom','Satuan'),
		'total_harga' : fields.float('Total Harga'),

		#### fiel bayangan untuk mempermudah perhitungan di form makloon ####     
		'size_s' : fields.float('Size S', readonly=False),
		'size_m' : fields.float('Size M', readonly=False),
		'size_l' : fields.float('Size L', readonly=False),
		'size_xl' : fields.float('Size XL', readonly=False),
		'size_xxl' : fields.float('Size XXL', readonly=False),
		'size_xxxl' : fields.float('Size XXXL', readonly=False),
		######################################################################
	}

	## ** Fungsi untuk mengalikan total harga dengan standard price ** ##
	def on_change_qty_total(self, cr, uid, ids, material, qty, name, context=None):
		# import pdb;pdb.set_trace()

		standard_price = self.pool.get('product.product').browse(cr, uid, material, context=context).standard_price
		if material!=False:
			return {
				'value' : {
					'total_harga' : standard_price * qty
				}
			}
		else:
			return {
				'value' : {
					'total_harga' : ''
				} 
			}

class vit_grade(osv.Model):
	_name = "vit.grade"
	_rec_name = "date"

	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',ondelete='cascade'),
		'date' : fields.date('Tanggal',required=True),
		'size_s' : fields.integer('Size S'),
		'size_m' : fields.integer('Size M'),
		'size_l' : fields.integer('Size L'),
		'size_xl' : fields.integer('Size XL'),
		'size_xxl' : fields.integer('Size XXL'),
		#### size_xxxl untuk little mutif ukuran 12 ###
		'size_xxxl' : fields.integer('Size 12/XXXL'), 

		'picking_ids' : fields.many2one('stock.picking','Internal Move'),
	}

	_defaults = {
		'date' : fields.date.context_today,
	}

	
	# def write(self, cr, uid, ids, vals, context=None):
	# 	import pdb;pdb.set_trace()
	# 	if context is None:
	# 		context = {}
	# 	if isinstance(ids, (int, long)):
	# 		ids = [ids]
	# 	return super(vit_grade, self).write(cr, uid, ids, vals, context=context)	
	
	def action_grade_b(self, cr, uid, ids, context=None):
		lokasi_scrapped = 'Scrapped'
		lokasi_makloon = 'Lokasi Makloon'
		lokasi_barang_jadi = 'Lokasi Barang Jadi'

		lokasi_makloon_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_makloon)])[0]
		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		lokasi_scrapped_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_scrapped)])[0]


		# Update : Pencarian lokasi melalui parameter
		# Pencarian source dan destinasi lokasi melalui master lokasi		
		if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_b_to_scrapped')]) == []:
			raise osv.except_osv("Konfigurasi Nama Method : action_grade_b_to_scrapped Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location], Misal source : QC Barang Jadi, Dest: Virtual Locations / Scrapped")
		else:	
			master_lokasi_out_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_b_to_scrapped')])[0]
			master_lokasi_out_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_out_id,)

		if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_scrapped_to_gudang')]) == []:
			raise osv.except_osv("Konfigurasi Nama Method : action_grade_scrapped_to_gudang Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location], Misal source : Virtual Locations / Scrapped, Dest: Lokasi Barang Jadi")
		else:	
			master_lokasi_in_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_scrapped_to_gudang')])[0]
			master_lokasi_in_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_in_id,)

	
		### Buat Internal Move Dari Gudang Jadi ke Produksi ####
		########################################################
		### Create Dahulu ######################################
		sp_obj   = self.pool.get('stock.picking')
		record_vit_grade = self.browse(cr,uid,ids,context)[0]

		if record_vit_grade.picking_ids.id != False:
			return True

		sp_data1 = {
				'origin'			: record_vit_grade.makloon_order_id.name,
				'spk_mkl_id'		: record_vit_grade.makloon_order_id.id,
			}

		sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)

		### Pencarian Id untuk field model
		model_product = record_vit_grade.makloon_order_id.model
		master_type_obj = self.pool.get('vit.master.type')
		master_type_obj_ids = record_vit_grade.makloon_order_id.type_product_id.id
		# master_type_obj_ids = master_type_obj.search(cr,uid,[('model_product','=',model_product)])

		## Cari Product Id Di BOM dengan search dari master_model_id == master_type_obj_ids[0]
		mrp_bom_obj = self.pool.get('mrp.bom')
		# mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('master_model_id','=',master_type_obj_ids[0])])
		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('master_model_id','=',master_type_obj_ids)])
		
		## Kategori Type Mutif/Little Mutif ###
		master_type_obj.browse(cr,uid,[master_type_obj_ids],)[0].categ_id
		
		loop_size = ['S','M','L','XL','XXL','XXXL']

		for mrp_id in mrp_bom_obj_ids:
			obj_mrp = mrp_bom_obj.browse(cr,uid,mrp_id,)
			for ls in loop_size:
				if obj_mrp.size == ls:
					if obj_mrp.size == 'S':
						size = record_vit_grade.size_s
					elif obj_mrp.size == 'M':
						size = record_vit_grade.size_m
					elif obj_mrp.size == 'L':
						size = record_vit_grade.size_l
					elif obj_mrp.size == 'XL':
						size = record_vit_grade.size_xl
					elif obj_mrp.size == 'XXL':
						size = record_vit_grade.size_xxl
					else :
						size = record_vit_grade.size_xxxl

					if size == 0.0:
						continue
					

					data_line = {
							'name'				: obj_mrp.product_id.name, 
							'product_id'        : obj_mrp.product_id.id,
							'product_qty'       : size,
							'product_uom'		: obj_mrp.product_id.uom_id.id,
							'location_id'       : master_lokasi_out_obj.source_loc_id.id,
							'location_dest_id'  : master_lokasi_out_obj.dest_loc_id.id,
							'spk_mkl_id'		: record_vit_grade.makloon_order_id.id,
							}
							
					move_lines = [(0,0,data_line)]
					stock_data = {
						'move_lines'     	: move_lines,
						}

					sp_obj.write(cr, uid, sp_id_create, stock_data, context=context)

					### Fungsi untuk Grade B ###
					############################
					obj_product_b = obj_mrp.product_id.name+' '+'-'+' '+'B'

					product_id = self.pool.get('product.product').search(cr, uid, [('name','=',obj_product_b)])
					if product_id ==[]:
						raise osv.except_osv(obj_product_b+' Tidak Dapat Ditemukan','Tambahkan / Periksa Penulisan Dan Spasinya')
					product_id = self.pool.get('product.product').browse(cr, uid, product_id,context=context)[0]
					data_line_b = {
							'name'				: product_id.name, 
							'product_id'        : product_id.id,
							'product_qty'       : size,
							'product_uom'		: product_id.uom_id.id,
							'location_id'       : master_lokasi_in_obj.source_loc_id.id,
							'location_dest_id'  : master_lokasi_in_obj.dest_loc_id.id,
							'spk_mkl_id'		: record_vit_grade.makloon_order_id.id,
							}
							
					move_lines2 = [(0,0,data_line_b)]
					stock_data2 = {
						'move_lines'     	: move_lines2,
						}
					sp_obj.write(cr, uid, sp_id_create, stock_data2, context=context)
		
		self.write(cr,uid,ids,{'picking_ids':sp_id_create},context=context)
		return True


class vit_makloon_order(osv.osv):
	_name = "vit.makloon.order"
	_description = 'Makloon Order'
	_rec_name = 'name'
	_order = 'name desc'
	_inherit = ['mail.thread']

	def button_dummy(self, cr, uid, ids, context=None):
		return True

	def move_dest(self, cr, uid, ids, context=None):
		"""
		Method Untuk Tombol move_dest, Memindahkan Product dari QC Ke Barang Jadi
		Pencarian dari stock move yang memiliki SPK Makloon terkait
		  - Filter : Lokasi dest_loc_id dari Master Lokasi dengan nama 
		  - Filter : is_copy = False, supaya mencegah double pengambilan id stock move yang akan di gunakan
		"""
		stock_move_obj = self.pool.get('stock.move')
		# Pencarian source dan destinasi lokasi melalui master lokasi		
		if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_move_dest_from_where_to_get')]) == []:
			raise osv.except_osv("Konfigurasi Nama Method : action_move_dest_from_where_to_get Tidak ditemukan, Dari Lokasi Mana akan difilter", "[Setting Di Configuration Setting -> Master Location]")
		else:	
			master_lokasi_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_move_dest_from_where_to_get')])[0]
			master_lokasi_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_id,)
		# stock_move_ids = stock_move_obj.search(cr,uid,[('spk_mkl_id','=',ids[0]),('location_dest_id','=',master_lokasi_obj.dest_loc_id.name),('is_copy','=',False)])
		stock_move_ids = stock_move_obj.search(cr,uid,[('picking_id.state','=','done'),('spk_mkl_id','=',ids[0]),('location_dest_id','=',master_lokasi_obj.dest_loc_id.name),('is_copy','=',False)])	
		"""Cek Dahulu stock move tersebut apakah sudah masuk ke gudang jadi atau belum """
		for stock_move_id in stock_move_ids:
			stock_move = stock_move_obj.browse(cr,uid,stock_move_id,context=context)
			if stock_move.picking_id.state =="draft":
				raise osv.except_osv("Stock Move dari Produksi ke QC Masih Draft atau Belum Ada", "Lakukan Proses Internal Move")

		### Buat Internal Move Dari Gudang Jadi ke Produksi ####
		########################################################
		### Create Dahulu ######################################
		sp_obj   = self.pool.get('stock.picking')
		sp_data1 = {
				'origin'			: self.browse(cr,uid,ids,context)[0].name,
				'makloon_id'		: self.browse(cr,uid,ids,context)[0].id,
				'note'				: "Move dari Qc ke Gudang Jadi",
			}

		# import pdb;pdb.set_trace()
		if stock_move_ids!=[]:
			sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)
		for stock_move_id in stock_move_ids:
			stock_move = stock_move_obj.browse(cr,uid,stock_move_id,context=context)

			if stock_move.picking_id.state =="assigned":
				continue
			else:
				# sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)
				self.copy(cr,uid,id,stock_move_id,sp_id_create, defaults=None,context=None)
				"""Update Dahulu Stok Move Yang Sudah Dibuatkan Copy nya, dengan is_copy = True, Supaya bila ada beberapa kali recevie tidak double"""
				stock_move_obj.write(cr,uid,stock_move_id,{'is_copy':True})

		return True

	def copy(self, cr, uid, id, stock_move_id, sp_id_create, defaults=None, context=None):
		# defaults['picking_id'] = sp_id_create
		stock_move_obj = self.pool.get('stock.move')
		defaults = {} if defaults is None else defaults.copy()

		# Pencarian source dan destinasi lokasi melalui master lokasi		
		if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_move_dest_qc_to_warehouse')]) == []:
			raise osv.except_osv("Konfigurasi Nama Method : action_move_dest_qc_to_warehouse Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location]")
		else:	
			master_lokasi_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_move_dest_qc_to_warehouse')])[0]
			master_lokasi_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_id,)

		defaults.update(picking_id=sp_id_create,location_id=master_lokasi_obj.source_loc_id.id,location_dest_id=master_lokasi_obj.dest_loc_id.id)
		return stock_move_obj.copy(cr, uid, stock_move_id, defaults, context=context)

	def updated_hpp(self,cr,uid,ids,context=None):
		# self.update_other_field(cr,uid,ids,reward_steam,total_hpp,context)
		int_move_ids = self.browse(cr,uid,ids,context=context)[0].int_move_ids
		for int_move_id in int_move_ids:
			if int_move_id.type == 'in' and int_move_id.state == 'done' and int_move_id.is_updated ==False:
				reward_steam = int_move_id.reward_steam
				""" wip_total_baku_acc_per_pcs =  Total WIP Bahan Baku/Pcs + Total WIP Accesories/Pcs """
				wip_total_baku_acc_per_pcs= self.browse(cr,uid,ids,context=context)[0].avg_qty_total_wip_spk_cut + self.browse(cr,uid,ids,context=context)[0].avg_qty_acc_total
				
				if int_move_id.reward_steam != 0 and int_move_id.qty_total_field!=0:
					hpp_reward = int_move_id.reward_steam / int_move_id.qty_total_field
				else:
					hpp_reward = 0
				id_int_move = int_move_id.id
				# qty = int_move_id.qty_total_field

				sql = """select sum(product_qty) from stock_move WHERE picking_id =' %s'"""%(id_int_move)
				cr.execute(sql)
				qty = cr.fetchone()
				qty = qty[0]
				# total_hpp = hpp_reward + self.browse(cr,uid,ids,context=context)[0].qty_all_total_wip_pcs
				total_hpp = self.browse(cr,uid,ids,context=context)[0].last_qty_all_total_wip_pcs
				"""Update Nilai Cost price dari Last Total WIP/Pcs  """
				# self.update_cost(cr,uid,ids,total_hpp,context)
				# self.update_other_field(cr,uid,ids,reward_steam,qty,hpp_reward,context)
				
				"""Update Dahulu Journal Entry Yang sudah dibuat Debit/Kredit Sesuaikan dengan Hpp Makloon"""
				name = int_move_id.name
				stock_picking_id = int_move_id.id
				total_line_overhead =self.browse(cr,uid,ids,context=context)[0].qty_total_harga_journal_value
				# import pdb;pdb.set_trace()
							
				self.update_acc_move(cr,uid,ids,name,stock_picking_id,wip_total_baku_acc_per_pcs,total_line_overhead,qty,reward_steam,hpp_reward,total_hpp,context)
				
				""" Update Status internal move menjadi True update costprice """
				self.is_updated(cr,uid,ids,id_int_move,context)

				

				"""Update Nilai Cost price dari Last Total WIP/Pcs
				     t_qty_all_total_wip_pcs : Harga WIP/Pcs Dari SPK Cutting + Harga WIP/Pcs Accessories + Total Overheads 
				     atau Nilai dari field : Total WIP/Pcs
			    """
				t_qty_all_total_wip_pcs = self.browse(cr,uid,ids[0],).qty_all_total_wip_pcs
				self.update_cost(cr,uid,ids,total_hpp,t_qty_all_total_wip_pcs,hpp_reward,context)
				self.update_other_field(cr,uid,ids,reward_steam,qty,hpp_reward,context)
				
				## Create Jurnal Reward Steam
				# self.journal_reward(cr,uid,ids,reward_steam,qty,context)
				

		return True
	
	# Fungsi Mengupdate other field seperti reward steareward_steam,n dan total reward di makloon
	def update_other_field(self,cr,uid,ids,reward_steam,qty,hpp_reward,context=None):
		self.write(cr,uid,ids[0],{'reward_steam':reward_steam,'last_qty_incoming':qty,'hpp_reward':hpp_reward},context=context)
		return True

	# Fungsi Mengupdate nilai account move debit kredit berdasarkan nilai real produksi maklon
	def update_acc_move(self,cr,uid,ids,name,stock_picking_id, wip_total_baku_acc_per_pcs,total_line_overhead,qty,reward_steam,hpp_reward,total_hpp,context=None):
		stock_move_obj = self.pool.get('stock.move')
		stock_picking = self.pool.get('stock.picking')
		account_move_obj = self.pool.get('account.move')
		account_move_line_obj = self.pool.get('account.move.line')
		stock_move_ids = stock_move_obj.search(cr,uid,[('picking_id','=',stock_picking_id)])
		for stock_move_id in stock_move_ids:
			stock_move = stock_move_obj.browse(cr,uid,stock_move_id,context=context)
			account_move_ids = account_move_obj.search(cr,uid,[('ref','=',stock_move.picking_id.name)])
			for account_move_id in account_move_ids:
				account_move = account_move_obj.browse(cr,uid,account_move_id,context=context)
				acc_id = account_move.id
				# self.check_state_acc_move(cr,uid,acc_id,context=context)
				if account_move.state == "posted" :
					account_move_obj.button_cancel(cr, uid, [account_move.id],context)

				for line in account_move.line_id:

					if line.name == stock_move.name:
						if (line.debit or line.credit)!=0:
							if line.debit !=0:
								aml_id = line.id
								account_move_line_obj.write(cr,uid,aml_id,{'debit': stock_move.product_qty * wip_total_baku_acc_per_pcs},context=context)
							else:
								aml_id = line.id
								account_move_line_obj.write(cr,uid,aml_id,{'credit': stock_move.product_qty * wip_total_baku_acc_per_pcs},context=context)
						else:
							""" Lakukan Pencarian Bila Debet/Kredit Di account move nya  awalnya 0.0, lakukan filter berdasarkan COA Virtualnya 
							    dan Update nilai kredit 
							"""
							picking_id = stock_picking.search(cr,uid,[('name','=',line.ref)])
							picking_obj = stock_picking.browse(cr,uid,picking_id,context=context)
							
							""" Ambil Salah Satu ukuran product dalam move_lines picking, dengan nilai account_id dari virtual source nya
								Misal didapat account = Persediaan dalam proses sebagai update pertama di kredit bila line.account_id di 
								account.move sama
							"""
							if picking_obj[0].move_lines[0].location_id.valuation_out_account_id.id == line.account_id.id:
								aml_id = line.id
								account_move_line_obj.write(cr,uid,aml_id,{'credit': stock_move.product_qty * wip_total_baku_acc_per_pcs},context=context)
							else:
								aml_id = line.id
								account_move_line_obj.write(cr,uid,aml_id,{'debit': stock_move.product_qty * wip_total_baku_acc_per_pcs},context=context)
			
		""" Update kan value wip makloon (total overhead + reward) """
		self.update_acc_move_wip_makloon(cr,uid,account_move_ids,total_line_overhead,qty,reward_steam,stock_move_ids,context)
		return True



	def update_acc_move_wip_makloon(self,cr,uid,account_move_ids,total_line_overhead,move_all_qty,reward_steam,stock_move_ids,context):
		"""
		Fungsi Untuk Mengupdate account_move dengan nilai dari total overhead + reward
		move_all_qty = Nilai total Quantity yang terima 
		total_line_overhead = Total Nilai overhead per pcs
		account_move_ids = list id account_move yang akan di update
		reward_steam = Nilai Reward steam
		"""
		account_move_obj = self.pool.get('account.move')	
		for move_id in account_move_ids:
			acc_move = account_move_obj.browse(cr,uid,move_id,context=context)
		
			"""Cari account_id di Master Jurnal dengan nama filter 'Overheads dan Reward'"""	
			master_journal_obj   = self.pool.get('vit.master.journal')
			if master_journal_obj.search(cr, uid,[('is_active','=', True),('name','=','Overheads dan Steam')], context=context) == []:
				raise osv.except_osv("Konfigurasi Nama Master Jurnal  : Overheads dan Steam", "[Setting Di Configuration Setting -> Master Jurnal]")
			else:
				master_ids   = master_journal_obj.search(cr, uid,[('is_active','=', True),('name','=','Overheads dan Steam')], context=context)
				master_journal = master_journal_obj.browse(cr,uid,master_ids[0],)


			"""Cari Nilai Qty Masing-masing ukuran pada saat stock move atau incoming
				stock_move_ids = id stock_move list [196891, 196892, 196893, 196894, 196895] sesuai dengan picking_id nya
				atau bisa di cari dengan filter name di account.move.line misal XXL == name di stock_move, didapat qty nya
			"""	
			"""Ambil Salah Satu Name dari line_id nya --> acc_move.line_id[0].name """
			
			stock_move_obj = self.pool.get('stock.move')
			
			for stock_move_id in stock_move_ids:
				stock_move = stock_move_obj.browse(cr,uid,stock_move_id,context=context)
				if stock_move.name == acc_move.line_id[0].name:
					product_qty = stock_move.product_qty

			"""Bila reward_steam per pcs"""
			if reward_steam != 0:
				debit = (total_line_overhead + (reward_steam / move_all_qty)) * product_qty
				credit = (total_line_overhead + (reward_steam / move_all_qty)) * product_qty
			else:
				debit = total_line_overhead * product_qty
				credit = total_line_overhead * product_qty

				
			debit ={
					'date'		 : acc_move.date,
					'name'       : 'Overheads dan Steam',
					'ref'        : acc_move.ref,
					'partner_id' : acc_move.partner_id.id,
					'account_id' : master_journal.debit_account_id.id,
					'debit'      : debit,
					'credit'     : 0.0 
					}

			credit ={
					'date'		 : acc_move.date,
					'name'       : 'Overheads dan Steam',
					'ref'        : acc_move.ref,
					'partner_id' : acc_move.partner_id.id,
					'account_id' :  master_journal.credit_account_id.id,
					'debit'      : 0.0,
					'credit'     : credit
					}

			lines = [(0,0,debit), (0,0,credit)]
			am_obj            = self.pool.get('account.move')
			am_data = {
						'line_id'      : lines ,
						}

			"""Jalankan Kembali Tombol Validate posted pada jurnal Entry"""
			# account_move_obj.button_validate(cr,uid, [acc_move.id],context)
			
			"""Jika destinasi lokasi nya adalah QC Barang Jadi maka dapat dilakukan update account move untuk menambahkan coa Overheads dan steam """
			# import pdb;pdb.set_trace()
			
			if stock_move.location_dest_id.name != "Lokasi Gudang Reject":
				am_id = am_obj.write(cr, uid,[acc_move.id], am_data, context=context)
			self.update_account_reject(cr,uid,acc_move,stock_move_ids,context)
		return True
	
	def update_account_reject(self, cr, uid, acc_move, stock_move_ids, context=None):
		stock_move = self.pool.get('stock.move')
		account_move_line_obj = self.pool.get('account.move.line')
		account_move_obj = self.pool.get('account.move')	
		sm = stock_move.browse(cr,uid,stock_move_ids)[0]
		location_dest = sm.location_dest_id.name
		# import pdb;pdb.set_trace()

		if location_dest == 'Lokasi Gudang Reject':
			for line_id in acc_move.line_id:
				if line_id.name == sm.name and line_id.debit != 0:
					method = "update_account_reject"
					account_id = self.get_account_id(cr,uid,method,context)
					account_move_line_obj.write(cr,uid,line_id.id,{'account_id': account_id.debit_account_id.id},context=context)
					
			"""Jalankan Kembali Tombol Validate posted pada jurnal Entry"""
			account_move_obj.button_validate(cr,uid, [acc_move.id],context)
		else:
			"""Jalankan Kembali Tombol Validate posted pada jurnal Entry"""
			account_move_obj.button_validate(cr,uid, [acc_move.id],context)

					

	def get_account_id(self,cr,uid,method,context):
		if method == "update_account_reject":
			"""Cari account_id di Master Jurnal dengan nama filter 'Gudang Reject'"""	
			master_journal_obj   = self.pool.get('vit.master.journal')
			if master_journal_obj.search(cr, uid,[('is_active','=', True),('name','=','Gudang Reject')], context=context) == []:
				raise osv.except_osv("Konfigurasi Nama Master Jurnal  : Gudang Reject", "[Setting Di Configuration Setting -> Master Jurnal]")
			else:
				master_ids   = master_journal_obj.search(cr, uid,[('is_active','=', True),('name','=','Gudang Reject')], context=context)
				master_journal = master_journal_obj.browse(cr,uid,master_ids[0],)
		return master_journal



	## FUngsi Update Cost Price Barang Jadi ###
	def update_cost(self, cr, uid, ids, total_hpp,t_qty_all_total_wip_pcs,hpp_reward,context=None):
		model = self.browse(cr,uid,ids,context=context)[0].model
		prod_obj = self.pool.get('product.product')
		product_ids = self.pool.get('product.product').search(cr, uid, [('name','like',model)])
		for product_id in product_ids:
			cost_price = prod_obj.browse(cr,uid,product_id,).standard_price
			# import pdb;pdb.set_trace()
			if cost_price != 0:
				total_hpp2 = (t_qty_all_total_wip_pcs + cost_price + hpp_reward)/2
				prod_obj.write(cr,uid,product_id,{'standard_price' : total_hpp2},context=context)
			else:
				total_hpp2 = t_qty_all_total_wip_pcs + hpp_reward
				prod_obj.write(cr,uid,product_id,{'standard_price' : total_hpp2},context=context)

			# if cost_price != 0:
			# 	total_hpp2 = (total_hpp + cost_price)/2
			# 	prod_obj.write(cr,uid,product_id,{'standard_price' : total_hpp2},context=context)
			# else:
			# 	prod_obj.write(cr,uid,product_id,{'standard_price' : total_hpp},context=context)
			
		return True

	def is_updated(self,cr,uid,ids,id_int_move,context):
		stock_picking_obj = self.pool.get('stock.picking')
		return stock_picking_obj.write(cr,uid,id_int_move,{'is_updated':True},context=context)

	def _calculate_order(self, cr, uid, ids, name, arg, context=None):
		res = {}
		qty = self.browse(cr,uid,ids,context=context)
		for x in qty:
			res[x.id] = x.s_order +  x.m_order +  x.l_order +  x.xl_order +  x.xxl_order + x.xxxl_order
		return res
 
	
	def conf_categ_id(self,cr,uid, category,context=None):
		# import pdb;pdb.set_trace()
		conf_cutting_pool = self.pool.get('conf.cutting')
		product_category_ids = self.pool.get('product.category').search(cr,uid,[('name','=',category)])
		conf_ids = conf_cutting_pool.search(cr,uid,[('categ_id','=',product_category_ids[0])])
		conf_size = conf_cutting_pool.browse(cr,uid,conf_ids[0],context=context).loop_size
		return conf_size

	def qty_acc_reload2(self, cr, uid, ids, context=None):
		self_obj = self.browse(cr,uid,ids,context=context)
		mrp_bom_obj = self.pool.get('mrp.bom')
		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('name','=',self_obj[0].type_product_id.model_product)])

		# import pdb;pdb.set_trace()
		
		len_size = self.conf_categ_id(cr,uid,self_obj[0].type_product_id.categ_id,context)
		try:
			self.conf_categ_id(cr,uid, self_obj[0].type_product_id.categ_id,context)
		except Exception, e:
			raise osv.except_osv( 'Warning!' , 'Lakukan Pengaturan dulu di Configuration Cutting, Loop size : 5 dengan Category  : Mutif, dan Loop size : 6 dengan Category : Little Mutif')	
		else:
			len_size = self.conf_categ_id(cr,uid, self_obj[0].type_product_id.categ_id,context)
			
		if self.conf_categ_id(cr,uid, self_obj[0].type_product_id.categ_id,context) == []:
			raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXXL yang di input QC cutting tidak boleh minus')	

		if len_size == 5:
			loop_size = ['S','M','L','XL','XXL']
			ls_id_list = []
			for id_ls in loop_size:
				mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',self_obj[0].type_product_id.model_product),('size','=',id_ls)])
				
				if mrp_bom_obj_by_id_ls ==[]:
					raise osv.except_osv( 'Lengkapi BOM untuk produk ini, satu product memiliki 5 Ukuran [S,M,L,XL,XXL]' , 'Tidak Bisa Dikalkulasi/Proses')
				ls_id_list.append(mrp_bom_obj_by_id_ls[0])
			print ls_id_list
			
			bom_s_list = []
			s_list = []
			bom_s = mrp_bom_obj.browse(cr,uid,ls_id_list[0],context =context)
			for bs in bom_s.bom_lines:
				if bs.component_type == 'accessories':
					s_list.append({'material' : bs.product_id.id,'qty': bs.product_qty * self_obj[0].s_order, 'uom_id':bs.product_uom.id})

			bom_m_list = []
			m_list = []
			bom_m = mrp_bom_obj.browse(cr,uid,ls_id_list[1],context =context)
			for bm in bom_m.bom_lines:
				if bm.component_type == 'accessories':
					m_list.append({'material' : bm.product_id.id, 'qty': bm.product_qty * self_obj[0].m_order, 'uom_id':bm.product_uom.id})


			bom_l_list = []
			l_list = []
			bom_l = mrp_bom_obj.browse(cr,uid,ls_id_list[2],context =context)
			for bl in bom_l.bom_lines:
				if bl.component_type == 'accessories':
					l_list.append({'material' : bl.product_id.id, 'qty': bl.product_qty * self_obj[0].l_order, 'uom_id':bl.product_uom.id})

			bom_xl_list = []
			xl_list = []
			bom_xl = mrp_bom_obj.browse(cr,uid,ls_id_list[3],context =context)
			for bx in bom_xl.bom_lines:
				if bx.component_type == 'accessories':
					xl_list.append({'material' : bx.product_id.id, 'qty': bx.product_qty * self_obj[0].xl_order, 'uom_id':bx.product_uom.id})


			bom_xxl_list = []
			xxl_list = []
			bom_xxl = mrp_bom_obj.browse(cr,uid,ls_id_list[4],context =context)
			for bxxl in bom_xxl.bom_lines:
				if bxxl.component_type == 'accessories':
					xxl_list.append({'material' : bxxl.product_id.id,'qty': bxxl.product_qty * self_obj[0].xxl_order, 'uom_id':bxxl.product_uom.id})

			acc_list = []#accessories
			
			acc_s 		= sorted(s_list)
			acc_m 		= sorted(m_list)
			acc_l 		= sorted(l_list)
			acc_xl 		= sorted(xl_list)
			acc_xxl 	= sorted(xxl_list)


			for x in xrange(len(acc_s)):
				# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
				### Karena dalam lima ukuran tiap bom nya sama maka dapat diambil nilai id product pada salah satu ukuran saja misal s ###
				if acc_s[x]['material'] == acc_m[x]['material']:
					mat = acc_s[x]['material']
					# tipe = acc_s[x]['type']
					qty = acc_s[x]['qty']+acc_m[x]['qty']+acc_l[x]['qty']+acc_xl[x]['qty']+acc_xxl[x]['qty']
					uom = acc_s[x]['uom_id']
					acc_list.append({'material' : mat,'qty':qty, 'uom_id' : uom})
				
			## Check Bom yang ternyata tidak sama tiap ukurannya misal  Label Mutif Size S, Label Mutif Size M, dll
			acc_list2 = []
			if len(acc_s) == len(acc_m) == len(acc_l) == len(acc_xl)== len(acc_xxl):			
				for x in xrange(len(acc_s)):
					# for y in xrange(len(acc_m)):
					if acc_s[x]['material'] != acc_m[x]['material'] !=  acc_l[x]['material'] != acc_xl[x]['material'] != acc_xxl[x]['material'] :
						acc = [acc_s[x]['material'],acc_m[x]['material'],acc_l[x]['material'],acc_xl[x]['material'],acc_xxl[x]['material']]
						qty_list = [acc_s[x]['qty'],acc_m[x]['qty'],acc_l[x]['qty'],acc_xl[x]['qty'],acc_xxl[x]['qty']]
						
						# import pdb;pdb.set_trace()
						for product_id in acc:
							# acc_list2.append({'material' : product_id, 'uom_id' : uom})
							acc_list2.append({'material' : product_id})
						acc_list2[0].update({'qty':qty_list[0]})
						acc_list2[1].update({'qty':qty_list[1]})
						acc_list2[2].update({'qty':qty_list[2]})
						acc_list2[3].update({'qty':qty_list[3]})
						acc_list2[4].update({'qty':qty_list[4]})

			##  Jika acc_list2 ada maka tambahkan ke acc_list
			if acc_list2 != []:
				acc_list+=acc_list2
			## ** ##

		
			### Bila Recalulate lebih dari satu kali, lakukan delete terlebih dahulu vit_consumed_line dan vit_accessories_line ###
			### Supaya tidak double write ###
			
			if self_obj[0].accessories_req_line_ids != []:
				cr.execute('delete from vit_accessories_req_line where makloon_order_id = %d' %(ids[0]))	
		
			for jk_item in acc_list:
				# import pdb;pdb.set_trace()
				self.write(cr,uid,ids,{'accessories_req_line_ids':[(0,0,{'material':jk_item['material'],
					'qty':jk_item['qty']})]})

		if len_size == 6 or self_obj[0].xxxl_order > 0:
			loop_size = ['S','M','L','XL','XXL','XXXL']
			ls_id_list = []
			for id_ls in loop_size:
				mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',self_obj[0].type_product_id.model_product),('size','=',id_ls)])
				
				if mrp_bom_obj_by_id_ls ==[]:
					raise osv.except_osv( 'Lengkapi BOM untuk produk ini, satu product memiliki 6 Ukuran [S,M,L,XL,XXL,XXXL]' , 'Tidak Bisa Dikalkulasi/Proses')
				ls_id_list.append(mrp_bom_obj_by_id_ls[0])
			print ls_id_list
			
			bom_s_list = []
			s_list = []
			bom_s = mrp_bom_obj.browse(cr,uid,ls_id_list[0],context =context)
			for bs in bom_s.bom_lines:
				if bs.component_type == 'accessories':
					s_list.append({'material' : bs.product_id.id,'qty': bs.product_qty * self_obj[0].s_order, 'uom_id':bs.product_uom.id})

			bom_m_list = []
			m_list = []
			bom_m = mrp_bom_obj.browse(cr,uid,ls_id_list[1],context =context)
			for bm in bom_m.bom_lines:
				if bm.component_type == 'accessories':
					m_list.append({'material' : bm.product_id.id, 'qty': bm.product_qty * self_obj[0].m_order, 'uom_id':bm.product_uom.id})


			
			l_list = []
			bom_l = mrp_bom_obj.browse(cr,uid,ls_id_list[2],context =context)
			for bl in bom_l.bom_lines:
				if bl.component_type == 'accessories':
					l_list.append({'material' : bl.product_id.id, 'qty': bl.product_qty * self_obj[0].l_order, 'uom_id':bl.product_uom.id})

			
			xl_list = []
			bom_xl = mrp_bom_obj.browse(cr,uid,ls_id_list[3],context =context)
			for bx in bom_xl.bom_lines:
				if bx.component_type == 'accessories':
					xl_list.append({'material' : bx.product_id.id, 'qty': bx.product_qty * self_obj[0].xl_order, 'uom_id':bx.product_uom.id})


			
			xxl_list = []
			bom_xxl = mrp_bom_obj.browse(cr,uid,ls_id_list[4],context =context)
			for bxxl in bom_xxl.bom_lines:
				if bxxl.component_type == 'accessories':
					xxl_list.append({'material' : bxxl.product_id.id,'qty': bxxl.product_qty * self_obj[0].xxl_order, 'uom_id':bxxl.product_uom.id})

			xxxl_list = []
			bom_xxxl = mrp_bom_obj.browse(cr,uid,ls_id_list[5],context =context)
			for bxxxl in bom_xxxl.bom_lines:
				if bxxxl.component_type == 'accessories':
					xxxl_list.append({'material' : bxxxl.product_id.id,'qty': bxxxl.product_qty * self_obj[0].xxxl_order, 'uom_id':bxxxl.product_uom.id})

			acc_list = []#accessories
			
			acc_s 		= sorted(s_list)
			acc_m 		= sorted(m_list)
			acc_l 		= sorted(l_list)
			acc_xl 		= sorted(xl_list)
			acc_xxl 	= sorted(xxl_list)
			acc_xxxl 	= sorted(xxxl_list)


			for x in xrange(len(acc_s)):
				# mat = bom_s_list[x]['material']+bom_m_list[x]['material']+bom_l_list[x]['material']+bom_xl_list[x]['material']+bom_xxl_list[x]['material']
				### Karena dalam lima ukuran tiap bom nya sama maka dapat diambil nilai id product pada salah satu ukuran saja misal s ###
				if acc_s[x]['material'] == acc_m[x]['material']:
					mat = acc_s[x]['material']
					# tipe = acc_s[x]['type']
					qty = acc_s[x]['qty']+acc_m[x]['qty']+acc_l[x]['qty']+acc_xl[x]['qty']+acc_xxl[x]['qty']+acc_xxxl[x]['qty']
					uom = acc_s[x]['uom_id']
					acc_list.append({'material' : mat,'qty':qty, 'uom_id' : uom})
				
			## Check Bom yang ternyata tidak sama tiap ukurannya misal  Label Mutif Size S, Label Mutif Size M, dll
			acc_list2 = []
			if len(acc_s) == len(acc_m) == len(acc_l) == len(acc_xl)== len(acc_xxl) == len(acc_xxxl):			
				for x in xrange(len(acc_s)):
					# for y in xrange(len(acc_m)):
					if acc_s[x]['material'] != acc_m[x]['material'] !=  acc_l[x]['material'] != acc_xl[x]['material'] != acc_xxl[x]['material'] != acc_xxxl[x]['material'] :
						acc = [acc_s[x]['material'],acc_m[x]['material'],acc_l[x]['material'],acc_xl[x]['material'],acc_xxl[x]['material'],acc_xxxl[x]['material']]
						qty_list = [acc_s[x]['qty'],acc_m[x]['qty'],acc_l[x]['qty'],acc_xl[x]['qty'],acc_xxl[x]['qty'],acc_xxxl[x]['qty']]
						
						for product_id in acc:
							# acc_list2.append({'material' : product_id, 'uom_id' : uom})
							acc_list2.append({'material' : product_id})
						acc_list2[0].update({'qty':qty_list[0]})
						acc_list2[1].update({'qty':qty_list[1]})
						acc_list2[2].update({'qty':qty_list[2]})
						acc_list2[3].update({'qty':qty_list[3]})
						acc_list2[4].update({'qty':qty_list[4]})
						acc_list2[5].update({'qty':qty_list[5]})


			##  Jika acc_list2 ada maka tambahkan ke acc_list
			if acc_list2 != []:
				acc_list+=acc_list2
			## ** ##

			### Bila Recalulate lebih dari satu kali, lakukan delete terlebih dahulu vit_consumed_line dan vit_accessories_line ###
			### Supaya tidak double write ###
			
			if self_obj[0].accessories_req_line_ids != []:
				cr.execute('delete from vit_accessories_req_line where makloon_order_id = %d' %(ids[0]))	
		
			for jk_item in acc_list:

				self.write(cr,uid,ids,{'accessories_req_line_ids':[(0,0,{'material':jk_item['material'],
					'qty':jk_item['qty']})]})


		"""Penjumlahan tiap baris accessories, Total Harga = Qty * Standard Price """
		acc_obj = self.pool.get('vit.accessories.req.line')
		for acc in self.browse(cr,uid,ids[0],).accessories_req_line_ids:
				total_harga = acc.qty * acc.material.standard_price
				uom_id = acc.material.uom_id.id
				# import pdb;pdb.set_trace()
				acc_obj.write(cr,uid,acc.id,{'uom_id':uom_id,'total_harga':total_harga},context=context)

		self.write(cr,uid,ids,{'loaded_acc':True},context=context)
		return True

	def qty_acc_reload(self, cr, uid, ids, context=None):

		if context is None:
			context = {}
		else: 
			my_obj = self.browse(cr,uid,ids[0],context=context)
			s_odr = my_obj.s_order
			m_odr = my_obj.m_order
			l_odr = my_obj.l_order
			xl_odr = my_obj.xl_order
			xxl_odr = my_obj.xxl_order
			xxxl_odr = my_obj.xxxl_order

			acc_obj = self.pool.get('vit.accessories.req.line')
			acc_sch = acc_obj.search(cr,uid,[('makloon_order_id','=',ids[0])],context=context)
			acc_bro = acc_obj.browse(cr,uid,acc_sch,context=context)

			### Update 18/04/15 ###
			"""Bila Terjadi Perubahan Quantity order di Tab Makloon :
			   1. Cek Nilai Quantity Baru nya misal s_order 
			   2. s_order * qty di bom nya
			"""	
			mrp_bom_obj = self.pool.get('mrp.bom')
			mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('name','=',my_obj.type_product_id.model_product)])
			# mrp_bom_obj_by_id_ls = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=',id_ls)])
			

			for acc_id_lines in my_obj.accessories_req_line_ids:
				if s_odr != 0.0:
					mrp_bom_s = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=','S')])
					bom_s = mrp_bom_obj.browse(cr,uid,mrp_bom_s[0],context =context)
					for bm in bom_s.bom_lines:
						if bm.component_type == "accessories" and bm.product_id.id == acc_id_lines.material.id:
							acc_s = s_odr * bm.product_qty
				else:
					acc_s = 0
				
				if m_odr != 0.0:

					mrp_bom_s = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=','M')])
					bom_m = mrp_bom_obj.browse(cr,uid,mrp_bom_s[0],context =context)
					for bm in bom_m.bom_lines:
						if bm.component_type == "accessories" and bm.product_id.id == acc_id_lines.material.id:
							acc_m = m_odr * bm.product_qty
				else:
					acc_m = 0
				
				if l_odr != 0.0:
					mrp_bom_l = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=','L')])
					bom_l = mrp_bom_obj.browse(cr,uid,mrp_bom_l[0],context =context)
					for bl in bom_l.bom_lines:
						if bl.component_type == "accessories" and bl.product_id.id == acc_id_lines.material.id:
							acc_l = l_odr * bl.product_qty
				else:
					acc_l = 0

				if xl_odr != 0.0:
					mrp_bom_xl = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=','XL')])
					bom_xl = mrp_bom_obj.browse(cr,uid,mrp_bom_xl[0],context =context)
					for bxl in bom_xl.bom_lines:
						if bxl.component_type == "accessories" and bxl.product_id.id == acc_id_lines.material.id:
							acc_xl = xl_odr * bxl.product_qty
				else:
					acc_xl = 0

				if xxl_odr != 0.0:
					mrp_bom_xxl = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=','XXL')])
					bom_xxl = mrp_bom_obj.browse(cr,uid,mrp_bom_xxl[0],context =context)
					for bxxl in bom_xxl.bom_lines:
						if bxxl.component_type == "accessories" and bxxl.product_id.id == acc_id_lines.material.id:
							acc_xxl = xxl_odr * bxxl.product_qty
				else:
					acc_xxl = 0
				
				if xxxl_odr != 0.0:
					mrp_bom_xxxl = mrp_bom_obj.search(cr,uid,[('master_model_id','=',my_obj.type_product_id.model_product),('size','=','XXXL')])
					bom_xxxl = mrp_bom_obj.browse(cr,uid,mrp_bom_xxxl[0],context =context)
					for bxxxl in bom_xxxl.bom_lines:
						if bxxxl.component_type == "accessories" and bxxxl.product_id.id == acc_id_lines.material.id:
							acc_xxxl = xxxl_odr * bxxxl.product_qty
				else:
					acc_xxxl = 0
				
				acc_tot = acc_s + acc_m + acc_l +acc_xl + acc_xxl + acc_xxxl
				# import pdb;pdb.set_trace()

				acc_obj.write(cr,uid,[acc_id_lines.id],{'qty':acc_tot})


			### Update 19/03/15 ###
			for acc in self.browse(cr,uid,ids[0],).accessories_req_line_ids:
				total_harga = acc.qty * acc.material.standard_price

				acc_obj.write(cr,uid,acc.id,{'total_harga':total_harga},context=context)


			#w: looping setiap baris accessories line
			# for x in acc_bro:
			# 	x_id = x.id

			# 	#w: qty ukuran = qty per ukuran(s,m,l,xl,xxl) pada bom * jml berdasarkan ukuran(s,m,l,xl,xxl) yg di input
			# 	qty_s = (x.size_s*s_odr)
			# 	qty_m = (x.size_m*m_odr)
			# 	qty_l = (x.size_l*l_odr)
			# 	qty_xl = (x.size_xl*xl_odr)
			# 	qty_xxl = (x.size_xxl*xxl_odr)
			# 	qty_xxxl = (x.size_xxxl*xxxl_odr)

			# 	#w: setelah dapat total bahan per ukuran(s,m,l,xl,xxl), jumlahkan total ke lima ukuran tsb


			# 	qty_total = qty_s+qty_m+qty_l+qty_xl+qty_xxl+qty_xxxl
			# 	# acc_obj.write(cr,uid,x_id,{'qty':qty_total},context=context)

			# 	#cari harga standard_price masing2
			# 	total_harga = qty_total * x.material.standard_price
			# 	## Check Dahulu Total Harga nya awalnya 0.0 maka dapat diupdate berdasarkan load default dari spk cutting
			# 	## Bila ada Total Harga > 0 maka dianggap sudah mengalami edit manual, hindari update dari default spk cutting nya
			# 	if x.total_harga == 0 :	
			# 		acc_obj.write(cr,uid,x_id,{'qty':qty_total,'total_harga':total_harga,'loaded_acc':True},context=context)

			self.write(cr,uid,ids,{'loaded_acc':True},context=context)
		return True

	def _get_int_move(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		my_form = self.browse(cr,uid,ids[0],context=context)
		makloon_no = my_form.name
		makloon_id = my_form.id

		pick_obj = self.pool.get('stock.picking')
		pick_ids = pick_obj.search(cr, uid, [
			('origin','=',makloon_no)], context=context)
		if pick_ids == []:
			return result		
		result[makloon_id] = pick_ids
		return result

	def _get_receive(self,cr,uid,ids,field,args,context=None):
		result = {}
		
		#merubah state form makloon menjadi done
		for res in self.browse(cr,uid,ids):
			pick_obj = self.pool.get('stock.picking.in')
			cari_pick =  pick_obj.search(cr,uid,[('origin','=',res.name)],context=context)
			cari_pick_in =  pick_obj.search(cr,uid,[('origin','=',res.name),('type','=','in')],context=context)
			cari_pick_internal =  pick_obj.search(cr,uid,[('origin','=',res.name),('type','=','internal')],context=context)
			if cari_pick_in != [] :
				pick_state = pick_obj.browse(cr,uid,cari_pick_in,context=context)
				for x in pick_state :
					if x.state =='done' and x.is_updated == False:
						self.write(cr,uid,ids[0],{'state':'tobeupdatedhpp'},context=context)
					# elif x.state != 'done' :
					# 	self.write(cr,uid,ids[0],{'state':'tobereceived'},context=context)
						break
					elif x.state =='done' and x.is_updated == True :
						self.write(cr,uid,ids[0],{'state':'done'},context=context)
					else:
						self.write(cr,uid,ids[0],{'state':'tobereceived'},context=context)
				
			if cari_pick_internal!=[]:
				pick_state_internal = pick_obj.browse(cr,uid,cari_pick_internal,context=context)
				for internal in pick_state_internal :
					if internal.state != 'done' and cari_pick_in!=[] :
						self.write(cr,uid,ids[0],{'state':'tobereceived'},context=context)
					
					# if x.state =='done' and x.type == 'in' and x.is_updated == False :
					# 	self.write(cr,uid,ids[0],{'state':'tobeupdatedhpp'},context=context)
					# if x.state =='done' and x.type == 'in' and x.is_updated == True :
					# 	self.write(cr,uid,ids[0],{'state':'done'},context=context)
					# if x.state != 'done' and ( x.state == 'draft' or x.state == 'confirmed' or x.state == 'assigned' or x.state == 'confirmed' or x.state == 'auto'):
		return result

	
	
	# def action_grade_b(self, cr, uid, ids, context=None):
	# 	lokasi_scrapped = 'Scrapped'
	# 	lokasi_makloon = 'Lokasi Makloon'
	# 	lokasi_barang_jadi = 'Lokasi Barang Jadi'

	# 	lokasi_makloon_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_makloon)])[0]
	# 	lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
	# 	lokasi_scrapped_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_scrapped)])[0]

	# 	# Update : Pencarian lokasi melalui parameter
	# 	# Pencarian source dan destinasi lokasi melalui master lokasi		
	# 	if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_b_to_scrapped')]) == []:
	# 		raise osv.except_osv("Konfigurasi Nama Method : action_grade_b_to_scrapped Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location], Misal source : Lokasi Bahan Baku Kain, Dest: Virtual/Production")
	# 	else:	
	# 		master_lokasi_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_b_to_scrapped')])[0]
	# 		master_lokasi_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_id,)

	# 	if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_scrapped_to_gudang')]) == []:
	# 		raise osv.except_osv("Konfigurasi Nama Method : action_grade_scrapped_to_gudang Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location], Misal source : Lokasi Bahan Baku Kain, Dest: Virtual/Production")
	# 	else:	
	# 		master_lokasi_in_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_grade_scrapped_to_gudang')])[0]
	# 		master_lokasi_in_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_id,)


	# 	### Buat Internal Move Dari Gudang Jadi ke lokasi_scrapped_id ####
	# 	########################################################
	# 	### Create Dahulu ######################################
	# 	sp_obj   = self.pool.get('stock.picking')
	# 	for record_vit_grade in self.browse(cr,uid,ids,context=context)[0].grade_ids:
	# 		# Lewati buat record_vit_grade.picking_ids.id yang sudah di create ##
	# 		#####################################################################
	# 		if record_vit_grade.picking_ids.id != False:
	# 			continue
	# 			return True

	# 		sp_data1 = {
	# 				'origin'			: record_vit_grade.makloon_order_id.name,
	# 			}

	# 		sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)

	# 		### Pencarian Id untuk field model
	# 		model_product = record_vit_grade.makloon_order_id.model
	# 		master_type_obj = self.pool.get('vit.master.type')
	# 		master_type_obj_ids = master_type_obj.search(cr,uid,[('model_product','=',model_product)])

	# 		## Cari Product Id Di BOM dengan search dari master_model_id == master_type_obj_ids[0]
	# 		mrp_bom_obj = self.pool.get('mrp.bom')
	# 		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('master_model_id','=',master_type_obj_ids[0])])

	# 		loop_size = ['S','M','L','XL','XXL']



	# 		for mrp_id in mrp_bom_obj_ids:
	# 			obj_mrp = mrp_bom_obj.browse(cr,uid,mrp_id,)
	# 			for ls in loop_size:
	# 				if obj_mrp.size == ls:
	# 					if obj_mrp.size == 'S':
	# 						size = record_vit_grade.size_s
	# 					elif obj_mrp.size == 'M':
	# 						size = record_vit_grade.size_m
	# 					elif obj_mrp.size == 'L':
	# 						size = record_vit_grade.size_l
	# 					elif obj_mrp.size == 'XL':
	# 						size = record_vit_grade.size_xl
	# 					else :
	# 						size = record_vit_grade.size_xxl

	# 					if size == 0.0:
	# 						continue
						
	# 					data_line = {
	# 							'name'				: obj_mrp.product_id.name, 
	# 							'product_id'        : obj_mrp.product_id.id,
	# 							'product_qty'       : size,
	# 							'product_uom'		: obj_mrp.product_id.uom_id.id,
	# 							'location_id'       : master_lokasi_obj.source_loc_id.id,
	# 							'location_dest_id'  : master_lokasi_obj.dest_loc_id.id,
	# 							}
								
	# 					move_lines = [(0,0,data_line)]
	# 					stock_data = {
	# 						'move_lines'     	: move_lines,
	# 						}

	# 					sp_obj.write(cr, uid, sp_id_create, stock_data, context=context)

	# 					### Fungsi untuk Grade B ###
	# 					############################
	# 					obj_product_b = obj_mrp.product_id.name+' '+'-'+' '+'B'

	# 					product_id = self.pool.get('product.product').search(cr, uid, [('name','=',obj_product_b)])
	# 					if product_id ==[]:
	# 						raise osv.except_osv(obj_product_b+' Tidak Dapat Ditemukan','Tambahkan / Periksa Penulisan Dan Spasinya')
	# 					product_id = self.pool.get('product.product').browse(cr, uid, product_id,context=context)[0]
	# 					data_line_b = {
	# 							'name'				: product_id.name, 
	# 							'product_id'        : product_id.id,
	# 							'product_qty'       : size,
	# 							'product_uom'		: product_id.uom_id.id,
	# 							'location_id'       : master_lokasi_in_id.source_loc_id.id,
	# 							'location_dest_id'  : master_lokasi_in_id.dest_loc_id.id,
	# 							}
								
	# 					move_lines2 = [(0,0,data_line_b)]
	# 					stock_data2 = {
	# 						'move_lines'     	: move_lines2,
	# 						}

	# 					sp_obj.write(cr, uid, sp_id_create, stock_data2, context=context)
			
	# 		### Update picking_ids di vit.grade nya dengan id internal move nya dari sp_id_create ###
	# 		##########################################################################################
	# 		pool_vit_grade = self.pool.get('vit.grade')
	# 		pool_vit_grade.write(cr,uid,record_vit_grade.id,{'picking_ids':sp_id_create},context=context)


	# 	return True

	def _qty_total_harga_acc_line(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
		for i in ids:
			val = 0.0
			for line in self.browse(cr, uid, i, context=context).accessories_req_line_ids:
				val += line.total_harga
			res[i] = val
		return res

	def _avg_qty_total(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].qty_total_harga_acc_line !=0 and  x[0].qty_order !=0 :
	 		res[x[0].id] = x[0].qty_total_harga_acc_line / x[0].qty_order
	 	else:
	 		res[x[0].id] = 0
		return res

	def _hpp_model(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	res[x[0].id] = x[0].avg_qty_acc_total + x[0].avg_qty_material_total + x[0].direct_labour + x[0].electricity_cost + x[0].factory_rent_cost + x[0].sewing_cost + x[0].cutting_cost 
		return res

	def _total_all_wip(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	res[x[0].id] = x[0].qty_total_wip_spk_cut + x[0].qty_total_harga_acc_line  + (x[0].qty_total_harga_journal_value * x[0].qty_order)
		return res

	def _total_all_wip_pcs(self, cr, uid, ids, name, arg, context=None):
		res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].qty_all_total_wip!=0 and x[0].qty_order!=0:
	 		res[x[0].id] = x[0].qty_all_total_wip / x[0].qty_order
	 	else:
	 		res[x[0].id] = 0
		return res

	def _last_total_all_wip(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].reward_steam!=0:
	 		res[x[0].id] = x[0].qty_all_total_wip + x[0].reward_steam
	 	else:
	 		res[x[0].id] = x[0].qty_all_total_wip 
		return res

	def _last_total_all_wip_pcs(self, cr, uid, ids, name, arg, context=None):
		res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].hpp_reward!=0 :
	 		res[x[0].id] = x[0].qty_all_total_wip_pcs +x[0].hpp_reward
	 	else:
	 		res[x[0].id] = x[0].qty_all_total_wip_pcs
		return res

	def _last_total_all_wip_last_incoming(self, cr, uid, ids, name, arg, context=None):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].reward_steam!=0:
	 		res[x[0].id] = x[0].qty_total_wip_spk_cut + x[0].qty_total_harga_acc_line + (x[0].reward_steam + (x[0].qty_total_harga_journal_value * x[0].last_qty_incoming))
	 	else:
	 		res[x[0].id] = 0
		return res

	def _last_total_all_wip_last_incoming_pcs(self, cr, uid, ids, name, arg, context=None):
		res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	if x[0].hpp_reward!=0 :
	 		# res[x[0].id] = x[0].qty_all_total_wip_pcs +x[0].hpp_reward
	 		res[x[0].id] = x[0].avg_qty_total_wip_spk_cut + x[0].avg_qty_acc_total + (x[0].reward_steam + (x[0].qty_total_harga_journal_value * x[0].last_qty_incoming))/ x[0].last_qty_incoming
	 	else:
	 		res[x[0].id] = 0
		return res

	def _qty_total_journal_value_line(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
		for i in ids:
			val = 0.0
			for line in self.browse(cr, uid, i, context=context).jurnal_value_ids:
				val += line.value
			res[i] = val
		return res

	def _qty_total_journal_all_pcs(self, cr, uid, ids, field_name, arg, context):
	 	res = {}
	 	x = self.browse(cr,uid,ids,context=context)
	 	res[x[0].id] = x[0].qty_order * x[0].qty_total_harga_journal_value
		return res

	def _get_default_journal(self, cr, uid, context=None):
		if context is None:
			context = {}
		jurnal_value_ids = []
		## Cari Id model berdasarkan self._name model yg sedang proses 
		## Lakukan pencarian master id dengan dari field appeareance == id ir_model_id
		## Masukan Id append ke one2many nya
		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
		master_journal_obj   = self.pool.get('vit.master.journal')
		master_ids   = master_journal_obj.search(cr, uid,[('appeareance','=',ir_model_id[0])])

		
		for master_id in master_ids:
			jurnal_value_ids.append((0,0,{'master_jurnal_id':master_id,'value':0}))
		return jurnal_value_ids
		

	_columns = {
		'name': fields.char('Order Makloon Reference', size=64, required=True,
			readonly=True, select=True),
		'state': fields.selection([
			('draft', 'Draft'),
			('open', 'Open'),
			('inprogres', 'Inprogres'),
			('tobereceived', 'To Be Received'),
			('grade', 'Split Grade'),
			('split', 'Finish Split'),
			('tobeupdatedhpp', 'To Be Updated Hpp'),
			('done', 'Done'),
			], 'Status', readonly=True, track_visibility='onchange',
			help="", select=True),
		'partner_id'	:fields.many2one('res.partner', 'Makloon', select=True, track_visibility='onchange',readonly=True,states={'draft': [('readonly', False)]}),
		# 'date_taking': fields.datetime('Tanggal Pengambilan', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		# 'date_end_completion'	: fields.datetime('Tanggal Penyelesaian', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'date_taking': fields.date('Tanggal Pengambilan', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'date_end_completion'	: fields.date('Tanggal Penyelesaian', select=True,readonly=True,states={'draft': [('readonly', False)]}),
		'address' : fields.char('Alamat', size=128,readonly=True,states={'draft': [('readonly', False)]}),
		# 'origin'  :fields.char('SPK Cutting', size=64),
		'origin'	:fields.many2one('vit.cutting.order', 'SPK Cutting',readonly=False,states={'draft': [('readonly', False)]}),
		'model'   :fields.char('Model', size=64,readonly=False),#states={'draft': [('readonly', False)]}),
		'type_product_id' : fields.many2one('vit.master.type', 'Model / Type'),
		'material_req_line_ids': fields.one2many('vit.material.req.line', 'makloon_order_id', 'Material Requirements Lines'),
		'accessories_req_line_ids': fields.one2many('vit.accessories.req.line', 'makloon_order_id', 'Accessories Requirements Lines'),
		'jurnal_value_ids':fields.one2many('vit.jurnal.value.makloon','makloon_order_id','Jurnal Value'),
		's_order' : fields.float('S/2',readonly=False,states={'draft': [('readonly', False)]}),
		'm_order' : fields.float('M/4',readonly=False,states={'draft': [('readonly', False)]}),
		'l_order' : fields.float('L/6',readonly=False,states={'draft': [('readonly', False)]}),
		'xl_order' : fields.float('XL/8',readonly=False,states={'draft': [('readonly', False)]}),
		'xxl_order' : fields.float('XXL/10',readonly=False,states={'draft': [('readonly', False)]}),
		'xxxl_order' : fields.float('XXXL/12',readonly=False,states={'draft': [('readonly', False)]}),
		'qty_order' :fields.function(_calculate_order, string='Total',type="integer"),
		'user_id'	:fields.many2one('res.users', 'Approved', select=True, track_visibility='onchange'),
		'patner_checker_id'	:fields.many2one('res.users', 'Checked By', select=True, track_visibility='onchange'),
		'state_incoming' : fields.selection([
			('not', 'Belum Create'),
			('draft', 'Draft'),
			('cancel', 'Cancelled'),
			('auto', 'Waiting Another Operation'),
			('confirmed', 'Waiting Availability'),
			('assigned', 'Ready to Transfer'),
			('done', 'Transferred'),
			], 'Status Incoming', readonly=True, track_visibility='onchange',
			help="", select=True),
		# 'picking_ids': fields.one2many('stock.picking.in', 'makloon_order_id', 'Related Picking', readonly=True, help="This is a list of delivery orders that has been generated for this sales order."),
		'is_receive' : fields.function(_get_receive,type="boolean",string='Receive'),
		'invoice_id': fields.many2one('account.invoice', 'Invoice',domain=[('type', '=','in_invoice')], readonly=True,),
		'int_move_ids' : fields.function(_get_int_move, type='many2many', relation="stock.picking", string="Internal Move"),
		'grade_ids' : fields. one2many('vit.grade','makloon_order_id', 'Grade'),
		'direct_labour' : fields.float('Direct Labour/Pcs'),
		'electricity_cost' : fields.float('Electricity Cost/Pcs'),
		'factory_rent_cost' : fields.float('Factory Rent Cost/Pcs'),
		'sewing_cost' : fields.float('Makloon Cost/pcs'),
		'cutting_cost' : fields.float('Cutting Internal Cost/pcs'),
		'qty_total_harga_acc_line': fields.function(_qty_total_harga_acc_line, string='Total WIP Accessories', type='float',store=True),
		'avg_qty_acc_total' : fields.function(_avg_qty_total, string='Harga WIP/Pcs Accessories', type='float'),
		'avg_qty_material_total' : fields.float('Harga Rata-rata Material Dari SPK'),
		'qty_total_wip_spk_cut' : fields.float('Total WIP Dari SPK Cutting', readonly=False),
		'avg_qty_total_wip_spk_cut': fields.float('Harga WIP/Pcs Dari SPK Cutting', readonly=False),
		'qty_all_total_wip': fields.function(_total_all_wip, string='Total WIP', type='float'),
		'qty_all_total_wip_pcs': fields.function(_total_all_wip_pcs, string='Total WIP/Pcs', type='float'),
		'last_qty_all_total_wip': fields.function(_last_total_all_wip, string='Last Total WIP', type='float'),
		'last_qty_all_total_wip_pcs': fields.function(_last_total_all_wip_pcs, string='Last Total WIP/Pcs', type='float'),
		'last_qty_all_total_wip_last_incoming': fields.function(_last_total_all_wip_last_incoming, string='Last Total WIP (Incoming)', type='float'),
		'last_qty_all_total_wip_last_incoming_pcs': fields.function(_last_total_all_wip_last_incoming_pcs, string='Last Total WIP/Pcs (Incoming)', type='float'),
		'hpp_model' : fields.function(_hpp_model, string='HPP Model', type='float'),
		'qty_total_harga_journal_value': fields.function(_qty_total_journal_value_line, string='Total Overheads', type='float',store=True),
		'qty_total_harga_journal_value_all_pcs': fields.function(_qty_total_journal_all_pcs, string='Total Overheads * Total Pcs', type='float',store=True),
		'reward_steam' : fields.float('Last Reward Steam',readonly=True),
		'last_qty_incoming' : fields.float('Last Pcs Quantity Incoming',readonly=True),
		'hpp_reward' : fields.float('Last Reward Steam/pcs',readonly=True),
		'loaded_acc' : fields.boolean('Loaded Accessories ?',readonly=True),
		'date_received'	: fields.date('Tanggal Received'),
		
  
	}

	_defaults = {
		
		'date_taking': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'date_end_completion': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
		'user_id': lambda self, cr, uid, c: uid,
		'name': lambda obj, cr, uid, context: '/',
		'state': 'draft',
		'state_incoming': 'not',
		# 'jurnal_value_ids' : _get_default_journal
   
	}

	def create(self, cr, uid, vals, context=None):

		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.makloon.order.seq') or '/'
		return super(vit_makloon_order, self).create(cr, uid, vals, context=context)

	def write(self, cr, uid, ids, vals, context=None):
		# self.update_value_journal(cr,uid,ids,vals,context)		
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		for x in self.browse(cr, uid, ids, context=context):
			s_qc = x.origin.s_qc
			m_qc = x.origin.m_qc
			l_qc = x.origin.l_qc
			xl_qc = x.origin.xl_qc
			xxl_qc = x.origin.xxl_qc

			#antisipasi penghitungan jmh yg di input untuk makloon harus di bawah atau sama dengan dr QC cutting dan tdk boleh minus
			if 's_order' in vals :
				if vals['s_order'] > s_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['s_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran S yang di input tidak boleh minus!')					
			if 'm_order' in vals :
				if vals['m_order'] > m_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['m_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran M yang di input tidak boleh minus!')					
			if 'l_order' in vals :
				if vals['l_order'] > l_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['l_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran L yang di input tidak boleh minus!')
			if 'xl_order' in vals :
				if vals['xl_order'] > xl_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input untuk makloon melebihi proses QC Qutting!')
				elif vals['xl_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XL yang di input tidak boleh minus!')
			if 'xxl_order' in vals :
				if vals['xxl_order'] > xxl_qc :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input untuk makloon melebihi proses QC Qutting!')																				
				elif vals['xxl_order'] < 0 :
					raise osv.except_osv( 'Warning!' , 'Jumlah qty ukuran XXL yang di input tidak boleh minus!')

		return super(vit_makloon_order, self).write(cr, uid, ids, vals, context=context)

	
	def update_value_journal(self,cr,uid,ids,partner_id, context):
		if ids != []:
			biaya_lains = self.browse(cr,uid,ids[0],).type_product_id.biaya_lain_ids
			for x in self.browse(cr,uid,ids[0],).jurnal_value_ids:
				cr.execute("""DELETE FROM vit_jurnal_value_makloon
						WHERE id = %s
						"""%(x.id))
				cr.commit()
			if biaya_lains != None:
				for biaya_lain in biaya_lains:
					data = [(0,0, { 'master_jurnal_id': biaya_lain.master_jurnal_id.id, 'value' :biaya_lain.value})]
					self.write(cr, uid, ids, {'jurnal_value_ids' : data}, context=context)

	def update_value_journal2(self,cr,uid,ids,type_product_id, context):
		biaya_lain_ids   = self.pool.get('vit.master.type').browse(cr,uid,type_product_id,).biaya_lain_ids
		for biaya_lain in biaya_lain_ids:
			jurnal_value_ids = []		
			data = (0,0, { 'master_jurnal_id': biaya_lain.master_jurnal_id.id, 'value' :biaya_lain.value})
			jurnal_value_ids.append(data)
		# return jurnal_value_ids
		
		

	def action_confirm(self, cr, uid, ids, context=None):																	
		#set to "confirmed" state
		self.write(cr, uid, ids, {'state':'open'}, context=context)
		return True

	
	def _get_jasa_makloon(self, cr, uid, context=None):
		
		product = self.pool.get('product.product').search(cr,uid,[('name','=','Jasa Maklon')])
		if product ==[] :
			raise osv.except_osv( 'Tidak Ditemukan!' , 'Setting --> Product : Name :Jasa Maklon, Categ_id : Jasa, Expense Account: 5-311002 Upah Jahit')
		else:
			prod = self.pool.get('product.product').browse(cr,uid,product)[0]
			prod_id = prod.id
			return prod_id

	def action_inprogress(self, cr, uid, ids, context=None):
		# Check Dahulu Load Qty Usage Material Accessories Supaya tidak terlewat dan nilai kosong
		self.check_loaded_acc(cr,uid,ids,context)

		#search jurnal purchase
		# jurnal = self.pool.get('account.journal').search(cr,uid,[('type','=','purchase')],context=context)[0]
		# #create juga supplier invoicenya
		# inv_makloon = self.pool.get('account.invoice').create(cr,uid,{'partner_id' : self.browse(cr,uid,ids[0],).partner_id.id,
		# 														'origin'  : self.browse(cr,uid,ids[0],).name,
		# 														'account_id' : self.browse(cr,uid,ids[0],).partner_id.property_account_payable.id,
		# 														'journal_id' : jurnal,
		# 														'type' : 'in_invoice',
		# 														}),

		# #search product (id 1 bawaan dari openerp pasti product service)
		# prod_name = self.pool.get('product.product').browse(cr,uid,self._get_jasa_makloon(cr,uid,context),context=context).name		
		# self.pool.get('account.invoice.line').create(cr,uid,{'invoice_id' : inv_makloon,
		# 														'product_id':self._get_jasa_makloon(cr,uid,context),
		# 														'name':prod_name,
		# 														'account_id': self.pool.get('product.product').browse(cr,uid,self._get_jasa_makloon(cr,uid,context),context=context).categ_id.property_account_expense_categ.id,
		# 														'price_unit':(self.browse(cr,uid,ids[0],).origin.type_product_id.cost_makl)*(self.browse(cr,uid,ids[0],).qty_order)})			
		# #set to "inprogress" state
		# self.write(cr, uid, ids, {'state':'inprogres','invoice_id':inv_makloon}, context=context)
		self.write(cr, uid, ids, {'state':'inprogres'}, context=context)
		self.action_move_accessories(cr,uid,ids,context=context)
		# self.journal_biaya(cr, uid, ids, context)

		return True

	def action_view_receive(self, cr, uid, ids, context=None):
		### Fungsi-fungsi untuk mengarahkan ke result list
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		## Arahkan Ke List Tree stock.picking.in dengan Ciri-ciri <record id="action_picking_tree4" model="ir.actions.act_window">
		result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
# 
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		
		pick_ids = []
		spk_name = self.browse(cr,uid,ids[0],).name
		## Cari Id di incoming shipment yang Sama dengan spk_name == origin
		incoming_obj = self.pool.get('stock.picking.in')
		incoming_obj_ids = incoming_obj.search(cr,uid,[('origin','=',spk_name)])

		if len(incoming_obj_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, incoming_obj_ids))+"])]"
			## Cek dan Update dulu state_incoming dari incoming nya Dari List nya
			# self.update_state3(cr,uid,ids, incoming_obj_ids, context)
		else :
			pick_ids = incoming_obj_ids
			res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = pick_ids and pick_ids[0] or False

			## Cek dan Update dulu state_incoming dari incoming 
			# self.update_state2(cr,uid,ids, pick_ids[0], context)

		return result

	def action_receive(self, cr, uid, ids, context=None):
		# self.update_cost(cr,uid,ids,context=context)
		lokasi_makloon = 'Lokasi Makloon'
		lokasi_barang_jadi = 'Lokasi Barang Jadi'
		virtual_production = 'Production'

		lokasi_makloon_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_makloon)])[0]
		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]

		# Update : Pencarian lokasi melalui parameter
		# Pencarian source dan destinasi lokasi melalui master lokasi		
		if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_receive')]) == []:
			raise osv.except_osv("Konfigurasi Nama Method : action_receive Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location]")
		else:	
			master_lokasi_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_receive')])[0]
			master_lokasi_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_id,)

		# Cek Dahaulu  Category Id dengan nama makloon
		if self.pool.get('res.partner.category').search(cr,uid,[('name','=',"makloon")]) == []:
			raise osv.except_osv(" name : makloon, tidak ditemukan di category_id ", "Tambahakan di res.partner.category")
		### Create Dahulu di stock.picking.in
		if self.browse(cr,uid,ids[0],).partner_id.category_id[0].name == "makloon":
			is_makloon = True
		else: 
			is_makloon = False
		
		stock_in_objs = self.pool.get('stock.picking.in')
		stock_in_obj = stock_in_objs.create(cr,uid,{'partner_id' : self.browse(cr,uid,ids[0],).partner_id.id, 'note':"Incoming dari Makloon",
													'is_invoiced' : True,'is_makloon_categ': is_makloon,
													'origin' : self.browse(cr,uid,ids[0],).name,'type':'in'})
		### Pencarian Id untuk field model
		master_type_obj = self.pool.get('vit.master.type')
		## master_type_obj_ids = master_type_obj.search(cr,uid,[('model_product','=',self.browse(cr,uid,ids[0],).model)])
		master_type_obj_id = self.browse(cr,uid,ids[0],).type_product_id.id
		## Cari Product Id Di BOM dengan search dari master_model_id == master_type_obj_ids[0]
		mrp_bom_obj = self.pool.get('mrp.bom')
		# mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('master_model_id','=',master_type_obj_ids[0])])
		mrp_bom_obj_ids = mrp_bom_obj.search(cr,uid,[('master_model_id','=',master_type_obj_id)])

		# loop_size = ['S','M','L','XL','XXL']
		ls_id_list = []
		check_xxxl_order=self.browse(cr,uid,ids[0],).xxxl_order
		if self.browse(cr,uid,ids[0],).type_product_id.categ_id =="Little Mutif" or check_xxxl_order > 0 :
			loop_size = ['S','M','L','XL','XXL','XXXL']
		else:
			loop_size = ['S','M','L','XL','XXL']
		
		for mrp_id in mrp_bom_obj_ids:
			obj_mrp = mrp_bom_obj.browse(cr,uid,mrp_id,)
			for ls in loop_size:
				if obj_mrp.size == ls:
					if obj_mrp.size == 'S':
						size = self.browse(cr,uid,ids,context)[0].s_order
					elif obj_mrp.size == 'M':
						size = self.browse(cr,uid,ids,context)[0].m_order
					elif obj_mrp.size == 'L':
						size = self.browse(cr,uid,ids,context)[0].l_order
					elif obj_mrp.size == 'XL':
						size = self.browse(cr,uid,ids,context)[0].xl_order
					elif obj_mrp.size == 'XXL':
						size = self.browse(cr,uid,ids,context)[0].xxl_order
					else :
						size = self.browse(cr,uid,ids,context)[0].xxxl_order

					if size == 0.0:
						continue
					
					data_line = {
							'name'				: ls, 
							'product_id'        : obj_mrp.product_id.id,
							'product_qty'       : size,
							'product_uom'		: obj_mrp.product_id.uom_id.id,
							'location_id'       : master_lokasi_obj.source_loc_id.id,
							'location_dest_id'  : master_lokasi_obj.dest_loc_id.id,
							'spk_mkl_id'		: self.browse(cr,uid,ids[0],).id
							}
							
					move_lines = [(0,0,data_line)]
					stock_data = {
						'move_lines'     	: move_lines,
						}

					stock_in_objs.write(cr, uid, stock_in_obj, stock_data, context=context)

		## Update Status Incoming 
		self.update_state(cr,uid,ids,context)

		### Fungsi-fungsi untuk mengarahkan ke result list
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		## Arahkan Ke List Tree stock.picking.in dengan Ciri-ciri <record id="action_picking_tree4" model="ir.actions.act_window">
		result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')

		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]

		return True

	def action_move_accessories(self, cr, uid, ids, context=None):
		
		lokasi_barang_jadi = 'Lokasi Bahan Baku Kain'
		lokasi_produksi = 'Lokasi Produksi'
		virtual_production = 'Production'
		lokasi_barang_jadi_id = self.pool.get('stock.location').search(cr,uid,[('name','=',lokasi_barang_jadi)])[0]
		virtual_production_id = self.pool.get('stock.location').search(cr,uid,[('name','=',virtual_production)])[0]
	
		# Update : Pencarian lokasi melalui parameter
		# Pencarian source dan destinasi lokasi melalui master lokasi		
		if self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_move_accessories')]) == []:
			raise osv.except_osv("Konfigurasi Nama Method : action_move_accessories Tidak ditemukan ", "[Setting Di Configuration Setting -> Master Location], Misal source : Lokasi Bahan Baku Kain, Dest: Virtual/Production")
		else:	
			master_lokasi_id = self.pool.get('vit.master.location').search(cr,uid,[('name','=','action_move_accessories')])[0]
			master_lokasi_obj = self.pool.get('vit.master.location').browse(cr,uid,master_lokasi_id,)

		### Buat Internal Move Dari Gudang Jadi ke Produksi ####
		########################################################
		### Create Dahulu ######################################
		sp_obj   = self.pool.get('stock.picking')
		sp_data1 = {
				'origin'			: self.browse(cr,uid,ids,context)[0].name,
				'note'				: "Pemakaian Accessories",
			}

		sp_id_create = sp_obj.create(cr, uid, sp_data1, context=context)

		### Update move_lines nya ###############################
		for acc_line in self.browse(cr,uid,ids,context)[0].accessories_req_line_ids:
			product_id = self.pool.get('product.product').browse(cr, uid, acc_line.material.id, context=context).id
			data_line = { 
				'name'				: self.browse(cr,uid,ids,context)[0].name,
				'product_id'        : product_id,
				'product_qty'       : acc_line.qty,
				'product_uom'		: acc_line.uom_id.id,
				'location_id'       : master_lokasi_obj.source_loc_id.id,
				'location_dest_id'  : master_lokasi_obj.dest_loc_id.id,
			}
			
			move_lines = [(0,0,data_line)]
			sp_data = {
				'move_lines'     	: move_lines,
			}
			sp_obj.write(cr, uid, sp_id_create, sp_data, context=context)
		### Lakukan Validate di Internal Move ####
		# sp_obj.draft_validate(cr,uid,[sp_id_create],context=context)
		# return self.write(cr, uid, ids, {'state':'inprogres', 'count_list_internal_move':1}, context=context)
		return True

	def check_loaded_acc(self,cr,uid,ids,context):
		if self.browse(cr,uid,ids,context)[0].loaded_acc == False:
			raise osv.except_osv("Lakukan Load Qty Di Tab Usage Material Accessories","!!")
		else:
			return True

	def update_state(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'tobereceived', 'state_incoming' : 'draft'},context=context)

	# def update_state2(self,cr,uid,ids,pick_id,context=None):
	# 	stock_in_objs = self.pool.get('stock.picking.in')
	# 	stock_in_obj = stock_in_objs.browse(cr,uid,pick_id,context=context)
	# 	import pdb;pdb.set_trace()
		
	# 	if stock_in_obj.state == 'done':
	# 		self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
	# 	return self.write(cr,uid,ids,{'state_incoming' : stock_in_obj.state},context=context)

	# def update_state3(self,cr,uid,ids,pick_id,context=None):
	# 	stock_in_objs = self.pool.get('stock.picking.in')
		
	# 	for x in pick_id:
	# 		stock_in_obj = stock_in_objs.browse(cr,uid,x,context=context)
	# 		if stock_in_obj.state != 'done':
	# 			if stock_in_obj.state != 'assigned':
	# 				if stock_in_obj.state != 'cancel':
	# 					if stock_in_obj.state != 'auto':
	# 						if stock_in_obj.state != 'confirmed':
	# 							x = 0
	# 							#w: jika int_move yg terakhir di looping draft, maka form makloon jd sraft juga
	# 							#self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
		
	# 	# if stock_in_obj.state == 'done':
	# 	# 	self.write(cr,uid,ids,{'state' : stock_in_obj.state},context=context)
	# 	return self.write(cr,uid,ids,{'state_incoming' : stock_in_obj.state},context=context)

	def action_split_grade(self, cr, uid, ids, context=None):																	
		#set to "confirmed" state
		self.write(cr, uid, ids, {'state':'grade'}, context=context)
		return True

	def on_partner_id(self, cr, uid, ids, partner_id, context=None):
		self.update_value_journal(cr,uid,ids,partner_id,context)
		if partner_id != False:
			partner_obj = self.pool.get('res.partner',)
			partner = partner_obj.browse(cr, uid, partner_id, context=context)
			return {
				'value' : {
					'address' : partner.street,
				}
			}
		else:
			return {
				'value' : {
					'address' : '',
				}
			}

	def on_type_product_id(self, cr, uid, ids, type_product_id, context=None):
		self.update_value_journal2(cr,uid,ids,type_product_id,context)
		if type_product_id != False:
			master_type_obj = self.pool.get('vit.master.type',)
			master = master_type_obj.browse(cr, uid, type_product_id, context=context)
			return {
				'value' : {
					'model' : master.model_product,
				}
			}
		else:
			return {
				'value' : {
					'model' : '',
				}
			}


	def on_change_id(self, cr, uid, ids, type_product_id, context=None):

		vit_master_type_obj = self.pool.get('vit.master.type',)
		master_type = vit_master_type_obj.browse(cr, uid, type_product_id, context=context)

		prod_categ_obj = self.pool.get('product.category')
		name_prod_categ_obj = prod_categ_obj.browse(cr,uid,master_type.categ_id.id,context=context)
		return {
			'value' : {
				'category' : name_prod_categ_obj.name,
				'component_main_qty' 		: master_type.main_qty,
				'component_variation_qty' 	: master_type.variation_qty,
			}
		}


	#################################################################################
	## Membuat Jurnal #######################################
	#################################################################################
	def journal_biaya(self, cr, uid, ids, context=None):

		##############################################################################
		# ambil master journal
		##############################################################################
		ir_model_obj = self.pool.get('ir.model')
		ir_model_ids = ir_model_obj.search(cr, uid, 
			[('model','=', self._name)], context=context) # dapat model_id dari cutting_order ex : [486]

		ir_model_fields_obj = self.pool.get('ir.model.fields')
		ir_model_fields_ids = ir_model_fields_obj.search(cr, uid, 
			[('model_id','=', ir_model_ids[0])], context=context) # dapat id dari ir.model.fields filter dari ir_model_ids (misal cutting_order)

		master_journal_obj   = self.pool.get('vit.master.journal')
		 
		# self.browse(cr,uid,ids[0],).jurnal_value_ids[0].master_jurnal_id.target_field.id #Id Field dari jurnal_value_ids misal : 4332 
		## Loop jurnal_value_ids
		for jurnal_value_id in self.browse(cr,uid,ids[0],).jurnal_value_ids:
			# master_ids   = master_journal_obj.search(cr, uid, 
			# 	[('is_active','=', True),('target_field','=',jurnal_value_id.master_jurnal_id.target_field.id)], context=context)
			master_ids   = master_journal_obj.search(cr, uid, 
				[('is_active','=', True),('name','=',jurnal_value_id.master_jurnal_id.name)], context=context)
			for master_id in master_ids:
				master = master_journal_obj.browse(cr,uid,master_id)
				########################################################################
				# create account move utk point
				#########################################################################
				if context==None:
					context={}
				context['account_period_prefer_normal']= True
				period_id 	= self.pool.get('account.period').find(cr,uid, self.browse(cr,uid,ids[0],).date_taking, context)[0]
				debit = {
					'date'       : self.browse(cr,uid,ids[0],).date_taking,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.debit_account_id.id,
					'debit'      : jurnal_value_id.value * self.browse(cr,uid,ids[0],).qty_order,
					'credit'     : 0.0 
				}
				
				credit = {
					'date'       : self.browse(cr,uid,ids[0],).date_taking,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.credit_account_id.id,
					'debit'      : 0.0 ,
					'credit'     : jurnal_value_id.value * self.browse(cr,uid,ids[0],).qty_order ,
					}

				lines = [(0,0,debit), (0,0,credit)]
				am_obj            = self.pool.get('account.move')
				am_data = {
					'journal_id'   : master.journal_id.id,
					'date'         :  self.browse(cr,uid,ids[0],).date_taking,
					'ref'          : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'period_id'    : period_id,
					'line_id'      : lines ,
					}

				am_id = am_obj.create(cr, uid, am_data, context=context)
				# am_obj.button_validate(cr, uid, [am_id], context=context)


	#################################################################################
	## Membuat Jurnal  reward #######################################
	#################################################################################
	def journal_reward(self,cr,uid,ids,reward_steam,qty,context=None):
		master_journal_obj   = self.pool.get('vit.master.journal')
		master_ids   = master_journal_obj.search(cr, uid, 
				[('is_active','=', True),('name','=','Reward Steam')], context=context)
		for master_id in master_ids:
			master = master_journal_obj.browse(cr,uid,master_id)
			########################################################################
			# create account move utk point
			#########################################################################
			if context==None:
				context={}
			context['account_period_prefer_normal']= True
			period_id 	= self.pool.get('account.period').find(cr,uid, self.browse(cr,uid,ids[0],).date_taking, context)[0]
			debit = {
					'date'       : self.browse(cr,uid,ids[0],).date_taking,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.debit_account_id.id,
					'debit'      : reward_steam,
					'credit'     : 0.0 
				}
				
			credit = {
					'date'       : self.browse(cr,uid,ids[0],).date_taking,
					'name'       : self.browse(cr,uid,ids[0],).name,
					'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
					'account_id' : master.credit_account_id.id,
					'debit'      : 0.0 ,
					'credit'     : reward_steam,
					}

			lines = [(0,0,debit), (0,0,credit)]
			am_obj            = self.pool.get('account.move')
			am_data = {
					'journal_id'   : master.journal_id.id,
					'date'         :  self.browse(cr,uid,ids[0],).date_taking,
					'ref'          : master.name +' '+self.browse(cr,uid,ids[0],).name,
					'period_id'    : period_id,
					'line_id'      : lines ,
					}

			am_id = am_obj.create(cr, uid, am_data, context=context)
				# am_obj.button_validate(cr, uid, [am_id], context=context)



	# #################################################################################
	# ## Membuat Jurnal MAKLON/ONGKOS JAHIT  #######################################
	# #################################################################################
	# def journal_ongkos_jahit(self, cr, uid, ids, context=None):
	# 	##############################################################################
	# 	# ambil master journal
	# 	##############################################################################
	# 	master_journal_obj   = self.pool.get('vit.master.journal')
	# 	master_ids   = master_journal_obj.search(cr, uid, 
	# 		[('is_active','=', True)], context=context)

	# 	master_type_obj   = self.pool.get('vit.master.type')
	# 	master_type_ids = master_type_obj.search(cr,uid,[('model_product','=',self.browse(cr,uid,ids[0],).model)])
	# 	master_type = master_type_obj.browse(cr,uid,master_type_ids[0])
		
	# 	kancing_price = master_type.kancing_price

	# 	for master_id in master_ids:
	# 		master = master_journal_obj.browse(cr,uid,master_id)
	# 		#########################################################################
	# 		# create account move utk point
	# 		#########################################################################
	# 		if context==None:
	# 			context={}
	# 		context['account_period_prefer_normal']= True
	# 		period_id 	= self.pool.get('account.period').find(cr,uid, self.browse(cr,uid,ids[0],).date_taking, context)[0]
			
	# 		if master.target_field.name == 'makloon_cost':
	# 			debit = {
	# 				'date'       : self.browse(cr,uid,ids[0],).date_taking,
	# 				'name'       : self.browse(cr,uid,ids[0],).name,
	# 				'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
	# 				#'ref'        : 'Upah Direct Labour %s' % (self.browse(cr,uid,ids[0],).name),
	# 				'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
	# 				'account_id' : master.debit_account_id.id,
	# 				'debit'      : (kancing_price * self.browse(cr,uid,ids[0],).qty_order)+(self.browse(cr,uid,ids[0],).sewing_cost * self.browse(cr,uid,ids[0],).qty_order),
	# 				'credit'     : 0.0, 
	# 			}
	# 			credit = {
	# 				'date'       : self.browse(cr,uid,ids[0],).date_taking,
	# 				'name'       : self.browse(cr,uid,ids[0],).name,
	# 				'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
	# 				'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
	# 				'account_id' : master.credit_account_id.id,
	# 				'debit'      : 0.0 ,
	# 				'credit'     : kancing_price * self.browse(cr,uid,ids[0],).qty_order ,
	# 				}

	# 			credit2 = {
	# 				'date'       : self.browse(cr,uid,ids[0],).date_taking,
	# 				'name'       : self.browse(cr,uid,ids[0],).name,
	# 				'ref'        : master.name +' '+self.browse(cr,uid,ids[0],).name,
	# 				'partner_id' : self.browse(cr,uid,ids[0],).user_id.id,
	# 				'account_id' : master.credit_account_id2.id,
	# 				'debit'      : 0.0 ,
	# 				'credit'     : self.browse(cr,uid,ids[0],).sewing_cost * self.browse(cr,uid,ids[0],).qty_order ,
	# 				}
		
			
	# 			lines = [(0,0,debit), (0,0,credit),(0,0,credit2)]
	# 			am_obj            = self.pool.get('account.move')
	# 			am_data = {
	# 				'journal_id'   : master.journal_id.id,
	# 				'date'         :  self.browse(cr,uid,ids[0],).date_taking,
	# 				'ref'          : master.name +' '+self.browse(cr,uid,ids[0],).name,
	# 				'period_id'    : period_id,
	# 				'line_id'      : lines ,
	# 				}

	# 			am_id = am_obj.create(cr, uid, am_data, context=context)
	# 			# am_obj.button_validate(cr, uid, [am_id], context=context)

	# 	return True

vit_makloon_order()



#class untuk value jurnal-jurnal tambahan dalam cutting relasi dengan master jurnal
class jurnal_value(osv.Model):
	_name = "vit.jurnal.value.makloon"

	_columns = {
		'makloon_order_id': fields.many2one('vit.makloon.order', 'Makloon Reference',required=True, ondelete='cascade', select=True),
		'master_jurnal_id': fields.many2one('vit.master.journal', 'Overheads',required=True),
		'value' : fields.float('Overhead Per Pcs',required=True),
	}


	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['master_jurnal_id'], context=context)

		res = []
		for record in reads:
			name = record['master_jurnal_id'][1]
			if record['master_jurnal_id'][1]:
				name = record['master_jurnal_id'][1]
			res.append((record['id'], name))
		return res
jurnal_value()
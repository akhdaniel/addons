import time
from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID

class mrp_production(osv.osv):
	_name = 'mrp.production'
	_description = 'Manufacturing Order'
	_inherit = 'mrp.production'

	def _get_default_overhead(self, cr, uid, context=None):
		if context is None:
			context = {}
		overhead_value_ids = []
		ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
		master_overhead_obj   = self.pool.get('vit.master.overheads')
		master_ids   = master_overhead_obj.search(cr, uid,[('appeareance','=',ir_model_id[0])])
		for master_id in master_ids:
			overhead_value_ids.append((0,0,{'master_overhead_id':master_id,'value':0}))
		return overhead_value_ids


	_columns = {
		'overhead_value_ids':fields.one2many('vit.overhead.value','mrp_prod_id','Overhead Value'),
		}

	_defaults = {
		'overhead_value_ids' : _get_default_overhead
	}



	def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context = {}):
		mrp_obj = self.pool.get('mrp.production')
		move_obj = self.pool.get('account.move')
		mrp_id = mrp_obj.browse(cr,uid,production_id)
		res = super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, context={})

		if production_mode == "consume":
			self.create_overhead_journal(cr,uid,production_qty,production_id,production_mode,context)
		else:
			move_line = []
			for overhead in mrp_id.overhead_value_ids:
				ref =  overhead.master_overhead_id.name +' '+mrp_id.name
				# move_line = move_obj.search(cr,uid,[('ref','=', ref),('is_flagged','=', False)])
				move_line = move_obj.search(cr,uid,[('ref','=', ref)])
			if move_line == []:
				return
			else:
				self.create_overhead_journal(cr,uid,production_qty,production_id,production_mode,context)
				move_line2 = move_obj.search(cr,uid,[('ref','=', ref),('is_flagged','=', False)])
				for mv_id in move_line2:
					""" Mencegah Kelebihan Create Overhead, Delete Terlebih dahulu id move_line yg is_flagged =  true terakhir """
					sql = """delete from account_move where id = %s """%(mv_id)
					cr.execute(sql)
					cr.commit()
			self.update_jurnal_stock(cr,uid,production_id,production_qty,context)
		return res

	

	def check_overhead(self,cr,uid,production_id,context=None):
		mrp_obj = self.pool.get('mrp.production')
		move_obj = self.pool.get('account.move')
		mrp_id = mrp_obj.browse(cr,uid,production_id)

		""" Loop Overheadnya"""
		move_line = []
		for overhead in mrp_id.overhead_value_ids:
			ref =  overhead.master_overhead_id.name +' '+mrp_id.name
			move_line = move_obj.search(cr,uid,[('ref','=', ref),('is_flagged','=', False)])
			
		if move_line == []:
			import pdb;pdb.set_trace()
			return True
		else:
			for mv_id in move_line:
				move_obj.write(cr,uid,[mv_id],{'is_flagged':True})
				
				""" Mencegah Kelebihan Create Overhead, Delete Terlebih dahulu id move_line yg is_flagged =  true terakhir """
				sql = """delete from account_move where id = %s """%(mv_id)
				cr.execute(sql)
				cr.commit()
			return False


	def create_overhead_journal(self,cr,uid,production_qty,production_id,production_mode,context=None):
		mrp_obj = self.pool.get('mrp.production')
		move_obj = self.pool.get('account.move')
		mrp_id = mrp_obj.browse(cr,uid,production_id)
		""" Loop Overheadnya"""
		for overhead in mrp_id.overhead_value_ids:
			period_id 	= self.pool.get('account.period').find(cr,uid, mrp_id.date_planned, context)[0]
			debit ={
					'date'		 : mrp_id.date_planned,
					'name'       : mrp_id.name,
					'account_id' : overhead.master_overhead_id.debit_account_id.id,
					'debit'      : overhead.value * production_qty,
					'credit'     : 0.0 
					}

			credit ={
					'date'		 : mrp_id.date_planned,
					'name'       : mrp_id.name,
					'account_id' : overhead.master_overhead_id.credit_account_id.id,
					'debit'      : 0.0,
					'credit'     : overhead.value * production_qty
					}

			lines = [(0,0,debit), (0,0,credit)]		
			
			if production_mode == "consume":
				am_data = {
						'journal_id'   : overhead.master_overhead_id.journal_id.id,
						'date'         : mrp_id.date_planned,
						'ref'          : overhead.master_overhead_id.name +' '+mrp_id.name,
						'period_id'    : period_id,
						'line_id'      : lines,
						'is_flagged'   : False,
						}
			else:
				am_data = {
						'journal_id'   : overhead.master_overhead_id.journal_id.id,
						'date'         : mrp_id.date_planned,
						'ref'          : overhead.master_overhead_id.name +' '+mrp_id.name,
						'period_id'    : period_id,
						'line_id'      : lines,
						'is_flagged'   : True,
						}


			am_id = move_obj.create(cr, uid, am_data, context=context)


	def update_jurnal_stock(self,cr,uid,production_id,production_qty,context=None):
		"""Object-object account move, account move line dan MRP
		"""
		move_obj = self.pool.get('account.move')
		move_line_obj = self.pool.get('account.move.line')
		mrp_obj = self.pool.get('mrp.production')
		mrp_id = mrp_obj.browse(cr,uid,production_id)
		
		account_id = mrp_id.product_id.categ_id.property_stock_valuation_account_id.id
		
		"""Cari Move Line Id dengan Name = Name di MRP
		   dan account_id = account_id di product dengan 
		   property_stock_valuation_account_id nya
		"""
		
		move_line_id = move_line_obj.search(cr,uid,[('name','=', mrp_id.name),('account_id','=', account_id)])
		if move_line_id ==[]:
			return


		""" Cari date,ref dll"""
		date = move_line_obj.browse(cr,uid,move_line_id[0]).date
		

		"""Temukan Kembali id account move yang akan ditargetkan di update dengan 
		   COA Overheadnya , dengan id yang di peroleh dari account.move.line nya
		"""
		move_id = move_line_obj.browse(cr,uid,move_line_id[0]).move_id

		move_line_id_acc_debit = move_line_obj.search(cr,uid,[('name','=', mrp_id.name),('debit','!=', 0.0),('move_id','=', move_id.id)])
		move_line_id_acc_credit = move_line_obj.search(cr,uid,[('name','=', mrp_id.name),('credit','!=', 0.0),('move_id','=', move_id.id)]) 
		
		account_id_deb = move_line_obj.browse(cr,uid,move_line_id_acc_debit[0]).account_id.id
		account_id_cre = move_line_obj.browse(cr,uid,move_line_id_acc_credit[0]).account_id.id
		# import pdb;pdb.set_trace()

		""" Loop Overheadnya"""
		for overhead in mrp_id.overhead_value_ids:
			debit ={
					'date'		 : date,
					'name'       : overhead.master_overhead_id.name,
					'account_id' : account_id_deb,
					'debit'      : overhead.value * production_qty,
					'credit'     : 0.0 
					}

			credit ={
					'date'		 : date,
					'name'       : overhead.master_overhead_id.name,
					'account_id' : account_id_cre,
					'debit'      : 0.0,
					'credit'     : overhead.value * production_qty
					}

			lines = [(0,0,debit), (0,0,credit)]		
			am_data = {
						'line_id'      : lines ,
					   }

			am_id = move_obj.write(cr, uid,[move_id.id], am_data, context=context)



class overhead_value(osv.Model):
	_name = "vit.overhead.value"

	_columns = {
		'mrp_prod_id': fields.many2one('mrp.production', 'Mrp Reference',required=True, ondelete='cascade', select=True),
		'master_overhead_id': fields.many2one('vit.master.overheads', 'Overheads',required=True),
		'value' : fields.float('Overhead Per Pcs',required=True),
	}


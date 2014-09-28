from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import math

_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
	_name 		= "sale.order"
	_inherit 	= "sale.order"

	def action_button_confirm(self, cr, uid, ids, context=None):
		res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

		##############################################################################
		# ambil master gift, jika ada gift hari ini, proceed cek SO
		##############################################################################
		gift_obj   = self.pool.get('vit_sale_gift.master_gift')
		gift_ids   = gift_obj.search(cr, uid, 
			[('is_active','=', True)], context=context)

		for gift_id in gift_ids:
			#########################################################################
			# hapus existing gifts from so line
			#########################################################################
			cr.execute("delete from sale_order_line where name like '%s' and order_id=%d" % ('FREE%' , ids[0]))

			#########################################################################
			# the gift record
			#########################################################################
			gift            = gift_obj.browse(cr, uid, gift_id) 

			#########################################################################
			# cek SO line apakah matching dengan konsisi gift;
			#########################################################################
			so              = self.browse(cr, uid, ids[0] , context=context)

			#########################################################################
			# TODO kondisi gift sesuai kompisisi produk
			#########################################################################
			if gift.product_condition_ids:
				sol_data = [{sol.product_id.id : sol.product_uom_qty} for sol in so.order_line]


			#########################################################################
			# kondisi gift sesuai komposisi category produk
			#########################################################################
			elif gift.categ_condition_ids:
				sol_data  = [(sol.product_id.categ_id.id,sol.product_uom_qty) for sol in so.order_line]
				gift_data = [(pl.product_categ_id.id,pl.min_qty) for pl in gift.categ_condition_ids]
				

				#import pdb; pdb.set_trace()
				######## pengecekan total semua qty so line
				if gift.total_qty>0:
					print gift_data
					print sol_data

					######## kalau categ gift = categ sol , incremet total_sol
					total_sol = 0.0
					total_min = gift.total_qty 
					for g in gift_data:
						for l in sol_data:
							if g[0] == l[0]:
								total_sol = total_sol + l[1]
					if total_sol >= gift.total_qty:
						print "total qty gift >= total so line "
						qty = self.find_multiply(cr, uid, gift, total_min, total_sol, context=context)

						old = [(0,0, { 
							'product_id'     : gift.product_id.id, 
							'name'           : "FREE %s" % (gift.product_id.name),
							'product_uom_qty': qty })]
						self.write(cr, uid, ids, {'order_line' : old}, context=context)

				######## pengecekan satu per satu so line sesaui min qty gift
				else:
					print "cek satu per satu so line apakah lebih dari minimal qty gift"
					sol_categ = {}
					for l in sol_data:
						categ_id = l[0]
						sol_categ[categ_id] = sol_categ.get(categ_id,0) + l[1]

					total_sol = 0.0
					total_min = 0.0
					for g in gift_data:
						total_min = total_min + g[1]
						for k in sol_categ.keys():
							if k == g[0]:                  # if same category
								if sol_categ[k] >= g[0]:   # if exceed gift minimum qty  
									total_sol = total_sol + sol_categ[k]
								else:
									total_sol = 0.0

					#kalau dapat gift:
					if total_sol > 0.0:
						qty = self.find_multiply(cr, uid, gift, total_min, total_sol, context=context)
						old = [(0,0, { 
							'product_id'     : gift.product_id.id, 
							'name'           : "FREE %s" % (gift.product_id.name),
							'product_uom_qty': qty })]
						self.write(cr, uid, ids, {'order_line' : old}, context=context)

			#########################################################################
			# jika matching, tambahkan gift product ke SO line
			#########################################################################

		return res

	def find_multiply(self, cr, uid, gift, total_min, total_sol, context=None):
		qty = 0.0
		if gift.multiple:
			m = math.trunc(total_sol / total_min)
			qty = gift.qty * m
		else:
			qty = gift.qty

		return qty 

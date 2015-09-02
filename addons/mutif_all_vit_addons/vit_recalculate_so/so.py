from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

 #    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
 #    	res= super(sale_order, self)._amount_all(cr, uid, ids, field_name, arg, context=context)
 #    	return res
    
 #    _columns = {
	# 	'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
 #            store = True,
 #            multi='sums', help="The amount without tax.", track_visibility='always')
	# }

    


    def recalculate(self, cr, uid, ids, context=None):
        
        for so in self.browse(cr, uid, ids, context=context):
        	for line in so.order_line:
	        	price = line.product_id.list_price
	        	id = line.id
	        	discount = so.partner_id.discount
	        	qty_available = line.product_id.qty_available
	        	outgoing_qty  = line.product_id.outgoing_qty
	        	virtual_available = line.product_id.virtual_available
	        	max_order = qty_available + outgoing_qty
	        	
	        	if virtual_available > 0.0:
       				# import pdb;pdb.set_trace()
		        	if line.product_uom_qty > max_order:
		        		can_ordered = max_order
		        	else:
		        		can_ordered = line.product_uom_qty
		        else:
		        	can_ordered = 0.00
		        	max_order = 0.00


	        	### Buat Variable diskon pengali berdasarkan line yang bila defaulnya 0.0 maka akan mendapatkan
	        	### Nilai diskon dari master, Bila else maka artinya nilai dari imputan manual di line
	        	if line.discount != 0.0:
	        		discount_pengali = line.discount
	        	else:
	        		discount_pengali = discount

	        	### Fungsi Menghasilkan Harga dari Kuantiti yang tersedia 	
	        	price_max_order = (can_ordered * line.price_unit) - (can_ordered * line.price_unit) * (discount_pengali/100)
	        	
	        	### Update nilai diskon dahulu
	        	if line.discount != 0.0:
       				cr.execute('update sale_order_line set discount=%f where id=%d' %(line.discount,id))
       			else:
       				cr.execute('update sale_order_line set discount=%f where id=%d' %(discount,id))

       			### Cari Dulu barang ongkos kirim untuk bisa di lewat dan Isi nilai default can ordered nya dengan 1 dan nilai diskonnya 0.00
       			if line.product_id.default_code == 'OK000002439' or line.product_id.name == 'Ongkos Kirim':
       				cr.execute('update sale_order_line set real_max_order=%f, price_max_order=%d, discount=%f   where id=%d' %(1,line.price_unit,0.00,id))
       				continue

       			### Cari Dulu barang Katalog untuk bisa di lewat dan Isi nilai default can ordered nya dengan 1 dan nilai diskonnya 0.00
       			if line.product_id.categ_id.name =='Katalog' or line.product_id.default_code == 'KL0020140002391' or line.product_id.name == 'Katalog 2014-2015':
       				cr.execute('update sale_order_line set real_max_order=%f, price_max_order=%d, discount=%f   where id=%d' %(can_ordered,line.price_unit*can_ordered,0.00,id))
       				continue

       			# Pada saat Progress atau statu di sale order jangan update field real_max_order, price_max_order
       			if so.state != 'progress':
		        	if line.product_uom_qty == 0:
		        		cr.execute('delete from sale_order_line where id = %d' %(id))
		        	else:
		        		# cr.execute('update sale_order_line set price_unit=%f, discount=%f, qty_hand=%s, outgoing =%s, forecast=%s  where id=%d' %(price,discount,qty_available,outgoing_qty,virtual_available,id))
	       				# cr.execute('update sale_order_line set price_unit=%f, discount=%f, qty_hand=%s, outgoing =%s, forecast=%s, real_max_order=%s ,max_order=%s, price_max_order=%s where id=%d' %(price,discount,qty_available,outgoing_qty,virtual_available ,can_ordered,max_order,price_max_order,id))
	       				cr.execute('update sale_order_line set price_unit=%f, qty_hand=%s, outgoing =%s, forecast=%s, real_max_order=%s ,max_order=%s, price_max_order=%s where id=%d' %(price,qty_available,outgoing_qty,virtual_available ,can_ordered,max_order,price_max_order,id))
	       		else:
	       			cr.execute('update sale_order_line set price_unit=%f, qty_hand=%s, outgoing =%s, forecast=%s ,max_order=%s where id=%d' %(price,qty_available,outgoing_qty,virtual_available ,max_order,id))



       			# if line.product_id.default_code == 'OK000002439':
       			# 	cr.execute('update sale_order_line set price_unit=%d where id=%d' %(line.price_unit,id))
       			
       			# if line.product_uom_qty > max_order:
       			# 	cr.execute('update sale_order_line set product_uom_qty=%d  where id=%d' %(max_order,id))

       			# import pdb;pdb.set_trace()
       			# if  line.product_uom_qty < max_order:
       			# 	cr.execute('update sale_order_line set product_uom_qty=%d  where id=%d' %(line.product_uom_qty,id))

        self.write(cr,uid,ids,{'order_line':[(0,0,{'name':'-'})]},context=context)    		
        

        for so2 in self.browse(cr, uid, ids, context=context):
        	for line in so2.order_line:
	        	id = line.id	
	        	if line.name == "-":
	        		cr.execute('delete from sale_order_line where id = %d' %(id))

	        	# if line.qty_hand =="0.0":
	        	# 	# import pdb;pdb.set_trace()
	        	# 	cr.execute('delete from sale_order_line where id = %d' %(id))

	    # for so3 in self.browse(cr, uid, ids, context=context):
	    # 	for line in so3.order_line:
	    # 		if line.qty_hand == 0:
	    #     		cr.execute('delete from sale_order_line where id = %d' %(id))
	    
	    ##################################################
	    ###  Cari Max_order < 0 ,lalu update menjadi 0 ###
	    ##################################################
		# for so4 in self.browse(cr, uid, ids, context=context):
		# 	for line in so4.order_line:
		# 		id = line.id
		# 		max_order = 0.00
		# 		if line.max_order < 0.00:
		# 			cr.execute('update sale_order_line set  max_order=%s  where id=%d' %(max_order,id))

		# ##################################################
	 # 	 ###  Cari price max order < 0 ,lalu update menjadi 0 ###
	 #    ##################################################
		# for so5 in self.browse(cr, uid, ids, context=context):
		# 	for line in so5.order_line:
		# 		id = line.id
		# 		price_max_order = 0.00
		# 		if line.price_max_order < 0.00:
		# 			cr.execute('update sale_order_line set  price_max_order=%s  where id=%d' %(price_max_order,id))


		#################################################
	    ##  Cari Max_order < 0 && real_max_order &&  price_max_order ,lalu update menjadi 0 ###
	    #################################################
		for so4 in self.browse(cr, uid, ids, context=context):
			for line in so4.order_line:
				id = line.id
				zero = 0.00
				max_order = 0.00
				if line.max_order and  line.real_max_order and line.price_max_order < 0.00:
					cr.execute('update sale_order_line set real_max_order=%d , max_order=%s, price_max_order=%d  where id=%d' %(zero,zero,zero,id))

	return True
        
sale_order()

# class sale_order_line(osv.osv):

# 	_name = 'sale.order.line'
# 	_inherit = "sale.order.line"
	
# 	_columns = {
# 		'real_max_order': fields.float('Can Ordered'),
# 		'max_order' : fields.float('Max Order'),
# 		'price_max_order' : fields.float('Price Max Order')
# 	}

# sale_order_line()




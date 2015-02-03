from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import sets
import math

#state surat jalan
SJ_STATES =[
	('draft','Draft'),
	('on_deliver','On Delivery'),
	('return','Done'),]

class fleet_vehicle(osv.osv):
	_inherit = "fleet.vehicle"
	_name = "fleet.vehicle"

	_columns = {
		'volume': fields.float('Capacity (Volume)',help="Dalam Satuan m3 (meter kubik)"),
		'tonase': fields.float('Capacity (weight)',help='Dalam Satuan Kg'),
		'driver_id2': fields.many2one('hr.employee','Driver'),
		}

class surat_jalan(osv.osv):
	_name = "surat.jalan"
	_order = 'name desc'


	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'surat.jalan') or '/'
		return super(surat_jalan, self).create(cr, uid, vals, context=context)

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(surat_jalan, self).unlink(cr, uid, ids, context=context)

	def onchange_volume(self,cr,uid,ids,car_id,context=None):
		result={}
		if not car_id:
			return results
		fle = self.pool.get('fleet.vehicle')
		flee = fle.search(cr,uid,[('id','=',car_id)])
		fleet = fle.browse(cr,uid,flee)[0].volume
		fleet2 = fle.browse(cr,uid,flee)[0].tonase
		sup = fle.browse(cr,uid,flee)[0].driver_id2.id

		val = {'volume':fleet,'weight':fleet2,'driver_id2':sup}
		return {'value':val}

	def action_draft(self,cr,uid,ids,context=None): 
		fl = self.browse(cr, uid, ids[0], context=context)
		mv_obj = self.pool.get('stock.move')
		#kembalikan status semua invoice ke draft
		inv = []
		for line in fl.inv_ids:
			inv_ori = line.origin

			mv = mv_obj.search(cr,uid,[('origin','=',inv_ori)],context=context)
			if mv == []:
				raise osv.except_osv(_('Error!!'), _('Faktur harus dibuat melalui SO!'))			
			mv_id = mv_obj.browse(cr,uid,mv[0])

			if mv_id.id :
				mv = mv_id.id
				#done kan stock move agar qty on hand berkurang
				mv_obj.write(cr,uid,mv_id.id,{'state':'assigned'},context=context)	


			if line.state not in ['open','paid']:
				acc = self.pool.get('account.invoice')
				ass = acc.write(cr,uid,[line.id],{'state':'draft','button_hidden':False},context=context)

			if line.state in ['draft','deliver']:
				inv_id = line.id
				inv.append(inv_id)

		#hapus/reset ulang semua product list
		for line2 in fl.list_product_ids:
			acc = self.pool.get('list.product')
			acc.unlink(cr,uid,[line2.id],context)

		# import pdb;pdb.set_trace()
		#hapus move  dan invoive list yg selain
		move_ids = []
		self.write(cr,uid,ids[0],{'move_ids':[(6, 0, move_ids)],'inv_ids':[(6, 0, inv)]})

		return self.write(cr,uid,ids,{'state':SJ_STATES[0][0]},context=context)
		
	def action_on_deliver(self,cr,uid,ids,context=None):
		
		mv_obj = self.pool.get('stock.move')
		acc = self.pool.get('account.invoice')
		mvp_obj = self.pool.get('stock.move.pick')

		fl = self.browse(cr, uid, ids[0], context=context)#FFFFFF#FFFFFF

		flo =fl.car_id.volume
		flo2 = fl.car_id.tonase
		 
		id_inv = []
		move_ids=[]
		val =  0.0
		brt = 0.0
		t_qty = 0.0
		for line in fl.inv_ids:
			val += line.volume
			brt += line.weight	
			idd = line.id
			id_inv.append(idd)	
			orig = line.origin
			#write invoice ke state deliver
			acc.write(cr,uid,[line.id],{'state':'deliver','button_hidden':True,'state2':'deliver'},context=context)

			for brg in line.invoice_line:
				qty = brg.quantity
				t_qty += qty
			#import pdb;pdb.set_trace()
			mv_sch = mv_obj.search(cr,uid,[('origin','=',orig)])
			if mv_sch != []:
				mv_brw = mv_obj.browse(cr,uid,mv_sch[0])
				mv_obj.write(cr,uid,mv_brw.id,{'state':'done'},context=context)
		#import pdb;pdb.set_trace()	
		# invs =tuple(id_inv)
		# cr.execute('select sum (sm.product_qty) '\
		# 	'from stock_move sm '\
		# 	'join account_invoice ai on sm.origin = ai.origin '\
		# 	'join account_invoice_line ail on ail.invoice_id = ai.id '\
		# 	'where ai.id in (%s)',(invs))
		# t = cr.fetchone()
		# t_q = list(t or 0.0) 
		# t_qty_t = t_q[0]
		t_qty_t = 0.0
		for mov in fl.move_ids :
			t_qty_t += mov.product_qty

		if t_qty != t_qty_t :			
			raise osv.except_osv(_('Error!!'), _('Qty produk tidak sama, Jumlah di invoice %s ,  Jumlah di Batch %s! \n' \
				'Tekan tombol "Fill Product" untuk reload !') % (t_qty,t_qty_t))		
			# cr.execute('select sum (ail.quantity) + (sum (ail.qty)/ail.uos_id.factor) as new_qty  '\
			# 	'from account_invoice ai '\
			# 	'join account_invoice_line ail on ail.invoice_id = ai.id '\
			# 	'join product_uom uom on uom.id = ail.uos_id '\
			# 	'where ai.id in %s ',(fl.inv_ids))
			# n_qty = cr.fatchone()

		gap = val - flo
		gap2 = brt - flo2	

		if val > flo :			
			raise osv.except_osv(_('Jumlah volume barang lebih besar dari kapasitas kendaraan!!'), _('Kapasitas kendaraan %s m3, Jumlah di list %s m3, Kurangi %s m3 lagi!') % (flo,val,gap))

		if brt > flo2 :			
			raise osv.except_osv(_('Jumlah berat barang lebih besar dari kapasitas kendaraan!!'), _('Kapasitas kendaraan %s kg, Jumlah di list %s kg, Kurangi %skg lagi!') % (flo2,brt,gap2))	

		if fl.move_ids == []:
			raise osv.except_osv(_('Tab Batch / Serial Number Kosong!!'), _('Tekan tombol "view product" untuk menampilkan product-produk dari faktur!'))
		if fl.move_ids != []:
			#cek semua product yg dikirim harus mengisi batch number
			for m in fl.move_ids:
				prod = m.name
				ori = m.origin
				batch = m.prodlot_id.id
				if not batch :
					raise osv.except_osv(_('Batch / Serial Number Kosong!!'), _('Kode dan nama barang %s dari nomor faktur %s, Batch / Serial Numbernya belum di isi !') % (prod,ori))	

		self.write(cr,uid,ids[0],{'state':'on_deliver'},context=context)		
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_custom_djislu', 'view_sj_tree')
		view_id = view_ref and view_ref[1] or False,
		return {
			'name' : _('Temporary View'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'surat.jalan',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'domain' : "[('state','=','draft')]",
			#'context': "{'default_state':'open'}",#
			'nodestroy': False,
			}
	

		#view sum product list
	def view_product_list(self,cr,uid,ids,context=None):

		fl = self.browse(cr, uid, ids[0], context=context)
		ls = self.pool.get('list.product')
		#tampilkan semua product yang ada di list invoice
		#tampung semua product di tab invoice
		liss_p = []
		for ln in fl.inv_ids:
			for line in ln.invoice_line :
				prod = line.product_id.id
				liss_p.append(prod)

		#susun dan merge semua product yang sama
		lp = sorted(set(liss_p))
		for prod_p in lp:
			bg = 0.00	
			sm = 0.00	
			#import pdb;pdb.set_trace()			
			for ln2 in fl.inv_ids :
				inv_ori = ln2.origin

				mv = mv_obj.search(cr,uid,[('origin','=',inv_ori)],context=context)
				mv_id = mv_obj.browse(cr,uid,mv[0])

				if mv_id.id :
					mv = mv_id.id
					move_ids.append(mv)
					#done kan stock move agar qty on hand berkurang
					mv_obj.write(cr,uid,mv_id.id,{'state':'done'},context=context)	

				for line2 in ln2.invoice_line:
					prod = line2.product_id.id
					bg_qty = line2.qty
					bg_uom = line2.uos_id.id
					sm_qty = line2.quantity2
					sm_uom = line2.uom_id.id	
			
					if 	prod == prod_p :
						bg += bg_qty
						sm += sm_qty
			 
			ls.create(cr, uid,{ 'product_id':prod_p,
								'big_qty': bg,
								'big_uom' : bg_uom,
								'small_qty' : sm,
								'small_uom' : sm_uom,
								'surat_jalan_id':ids[0]})	
		return True

		#view product di stock move
	def view_product(self,cr,uid,ids,context=None):
		
		mv_obj = self.pool.get('stock.move')
		acc = self.pool.get('account.invoice')
		mvp_obj = self.pool.get('stock.move.pick')

		fl = self.browse(cr, uid, ids[0], context=context)
		ls = self.pool.get('list.product')

		
		move_ids = []
		prod_ids = []
		prodlot_ids = []
		for line2 in fl.inv_ids:
			inv_ori = line2.origin
			mv = mv_obj.search(cr,uid,[('origin','=',inv_ori),('location_dest_id','=',9)],context=context)# dest = customer
			mv_id = mv_obj.browse(cr,uid,mv)
			bg = 0.00	
			sm = 0.00	
			for x in mv_id :
				if x.id :
					mv = x.id
					prod = x.product_id.id
					bg_qty = round(x.product_qty * x.product_uos.factor_inv,3)
					bg_uom = x.product_uos
					sm_qty = x.product_qty
					sm_uom = x.product_uom

					move_ids.append(mv)
					prod_ids.append(prod)

					if x.prodlot_id.id:
						lot = x.prodlot_id.id
						prodlot_ids.append(lot)
		
		if fl.list_product_ids != []:
			for x in fl.list_product_ids:
				acc = self.pool.get('list.product')
				acc.unlink(cr,uid,[x.id],context)				

		mov = tuple(move_ids)
		prod_id = set(prodlot_ids)#merge sn id yg sama

		######### diganti dengan looping karena factor_inv pada product.uom field function tdk bisa di query #########
		# for mv in prod_id :
		# 	cr.execute ('select product_uom, product_uos, product_id, sum(product_qty),uom.factor '\
		# 		'from stock_move sm '\
		# 		'join product_uom uom on sm.product_uos = uom.id '\
		# 		'where id in %s '\
		# 		'and prodlot_id = %s '\
		# 		'Group by product_uom, product_uos, product_id, uom.factor',(mov,mv))
		# 	crf = cr.fetchone()
		# 	cr_mv = list(crf or 0)#karena dlm bentuk tuple di list kan dulu
		# 	uom = cr_mv[0]
		# 	uos = cr_mv[1]
		# 	product = cr_mv[2]
		# 	qty = cr_mv[3]

		mv_search = mv_obj.search(cr,uid,[('id','in',move_ids)],context=context)
		mv_browse = mv_obj.browse(cr,uid,mv_search)
		
		for lot in prod_id :
			qty = 0.00	
			for mo in mv_browse :
				product = mo.product_id.id
				uos = mo.product_uos.id
				uos_fac = mo.product_uos.factor_inv
				uom = mo.product_uom.id
				small_qty = mo.product_qty
				mv = mo.prodlot_id.id
				if lot == mv :
					qty += small_qty

			#import pdb;pdb.set_trace() 
			bs_qty = qty / uos_fac
			#pisahkan bilangan bulat dan pecahanya
			qqty = math.modf(bs_qty)
			#bilangan bulat
			b_qty = qqty[1]
			#bilangan pecahan atau sisanya
			s_qty = qqty[0]

			ls.create(cr, uid,{ 'product_id':product,
								'big_qty': b_qty,
								'big_uom' : uos,
								'small_qty' : s_qty*uos_fac,
								'small_uom' : uom,
								'prodlot_id' :lot,
								'surat_jalan_id':ids[0]})
				
		self.write(cr,uid,ids[0],{'move_ids':[(6, 0, move_ids)]})	

		return True	

	def action_return(self,cr,uid,ids,context=None): 
		fl = self.browse(cr, uid, ids[0], context=context)
		inv = self.pool.get('account.invoice')

		for line in fl.inv_ids:		
			if line.state in ['deliver','ttf']:
				raise osv.except_osv(_('Error!'), _('Ada faktur yang masih berstatus deliver / TTF !'))
			if not line.description:
				raise osv.except_osv(_('Error!'), _('Ada faktur yang belum di isi alasan!'))
			inv.write(cr,uid,line.id,{'button_hidden':False,'state2':'done'},context=context)
		self.write(cr,uid,ids,{'state':SJ_STATES[2][0]},context=context)
		return True

	#default shop sesuai cabang di master employee log in
	def _get_default_werehouse(self, cr, uid, context=None):
		#
		emplo = self.pool.get('hr.employee').search(cr,uid,[('user_id','=',uid)])
		if not emplo:
			raise osv.except_osv(_('Error!'), _('User tidak di link kan ke master pegawai!'))
		emp = self.pool.get('hr.employee').browse(cr,uid,emplo)[0]
		em = emp.location_id.id

		return em


	_columns = {
		'name': fields.char('Code',readonly=True),
		'car_id': fields.many2one('fleet.vehicle','Car',required=True),
		'based_route_id' : fields.many2one('master.based.route','Route',required=True),
		'date':fields.date('Date',required=True,readonly=True),
		'location_id' : fields.many2one('sale.shop','Location',required=True,readonly=True),
		'user_id': fields.many2one('res.users','Creator',readonly=True),
		'inv_ids' : fields.many2many('account.invoice','picking_rel','surat_jalan_id','invoice_id',
			domain="[('type','=','out_invoice'),\
			('state','=','draft'),\
			('based_route_id','=',based_route_id),\
			('location_id','=',location_id)]",
			string='Invoice List'),
		# 'inv_ids' : fields.many2many('account.invoice','picking_rel','surat_jalan_id','invoice_id',
		# 	domain="[('type','in',['out_refund','out_invoice']),\
		# 	('state','=','draft'),\
		# 	('date_invoice','=',date),\
		# 	('based_route_id','=',based_route_id),\
		# 	('location_id','=',location_id),\
		# 	('user_id2','=',user_id)]",
		# 	string='Invoice List'),
		'volume' : fields.float('Capacity (Volume) m3',help="Dalam Satuan m3 (meter kubik)",readonly=True,store=True),
		'weight' : fields.float('Capacity (weight) Kg',help='Dalam Satuan Kg',readonly=True),
		'vol_in_list' : fields.float("Volume Total in List "),
		'driver_id2' : fields.many2one('hr.employee','Driver'),
		'state': fields.selection(SJ_STATES, 'State', readonly=True, help="Status Pengiriman"),
		'list_product_ids' : fields.one2many('list.product','surat_jalan_id','List Product'),
		'move_ids' : fields.many2many('stock.move','move_rel','surat_jalan_id','move_id',string='Batch Number'),
		'move_id' : fields.one2many('stock.move.pick','surat_jalan_id',string='Batch Number'),
		'prodlot_ids' : fields.one2many('prodlot.sj','surat_jalan_id',string='Batch'),
		'note':fields.text('Note'),
		}	

	_defaults ={
		'user_id': lambda obj, cr, uid, context: uid,
		'date' : fields.date.context_today,
		'state': SJ_STATES[0][0],
		'location_id' : _get_default_werehouse
		}	


class list_product(osv.osv):
	_name = "list.product"

	_columns = {
		'surat_jalan_id' : fields.many2one('surat.jalan','SJ'),
		'product_id':fields.many2one('product.product','Product'),
		'big_qty': fields.float('Big Qty'),
		'big_uom' : fields.many2one('product.uom','Big UoM'),
		'small_qty' : fields.float('Small Qty'),
		'small_uom' : fields.many2one('product.uom','Small UoM'),
		'prodlot_id': fields.many2one('stock.production.lot','Batch Number'),
		}				

class account_invoice(osv.osv):		
	_inherit = "account.invoice"

	_columns ={
		'surat_jalan_ids' : fields.many2many('surat.jalan','surat_jalan_rel','surat_jalan_id','invoice_id',string="SJ"),
		'state2' : fields.selection([('draft','Draft'),('deliver','On Delivery'),('done','On Done')],'Status'),
		#'volume_tot': fields.float('Volume Total'),
		}				

class stock_move(osv.osv):
	_inherit ="stock.move"
	_name ="stock.move"

	def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False,
						loc_id=False, product_id=False, uom_id=False, context=None):
		""" On change of production lot gives a warning message.
		@param prodlot_id: Changed production lot id
		@param product_qty: Quantity of product
		@param loc_id: Location id
		@param product_id: Product id
		@return: Warning message
		"""
		if not prodlot_id or not loc_id:
			return {}

			
		ctx = context and context.copy() or {}
		ctx['location_id'] = loc_id
		ctx.update({'raise-exception': True})
		uom_obj = self.pool.get('product.uom')
		product_obj = self.pool.get('product.product')
		product_uom = product_obj.browse(cr, uid, product_id, context=ctx).uom_id
		prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context=ctx)
		location = self.pool.get('stock.location').browse(cr, uid, loc_id, context=ctx)
		uom = uom_obj.browse(cr, uid, uom_id, context=ctx)
		amount_actual = uom_obj._compute_qty_obj(cr, uid, product_uom, prodlot.stock_available, uom, context=ctx)
		warning = {}
		#import pdb;pdb.set_trace()
		if ids != []:
			self.write(cr,uid,ids[0],{'prodlot_id':prodlot_id})
		if (location.usage == 'internal') and (product_qty > (amount_actual or 0.0)):
			warning = {
				'title': _('Insufficient Stock for Serial Number !'),
				'message': _('You are moving %.2f %s but only %.2f %s available for this serial number.') % (product_qty, uom.name, amount_actual, uom.name)
			}
			if ids != []:
				self.write(cr,uid,ids[0],{'prodlot_id':False})
		return {'warning': warning}

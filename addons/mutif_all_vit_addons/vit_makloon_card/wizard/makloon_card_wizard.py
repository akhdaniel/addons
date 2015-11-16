from osv import osv,fields
from openerp.tools.translate import _
import datetime 
import openerp.addons.decimal_precision as dp
import sets

class makloon_card_wizard(osv.TransientModel): 
	_name = 'makloon.card.wizard' 

	_columns = {
		'date_start' : fields.date('Date Start',required=True),
		'date_end'   : fields.date('Date End',required=True),
		'partner_id' : fields.many2one('res.partner',string='Makloon',required=True),
	}

	_defaults = {
		'date_start'  	: lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'		: fields.date.context_today,	
	}


	def create_makloon_card_detail(self, cr, uid, makloon_card_id, date, mk, model_type_id, size, order, finish, hold, qty_balance, price_balance, context):
		self.pool.get('makloon.card.detail').create(cr,uid,{'makloon_card_id'	: makloon_card_id,
															'date_end'			: date,
															'makloon_id'		: mk,	
															'model_type_id'		: model_type_id,
															'size'				: size,
															'total_mkl'			: order,
															'total_finish'		: finish,
															'total_hold' 		: hold,
															'qty_balance'		: qty_balance,
															'price_balance'		: price_balance},
															context=context)

	def hasil(self, cr, uid, desc, report, view_id, domain, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'form',			
			'res_model': 'makloon.card',
			'res_id': report,
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			#'domain' : domain,
			#'context': context,
			'nodestroy': False,
			}


	def fill_table(self, cr, uid, ids, context=None):
		loc_obj = self.pool.get('stock.location')
		wizard  = self.browse(cr, uid, ids[0], context=context) 
		
		sql = "delete from makloon_card where user_id = %s" % (uid)
		
		cr.execute(sql)
		
		makloon_card_id = self.pool.get('makloon.card').create(cr,uid,{'partner_id':wizard.partner_id.id,
																		'date_start': wizard.date_start,
																		'date_end': wizard.date_end,
																		'user_id':uid})

		makloon_obj = self.pool.get('vit.makloon.order')
		#search_makloon = makloon_obj.search(cr,uid,['|',('date_end_completion','>=',wizard.date_start),('date_end_completion','>=',wizard.date_end)])
		
		cr.execute('SELECT id AS id FROM vit_makloon_order WHERE partner_id = %s AND (date_taking >= %s AND date_taking <= %s) order by date_taking ASC',(wizard.partner_id.id,wizard.date_start,wizard.date_end))
		search_makloon = cr.fetchall()
		if not search_makloon :
			raise osv.except_osv(_('Error!'), _('Data not found !'))
		move_obj = self.pool.get('stock.move')
		qty_order_total = 0
		qty_finish_total = 0
		qty_hold_total = 0 
		qty_balance_total = 0
		price_balance_total = 0	
		date_mk = False
		spk_mk = False
		type_product = False
		for mkl in search_makloon :
			mk = mkl[0]
			
			makloon = makloon_obj.browse(cr,uid,mk,context=context)
			makloon_model_name = makloon.type_product_id.model_product
			makloon_model_id = makloon.type_product_id.id
			date = makloon.date_end_completion
			
			s_order = int(makloon.s_order)
			m_order =int(makloon.m_order)
			l_order =int(makloon.l_order)
			xl_order = int(makloon.xl_order)
			xxl_order = int(makloon.xxl_order)
			xxxl_order = int(makloon.xxxl_order)
			#import pdb;pdb.set_trace()
			mv_ids = move_obj.search(cr, uid, [
				('origin','=',makloon.name),('type','in',('in','internal')),('location_dest_id','=',29)], context=context)	
			mv_return_ids = move_obj.search(cr, uid, [
				('origin','=',makloon.name),('type','=','out'),('location_id','=',29),('location_dest_id','=',7)], context=context)				
			move_reject_ids = move_obj.search(cr, uid, [
				('origin','=',makloon.name),('type','in',('in','internal')),('state','=','done'),('location_dest_id','=',30)], context=context)						
			scrap_location = loc_obj.search(cr,uid,[('scrap_location','=',True)])
			scrap = False
			if scrap_location :
				scrap = scrap_location[0]	
			move_ids = set(mv_ids+mv_return_ids+move_reject_ids)
			if move_ids :
				s_price_balance = 0
				m_price_balance = 0
				l_price_balance = 0
				xl_price_balance = 0
				xxl_price_balance = 0
				xxxl_price_balance = 0

				s_finish = 0
				s_hold = 0

				m_finish = 0
				m_hold = 0

				l_finish = 0
				l_hold = 0

				xl_finish = 0
				xl_hold = 0			

				xxl_finish = 0
				xxl_hold = 0

				xxxl_finish = 0
				xxxl_hold = 0
				move_ids_sorted = sorted(move_ids)
				for move in move_ids_sorted :
					move = move_obj.browse(cr,uid,move,context=context)
					product_name = move.product_id.name
					backorder = move.picking_id.backorder_id	
					state = move.state	
					#import pdb;pdb.set_trace()
					# jika finish good
					if state == 'done' and move.location_dest_id.id == 29 :
				 		if move.location_id.id != scrap :
							if product_name == makloon_model_name+' S' or product_name == makloon_model_name+' S - B' or product_name == makloon_model_name+' S - C' or product_name == makloon_model_name+' 2':
								product_qty  = move.product_qty
								s_finish += product_qty 
							if product_name == makloon_model_name+' M' or product_name == makloon_model_name+' M - B' or product_name == makloon_model_name+' M - C' or product_name == makloon_model_name+' 4':
								product_qty  = move.product_qty
								m_finish += product_qty 
							if product_name == makloon_model_name+' L' or product_name == makloon_model_name+' L - B' or product_name == makloon_model_name+' L - C' or product_name == makloon_model_name+' 6':
								product_qty  = move.product_qty
								l_finish += product_qty 
							if product_name == makloon_model_name+' XL' or product_name == makloon_model_name+' XL - B' or product_name == makloon_model_name+' XL - C' or product_name == makloon_model_name+' 8':
								product_qty  = move.product_qty
								xl_finish += product_qty 
							if product_name == makloon_model_name+' XXL' or product_name == makloon_model_name+' XXL - B' or product_name == makloon_model_name+' XXL - C' or product_name == makloon_model_name+' 10':
								product_qty  = move.product_qty
								xxl_finish += product_qty 
							if product_name == makloon_model_name+' XXXL' or product_name == makloon_model_name+' XXXL - B' or product_name == makloon_model_name+' XXXL - C' or product_name == makloon_model_name+' 12':
								product_qty = move.product_qty
								xxxl_finish += product_qty
					# jika retur
					if state == 'done' and move.location_id.id == 29 and move.location_dest_id.id == 7:
				 		if move.location_id.id != scrap :
							if product_name == makloon_model_name+' S' or product_name == makloon_model_name+' S - B' or product_name == makloon_model_name+' S - C' or product_name == makloon_model_name+' 2':
								product_qty  = move.product_qty
								s_finish -= product_qty 
							if product_name == makloon_model_name+' M' or product_name == makloon_model_name+' M - B' or product_name == makloon_model_name+' M - C' or product_name == makloon_model_name+' 4':
								product_qty  = move.product_qty
								m_finish -= product_qty 
							if product_name == makloon_model_name+' L' or product_name == makloon_model_name+' L - B' or product_name == makloon_model_name+' L - C' or product_name == makloon_model_name+' 6':
								product_qty  = move.product_qty
								l_finish -= product_qty 
							if product_name == makloon_model_name+' XL' or product_name == makloon_model_name+' XL - B' or product_name == makloon_model_name+' XL - C' or product_name == makloon_model_name+' 8':
								product_qty  = move.product_qty
								xl_finish -= product_qty 
							if product_name == makloon_model_name+' XXL' or product_name == makloon_model_name+' XXL - B' or product_name == makloon_model_name+' XXL - C' or product_name == makloon_model_name+' 10':
								product_qty  = move.product_qty
								xxl_finish -= product_qty 
							if product_name == makloon_model_name+' XXXL' or product_name == makloon_model_name+' XXXL - B' or product_name == makloon_model_name+' XXXL - C' or product_name == makloon_model_name+' 12':
								product_qty = move.product_qty
								xxxl_finish -= product_qty											

					# jika incoming hold
					elif move.location_dest_id.id == 30:
						if product_name == makloon_model_name+' S' or product_name == makloon_model_name+' S - B' or product_name == makloon_model_name+' S - C' or product_name == makloon_model_name+' 2':
							product_qty  = move.product_qty
							s_hold += product_qty 
						if product_name == makloon_model_name+' M' or product_name == makloon_model_name+' M - B' or product_name == makloon_model_name+' M - C' or product_name == makloon_model_name+' 4':
							product_qty  = move.product_qty
							m_hold += product_qty 
						if product_name == makloon_model_name+' L' or product_name == makloon_model_name+' L - B' or product_name == makloon_model_name+' L - C' or product_name == makloon_model_name+' 6':
							product_qty  = move.product_qty
							l_hold += product_qty 
						if product_name == makloon_model_name+' XL' or product_name == makloon_model_name+' XL - B' or product_name == makloon_model_name+' XL - C' or product_name == makloon_model_name+' 8':
							product_qty  = move.product_qty
							xl_hold += product_qty 
						if product_name == makloon_model_name+' XXL' or product_name == makloon_model_name+' XXL - B' or product_name == makloon_model_name+' XXL - C' or product_name == makloon_model_name+' 10':
							product_qty  = move.product_qty
							xxl_hold += product_qty 
						if product_name == makloon_model_name+' XXXL' or product_name == makloon_model_name+' XXXL - B' or product_name == makloon_model_name+' XXXL - C' or product_name == makloon_model_name+' 12':
							product_qty = move.product_qty
							xxxl_hold += product_qty

				s_qty_balance = 0
				s_price_balance = 0
				if s_order != 0 :

					s_qty_balance 	= s_order-(s_finish+s_hold)
					s_price_balance = (makloon.avg_qty_total_wip_spk_cut+makloon.avg_qty_acc_total) * (s_order-(s_finish+s_hold))						
					self.create_makloon_card_detail(cr, uid, makloon_card_id, date, mk, makloon_model_id, 'S', s_order, s_finish, s_hold, s_qty_balance, s_price_balance, context)
					qty_order_total += s_order
					qty_finish_total += s_finish
					qty_hold_total += s_hold
					qty_balance_total += s_qty_balance
					price_balance_total += s_price_balance
					date = False
					mk = False
					makloon_model_id = False

				m_qty_balance = 0	
				m_price_balance = 0
				if m_order != 0 :		
					m_qty_balance 	= m_order-(m_finish+m_hold)
					m_price_balance = (makloon.avg_qty_total_wip_spk_cut+makloon.avg_qty_acc_total) * (m_order-(m_finish+m_hold))
					self.create_makloon_card_detail(cr, uid, makloon_card_id, date, mk, makloon_model_id, 'M', m_order, m_finish, m_hold, m_qty_balance, m_price_balance, context)
					qty_order_total += m_order
					qty_finish_total += m_finish
					qty_hold_total += m_hold					
					qty_balance_total += m_qty_balance
					price_balance_total += m_price_balance	
					date = False
					mk = False
					makloon_model_id = False

				l_qty_balance = 0 		
				l_price_balance = 0								
				if l_order != 0 :		
					l_qty_balance 	= l_order-(l_finish+l_hold)
					l_price_balance = (makloon.avg_qty_total_wip_spk_cut+makloon.avg_qty_acc_total) * (l_order-(l_finish+l_hold))
					self.create_makloon_card_detail(cr, uid, makloon_card_id, date, mk, makloon_model_id, 'L', l_order, l_finish, l_hold, l_qty_balance, l_price_balance, context)
					qty_order_total += l_order
					qty_finish_total += l_finish
					qty_hold_total += l_hold					
					qty_balance_total += l_qty_balance
					price_balance_total += l_price_balance	
					date = False
					mk = False
					makloon_model_id = False	

				xl_qty_balance = 0
				xl_price_balance = 0									
				if xl_order != 0 :		
					xl_qty_balance 	= xl_order-(xl_finish+xl_hold)
					xl_price_balance = (makloon.avg_qty_total_wip_spk_cut+makloon.avg_qty_acc_total) * (xl_order-(xl_finish+xl_hold))
					self.create_makloon_card_detail(cr, uid, makloon_card_id, date, mk, makloon_model_id, 'XL', xl_order, xl_finish, xl_hold, xl_qty_balance, xl_price_balance, context)
					qty_order_total += xl_order
					qty_finish_total += xl_finish
					qty_hold_total += xl_hold					
					qty_balance_total += xl_qty_balance
					price_balance_total += xl_price_balance	
					date = False
					mk = False
					makloon_model_id = False	

				xxl_qty_balance	= 0			
				xxl_price_balance = 0					
				if xxl_order != 0 :		
					xxl_qty_balance 	= xxl_order-(xxl_finish+xxl_hold)
					xxl_price_balance = (makloon.avg_qty_total_wip_spk_cut+makloon.avg_qty_acc_total) * (xxl_order-(xxl_finish+xxl_hold))
					self.create_makloon_card_detail(cr, uid, makloon_card_id, date, mk, makloon_model_id, 'XXL', xxl_order, xxl_finish, xxl_hold, xxl_qty_balance, xxl_price_balance, context)	
					qty_order_total += xxl_order
					qty_finish_total += xxl_finish
					qty_hold_total += xxl_hold					
					qty_balance_total += xxl_qty_balance
					price_balance_total += xxl_price_balance	
					date = False
					mk = False
					makloon_model_id = False	

				xxxl_qty_balance = 0		
				xxxl_price_balance = 0																
				if xxxl_order != 0 :		
					xxxl_qty_balance 	= xxxl_order-(xxxl_finish+xxxl_hold)
					xxxl_price_balance = (makloon.avg_qty_total_wip_spk_cut+makloon.avg_qty_acc_total) * (xxxl_order-(xxxl_finish+xxxl_hold))
					self.create_makloon_card_detail(cr, uid, makloon_card_id, date, mk, makloon_model_id, 'XXXL', xxxl_order, xxxl_finish, xxxl_hold, xxxl_qty_balance, xxxl_price_balance, context)
					qty_order_total += xxxl_order
					qty_finish_total += xxxl_finish
					qty_hold_total += xxxl_hold					
					qty_balance_total += xxxl_qty_balance
					price_balance_total += xxxl_price_balance	
					date = False
					mk = False
					makloon_model_id = False
					
				self.pool.get('makloon.card.detail').create(cr,uid,{'makloon_card_id'	: makloon_card_id,
															'size'				: 'SUB TOTAL',
															'total_mkl'			: s_order+m_order+l_order+xl_order+xxl_order+xxxl_order,
															'total_finish'		: s_finish+m_finish+l_finish+xl_finish+xxl_finish+xxxl_finish,
															'total_hold' 		: s_hold+m_hold+l_hold+xl_hold+xxl_hold+xxxl_hold,
															'qty_balance'		: s_qty_balance+m_qty_balance+l_qty_balance+xl_qty_balance+xxl_qty_balance+xxxl_qty_balance,
															'price_balance'		: s_price_balance+m_price_balance+l_price_balance+xl_price_balance+xxl_price_balance+xxxl_price_balance},
															context=context)
				self.pool.get('makloon.card.detail').create(cr,uid,{'makloon_card_id'	: makloon_card_id,
															'size'				: '---',
															'total_mkl'			: False,
															'total_finish'		: False,
															'total_hold' 		: False,
															'qty_balance'		: False,
															'price_balance'		: False,},														
															context=context)				
		self.pool.get('makloon.card').write(cr,uid,makloon_card_id,{'total_order'	:qty_order_total,
																	'total_finish'	:qty_finish_total,
																	'total_hold'	:qty_hold_total,
																	'total_qty'		:qty_balance_total,
																	'total_balance'	:price_balance_total})
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_makloon_card', 'vit_makloon_card_form')
		view_id = view_ref and view_ref[1] or False,	
		
		desc 	= 'Makloon Card'
		domain 	= []
		context = {}

		return self.hasil(cr, uid, desc, makloon_card_id, view_id, domain, context)	
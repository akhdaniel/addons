from openerp.osv import fields,osv
from openerp.tools.translate import _

class res_partner(osv.osv):

	_inherit = "res.partner"
	_name = "res.partner"


	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		args = args[:]
		ids = []

		if name:
			ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
			# if not ids:
			#     ids = self.search(cr, user, [('shortcut', '=', name)]+ args, limit=limit)
			if not ids:
				ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
				if not ids:
					ids = self.search(cr, user, [('street', operator, name)]+ args, limit=limit)
								
			if not ids and len(name.split()) >= 2:
				#Separating code and name of account for searching
				operand1,operand2 = name.split(' ',1) #name can contain spaces e.g. OpenERP S.A.
				ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
		else:
			ids = self.search(cr, user, args, context=context, limit=limit)
		return self.name_get(cr, user, ids, context=context)

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['code']:
				name = '['+record['code'] +']'+ ' ' + name
			res.append((record['id'], name))
		return res


	_columns  = {
		'code' : fields.char('Code', size=64, required=True),
		#'type_customer_id' : fields.many2one('master.type.customer','Type Customer'),
		'limit_ids' : fields.one2many('limit.customer','partner_id2','Limit', ondelete='cascade'),
		'cust_term_id' : fields.many2one('master.term','Customer Term', ondelete='cascade'),
		'supp_term_id' : fields.many2one('master.term','Supplier Term', ondelete='cascade'),
		#'area_id' : fields.many2one('master.area','Area'),
		'address_2' : fields.text('Address 2'),
		'street_2' : fields.char('Street'),
		'zip_2' : fields.char('ZIP',size=12),
		'address_3' : fields.text('Address 3'),
		'street_3' : fields.char('Street'),
		'zip_3' : fields.char('ZIP',size=12),
		'tax_id' : fields.many2one('hr.employee.npwp','NPWP', ondelete='cascade'),
		'name_tax' : fields.related('tax_id','name',string='Nama', type='char', readonly=True),
		'address_tax' : fields.related('tax_id','address',string="Address", type="char", readonly=True),
		'date_tax' : fields.related('tax_id','date',string='Date Registered', type="date", readonly=True ),
		'reg_date' : fields.date('Date Registered'),
		'trouble' : fields.boolean('Trouble'),
		'pareto' : fields.boolean('Pareto'),
		'warehouse_id' : fields.many2one('stock.warehouse','Cabang', ondelete='cascade'),
		'location_id' : fields.many2one('sale.shop','Location', ondelete='cascade'),
		'type_partner_id' : fields.many2one('master.type.partner','Group Price',change_default=True,required=True, ondelete='cascade'),

		'latitude' : fields.float('Latitude'),
		'longitude' : fields.float('Longitude'),

		'one_bill_sys' : fields.boolean('One Bill System'),

		'based_route_id' : fields.many2one('master.based.route','Route'),
		
		}

	_sql_constraints = [
	   ('default_code_uniq', 'unique (default_code)', 'Kode Partner sudah ada!')
	]

class limit_customer(osv.osv):
	_name = "limit.customer"

	def _get_limit_per_supplier(self, cr, uid, ids, field_names, arg, context=None):
		
		llc_p = self.browse(cr,uid,ids)
		lc = []
		for cc in llc_p:
			lc.append(cc.partner_id.id)

		lcc = tuple(lc)
		#import pdb;pdb.set_trace()
		results = {}
		for x in self.browse(cr,uid,ids,context=context):
			cr.execute("""SELECT SUM(residual)
							FROM account_invoice
							WHERE partner_id =%s
							AND partner_id2=""" + str(x.partner_id.id) + """
						  """,
					   ((x.partner_id2.id),))

			tot = cr.fetchall()
			
			if tot == [] :
				results[x.id] = 0.0
			#res = {}
			else:
				tota = list(tot or 0)#karena dlm bentuk tuple di list kan dulu
				total = tota[0]			
				results[x.id] = total[0]

			self.write(cr,uid,x.id,{'payable_field':total[0]},context=context)

		return results		

	_columns ={
		'partner_id2' : fields.many2one('res.partner','Customer',domain=[('supplier','=',True)],required=True, ondelete='cascade'),    
		'partner_id' : fields.many2one('res.partner','Supplier',domain=[('supplier','=',True)],required=True, ondelete='cascade'),    
		'limit' : fields.float('Limit',required=True),
		'payable' : fields.function(_get_limit_per_supplier,type="float",string='Receivable',required=True),
		#'payable' : fields.float('Hutang',readonly=True),
		'type_partner_id' : fields.many2one('master.type.partner','Group Price', ondelete='cascade'),
		'type_cust' : fields.selection([('gt','GT'),('mt','MT')],'Type'),
		'type_id' : fields.many2one('master.type.cust.supp','Type',required=True, ondelete='cascade'),
		'employee_id' : fields.many2one('hr.employee','Salesman',required=True, ondelete='cascade'),
		'name' : fields.related('partner_id','name',type='char',string='Name'),
		'payable_field':fields.float('AR'),
		
		}			

class master_term(osv.osv):
	_name = "master.term"

	_columns = {
		'code' : fields.char('Code', size=64, required=True),
		'name' : fields.char('Name', size=128, required=True),

	}


class master_tax(osv.osv):
	_name= "master.tax"
	_rec_name = "npwp"

	_columns = {
		'npwp' : fields.char('No', size=64, required=True),
		'name' : fields.char('Name ', size=128, required=True),	
		'Alamat' : fields.text('Address', required=True),
		#'street' : fields.char('street'),
		#'zip' : fields.char('ZIP', size=12),
		}

class master_type_partner(osv.osv):
	_name = "master.type.partner"

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace()
		if 'is_reference' in vals.keys():
			viv = vals['is_reference']
			viva = self.search(cr,uid,[('is_reference','=',True)])

			if viva != [] :
				raise osv.except_osv(_('Error!'), _('Referensi untuk harga jual product sudah dipakai!'))

		return super(master_type_partner, self).create(cr, uid, vals, context=context) 

	_columns = {
		'code' : fields.char('Code',size=64,required=True),
		'name' : fields.char('Name',size=128,required=True),
		'parent_id' : fields.many2one('master.type.partner','Parent', select=True, ondelete='cascade'),
		'is_reference' : fields.boolean('Ref for Sale Price'),
		#'date' : fields.date('Tanggal Berlaku'),
		} 


class master_based_route(osv.osv):
	_name = "master.based.route"

	_columns = {
		'code' : fields.char('Code',size=64,required=True),
		'name' : fields.char('Ruote',size=128,required=True),
		}

class master_call_plan(osv.osv): 
	_name = "master.call.plan"
	_rec_name = "day"

	_columns = {
		'user_id' : fields.many2one('res.users','Creator',readonly=True),
		'based_route_id' : fields.many2one('master.based.route','Based Route', required=True, ondelete='cascade'),
		'employee_id' : fields.many2one('hr.employee','Salesman', required=True, ondelete='cascade'),
		'day' : fields.selection([('senin','Senin'),('selasa','Selasa'),('rabu','Rabu'),('kamis','Kamis'),('jumat','Jumat'),('sabtu','Sabtu')],'Day', required=True),
		'partner_ids' : fields.many2many('res.partner',
			'call_plan_rel',
			'pertner_id',
			'call_plan_id',
			domain="[('customer','=',True),\
			('based_route_id','=',based_route_id)]",		
			string='Customer'),
		'is_active': fields.boolean('Active'),
		}
		

	_defaults = {  
		'user_id': lambda obj, cr, uid, context: uid,
		'is_active' : True,
		}

	def onchange_salesman(self, cr, uid, ids, employee_id, based_route_id, partner_ids,context=None):
		#import pdb;pdb.set_trace()
		results = {}
		if not employee_id or not based_route_id:
			return results
		
		cr.execute('SELECT rp.id from limit_customer lc '\
			'LEFT JOIN res_partner rp ON lc.partner_id2 = rp.id '\
			'LEFT JOIN hr_employee he ON he.id = lc.employee_id '\
			'WHERE rp.based_route_id ='+ str(based_route_id)+' '\
			'AND lc.employee_id = '+ str(employee_id))

		p_id = []
		for cs in cr.dictfetchall():
			p_id.append(cs['id'])
		part_obj = self.pool.get('res.partner')
		part_ids = part_obj.search(cr, uid, [('id','in',p_id)], context=context)

		#insert many2many records
		partner_ids = [(6,0,part_ids)]
		results = {
			'value' : {
				'partner_ids' : partner_ids
			}
		}
		return results

class res_partner_route(osv.osv):
	_name = "res.partner.route"

	_columns={
		'master_call_plan_id' : fields.many2one('master.call.plan','Plan', ondelete='cascade'),
		'partner_id' : fields.many2one('res.partner',domain=[('customer','=',1)],required=True,string='Customer', ondelete='cascade'),
		'no' : fields.char('No.')
	}        

class master_target_salesman(osv.osv):
	_name = "master.target.salesman"

	def create(self, cr, uid, vals, context=None):
		if vals.get('name','/')=='/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'master_target_salesman') or '/'
		return super(master_target_salesman, self).create(cr, uid, vals, context=context)

	_columns = {
		'name' : fields.char('No',size=32, readonly=True),
		'user_id' : fields.many2one('res.users','Creator',readonly=True),
		'date_from' : fields.date('Start Date',required=True),
		'date_to' : fields.date('End Date',required=True),
		'target_ids' : fields.one2many('master.target.salesman.detail','master_target_salesman_id','Target'),
	}
	_defaults = {
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.target.salesman'),    
		'user_id': lambda obj, cr, uid, context: uid,
		}

class master_target_salesman_detail(osv.osv):
	_name = "master.target.salesman.detail"

	_columns = {
		'employee_id' : fields.many2one('hr.employee','Salesman', ondelete='cascade', required=True),
		'partner_id' : fields.many2one('res.partner','Supplier',domain=[('supplier','=',1)], required=True),
		'master_target_salesman_id' : fields.many2one('master.target.salesman','Target'),
		'sales' : fields.float('Sales'),
		'ao' : fields.float('AO'),
		'el' : fields.float('EL'),
	}         
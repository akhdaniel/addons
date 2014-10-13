from openerp.osv import fields,osv

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
		'code' : fields.char('Kode', size=64, required=True),
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
		'location_id' : fields.many2one('stock.location','Location', ondelete='cascade'),
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

	_columns ={
		'partner_id2' : fields.many2one('res.partner','Customer',domain=[('supplier','=',True)],required=True, ondelete='cascade'),    
		'partner_id' : fields.many2one('res.partner','Supplier',domain=[('supplier','=',True)],required=True, ondelete='cascade'),    
		'limit' : fields.float('Limit',required=True),
		'payable' : fields.float('Hutang',readonly=True),
		'type_partner_id' : fields.many2one('master.type.partner','Group Price', ondelete='cascade'),
		'type_cust' : fields.selection([('gt','GT'),('mt','MT')],'Type'),
		'type_id' : fields.many2one('master.type.cust.supp','Type',required=True, ondelete='cascade'),
		'employee_id' : fields.many2one('hr.employee','Salesman',required=True, ondelete='cascade'),
		'name' : fields.related('partner_id','name',type='char',string='Name'),
		


		}			

# class master_type_customer(osv.osv):

# 	_name = "master.type.customer"
# 	_rec_name = "code"

# 	_columns = {
# 		'code' : fields.char('Code', size=64, required=True),
# 		'name' : fields.char('Name', size=128, required=True),
# 		'is_active' : fields.boolean('is_active'),
# 		'with_so' : fields.boolean('With SO'),

# 		}

# class mastera_group_customer(osv.osv):

# 	_name =	"master.group.customer"
# 	_rec_name = "code"

# 	_columns = {
# 		'code' : fields.char('Code', size=64, required=True),
# 		'name' : fields.char('Name', size=128, required=True),
# 		'cabang_id' : fields.char('slu.cabang','Branch'),

# 		}	

# class master_cabang(osv.osv):

# 	_name = "master.cabang"
# 	_rec_name = "code"

# 	_columns = {
# 		'code' : fields.char('Code', size=64, required=True),
# 		'name' : fields.char('Name', size=128, required=True),
#         'address' : fields.char('Alamat'),
#         'city': fields.char('Kota'),	
#         'tax_id' : fields.many2one('hr.employee.npwp','NPWP'),		

# 		}

class master_term(osv.osv):
	_name = "master.term"

	_columns = {
		'code' : fields.char('Code', size=64, required=True),
		'name' : fields.char('Name', size=128, required=True),

	}

# class master_area(osv.osv):
# 	_name = "master.area"	

# 	_columns = {
# 		'code' : fields.char('Code', size=64, required=True),
# 		'name' : fields.char('Name', size=128, required=True),	
# 		'cabang_id' : fields.many2one('master.cabang','Branch'),
# 		}

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

	_columns = {
		'code' : fields.char('code',size=64,required=True),
		'name' : fields.char('Name',size=128),
		'parent_id' : fields.many2one('master.type.partner','Parent', select=True, ondelete='cascade'),
		#'date' : fields.date('Tanggal Berlaku'),
		} 


class master_based_route(osv.osv):
	_name = "master.based.route"

	_columns = {
		'code' : fields.char('code',size=64,required=True),
		'name' : fields.char('Ruote',size=128,required=True),
		}

class master_call_plan(osv.osv): 
	_name = "master.call.plan"

	_columns = {
		'based_route_id' : fields.many2one('master.based.route','Based Route', required=True, ondelete='cascade'),
		'employee_id' : fields.many2one('hr.employee','Salesman', required=True, ondelete='cascade'),
		'day' : fields.selection([('senin','Senin'),('selasa','Selasa'),('rabu','Rabu'),('kamis','Kamis'),('jumat','Jumat'),('sabtu','Sabtu')],'Day', required=True),
		'partner_ids' : fields.one2many('res.partner.route','master_call_plan_id','Customer'),

		}

class res_partner_route(osv.osv):
	_name = "res.partner.route"

	_columns={
		'master_call_plan_id' : fields.many2one('master.call.plan','Plan', ondelete='cascade'),
		'partner_id' : fields.many2one('res.partner',domain=[('customer','=',1)],required=True,string='Customer', ondelete='cascade'),
		'no' : fields.char('No.')
	}        

class master_target_salesman(osv.osv):
		_name = "master.target.salesman"
		_res_name = "no"

		_columns = {
			'no' : fields.char('No',size=32, required=True),
			'date_from' : fields.date('Start Date',required=True),
			'date_to' : fields.date('End Date',required=True),
			'target_ids' : fields.one2many('master.target.salesman.detail','master_target_salesman_id','Target'),
		}

class master_target_salesman_detail(osv.osv):
	_name = "master.target.salesman.detail"

	_columns = {
		'employee_id' : fields.many2one('hr.employee','Salesman', ondelete='cascade'),
		'partner_id' : fields.many2one('res.partner','Supplier',domain=[('supplier','=',1)]),
		'master_target_salesman_id' : fields.many2one('master.target.salesman','Target'),
		'sales' : fields.float('Sales'),
		'ao' : fields.float('AO'),
		'el' : fields.float('EL'),
	}         
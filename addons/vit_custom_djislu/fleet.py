from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

#state surat jalan
SJ_STATES =[
	('draft','Draft'),
	('on_deliver','On Delivery'),
	('return','Return'),]

class fleet_vehicle(osv.osv):
	_inherit = "fleet.vehicle"

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

	def onchange_volume(self,cr,uid,ids,car_id,context=None):
		result={}
		#import pdb;pdb.set_trace()
		fle = self.pool.get('fleet.vehicle')
		flee = fle.search(cr,uid,[('id','=',car_id)])
		fleet = fle.browse(cr,uid,flee)[0].volume
		fleet2 = fle.browse(cr,uid,flee)[0].tonase
		sup = fle.browse(cr,uid,flee)[0].driver_id2.id

		val = {'volume':fleet,'weight':fleet2,'driver_id2':sup}
		return {'value':val}

	def action_draft(self,cr,uid,ids,context=None): 
		return self.write(cr,uid,ids,{'state':SJ_STATES[0][0]},context=context)
		
	def action_on_deliver(self,cr,uid,ids,context=None):
		#import pdb;pdb.set_trace() 
		fl = self.browse(cr, uid, ids[0], context=context)
		flo =fl.volume
		val =  0.0
		for line in fl.inv_ids:
			val += line.volume
		tval = val	
		gap = val-flo
		if tval > flo :			
			raise osv.except_osv(_('Jumlah volume barang lebih besar dari kapasitas kendaraan!!'), _('Kapasitas kendaraan %s m3, Jumlah di list %s m3, Kurangi %s m3 lagi!') % (flo,tval,gap))
		else :
			#import pdb;pdb.set_trace()
			self.write(cr,uid,ids,{'state':SJ_STATES[1][0],'vol_in_list':tval},context=context)
			for line2 in fl.inv_ids:
				acc = self.pool.get('account.invoice')
				ass = acc.write(cr,uid,[line2.id],{'state':'deliver'},context=context)

		return  True	

	def action_return(self,cr,uid,ids,context=None): 
		return self.write(cr,uid,ids,{'state':SJ_STATES[2][0]},context=context)
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
		'date':fields.date('Date',required=True),
		'location_id' : fields.many2one('stock.location','Location',required=True,readonly=True),

		'inv_ids' : fields.many2many('account.invoice','picking_rel','surat_jalan_id','invoice_id',domain=[('type','in',['out_refund','out_invoice'])],string='Invoice List'),
		'volume' : fields.float('Capacity (Volume) m3',help="Dalam Satuan m3 (meter kubik)",readonly=True),
		'weight' : fields.float('Capacity (weight) Kg',help='Dalam Satuan Kg',readonly=True),
		'vol_in_list' : fields.float("Volume Total in List "),

		'driver_id2' : fields.many2one('hr.employee','Driver'),

		'state': fields.selection(SJ_STATES, 'State', readonly=True, help="Status Pengiriman"),
		}	

	_defaults ={
		'date' : fields.date.context_today,
		'state': SJ_STATES[0][0],
		'location_id' : _get_default_werehouse
		}			

class account_invoice(osv.osv):		
	_inherit = "account.invoice"

	_columns ={
		'surat_jalan_ids' : fields.many2many('surat.jalan','surat_jalan_rel','invoice_id','surat_jalan_id',string="SJ"),
		'state2' : fields.selection([('delivered','Delivered'),('cn','CN Confirmation')],'Status'),
		#'volume_tot': fields.float('Volume Total'),
		}
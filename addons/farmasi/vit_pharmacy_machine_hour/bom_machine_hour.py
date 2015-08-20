import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re



""" BOM Machine Hour """
class bom_machine_hour(osv.osv):
    _name = 'vit_pharmacy_machine_hour.bom_machine_hour'
    _description = 'Bom Man Hour'

    _columns = {
        'bom_id'	   				: fields.many2one('mrp.bom','BOM'),
        'machine_hour'	 			: fields.float('Machine Hour',digits=(16, 2)),  
        'machine_id'				: fields.many2one('vit_pharmacy_machine_hour.machine_master','Machine'), 
        'is_parallel'               : fields.boolean('Parallel'),
        'routing_id'  			    : fields.related('bom_id','routing_id', type='many2one', relation='mrp.routing', string='Routing', store=True, readonly=True),
        'workcenter_operation_id'   : fields.many2one('mrp.routing.workcenter',"Workcenter Operation",domain="[('routing_id','=',routing_id)]",required=False, change_default=True, track_visibility='always',),
        'workcenter_id'             : fields.many2one('mrp.workcenter',"Workcenter")
    }


    def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['bom_id'], context=context)

		res = []
		for record in reads:
			name = record['bom_id'][1]
			if record['bom_id'][1]:
				name = record['bom_id'][1]
			res.append((record['id'], name))
		return res

    def onchange_bom_id(self, cr, uid, ids, bom_id, context=None):
        res = {}
        if bom_id:
            bom = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context=context)
            res['value'] = {
                'routing_id' : bom.routing_id.id,
            }
        return res

class mrp_bom(osv.osv):
    _name = 'mrp.bom'
    _description = 'Bill of Material'
    _inherit = 'mrp.bom'

    _columns = {
    	'machine_hour_lines': fields.one2many('vit_pharmacy_machine_hour.bom_machine_hour', 'bom_id', 'Machine Hour'),
        'lead_time_product' : fields.float('Lead Time Product')
    }
   
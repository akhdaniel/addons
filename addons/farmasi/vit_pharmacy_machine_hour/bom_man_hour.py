import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re



""" BOM Man Hour """
class bom_man_hour(osv.osv):
    _name = 'vit_pharmacy_machine_hour.bom_man_hour'
    _description = 'Bom Man Hour'

    _columns = {
        'bom_id'	   				: fields.many2one('mrp.bom','BOM'),
        'man_hour'	 				: fields.float('Man Hour',digits=(16, 2)),  
        'man_number'				: fields.integer('Man Number'), 
        'routing_id'  			    : fields.related('bom_id','routing_id', type='many2one', relation='mrp.routing', string='Routing', store=True, readonly=True),
        'workcenter_operation_id'   : fields.many2one('mrp.routing.workcenter',"Workcenter Operation",domain="[('routing_id','=',routing_id)]",required=False, change_default=True, track_visibility='always',),
        'lead_time_process'         : fields.float('Lead Time Process',digits=(16, 2)),  
        # 'workcenter_lines'			: fields.one2many('mrp.routing.workcenter', 'bom_man_hour_id', 'Work Centers'),
        # 'workcenter_operation_id'	: fields.many2one('mrp.routing.workcenter','Workcenter Operation'),
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
    	'workcenter_lines': fields.one2many('vit_pharmacy_machine_hour.bom_man_hour', 'bom_id', 'Work Centers'),
    }
   
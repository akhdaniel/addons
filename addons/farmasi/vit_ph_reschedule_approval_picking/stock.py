import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re




class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _description = "Picking List"

    _columns = {
        'req_scheduled': fields.selection([('no', 'No'),
                           ('req', 'Requested'),
                           ('approved', 'Approved'),
                           ('confirmed','Confirmed'),
                           ], 'Req Scheduled', readonly=True, select=True, copy=False,
         ),
    }

    _defaults = {
    	'req_scheduled': 'no',
    }

    def reschedule(self, cr, uid, ids, context=None):
    	return self.write(cr,uid,ids,{'req_scheduled':'req'})

    def approve_reschedule(self, cr, uid, ids, context=None):
    	return self.write(cr,uid,ids,{'req_scheduled':'approved'})

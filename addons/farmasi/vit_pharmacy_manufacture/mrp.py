import time
from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID

class mrp_production(osv.osv):
	_name = 'mrp.production'
	_description = 'Manufacturing Order'
	_inherit = 'mrp.production'

	_columns = {
		'wps_id':fields.many2one('vit_pharmacy_manufacture.wps','WPS',
            readonly=False,
            states={'done':[('readonly',True)], 
                'cancel':[('readonly',True)],
                'in_production':[('readonly',True)]},
			),
        'batch_numbering_start' : fields.selection([('kecil','K'),('besar','B')],'B/K',
            readonly=False,
            states={'done':[('readonly',True)], 
                'cancel':[('readonly',True)],
                'in_production':[('readonly',True)]},
        	),
	}


	_defaults = {
		'date_planned': lambda *a: time.strftime("%Y-%m-%d 00:00:00")
	}

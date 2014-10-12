from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class partner(osv.osv):
    _name = 'res.partner'
    _description = 'Partner'
    _inherit = "res.partner"

    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
     
      try:
        category_id[0][2][0]
      except Exception, e:
        print e
      else:
        if category_id[0][2][0]:
          categ = self.pool.get('res.partner.category').browse(cr, uid, category_id[0][2][0])
          vit_master_disc_id = self.pool.get('vit_master_disc').search(cr,uid,[('name','=',str(categ.name))],context =context)

          if vit_master_disc_id:
            master = self.pool.get('vit_master_disc').browse(cr, uid, vit_master_disc_id[0], context=context)
            return {'value':{'discount':master.value}}
          else:
            return {'value':{'discount':0.00}} 
      return {'value':{'discount':0.00}}  

partner()
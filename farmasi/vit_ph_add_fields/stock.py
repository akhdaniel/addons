from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging




class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    _columns = {

        'note_release': fields.char('Note Release'),
        
    }

    def split(self, cr, uid, move, qty, restrict_lot_id=False, restrict_partner_id=False, context=None):
        res = super(stock_move, self).split(cr, uid, move, qty, restrict_lot_id=False, restrict_partner_id=False, context={})
       
        return res


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _columns = {
       
        'uji_mikro': fields.selection([('with_uji_mikro','Dengan Uji Mikro'),('without_uji_mikro','Tanpa Uji Mikro')],'Uji Mikro'),
        'release_date': fields.datetime('Release Date'),
        'priority': fields.selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority', select=True),

    }

    _defaults = {
        'priority': '0',   
    }

class stock_pack_operation(osv.osv):
    _name = "stock.pack.operation"
    _inherit = "stock.pack.operation"
    _description = "Packing Operation"

    _columns = {

        'note_release': fields.char('Note Release'),
    }

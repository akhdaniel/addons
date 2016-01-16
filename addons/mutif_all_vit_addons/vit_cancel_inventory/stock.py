from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _name = "stock.inventory"

    def action_cancel_inventory(self, cr, uid, ids, context=None):
            """ Cancels both stock move and inventory
            @return: True
            """
            
            move_obj = self.pool.get('stock.move')
            account_move_obj = self.pool.get('account.move')
            for inv in self.browse(cr, uid, ids, context=context):
                move_obj.action_cancel(cr, uid, [x.id for x in inv.move_ids], context=context)
                for move in inv.move_ids:
                     # import pdb;pdb.set_trace()
                     account_move_ids = account_move_obj.search(cr, uid, [('name', '=', move.name)])
                     account_move_ids2 = account_move_obj.search(cr, uid, [('ref', '=', move.name)])
                     account_move_obj.unlink(cr, uid, account_move_ids2, context=context)

                     if account_move_ids:
                         account_move_data_l = account_move_obj.read(cr, uid, account_move_ids, ['state'], context=context)
                         for account_move in account_move_data_l:
                             if account_move['state'] == 'posted':
                                 raise osv.except_osv(_('User Error!'),
                                                      _('In order to cancel this inventory, you must first unpost related journal entries.'))
                             account_move_obj.unlink(cr, uid, [account_move['id']], context=context)

                self.write(cr, uid, [inv.id], {'state': 'cancel'}, context=context)
            return True

stock_inventory()
   
  
from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)

class master_reward(osv.osv):
    _name 		= "vit_sale_reward.master_reward"
    _columns 	= {
        'name'       : fields.char('Name', required=True),
        'date_from'  : fields.date('Start Date'),
        'date_to'    : fields.date('End Date'),
        'is_active'  : fields.boolean('Active?'),
        'so_total'   : fields.float('Total Sale Order', required=True),
        'point'      : fields.float('Reward Point', required=True),
        'amount'     : fields.float('Amount', required=True),
        'multiple'   : fields.boolean('Multiple Apply'),   
        'journal_id' : fields.many2one('account.journal', 'Journal', required=True),     
        'credit_account_id'    : fields.many2one('account.account', 'Credit Account', 
            required=True,
            domain="[('type','!=','view')]" ),
        'debit_account_id'     : fields.many2one('account.account', 'Debit Account', 
            required=True,
            domain="[('type','!=','view')]"),
    }

    _defaults = {
        'is_active'     : True,
        'date_from'  : lambda *a : time.strftime("%Y-%m-%d") ,
        'date_to'    : lambda *a : time.strftime("%Y-%m-%d") ,
    }  

class partner_reward(osv.osv):
    _name       = "vit_sale_reward.partner_reward"
    _columns    = {
        'partner_id'        : fields.many2one('res.partner', 'Partner'),
        'point'             : fields.float('Point'),
        'type'              : fields.selection(
            [('in','Addition'),
            ('out','Deduction')],'Transaction Type',required=True),
        'date'              : fields.date('Transaction Date'),
        'source'            : fields.char('Source Document')
    }

    def point_trx(self, cr, uid, partner_id, point, type, source, context=None):
        data = {
            'partner_id' : partner_id, 
            'point'      : point,
            'type'       : type,
            'date'       : time.strftime("%Y-%m-%d"),
            'source'     : source,
        }
        res = self.create(cr, uid, data, context=context)
        return res



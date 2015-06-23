# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _name = 'purchase.order.line'

    _columns = {
        'description': fields.related('product_id','description',type='text',string='Description',readonly=True),
    }
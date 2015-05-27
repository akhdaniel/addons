# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class stock_picking(models.Model):
    _inherit='product.template'
    
    
    @api.onchange('sale_ok')
    def _onchange_product_category_cubic(self):
        if self.sale_ok==True:
            self.product_category='cubic'
        
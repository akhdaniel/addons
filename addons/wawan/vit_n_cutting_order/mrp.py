# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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

class mrp_bom(osv.osv):
    """
    Defines bills of material for a product.
    """
    _name = 'mrp.bom'
    _description = 'Bill of Material'
    _inherit = 'mrp.bom'

    
    _columns = {
        'size' : fields.selection([('S','S/2'),('M','M/4'),('L','L/6'),('XL','XL/8'),('XXL','XXL/10'),('XXXL','XXXL/12')],'Size',required=True),
        'master_model_id': fields.many2one('vit.master.type', string = "Type Model",required=True),
        'component_type': fields.selection([('main','Body'),('variation','Variation'),('accessories','Accessories')], 'Component Type', required=True,
                                 help= ""),
    }
    _defaults = {
        'component_type': lambda *a: 'main',
    }

    # def onchange_master_id(self, cr, uid, ids, master_id, context=None):
    #     import pdb;pdb.set_trace()
    #     if master_id:
    #         mast = self.pool.get('vit.master.type').browse(cr, uid, master_id, context=context)
    #         return {'value': {'name': mast.name}}
    #     return {}
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

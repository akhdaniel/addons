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
        'yield' : fields.float('Standard Yield'),
    }

class mrp_bom_line(osv.osv):
    """
    Defines bills of material for a product.
    """
    _name = 'mrp.bom.line'
    _inherit = 'mrp.bom.line'

    _columns = {
        'component_type': fields.selection(
            [('raw_material','Raw Material'),
            ('kemas_primer','Kemas Primer'),
            ('kemas_sekunder','Kemas Sekunder')], 'Component Type', required=True, help= ""),
    }
    _defaults = {
        'component_type': lambda *a: 'raw_material',
    }

   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

import math
import re
import time
#from _common import ceiling

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare


class product_category(osv.osv):
    _inherit = "product.category"

    _columns = {
        'best_before_days'	: fields.integer('Best Before Months'),
        'end_of_life_days'	: fields.integer('End of Life Months'),
        'removal_days'		: fields.integer('Removal Months'),
        'alert_days' 		: fields.integer('Retest Months'),
        'mrp_location_id'   : fields.many2one('stock.location', 'MRP Source Location'),
        'wo_start_no_stock' : fields.boolean('WO can start with No Stock', help="The Work Order can start even though this product is not yet in stock")
    }
product_category()


class product_template(osv.osv):
    _inherit = "product.template"    

    _columns = {
        'best_before_days'	: fields.integer('Best Before Months'),
        'end_of_life_days'	: fields.integer('End of Life Months'),
        'removal_days'		: fields.integer('Removal Months'),
        'alert_days' 		: fields.integer('Retest Months'),
    }
product_template()        
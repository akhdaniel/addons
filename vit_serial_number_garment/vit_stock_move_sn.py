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


class stock_move(osv.osv):
    _inherit = "stock.move"	

    _columns = {
    	'stock_move_serial_number_ids' 	: fields.one2many('stock.move.serial.number','stock_move_id',string='Serial Number'),
    	'is_serial_number'		   		: fields.boolean('Has Entered SN'),
    }

    _defaults = {
    	'is_serial_number' : False,
    }
stock_move()

class stock_move_serial_number(osv.osv):
	_name = 'stock.move.serial.number'

	_columns = {
		'stock_move_id' 	: fields.many2one('stock.move',string='Stock Move'),
		'type'				: fields.related('stock_move_id','type',type='char',string='Type',store=True),
		'serial_number_id' 	: fields.many2one('stock.production.lot',string='Serial Number'),
		'picking_id' 		: fields.many2one('stock.picking',string='Picking'),
		'date_picking'		: fields.related('picking_id','date',type='datetime',string='Picking Date',store=True),
		'product_id'		: fields.related('stock_move_id','product_id',relation='product.product',type='many2one',string='Product',store=True),
		'qty'				: fields.float('Qty'),
		'sale_order_id'		: fields.many2one('sale.order',string='Sales Order'),
		'date_sale'			: fields.related('sale_order_id','date_order',type='date',string='SO Date',store=True),
		'invoice_id'		: fields.many2one('account.invoice',string='Invoice'),
		'date_invoice'		: fields.related('invoice_id','date_invoice',type='date',string='Invoice Date',store=True),
		'unit_price'		: fields.related('invoice_id','net_total',type='float',string='Invoice Price',store=True),
	}    

	_defaults = {
		'qty'	: 1,
	}

stock_move_serial_number()	
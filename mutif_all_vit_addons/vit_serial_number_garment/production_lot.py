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



class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'prefix', 'ref'], context)
        res = []
        for record in reads:
            name = record['name']
            prefix = record['prefix']
            if prefix:
                name = prefix + '/' + name
            if record['ref']:
            	name = '%s' % (name)
                #name = '%s [%s]' % (name, record['ref'])
            res.append((record['id'], name))
        return res

    def _get_history_sn(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        #import pdb;pdb.set_trace()
        history_obj = self.pool.get('stock.move.serial.number')
        for obj in self.browse(cr,uid,ids,context=context):
			product_id 	= obj.product_id.id
			sn_id 		= obj.id
			history_ids = history_obj.search(cr,uid,[('serial_number_id','=',sn_id),('product_id','=',product_id),('type','=','in')],context=context)			
			if history_ids :
				result[obj.id] = history_ids
			return result

    def _get_history_sn2(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        #import pdb;pdb.set_trace()
        history_obj = self.pool.get('stock.move.serial.number')
        for obj in self.browse(cr,uid,ids,context=context):
            product_id  = obj.product_id.id
            sn_id       = obj.id
            history_ids = history_obj.search(cr,uid,[('serial_number_id','=',sn_id),('product_id','=',product_id),('type','=','out')],context=context)           
            if history_ids :
                result[obj.id] = history_ids
            return result

    _columns = {
        'product_id'    	: fields.many2one('product.product', 'Product', required=False, domain=[('type', '<>', 'service')]),
        'spk_cutting_id'   	: fields.many2one('vit.cutting.order',string='SPK Cutting'),
        'spk_makloon_id'   	: fields.many2one('vit.makloon.order',string='SPK Makloon'),
        'makloon'       	: fields.related('spk_makloon_id','partner_id',type='many2one',relation='res.partner',string='Makloon',store=True),  
        'tanggal'       	: fields.date('Tanggal Penyerahan'),
        'history_sn_ids'	: fields.function(_get_history_sn,type='many2many',relation='stock.move.serial.number',string='History'),#in
        'history2_sn_ids'   : fields.function(_get_history_sn2,type='many2many',relation='stock.move.serial.number',string='History'),#out
        'is_used'			: fields.boolean('Is Used'),
        'date_sn_input'     : fields.date('Tanggal DO',readonly=True),
        'date_sn_input_in'  : fields.date('Tanggal Incoming',readonly=True),
    }

    _sql_constraints = [('name_uniq', 'unique(name)','Serial Number tidak boleh sama !')]
    
    _defaults = {
    	'is_used' 	: False,
    }

    
stock_production_lot()
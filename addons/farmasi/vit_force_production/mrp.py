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
import datetime
import openerp.addons.decimal_precision as dp
from collections import OrderedDict
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import float_compare, float_is_zero
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

# from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class mrp_production(osv.osv):
	_inherit = 'mrp.production'

	def force_production(self, cr, uid, ids, *args):
		""" Assigns products.
		@param *args: Arguments
		@return: True
		"""
		from openerp import workflow
		move_obj = self.pool.get('stock.move')
		#import pdb;pdb.set_trace()
		for order in self.browse(cr, uid, ids):
			#move_obj.force_assign(cr, uid, [x.id for x in order.move_lines])
			#eksekusi yg product categ == kategory kemas
			move_obj.force_assign(cr, uid, [x.id for x in order.move_lines if x.product_id.categ_id.kategori_kemas == 'sekunder'])
			if self.pool.get('mrp.production').test_ready(cr, uid, [order.id]):
				workflow.trg_validate(uid, 'mrp.production', order.id, 'moves_ready', cr)
		return True

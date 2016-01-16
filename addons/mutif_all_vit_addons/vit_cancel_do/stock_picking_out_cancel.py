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


from openerp.osv import fields, osv

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking_out(osv.osv):
	_name = "stock.picking.out"
	_inherit = "stock.picking"
	_table = "stock_picking"
	_description = "Delivery Orders"

	def vit_cancel_do(self,cr,uid,ids,context=None):

		move 	= self.pool.get('stock.move')
		for do in self.browse(cr, uid, ids, context=context):
			for line in do.move_lines:
				move.write(cr,uid,[line.id],{'state':'cancel'},context=context)
			self.write(cr,uid,do.id,{'state':'cancel'},context=context)

		return True

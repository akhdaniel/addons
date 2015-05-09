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

# from datetime import date, datetime
# from dateutil import relativedelta
# import json
# import time

from openerp.osv import fields, osv
from openerp import api

# ----------------------------------------------------
# Move
# ----------------------------------------------------

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        """Assign a picking on the given move_ids, which is a list of move supposed to share the same procurement_group, location_from and location_to
        (and company). Those attributes are also given as parameters.
        """
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', procurement_group),
                ('location_id', '=', location_from),
                ('location_dest_id', '=', location_to),
                ('state', 'in', ['draft', 'confirmed', 'waiting'])], context=context)
        if picks:
            pick = picks[0]
        else:
            move = self.browse(cr, uid, move_ids[0], context=context)
            print(move)
            values = {
                'origin': move.origin,
                'company_id': move.company_id and move.company_id.id or False,
                'move_type': move.group_id and move.group_id.move_type or 'direct',
                'partner_id': move.partner_id.id or False,
                'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
            }
            print(values)
            pick = pick_obj.create(cr, uid, values, context=context)
            # Tulis other_vals di DO/picking
            if "SO" in move.origin :
                grup = move.group_id.id
                so_obj = self.pool.get("sale.order")
                so_ids = so_obj.search(cr,uid,[('procurement_group_id','=',grup)],) 
                if so_ids:
                    so = so_obj.browse(cr,uid,so_ids[0],)
                    other_vals = {
                        "shop_id"   : so.shop_id.id,
                        "party_datetime": so.party_datetime,
                        "delivery_date": so.delivery_date,
                    }
                pick_obj.write(cr, uid, pick, other_vals, context=context)
        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
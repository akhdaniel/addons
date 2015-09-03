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
import openerp.addons.decimal_precision as dp

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"

    def do_produce(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        production_id = context.get('active_id', False)
        assert production_id, "Production Id should be specified in context as a Active ID."
        data = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('mrp.production').action_produce(cr, uid, production_id,data.product_qty, data.mode, data, context=context)
        mrp_obj     = self.pool.get('mrp.production')
        production  = mrp_obj.browse(cr,uid,production_id)
        if production.split:
            cr.commit()
            move_obj    = self.pool.get('stock.move')
            lot_obj     = self.pool.get('stock.production.lot')

            # search batch number utk di duplicate mejadi A dan B
            lot_id = lot_obj.search(cr,uid,[('name','=',production.batch_number)])
            if lot_id :
                lot_duplicate   = lot_obj.copy(cr, uid, lot_id[0], default=None, context=None)
                lot_edit        = lot_obj.write(cr,uid,lot_duplicate,{'name':str(production.batch_number+'B')})
                lot_awal        = lot_obj.write(cr,uid,lot_id[0],{'name':str(production.batch_number+'A')})
        
                qty_split = mrp_obj.browse(cr,uid,production_id).product_qty/2
                move = production.move_created_ids2.id
                move_duplicate = move_obj.copy(cr, uid, move, default=None, context=None)
                move_obj.write(cr,uid,move_duplicate,{'product_uom_qty': qty_split,'restrict_lot_id':lot_duplicate,'state':'done'})
                move_obj.write(cr,uid,move,{'product_uom_qty': qty_split})

        return {}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
# self.pool.get('stock.move').browse(cr,uid,az).state
# self.pool.get('mrp.production').browse(cr,uid,production_id).move_created_ids.id
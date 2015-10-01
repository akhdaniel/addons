from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.osv import fields, osv



class stock_transfer_details(models.TransientModel):
    _name = 'stock.transfer_details'
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'


    @api.one
    def do_detailed_transfer(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                    'note_release':prod.note_release,
                }
                if prod.packop_id:
                    prod.packop_id.write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                    # import pdb;pdb.set_trace()
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
                    # import pdb;pdb.set_trace()
                    # import pdb;pdb.set_trace()

        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        for packop in packops:
            packop.unlink()

        # Execute the transfer of the picking
        # import pdb;pdb.set_trace()

        self.picking_id.do_transfer()

        return True

    # @api.multi
    # def wizard_view(self):
    #     view = self.env.ref('stock.view_stock_enter_transfer_details')

    #     return {
    #         'name': _('Enter transfer details'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'stock.transfer_details',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': self.ids[0],
    #         'context': self.env.context,
    #     }

#----------------------------------------------------------
# stock_transfer_details_items
#----------------------------------------------------------
class stock_transfer_details_items(models.TransientModel):
    _name = 'stock.transfer_details_items'
    _inherit = 'stock.transfer_details_items'
    _description = 'Picking wizard items'

    _columns = {
        'note_release': fields.char('Note Release'),
    }
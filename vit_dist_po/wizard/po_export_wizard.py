from openerp.osv import osv,fields

class po_export_wizard(osv.TransientModel):
    """docstring for  po.export.wizard"""
    _name = 'po.export.wizard'

    _columns = {
        # 'no'  : fields.char("No."),
        'type': fields.selection([('po_rfq','PO/RFQ'),('sch_do','Incoming Shipment Plan')],"Report",required=True),
    }

    _defaults = {
        'type': 'po_rfq',
    }

    def po_xls_export(self,cr,uid,ids,context=None):
        # import pdb;pdb.set_trace()
        datas = {
            'model': 'purchase.order',
            'ids': context.get('active_id',False),
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'vit.po.detail.export.xls',
                'datas': datas}
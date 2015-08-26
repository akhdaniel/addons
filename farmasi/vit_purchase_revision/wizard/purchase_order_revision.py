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
from openerp.tools.translate import _

class purchase_order_revision(osv.osv_memory):
    _name = 'purchase.order.revision'

    _columns = {
        'name'         : fields.text('Reason',required=True),
    }    

    def create_revision_po(self, cr, uid, ids, context=None):
        po_obj = self.pool.get('purchase.order')
        #import pdb;pdb.set_trace()
        for data in self.browse(cr, uid, ids, context=context):
            po_revision = po_obj.copy(cr, uid, context['active_id'], default=None, context=None)
            data_browse = po_obj.browse(cr,uid,context['active_id'])

            po_name = data_browse.name
            po_exist = po_obj.search(cr,uid,[('name','=',po_name)])
            total_po_exist = len(po_exist)
            po_obj.write(cr,uid,po_revision,{'notes':'Revisi ke - '+str(total_po_exist),
                                            'name':po_name,
                                            'user_revision_id':uid,
                                            'reason':'Alasan Revisi : '+data.name,
                                            'po_asal_id':context['active_id']},context=context)
            po_obj.write(cr,uid,context['active_id'],{'po_revisi_id':po_revision,'reason':'Alasan Cancel : '+data.name,},context=context)    

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
        view_id = view_ref and view_ref[1] or False,    
        return {
            'name' : _('Revision'),
            'view_type': 'form',
            'view_mode': 'form',            
            'res_model': 'purchase.order',
            'res_id': po_revision,
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': False,
            }
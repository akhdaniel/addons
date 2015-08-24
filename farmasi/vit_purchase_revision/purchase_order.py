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


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    _columns = {
        'user_revision_id'  : fields.many2one('res.users','Revision By',readonly=True),
        'notes'             : fields.text('Notes',readonly=True),
        'notes2'            : fields.text('Notes'),
        'reason'            : fields.text('Alasan Revisi'),
        'po_revisi_id'      : fields.many2one('purchase.order','PO Revisi',readonly=True),
        'po_asal_id'        : fields.many2one('purchase.order','Dari PO',readonly=True),
    }  

    _sql_constraints = [
        ('name_uniq', 'unique(name, notes, company_id)', 'Order Reference must be unique per Company !'),
    ]     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
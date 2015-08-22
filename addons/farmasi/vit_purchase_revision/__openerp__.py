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

{
    'name' : 'Track Purchase Orders Cancelled',
    'version' : '1.0',
    'category': 'Purchase Management',
    'depends' : ['base','purchase'],
    'author' : 'vitraining.com',
    'description': """
untuk revisi nomor PO nya kalau bisa sama, dan keluar juga di print out, notif penanda untuk disampaikan ke akunting bila ada cancel atau revisi, kolom keterangan karena cancel, kolom keterangan mandatory bila cancel

PO:
tambahn action_revisi,
logicnya:
- copy exiting PO, nomor sama, tapi revisi_no increment (awalnya 0)
- PO lama jadi cancel

jika No PO unique consttain: modif uniq nya jadi No + revisi
    """,
    'website': 'http://www.vitraining.com',
    'data': [
        'purchase_order_view.xml',
        'wizard/purchase_order_revision_wizard.xml',
        #'security/ir.model.access.csv',
    ],
    'test': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


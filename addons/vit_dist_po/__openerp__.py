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
    'name': 'PO Distributor',
    'version': '1.2',
    'category': 'Purchase Management',
    'summary': 'Purchase Orders for Distributor',
    'description': """
Add CMO to the Purchase Orders
    """,
    'author': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'depends': [
        'purchase',
        'product',
        'vit_custom_users',
        'fleet',
        'stock',
        'web_m2x_options',
        'report_webkit',
        'vit_custom_djislu',
        'web_printscreen_zb',
        'product_expiry',
    ],
    'data': [
        'stock_view.xml',
        'purchase_view.xml',
        'stock_prod_lot.xml',
        'report/po_webkit_header.xml',
        'report/purchase_order.xml',
        'cron_job.xml',
        'invoice_view.xml',
        'wizard/po_export_wizard_view.xml',
        # 'stock_workflow.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'css':[
        'static/src/css/distcustom.css',
    ],
    'js' : [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

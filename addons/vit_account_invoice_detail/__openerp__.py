# -*- coding: utf-8 -*-
##############################################################################
#
#    Filter on Stock quantity - OpenERP Module
#    Copyright (C) 2013 Shine IT (<http://www.openerp.cn>).
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
    'name': 'Account Invoice Detail',
    'version': '0.2',
    'author': 'vitraining.com',
    'summary': 'Account Invoice Detail',
    'description' : """
Tambah fitur:
  - Customer Invoice Detail
  - Customer Refund Detail
  - Supplier Invoice Detail
  - Supplier Refund Detail
    """,
    'website': 'http://www.vitraining.com',
    'depends': ['account','account_accountant'],
    'category': 'Accounting',
    'sequence': 20,
    'update_xml':[
                'account_invoice_detail_view.xml',
                ],    
    'demo': [],
    'data': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
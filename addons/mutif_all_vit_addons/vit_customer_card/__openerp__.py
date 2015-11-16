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
    'name': 'Customer Card',
    'version': '0.1',
    'author': 'vitraining.com',
    'summary': 'Kartu Hutang/Piutang Customer',
    'description' : """
Journal yang harus ada:
Point Reward, kode PR
Cash Back, kode CB
Selisih Penjualan kode SP

CoA yang harus ada:
2-500016 - Hutang Ongkos Kirim
6-211007 - Point Reward
4-110012 - Cash Back
4-110011 - Selisih Penjualan Barang
    """,
    'website': 'http://www.vitraining.com',
    'depends': ['base','account','account_accountant'],
    'update_xml':[],    
    'data': [
            #'report/customer_card_report.xml',
            'view_customer_card.xml',
            'wizard/view_customer_card_wizard.xml',

            ],
    'active': False,
    'installable': True,
    'application': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
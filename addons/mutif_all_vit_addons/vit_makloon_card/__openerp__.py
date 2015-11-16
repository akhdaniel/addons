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
    'name': 'Makloon Card',
    'version': '0.1',
    'author': 'vitraining.com',
    'summary': 'Kartu Makloon',
    'description' : """
Kartu Makloon
    """,
    'website': 'http://www.vitraining.com',
    'depends': ['base','account','vit_n_cutting_order'],
    'update_xml':[],    
    'data': [
            'report/makloon_card_report.xml',
            'view_makloon_card.xml',
            'wizard/view_makloon_card_wizard.xml',
            'security/ir.model.access.csv',
            ],
    'active': False,
    'installable': True,
    'application': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
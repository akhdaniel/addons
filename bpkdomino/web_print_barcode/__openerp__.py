# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Print to barcode zebra',
    'version': '1.0',
    'category': 'Web',
    'author': "aiksuwandra(at)gmail.com",
    'website': 'Vitraining.com',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'siu_mrp',
        'vit_field_barcode_siu_mrp'
    ],
    'data': [
        'view/web_print_barcode.xml',
    ],
    'qweb': [
        'static/src/xml/web_print_barcode_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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
    "name": "Human Resources: overtime management",
    "version": "1.0",
    "author": "ISA srl",
    "category": "Human Resources",
    "website": "www.isa.it",
    "description": """Human Resources: Overtime tracking and workflow
   
""",
    #'depends': ['hr','resource','report_aeroo_ooo',],
    'depends': ['hr','resource',],
    #'init_xml': [],
    'update_xml': [
        'hr_overtime_view.xml',
        'hr_overtime_workflow.xml',
        #"report/report.xml",
        #'wizard/hr_overtime_bymonth_view.xml',
        #'security/ir.model.access.csv','security/ir_rule.xml'
        ],
    #'demo_xml': [],
    #'test': [],
    'installable': True,
    #'active': False,
    #'certificate': '',
}


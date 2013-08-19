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
# Generated by the OpenERP plugin for Dia !
{
        "name" : "EProc",
        "version" : "0.1",
        "author" : "Tiny",
        "website" : "http://openerp.com",
        "category" : "Unknown",
        "description": """  """,
        "depends" : ['base','product'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "update_xml" : [
                'supplier_view.xml', 
                'lelang_view.xml',
                'security/groups.xml',
                'security/ir.model.access.csv',
                'action.xml',                
                'tambah_tab.xml',
                'eproc_workflow.xml'
        ],
        "installable": True
}

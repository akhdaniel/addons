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
        "name" : "vit_claim",
        "version" : "0.1",
        "author" : "vitraining.com",
        "website" : "http://vitraining.com",
        "category" : "Unknown",
        "description": """  """,
        "depends" : ['base','vit_actuary', 'vit_member'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "data" : [
                'security/ir.model.access.csv',
                'security/group.xml',

                'vit_claim_view.xml', 
                'data/claim_status.xml',
                'data/sequence.xml',

                'wizard/show_member_plan_view.xml',
                'wizard/show_member_claim_history_view.xml',

                'menu.xml',
        ],
        "installable": True
}
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
        "name" : "vit_actuary",
        "version" : "0.1",
        "author" : "vitraining",
        "website" : "http://vitraining.com",
        "category" : "Unknown",
        "description": """  """,
        "depends" : ['base'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "data" : [
                'security/group.xml',
                'security/ir.model.access.csv',
                
                'views/age_band.xml', 
                'views/benefit.xml', 
                'views/benefit_unit.xml', 
                'views/diagnosis.xml', 
                'views/existing_insurance.xml', 
                'views/gender.xml', 
                'views/gl_notes.xml', 
                'views/group_size.xml', 
                'views/holiday.xml', 
                'views/lob.xml', 
                'views/marital_status.xml', 
                'views/membership.xml', 
                'views/membership_factor.xml', 
                'views/modal_factor.xml', 
                'views/product.xml', 
                'views/product_plan_base.xml', 
                'views/product_plan.xml', 
                'views/product_type.xml', 
                'views/reason.xml', 
                'views/province.xml', 
                'views/region.xml', 
                'views/salutation.xml', 
                'views/annual_income.xml', 
                'views/religion.xml', 
                'views/employment.xml', 
                'views/users.xml',
                'views/provider_view.xml',
                'views/provider_level_view.xml',
                'views/provider_type_view.xml',
                'views/profile_view.xml',
                'views/room_view.xml',
                'views/default_limit.xml',

                'data/provider_level_data.xml',
                'data/provider_type_data.xml',
                'data/product_type.xml', 
                'data/membership_data.xml', 
                'data/product.xml', 
                'data/product_plan_base.xml', 
                'data/product_plan.xml',                 
                'data/netpro.reason.csv',
                'data/netpro.diagnosis.csv',
                'data/netpro.benefit.csv',
                'data/netpro.benefit_unit.csv',
                'data/netpro.region.csv',
                'data/res.country.state.csv',
                'data/sequence.xml',
                'data/netpro.lob.csv',
                'data/netpro.holiday.csv',
                'data/netpro.membership_factor.csv',

                'menu.xml',
                # 'data/sequence.xml',
                # 'data/master_data_actuary.xml'
        ],
        "installable": True
}
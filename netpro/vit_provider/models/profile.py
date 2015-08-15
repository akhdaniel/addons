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
from openerp.osv import fields,osv
class netpro_profile(osv.osv):
    _name = 'netpro.profile'
    _inherits = {'res.partner': 'partner_id'}
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', 
            required=True, select=True, ondelete='cascade'),
        #'name': fields.char('Profile ID'),
        'reference_id': fields.char('Reference ID'),
        'external_profile_id': fields.char('External Profile ID'),
        'corporate': fields.boolean('Coorporate'),
        'provider': fields.boolean('Provider'),
        'tpa': fields.boolean('TPA'),
        'dump_profile': fields.boolean('Dump Profile'),
        'salutation_id': fields.many2one('netpro.salutation', 'Salutation'),
        'initial': fields.char('Initial'),
        'branch': fields.integer('Branch'),
        'profile_type': fields.selection([('D', 'Direct Business'), ('C', 'Captive'), ('M', 'Intermediaries'), ('I', 'Inward Business'), ('O', 'Outward Business'), ('T', 'Others')], 'Profile Type'),
        'line_of_business_id': fields.many2one('netpro.lob', 'Line Of Business'),
        'referral': fields.many2one('netpro.profile', 'Referral'),
        'pic_name': fields.char('PIC Name'),
        'pic_title': fields.char('PIC Title'),
        'pic_address': fields.text('PIC Address'),
        'pic_phone': fields.char('PIC Phone'),
        'company_group_id': fields.many2one('res.partner.category', 'Company Category'),
        'sub_company_category_id': fields.many2one('res.partner.category', 'Sub Comp. Category'),
        'company_type': fields.selection([('GOV', 'Government'), ('PRIV', 'Provate'), ('JV', 'Join Venture'), ('BUMN', 'BUMN'), ('BUMD', 'BUMD')], 'Company Type'),
        'company_rating': fields.integer('Company Rating'),
        'company_siup': fields.char('Company SIUP'),
        'company_tdp': fields.char('Company TDP'),
        'biz_license_no': fields.char('Biz. License No.'),
        'biz_license_date': fields.date('Biz. License Date'),
        'bod_name_1': fields.char('BOD (1) Name'),
        'bod_function_1': fields.char('Function BOD (1)'),
        'bod_name_2': fields.char('BOD (2) Name'),
        'bod_function_2': fields.char('Function BOD (2)'),
        'bod_name_3': fields.char('BOD (3) Name'),
        'bod_function_3': fields.char('Function BOD (3)'),
        'share_holder_name_1': fields.char('Share Holder (1) Name'),
        'share_holder_name_2': fields.char('Share Holder (2) Name'),
        'share_holder_name_3': fields.char('Share Holder (3) Name'),
        'gender': fields.selection([('M', 'Male / Pria'), ('F', 'Female / Perempuan')], 'Gender'),
        'birthplace': fields.char('Birth Place'),
        'marital_status': fields.selection([('S', 'Single'), ('M', 'Married')], 'Marital Status'),
        'religion_id': fields.many2one('netpro.religion', 'Religion'),
        'idcard_type': fields.selection([('KTP', 'KTP'), ('SIM', 'SIM'), ('PASSPORT', 'PASSPORT')], 'ID Card Type'),
        'personal_id_no': fields.char('Personal ID No'),
        'personal_id_name': fields.char('Personal ID Name'),
        'personal_id_date': fields.date('Personal ID Date'),
        'nickname': fields.char('Nickname'),
        'citizenship': fields.selection([('WNI', 'WNI'), ('WNA', 'WNA')], 'Citizenship'),
        'employment_id': fields.many2one('netpro.employment', 'Employment'),
        'annual_income_id': fields.many2one('netpro.annual_income', 'Annual Income (IDR)'),
        'other_source_income': fields.selection([('WARISAN', 'Warisan'), ('HIBAH', 'Hibah'), ('LAINNYA', 'Lainnya')], 'Other Source Of Income'),
        'company_working_name': fields.char('Company Working Name'),
        'company_working_address': fields.text('Company Working Address'),
        'company_working_phone': fields.char('Company Working Phone'),
        'vat': fields.boolean('VAT'),
        'tax': fields.boolean('TAX'),
        'taxation_id': fields.char('Taxation ID (NPWP)'),
        'taxation_name': fields.char('Taxation Name'),
        'taxation_address': fields.text('Taxation Address'),
        'restrict_this_profile': fields.boolean('Restrict This Profile'),
        'restrict_remarks': fields.text('Restrict Remarks'),
        'reflag_this_profile': fields.boolean('Reflag This Profile'),
        'reflag_date': fields.datetime('Reflag Date'),
        'user_id': fields.many2one('res.partner', 'By User'),
        'reflag_remarks': fields.text('Reflag Remarks'),
        'agent_license_no': fields.char('Agent License No'),
        'default_wpc': fields.integer('Default WPC (in day(s))'),
        'default_grace_period': fields.integer('Default Grace Period (in day(s))'),
        'default_discount': fields.float('Default Discount'),
        'default_comission': fields.float('Default Comission'),
        'net_comission': fields.boolean('Net Comission (After Payor Discount)'),
        'max_out_go': fields.float('Max Out Go'),
        'purpose_of_insurance': fields.selection([('POA', 'Perlindungan Objek Asuransi'), ('PK', 'Persyaratan Kredit'), ('KK', 'Keamanan Dan Kenyamanan'), ('L', 'Lainnya')], 'Purpose Of Insurance'),
        'alias_ids': fields.one2many('netpro.alias', 'profile_id', 'Profile', ondelete='cascade'),
        'created_by_id' : fields.many2one('res.users', 'Creator', readonly=True),
    }
netpro_profile()

class netpro_alias(osv.osv):
    _name = 'netpro.alias'
    _columns = {
        'profile_id': fields.many2one('netpro.profile', 'Profile'),
        'merged_profile_id': fields.many2one('netpro.profile', 'Merged Profile ID'),
        'merged_reference_id': fields.char('Merged Reference ID'),
        'address': fields.text('Address'),
        'phone': fields.char('Phone'),
        'fax': fields.char('Fax'),
        'email': fields.char('Email'),
        'type': fields.selection([('D', 'Delivery'), ('C', 'Correspondence'), ('M', 'Merged')], 'Type'),
        'notes': fields.text('Notes'),
    }
netpro_alias()


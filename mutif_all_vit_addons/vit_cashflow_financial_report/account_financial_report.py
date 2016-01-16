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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

# ---------------------------------------------------------
# Account Financial Report Inherit
# ---------------------------------------------------------

class account_financial_report(osv.osv):
    _name = "account.financial.report"
    _inherit = "account.financial.report"

# ---------------------------------------------------------
# karena ketika di inherit idsnya tidak lengkap seperti objek aslinya misal ids objek asli=[1,2,3] ketika diturunkan ids menjadi=[2,3]
# maka semetara di edit manual di file aslinya /opt/openerp/openerp-7/openerp/addons/account/report/account_financial_report.py
# ---------------------------------------------------------

    # def _get_balance(self, cr, uid, ids, field_names, args, context=None):
    #     '''returns a dictionary with key=the ID of a record and value=the balance amount 
    #        computed for this record. If the record is of type :
    #            'accounts' : it's the sum of the linked accounts
    #            'account_type' : it's the sum of leaf accoutns with such an account_type
    #            'account_report' : it's the amount of the related report
    #            'sum' : it's the sum of the children of this record (aka a 'view' record)'''
    #     account_obj = self.pool.get('account.account')
    #     res = {}
        
    #     for report in self.browse(cr, uid, ids, context=context):
    #         if not report.starting_ending:
    #             if report.id in res:
    #                 continue
    #             res[report.id] = dict((fn, 0.0) for fn in field_names)
    #             if report.type == 'accounts':
    #                 # it's the sum of the linked accounts
    #                 for ax in report.account_ids:
    #                     for field in field_names:
    #                         res[report.id][field] += getattr(ax, field)
    #             elif report.type == 'account_type':
    #                 # it's the sum the leaf accounts with such an account type
    #                 report_types = [x.id for x in report.account_type_ids]
    #                 account_ids = account_obj.search(cr, uid, [('user_type','in', report_types), ('type','!=','view')], context=context)
    #                 for a in account_obj.browse(cr, uid, account_ids, context=context):
    #                     for field in field_names:
    #                         res[report.id][field] += getattr(a, field)
    #             elif report.type == 'account_report' and report.account_report_id:               
    #                 # it's the amount of the linked report
    #                 res2 = self._get_balance(cr, uid, [report.account_report_id.id], field_names, False, context=context)
    #                 for key, value in res2.items():
    #                     for field in field_names:
    #                         res[report.id][field] += value[field]
    #             elif report.type == 'sum':
    #                 # it's the sum of the children of this account.report
    #                 res2 = self._get_balance(cr, uid, [rec.id for rec in report.children_ids], field_names, False, context=context)
    #                 for key, value in res2.items():
    #                     for field in field_names:
    #                         res[report.id][field] += value[field]

    #         if report.starting_ending:
    #             #jika starting balance
    #             if report.starting_ending == 'starting':
    #                 # jika period
    #                 if 'period_to' in context:          
    #                     period_from = context['period_from']
    #                     period_to = context['period_to'] 
    #                     context.update({'period_from':report.period_from.id,'period_to':period_from-1,'periods':[i for i in range(int(report.period_from.id),int(period_from))]})
                            
    #                     rpt = self.browse(cr, uid, report.id, context=context)
    #                     res[rpt.id] = dict((fn, 0.0) for fn in field_names)
    #                     if rpt.type == 'accounts':
    #                         # it's the sum of the linked accounts
    #                         for ax in rpt.account_ids:
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(ax, field)
    #                     elif rpt.type == 'account_type':
    #                         # it's the sum the leaf accounts with such an account type
    #                         report_types = [x.id for x in rpt.account_type_ids]
    #                         account_ids = account_obj.search(cr, uid, [('user_type','in', report_types), ('type','!=','view')], context=context)
    #                         for a in account_obj.browse(cr, uid, account_ids, context=context):
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(a, field)
    #                     elif rpt.type == 'account_report' and rpt.account_report_id:               
    #                         # it's the amount of the linked report
    #                         res2 = self._get_balance(cr, uid, [rpt.account_report_id.id], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]
    #                     elif rpt.type == 'sum':
    #                         # it's the sum of the children of this account.report
    #                         res2 = self._get_balance(cr, uid, [rec.id for rec in rpt.children_ids], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]                                    
    #                     context.update({'period_from':period_from,'period_to':period_to,'periods':[i for i in range(int(period_from),int(period_to+1))]})                


    #                 if 'date_to' in context:         
    #                     date_from = context['date_from']
    #                     date_to = context['date_to'] 
    #                     new_date = datetime.datetime.strptime(date_from,"%Y-%m-%d")
    #                     min1 = datetime.timedelta(days=1)
    #                     new_date1 = new_date - min1
    #                     new_date_to = str(new_date1)[:10]

    #                     context.update({'date_from':report.date_from,'date_to':new_date_to})
    #                     rpt = self.browse(cr, uid, report.id, context=context)
    #                     res[rpt.id] = dict((fn, 0.0) for fn in field_names)
    #                     if rpt.type == 'accounts':
    #                         # it's the sum of the linked accounts
    #                         for ax in rpt.account_ids:
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(ax, field)
    #                     elif rpt.type == 'account_type':
    #                         # it's the sum the leaf accounts with such an account type
    #                         report_types = [x.id for x in rpt.account_type_ids]
    #                         account_ids = account_obj.search(cr, uid, [('user_type','in', report_types), ('type','!=','view')], context=context)
    #                         for a in account_obj.browse(cr, uid, account_ids, context=context):
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(a, field)
    #                     elif rpt.type == 'account_report' and rpt.account_report_id:               
    #                         # it's the amount of the linked report
    #                         res2 = self._get_balance(cr, uid, [rpt.account_report_id.id], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]
    #                     elif rpt.type == 'sum':
    #                         # it's the sum of the children of this account.report
    #                         res2 = self._get_balance(cr, uid, [rec.id for rec in rpt.children_ids], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]                                    
    #                     context.update({'date_from':date_from,'date_to':date_to})                             

    #             #jika starting balance
    #             if report.starting_ending == 'ending':
    #                 # jika period
    #                 if 'period_to' in context:          
    #                     period_from = context['period_from']
    #                     period_to = context['period_to'] 
    #                     context.update({'period_from':report.period_from.id,'period_to':period_from,'periods':[i for i in range(int(report.period_from.id),int(period_from+1))]})
                            
    #                     rpt = self.browse(cr, uid, report.id, context=context)
    #                     res[rpt.id] = dict((fn, 0.0) for fn in field_names)
    #                     if rpt.type == 'accounts':
    #                         # it's the sum of the linked accounts
    #                         for ax in rpt.account_ids:
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(ax, field)
    #                     elif rpt.type == 'account_type':
    #                         # it's the sum the leaf accounts with such an account type
    #                         report_types = [x.id for x in rpt.account_type_ids]
    #                         account_ids = account_obj.search(cr, uid, [('user_type','in', report_types), ('type','!=','view')], context=context)
    #                         for a in account_obj.browse(cr, uid, account_ids, context=context):
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(a, field)
    #                     elif rpt.type == 'account_report' and rpt.account_report_id:               
    #                         # it's the amount of the linked report
    #                         res2 = self._get_balance(cr, uid, [rpt.account_report_id.id], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]
    #                     elif rpt.type == 'sum':
    #                         # it's the sum of the children of this account.report
    #                         res2 = self._get_balance(cr, uid, [rec.id for rec in rpt.children_ids], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]                                    
    #                     context.update({'period_from':period_from,'period_to':period_to,'periods':[i for i in range(int(period_from),int(period_to+1))]})                


    #                 if 'date_to' in context:         
    #                     date_from = context['date_from']
    #                     date_to = context['date_to'] 
    #                     new_date = datetime.datetime.strptime(date_from,"%Y-%m-%d")
    #                     min1 = datetime.timedelta(days=1)
    #                     new_date1 = new_date - min1
    #                     new_date_to = str(new_date1)[:10]

    #                     context.update({'date_from':report.date_from})
    #                     rpt = self.browse(cr, uid, report.id, context=context)
    #                     res[rpt.id] = dict((fn, 0.0) for fn in field_names)
    #                     if rpt.type == 'accounts':
    #                         # it's the sum of the linked accounts
    #                         for ax in rpt.account_ids:
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(ax, field)
    #                     elif rpt.type == 'account_type':
    #                         # it's the sum the leaf accounts with such an account type
    #                         report_types = [x.id for x in rpt.account_type_ids]
    #                         account_ids = account_obj.search(cr, uid, [('user_type','in', report_types), ('type','!=','view')], context=context)
    #                         for a in account_obj.browse(cr, uid, account_ids, context=context):
    #                             for field in field_names:
    #                                 res[rpt.id][field] += getattr(a, field)
    #                     elif rpt.type == 'account_report' and rpt.account_report_id:               
    #                         # it's the amount of the linked report
    #                         res2 = self._get_balance(cr, uid, [rpt.account_report_id.id], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]
    #                     elif rpt.type == 'sum':
    #                         # it's the sum of the children of this account.report
    #                         res2 = self._get_balance(cr, uid, [rec.id for rec in rpt.children_ids], field_names, False, context=context)
    #                         for key, value in res2.items():
    #                             for field in field_names:
    #                                 res[rpt.id][field] += value[field]                                    
    #                     context.update({'date_from':date_from}) 

    #     return res

    _columns = {
        'starting_ending': fields.selection([('starting', 'Starting Balance'),('ending', 'Ending Balance')],'Starting/Ending Balance', help="Set hitungan di report apakah dihitung normal, starting balance atau ending balance"),
        'period_from': fields.many2one('account.period', 'Default Start Period'),
        'date_from': fields.date("Default Start Date"),
        }
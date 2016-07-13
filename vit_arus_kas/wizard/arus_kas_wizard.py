# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
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
from openerp import models, fields, api, _
import time
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from datetime import datetime


class arus_kas_wizard(models.TransientModel): 
    _name = 'arus.kas.wizard' 

    def _get_period(self, cr, uid, context=None):
        ctx = dict(context or {})
        period_ids = self.pool.get('account.period').find(cr, uid, context=ctx)
        return period_ids[0]

    period_start_id     = fields.Many2one('account.period','Period Start',required=True)
    period_end_id       = fields.Many2one('account.period','Period End',required=True)
    account_id          = fields.Many2one('account.account','Chart of Account',required=True)

    def _get_total_debit_credit(self, cr, uid, ids, l_state, m_state, period_id, account_id, context):
        cr.execute('SELECT '\
                'sum(l.debit) as debit, '\
                'sum(l.credit) as credit '\
            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state = %s '\
                'AND am.state = %s '\
                'AND am.period_id < %s '\
                'AND l.account_id = %s '\
                'AND (l.debit != 0 or l.credit != 0) ',(l_state, m_state, period_id, account_id))     
        debit = 0
        credit = 0
        output = cr.fetchone()
        if output[0] != None :
            debit = output[0]
        if output[1] != None :
            credit = output[1]
        opening_balance = (debit,credit)

        return opening_balance


    def hasil(self, cr, uid, desc, report, view_id, domain, context):
        return {
            'name' : _(desc),
            'view_type': 'form',
            'view_mode': 'form',            
            'res_model': 'arus.kas',
            'res_id': report,
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'target': 'current',
            #'domain' : domain,
            #'context': context,
            'nodestroy': False,
            }


    def fill_table(self, cr, uid, ids, context=None):
        wizard  = self.browse(cr, uid, ids[0], context=context) 
        sql = "delete from arus_kas where user_id = %s" % (uid)
        cr.execute(sql)

        l_state = 'valid'   
        am_state = 'posted' 

        arus_kas_id = self.pool.get('arus.kas').create(cr,uid,{'account_id':wizard.account_id.id,
                                                                        'period_start_id': wizard.period_start_id.id,
                                                                        'period_end_id': wizard.period_end_id.id,
                                                                        'user_id':uid})

        #cari opening balance_get_total_balance
        opening = self._get_total_debit_credit(cr, uid, ids, l_state, am_state, wizard.period_start_id.id, wizard.account_id.id, context=context)
        opening_balance = opening[0]-opening[1]

        cr.execute('SELECT '\
                'am.date as date, '\
                'l.name as description, '\
                'am.narration as narration, '\
                'l.debit as debit, '\
                'l.credit as credit, '\
                'l.debit-l.credit as balance, '\
                'am.name as number '\

            'FROM '\
                'account_move_line l '\
                'left join account_account a on (l.account_id = a.id) '\
                'left join account_move am on (am.id=l.move_id) '\

            'WHERE l.state = %s '\
                'AND am.state = %s '\
                'AND am.period_id >= %s and am.period_id <= %s '\
                'AND l.account_id = %s '\
                'AND (l.debit != 0 or l.credit != 0) '\
            'ORDER BY am.date,am.name ASC' ,(l_state,am_state, wizard.period_start_id.id,wizard.period_end_id.id,wizard.account_id.id))

        hasil_query = cr.fetchall()
        
        self.pool.get('arus.kas.detail').create(cr,uid,{'arus_kas_id'      : arus_kas_id,
                                                            'description'       : 'Opening Balance',
                                                            'initial_balance'   : opening_balance,
                                                            'balance'           : opening_balance,
                                                            })
        balance = opening_balance
        if hasil_query:
            balance = opening_balance
            init_balance = opening_balance
            for execute in hasil_query: 
                balance += execute[3]
                balance -= execute[4] 
                self.pool.get('arus.kas.detail').create(cr,uid,{'arus_kas_id'       : arus_kas_id,
                                                                    'date'          : execute[0] or False,
                                                                    'description'   : execute[1],
                                                                    'narration'     : execute[6],
                                                                    'initial_balance' : init_balance,
                                                                    'debit'         : execute[3],
                                                                    'credit'        : execute[4],
                                                                    'balance'       : balance})
                init_balance += execute[3]
                init_balance -= execute[4] 
                                                                                      
        #import pdb;pdb.set_trace()              
        self.pool.get('arus.kas').write(cr,uid,arus_kas_id,{'t_initial_balance'  : opening_balance ,
                                                            't_balance'           : balance})

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_arus_kas', 'vit_arus_kas_form')
        view_id = view_ref and view_ref[1] or False,    
        
        desc    = 'Arus Kas'
        domain  = []
        context = {}

        return self.hasil(cr, uid, desc, arus_kas_id, view_id, domain, context)
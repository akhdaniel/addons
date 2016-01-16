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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import mute_logger
import sets
import logging
_logger = logging.getLogger(__name__)

class stock_update_inventory(osv.osv_memory):
    _name = "stock.update.inventory"

    _columns = {
        'date_move'         : fields.date('Date'),
        'date_journal'      : fields.date('Date'),
        'period_journal_id' :fields.many2one('account.period', 'Period'),
    }

    def update_inventory(self, cr, uid, ids, context=None):       
        if context is None:
            context = {}
        res = self.execute_update(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

    def execute_update(self, cr, uid, ids, inv_ids, context=None):
        
        if context is None:
            context = {}  
        wizard = self.browse(cr,uid,ids)[0]
        date_move = wizard.date_move
        date_journal = wizard.date_journal
        period_id = wizard.period_journal_id.id
        if not date_move and not date_journal and not period_id :
            raise osv.except_osv(_('Error!'),  _('Isi dulu minimal 1 data update !'))
        phy_obj = self.pool.get('stock.inventory') 
        move_obj = self.pool.get('stock.move') 
        acc_move_obj = self.pool.get('account.move')
        acc_move_line_obj = self.pool.get('account.move.line') 
        usr_obj = self.pool.get('res.users')

        for inv in phy_obj.browse(cr,uid,inv_ids,context=context):
            old_move_date = '-'
            old_journal_date = '-'
            old_journal_period = '-'
            name_phy = 'INV:'+str(inv.name)
            if date_move:
                cr.execute('''select
                        move_id
                    from
                        stock_inventory_move_rel
                    where
                        inventory_id = %s ''',(inv_ids[0],))
                res = cr.fetchall()
                move_ids = map(lambda x: x[0], res) # atau  [i for (i,) in res]
                old_move_date = move_obj.browse(cr,uid,move_ids[0]).date
                cr.execute('update stock_move set date=%s where id in %s', (date_move, tuple(move_ids),))             
            if date_journal and period_id:
                cr.execute('''select
                        id
                    from
                        account_move_line
                    where
                        name = %s ''',(name_phy,))
                res = cr.fetchall()
                aml_ids = map(lambda x: x[0], res) # atau  [i for (i,) in res] 
                old_journal_date = acc_move_line_obj.browse(cr,uid,aml_ids[0]).date
                cr.execute('update account_move_line set date=%s,period_id=%s where id in %s', (date_journal,period_id, tuple(aml_ids),))                   
                cr.commit()

                cr.execute('''select
                        move_id
                    from
                        account_move_line
                    where
                        name = %s ''',(name_phy,))
                res = cr.fetchall()
                #import pdb;pdb.set_trace()
                journal_ids = map(lambda x: x[0], res) # atau  [i for (i,) in res] 

                old_journal_period = acc_move_obj.browse(cr,uid,journal_ids[0]).period_id.name
                #update tanggal dan period
                cr.execute('update account_move set date=%s,period_id=%s where id in %s', (date_journal,period_id, tuple(journal_ids),)) 

            user_name = usr_obj.browse(cr,uid,uid).name
            old_history = inv.history
            space = ''
            if old_history:
                space = old_history
                phy_obj.write(cr,uid,inv_ids[0],{'history': str(space)+'Tanggal Move dan Journal telah diperbaharui oleh '+str(user_name)
                                                            +' pada tanggal '+str(fields.date.today())+', '
                                                            +'[Move Date = '+ str(old_move_date[:10])+', '
                                                            +' Journal Date = '+ str(old_journal_date)+', '
                                                            +' Period  = '+ str(old_journal_period)+'], '})
            
        return True       
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

import openerp
from openerp.osv import fields, osv
import re
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import html2plaintext


class sale_order(osv.osv):
    """ Helpdesk Cases """
    _inherit = 'sale.order'


    _columns = {
        'email_from': fields.char('Customer Email'),
        }


    # -------------------------------------------------------
    # Mail gateway
    # -------------------------------------------------------

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        
        print'Partner Name>>>>>>>>',msg.get('from')
        partner_ids = None
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name': '/',
            'note': desc,
            'user_id': uid,
        }
        if msg.get('author_id', False) == False:
            index = str(msg.get('from')).find('<')
            partner_name = str(msg.get('from'))[:index-1].strip()
            print'Partner Name With ..>>>>>>>>',partner_name
            partner_ids = self.pool.get('res.partner').search(cr,uid,[('name','=',partner_name)],context=context)
            client_mail = re.search(r'[\w\.-]+@[\w\.-]+', msg.get('from')).group(0)
            partner_id = None
            if not partner_ids:
                partner_id = self.pool.get('res.partner').create(cr,uid,{'name':partner_name, 'email':client_mail},context=context)
                defaults.update({'partner_id':partner_id})
            else:
                defaults.update({'partner_id':partner_ids[0]})
        
        else:
            defaults.update({'partner_id':msg.get('author_id')})
        if custom_values is None:
            custom_values = {}
        
        #partner_ids = self.pool.get('res.partner').search(cr,uid,[('customer','=',Ture)],context=context)
        defaults.update(custom_values)
        return super(sale_order, self).message_new(cr, uid, msg, custom_values=defaults, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

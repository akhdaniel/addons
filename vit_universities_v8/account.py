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
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp


class account_voucher(osv.osv):
	_inherit = "account.voucher"

	def proforma_voucher(self, cr, uid, ids, context=None):
		self.action_move_line_create(cr, uid, ids, context=context)

		# create notifikasi ke email
		mail_obj = self.pool.get('mail.mail')
		for vc in self.browse(cr,uid,ids,context=context):
			if vc.partner_id.is_mahasiswa :
				mail_obj.create(cr,uid,{'subject' : 'Pembayaran ISTN',
							'email_to' : vc.partner_id.id,
							'recipient_ids' : [(6, 0, [vc.partner_id.id])],
							'notification' : True,
							'body_html': 'Terima Kasih '+str(vc.partner_id.name)+', pembayaran sebesar Rp.'+str(vc.amount)+' telah diterima, silahkan cek status pembayaran anda di portal mahasiswa !'

							})          
		return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

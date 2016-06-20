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

import itertools
from lxml import etree
from datetime import datetime,date
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
	_inherit = "account.invoice"

	####################################################################################################
	# Cron Job untuk validasi invoice otomatis pendaftaran
	####################################################################################################
	def cron_validate_invoice(self, cr, uid, ids=None,context=None):
		date_now 	= date.today().strftime('%Y-%m-%d')
		inv_to_validate = self.search(cr,uid,[('state','=','draft'),('date_invoice','=',date_now)])
		if inv_to_validate :
			for inv in inv_to_validate :
				invs = self.browse(cr,uid,inv)
				wf_service = netsvc.LocalService('workflow')
				wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)
				_logger.info(" invoice validated number : %s" % (invs.number) )
		return True    

account_invoice()		
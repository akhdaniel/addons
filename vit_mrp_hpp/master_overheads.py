from openerp.osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
# from openerp.addons.vit_upi_uang_persediaan import terbilang_func

_logger = logging.getLogger(__name__)


class vit_master_overheads(osv.osv):
	_name = "vit.master.overheads"
	_description = 'Master Overheads'

	_columns = {
		'name'       : fields.char('Name', required=True),
		'appeareance': fields.many2one('ir.model', string="Appearance"), #appearance
		'journal_id' : fields.many2one('account.journal', 'Journal', required=True),     
		'credit_account_id'    : fields.many2one('account.account', 'Credit Account', 
			required=True,
			domain="[('type','!=','view')]" ),
		'debit_account_id'     : fields.many2one('account.account', 'Debit Account', 
			required=True,
			domain="[('type','!=','view')]"),
		'is_active'  : fields.boolean('Active?'),	
}

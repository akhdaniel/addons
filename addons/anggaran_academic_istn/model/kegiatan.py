from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class kegiatan(osv.osv):
	_name 		= "anggaran.kegiatan"
	_columns 	= {
		'program_id' 	: fields.many2one('anggaran.program', 'Program'),
		'kebijakan_id'  : fields.related('program_id', 'kebijakan_id' , type="many2one", 
			relation="anggaran.kebijakan", string="Kebijakan", store=True),
		'code'  		: fields.char('Kode'),
		'name'  		: fields.text('Nama'),
		'coa'   		: fields.many2one('account.account', 'COA')
	}
from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class import_zip_ls(osv.osv):
	_name 		= "reliance.import_zip_ls"
	_columns 	= {
	}
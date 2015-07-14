from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class netpro_benefit_unit(osv.osv):
    _name = 'netpro.benefit_unit'
    _columns = {
        'name'			: fields.char('Name'),
        'description'	: fields.char('Description'),
        'unit_limit'	:  fields.selection([('ANN','Annum'),('CON','Confinement'),('OCC','Occurence')],'Unit Limit By'),
    }
netpro_benefit_unit()
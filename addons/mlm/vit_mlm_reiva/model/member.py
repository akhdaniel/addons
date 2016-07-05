from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

MEMBER_STATES = [('draft', 'Guest'), ('open', 'Verification'), ('reject', 'Rejected'),
                 ('aktif', 'Active'), ('nonaktif', 'Non Active'), ('pre','=','Pre Registered')]

class member(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"


    _columns = {
        'state'			: fields.selection( MEMBER_STATES, 'Status',readonly= True,required=True),
    }

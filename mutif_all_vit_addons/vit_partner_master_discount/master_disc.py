from openerp.osv import fields,osv
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class master_gift(osv.osv):
    _name = "vit_master_disc"

    _columns = {
        'name'       : fields.char('Tag Name', required=True),
        'value'        : fields.float('Discount(%)', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
    } 

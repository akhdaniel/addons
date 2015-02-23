from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_util(osv.osv):
	_name 		= "mlm.util"

	def _init_ltree(self, cr, uid, context=None):
		sql = "CREATE extension ltree"
		cr.execute(sql)

		sql = "ALTER table res_partner ADD column path_ltree ltree"
		cr.execute(sql)

		sql = "CREATE INDEX path_gist_res_partner_idx ON res_partner USING GIST(path_ltree)"
		cr.execute(sql)

		sql = "CREATE INDEX path_res_partner_idx ON res_partner USING btree(path_ltree)"
		cr.execute(sql)
		return True
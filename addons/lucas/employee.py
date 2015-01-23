from openerp.osv import fields, osv
import datetime
import time
from datetime import date
from time import strptime
from time import strftime
from datetime import datetime
from openerp.osv.osv import object_proxy
from openerp.tools.translate import _
from openerp import pooler
from openerp import tools
from openerp import SUPERUSER_ID


class employee(osv.osv):
    _name = "hr.employee"
    _inherit = 'hr.employee'

    _columns = {
    	'job_des'		:fields.many2one('hr.job.position','Job position'),
    	'job_id'		: fields.many2one('hr.job', 'Job Name'),
    	'work_location2': fields.selection([('lucas','Lucas'),('marin','Marin')],'Lokasi Kerja',required=True), 
    }
employee()
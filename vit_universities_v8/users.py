from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class res_users(osv.osv):
	_inherit = "res.users"

	_columns = {
		# 'fakultas_id':fields.many2one('master.fakultas',string='Fakultas', domain=[('is_internal','=',True)]),
		# 'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('fakultas_id','=',fakultas_id),('is_internal','=',True)]"),
		'is_baak' : fields.boolean('BAAK'),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas'),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('is_internal','=',True)]"),

	}
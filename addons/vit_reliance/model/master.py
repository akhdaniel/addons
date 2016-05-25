from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class agama(osv.osv):
	_name 		= "reliance.agama"
	_columns 	= {
		"name"			: fields.char("Name"),
		"name_ls"		: fields.char("LS Name"),
		"name_arg"		: fields.char("ARG Name"),
		"name_ajri"		: fields.char("AJRI Name"),
		"name_refi"		: fields.char("REFI Name"),
		"name_rmi"		: fields.char("RMI Name"),
		"name_health"	: fields.char("Health Name"),
	}

	def get(self , cr, uid, bu, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search(cr, uid, [('name_'+bu,'ilike',name)], context=context)
		if res:
			return res[0]
		else:
			return False

class jenis_kelamin(osv.osv):
	_name 		= "reliance.jenis_kelamin"
	_columns 	= {
		"name"			: fields.char("Name"),
		"name_ls"		: fields.char("LS Name"),
		"name_arg"		: fields.char("ARG Name"),
		"name_ajri"		: fields.char("AJRI Name"),
		"name_refi"		: fields.char("REFI Name"),
		"name_rmi"		: fields.char("RMI Name"),
		"name_health"	: fields.char("Health Name"),
	}

	def get(self , cr, uid, bu, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search(cr, uid, [('name_'+bu,'ilike',name)], context=context)
		if res:
			return res[0]
		else:
			return False

class range_penghasilan(osv.osv):
	_name 		= "reliance.range_penghasilan"
	_columns 	= {
		"name"			: fields.char("Name"),
		"urutan"		: fields.integer("Urutan"),
		"min"			: fields.float("Minimum"),
		"max"			: fields.float("Maximum"),
		"name_ls"		: fields.char("LS Name"),
		"name_arg"		: fields.char("ARG Name"),
		"name_ajri"		: fields.char("AJRI Name"),
		"name_refi"		: fields.char("REFI Name"),
		"name_rmi"		: fields.char("RMI Name"),
		"name_health"	: fields.char("Health Name"),
	}

class range_penghasilan_ls(osv.osv):
	_name 		= "reliance.range_penghasilan_ls"
	_columns 	= {
		"range_penghasilan_id"	: fields.many2one('reliance.range_penghasilan', 'Range Penghasilan'),
		"name"			: fields.char("Name LS"),
	}
	def get(self , cr, uid, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["range_penghasilan_id"][0]
		else:
			return False

class range_penghasilan_rmi(osv.osv):
	_name 		= "reliance.range_penghasilan_rmi"
	_columns 	= {
		"range_penghasilan_id"	: fields.many2one('reliance.range_penghasilan', 'Range Penghasilan'),
		"name"			: fields.char("Name RMI"),
	}
	def get(self , cr, uid, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["range_penghasilan_id"][0]
		else:
			return False

class range_penghasilan_refi(osv.osv):
	_name 		= "reliance.range_penghasilan_refi"
	_columns 	= {
		"range_penghasilan_id"	: fields.many2one('reliance.range_penghasilan', 'Range Penghasilan'),
		"name"			: fields.char("Name REFI"),
	}
	def get(self , cr, uid, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["range_penghasilan_id"][0]
		else:
			return False


class warga_negara(osv.osv):
	_name 		= "reliance.warga_negara"
	_columns 	= {
		"name"			: fields.char("Name"),
		"name_ls"		: fields.char("LS Name"),
		"name_arg"		: fields.char("ARG Name"),
		"name_ajri"		: fields.char("AJRI Name"),
		"name_refi"		: fields.char("REFI Name"),
		"name_rmi"		: fields.char("RMI Name"),
		"name_health"	: fields.char("Health Name"),
	}
	def get(self , cr, uid, bu, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search(cr, uid, [('name_'+bu,'=',name)], context=context)
		if res:
			return res[0]
		else:
			return False

class pekerjaan(osv.osv):
	_name 		= "reliance.pekerjaan"
	_columns 	= {
		"name"			: fields.char("Name"),
	}

class pekerjaan_ls(osv.osv):
	_name 		= "reliance.pekerjaan_ls"
	_columns 	= {
		"pekerjaan_id"	: fields.many2one('reliance.pekerjaan', 'Pekerjaan'),
		"name"			: fields.char("Name LS"),
	}
	def get(self , cr, uid, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["pekerjaan_id"][0]
		else:
			return False

class pekerjaan_rmi(osv.osv):
	_name 		= "reliance.pekerjaan_rmi"
	_columns 	= {
		"pekerjaan_id"	: fields.many2one('reliance.pekerjaan', 'Pekerjaan'),
		"name"			: fields.char("Name RMI"),
	}
	def get(self , cr, uid, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["pekerjaan_id"][0]
		else:
			return False

class pekerjaan_refi(osv.osv):
	_name 		= "reliance.pekerjaan_refi"
	_columns 	= {
		"pekerjaan_id"	: fields.many2one('reliance.pekerjaan', 'Pekerjaan'),
		"name"			: fields.char("Name REFI"),
	}
	def get(self , cr, uid, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["pekerjaan_id"][0]
		else:
			return False

class status_nikah(osv.osv):
	_name 		= "reliance.status_nikah"
	_columns 	= {
		"name"			: fields.char("Name"),
		"name_ls"		: fields.char("LS Name"),
		"name_arg"		: fields.char("ARG Name"),
		"name_ajri"		: fields.char("AJRI Name"),
		"name_refi"		: fields.char("REFI Name"),
		"name_rmi"		: fields.char("RMI Name"),
		"name_health"	: fields.char("Health Name"),
	}
	def get(self , cr, uid, bu, name, context=None):
		if not name:
			return False
		name = name.strip()

		res = self.search(cr, uid, [('name_'+bu,'=',name)], context=context)
		if res:
			return res[0]
		else:
			return False

class state(osv.osv):
	_name 		= "res.country.state"
	_inherit 	= "res.country.state"
	_columns 	= {
        'code': fields.char('State Code', size=10,
            help='The state code in max. three chars.', required=True),
	}


class states_mapping(osv.osv):
	_name 		= "reliance.states_mapping"
	_columns 	= {
		"state_id"		: fields.many2one('res.country.state', 'State'),
		"name"			: fields.char("Name"),
	}

	def get(self , cr, uid, name, context=None):

		
		if not name:
			return False
		name = name.strip()

		state = self.pool.get('res.country.state')
		state_id = state.search(cr, uid, [('name','=',name)], context=context)
		if state_id:
			return state_id[0]

		res = self.search_read(cr, uid, [('name','=',name)], context=context)
		if res:
			return res[0]["state_id"][0]
		else:
			return False

class hobby(osv.osv):
	_name 		= "reliance.hobby"
	_columns 	= {
		"name"			: fields.char("Name"),
	}

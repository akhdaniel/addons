from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _


# edit res country

_logger = logging.getLogger(__name__)

class country(osv.osv):
	_name 		= "res.country"
	_inherit 	= "res.country"

	def find_or_create_country(self, cr, uid, name, context=None):

		# country = self.pool.get('res.country')
		country = self
		country_id = country.search(cr, uid, [('name','ilike',name)], context=context)
		if not country_id:
			data = {'name': name.title() }
			country_id = country.create(cr, uid, data, context=context)
		else:
			country_id = country_id[0]
		return country_id
		
	def find_or_create_state(self, cr, uid, name, country_id, context=None):
		state = self.pool.get('res.country.state')
		state_id = state.search(cr, uid, [('name','ilike',name),('country_id','=',country_id)], context=context)
		if not state_id:
			data = {'name': name.title() ,'country_id':country_id, 'code': name[0:1]}
			state_id = state.create(cr, uid, data, context=context)
		else:
			state_id = state_id[0]
		return state_id	

from spyne import Application, ServiceBase, rpc
from spyne import String, Integer

from spyne import Mandatory as M
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.model import complex

from openerp.service import db
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def get_registry_cr_uid_context(db_name):
    if db.exp_list():
    	#db_name = db_name[2]
        registry = RegistryManager.get(db_name)
        cr = registry.cursor()
        context = registry['res.users'].context_get(cr, SUPERUSER_ID)
        return registry, cr, SUPERUSER_ID, context
    #raise Warning(u"NO DATABASE FOUND")

class ResponseDataMember(complex.ComplexModel):
    member_no = String
    employee_name = String    
    policy_no = String

class MyService(ServiceBase):

	@rpc(M(String), _returns=M(ResponseDataMember))
	def get_member(self, member_no):
	#path url
		path=self.transport.get_path()
		db_name = path.split('/')[2]
		registry, cr, uid, context = get_registry_cr_uid_context(db_name)
		member_model = registry['netpro.member']
		member_id = member_model.search(cr, uid, [('member_no', '=', member_no)], context=context)

		if member_id:
			member = member_model.browse(cr, uid, member_id, context=context)
			response= ResponseDataMember()
			response.member_no = member.member_no
			if member.employee_id.name:
				response.employee_name = member.employee_id.name
			response.policy_no = member.policy_id.policy_no
			return response



class SOAPWsgiApplication(WsgiApplication):

    def __call__(self, req_env, start_response, wsgi_url=None):
        """Only match URL requests starting with '/soap/'."""
        if req_env['PATH_INFO'].startswith('/soap/'):
            return super(SOAPWsgiApplication, self).__call__(
                req_env, start_response, wsgi_url)
        # return None: let's the other WSGI applications (like the Root one)
        # try to handle the request

# Spyne application
application = Application(
    [MyService],
    'http://example.com/soap/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11())

# WSGI application
wsgi_application = SOAPWsgiApplication(application)


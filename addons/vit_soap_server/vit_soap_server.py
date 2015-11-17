from openerp.service.wsgi_server import module_handlers
from .my_service import wsgi_application

module_handlers.insert(0, wsgi_application)
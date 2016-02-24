# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import openerp
import base64
import simplejson
import os

class Export(http.Controller):
	@http.route('/vit_myob_po/', auth='public', website=True)
	def index(self, **kw):
		mpath = openerp.modules.get_module_path('vit_myob_po')
		contents = '<ul>'
		for filename in sorted(os.listdir(mpath + '/static'), reverse=True):
			contents += '<li><a href="/vit_myob_po/static/'+filename+'">' + filename + '</a></li>'
		contents += '</ul>'

		return http.request.make_response(
			contents
		)
# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson

class Member(http.Controller):
    @http.route('/mlm/member/create', auth='user', website=True)
    def create(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        return super(Member, self).create( **kwargs)

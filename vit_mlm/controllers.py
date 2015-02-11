# -*- coding: utf-8 -*-
from openerp import http

class Member(http.Controller):
    @http.route('/mlm/member/tree/',  auth='public', website=True)
    def index(self, **kw):
        Members = http.request.env['res.partner']
        return http.request.render('website.tree', {
            'members': Members.search([('parent_id','=',False),('path','<>',False)])
        })

    @http.route('/mlm/member/list',  auth='public', website=True)
    def list(self, **kw):
        Members = http.request.env['res.partner']
        return http.request.render('website.member_list', {
            'members': Members.search([])
        })  

    @http.route('/mlm/member/view/<model("res.partner"):member>',  auth='public', website=True)
    def view(self, member):
        return http.request.render('website.member_view', {
            'member': member
        })

    @http.route('/mlm/member/json/<int:parent_id>',  auth='public', website=True)
    def json(self, parent_id):
        Members = http.request.env['res.partner']
        members = Members.search([('parent_id','=',parent_id)])
        return members

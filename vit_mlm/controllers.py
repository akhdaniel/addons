# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

class Member(http.Controller):
    @http.route('/mlm/member/tree/',  auth='public', website=True)
    def index(self, **kw):
        Members = http.request.env['res.partner']
        return http.request.render('website.tree', {
            'members': Members.search([('parent_id','=',False),('path','<>',False)])
        })

    @http.route('/mlm/member/list', auth='user', website=True)
    def list(self, **kw):
        Members = http.request.env['res.partner']
        return http.request.render('website.member_list', {
            'members': Members.search([])
        })  

    @http.route('/mlm/member/view/<model("res.partner"):member>',  auth='user', website=True)
    def view(self, member):
        return http.request.render('website.member_view', {
            'member': member
        })

    @http.route('/mlm/member/json/<int:parent_id>',  auth='user', website=True)
    def json(self, parent_id):
        Members = http.request.env['res.partner']
        members = Members.search([('parent_id','=',parent_id)])
        return members

    @http.route('/mlm/stockist',  auth='user', website=True)
    def stockist(self, **kw):
        Members = http.request.env['res.partner']
        members = Members.search([('is_stockist','=',True)])
        return http.request.render('website.member_list', {
            'members': members
        })

    @http.route('/mlm/member/create',  auth='user', website=True)
    def create(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        Users  = pool['res.users']
        user   = Users.browse(cr, uid, uid, context=context)
        parent = user.partner_id

        return http.request.render('website.member_create', {
            'parent' : parent
        })
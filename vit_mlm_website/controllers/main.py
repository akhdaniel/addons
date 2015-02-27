# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

class vit_mlm_website(http.Controller):
    @http.route('/mlm/member/stockist',  auth='user', website=True)
    def stockist(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        domain = [('is_stockist', '=', True)]
        Partner = pool.get('res.partner')
        Partner_ids = Partner.search(cr, uid, domain, context=context)
        Partners = Partner.browse(cr, uid, Partner_ids, context=context)

        return http.request.render('website.member_list', {
            'members': Partners,
        })
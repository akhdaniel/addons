# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson
from openerp.tools.translate import _

class Member(http.Controller):

    @http.route('/mlm/', auth='public', website=True)
    def index(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        message_error = kw.get('message_error', '')
        message_success = kw.get('message_success', '')

        # update state kalau masih invited
        Users = pool['res.users']
        user = Users.browse(cr, uid, uid, context=context)
        if user:
            state = user.partner_id.state
            if state == 'invited':
                Partner =request.registry['res.partner']
                Partner.write(cr, SUPERUSER_ID,
                    [user.partner_id.id], {'state':'pre'}, context)


        return http.request.render('vit_mlm_website.mlm_homepage', {
            'message_error': message_error,
            'message_success': message_success,
        })

    @http.route('/mlm/member/invite/<model("res.partner"):member>', auth='user', website=True)
    def send_invitation(self, member, **kwargs):
        print "ni"
        try:
            request.registry['res.partner'].action_invite(request.cr, SUPERUSER_ID, [member.id], request.context)
            message = _("Invitation sent to %s") % (member.name)
            #Votre invitation a été transmise à
            return request.redirect('/mlm?message_success=%s' % (message), code=301)
        except Exception, e:
            message = str(e)
            return request.redirect('/mlm?message_error=%s' % (message), code=301)

    @http.route('/mlm/member/accept_invitation/<model("res.users"):user>', auth='user', website=True)
    def accept_invitation(self, user, **kwargs):
        #update member state to Pre-Registration
        data = {
            'state' : 'pre'
        }
        request.registry['res.partner'].write(request.cr, SUPERUSER_ID, [user.partner_id.id], data, request.context)
        message = "Thank you for accepting invitation. You can now proceed to the next steps."
        return request.redirect('/mlm?message_success=%s' % (message), code=301)
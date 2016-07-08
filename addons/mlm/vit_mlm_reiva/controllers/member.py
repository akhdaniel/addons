# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson

class Member(http.Controller):


    @http.route('/mlm/member/invite/<model("res.partner"):member>', auth='user', website=True)
    def send_invitation(self, member, **kwargs):
        try:
            request.registry['res.partner'].action_invite(request.cr, SUPERUSER_ID, [member.id], request.context)
            message = "Invitation sent to %s." % (member.name)
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
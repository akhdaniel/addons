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



    def _cari_users_members(self, cr, uid, user_id, context=None):
        Users = request.registry['res.users']
        user = Users.browse(cr, uid, user_id, context=context)
        path = user.partner_id and user.partner_id.path
        partner_uid = user.partner_id and user.partner_id.id
        
        # if group mlm head network: can see all downlines
        gid = "vit_mlm_reiva.group_mlm_vp"
        if user.has_group( gid ):
            cond = "path_ltree <@ '%s'" % (path)
        else:
            cond="path_ltree ~ '%s.*{1,1}'" % (path)
            
        sql = "select id from res_partner where %s \
            or (path_ltree is null and sponsor_id = %d) or (path_ltree is null and parent_id = %d) \
            order by path_ltree" % (cond, partner_uid, partner_uid)
            
        cr.execute(sql)
        member_ids = cr.fetchall()
        return [x[0] for x in member_ids]

    def _cari_member_count_by_status(self, cr, uid, my_members, context=None):
        res = {'draft': 0, 'aktif': 0, 'open': 0, 'invited': 0, 'pre': 0,}
        for member in my_members:
            res[member.state] += 1
        return res
    
    @http.route('/mlm/member/list', auth='user', website=True)
    def list(self, **kw):
        lang = request.context['lang']
        Partners = http.request.env['res.partner']
        my_member_ids = self._cari_users_members(request.cr, SUPERUSER_ID, request.uid, request.context)
        my_members = Partners.search([('id', 'in', my_member_ids)])
        member_count_by_status = self._cari_member_count_by_status(request.cr, request.uid, my_members, request.context)
        return http.request.render('vit_mlm_website.member_list', {
            'members': my_members,
            'member_count_by_status': member_count_by_status,
            'lang': lang,
        
        })

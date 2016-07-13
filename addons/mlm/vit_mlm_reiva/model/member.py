from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

MEMBER_STATES = [('draft', 'Draft'), ('open', 'Verification'), ('reject', 'Rejected'),
                 ('aktif', 'Active'), ('nonaktif', 'Non Active'),
                 ('invited','Guest'), ('pre','Pre-registration')]

class member(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"


    _columns = {
        'state'			: fields.selection( MEMBER_STATES, 'Status',readonly= True,required=True),
    }

    def _get_default_parent(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        pid = user[0].partner_id.id or False
        return pid

    def _get_default_paket(self, cr, uid, context=None):

        pid = self.pool.get('mlm.paket').search(cr, uid, [('code','=','X')], context=context)
        if not pid:
            raise osv.except_osv(_('error'),_("No Package with Code X") )
        pid = pid[0]
        return pid

    _defaults = {
        'parent_id' : _get_default_parent,
        'paket_id' : _get_default_paket
    }


    def action_confirm(self, cr, uid, ids, context=None):
        return super(member, self).action_confirm(cr, uid, ids, context=context)

    def action_invite(self, cr, uid, ids, context=None):
        mtp = self.pool.get('email.template')
        mail_template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
           'vit_mlm_reiva',
           'email_template_invitation')
        for partner_id in ids:
            mtp.send_mail(cr, uid, mail_template_id[1], partner_id, force_send=True, context=context)

        self.action_confirm(cr, uid, ids, context=context)
        self.action_aktif(cr, uid, ids, context=context)
        self.write(cr, uid, ids[0], {
            'state': MEMBER_STATES[5][0]}, context=context)

        user_obj = self.pool.get('res.users')
        user_id = user_obj.search(cr, uid, [('partner_id','=',ids[0])], context=context)
        user_obj.action_reset_password(cr, uid, user_id, context=context)

    def action_preaktif(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': MEMBER_STATES[3][0]}, context=context)

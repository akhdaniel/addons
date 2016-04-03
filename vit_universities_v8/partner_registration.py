# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

is_confirm = """
Pendaftaran berhasil, data diri anda sudah terupdate dan masuk ke Sistem !
*) Silahkan cek di menu pembayaran kuliah untuk mengetahui tagihan uang pendaftaran anda
*) Gunakan nomor invoice sebagai ID tagihan untuk pembayaran via BNI
"""
not_confirm = """
Anda belum melakukan update data calon mahasiswa, silahkan klik tombol "Update Data" agar data diri anda masuk ke sistem !
"""

class partner_registration(models.Model):
    _name = 'partner.registration'
    _rec_name = 'no_reg'

    def _get_confirm_online(self, cr, uid, context=None):
        #import pdb;pdb.set_trace()
        user_obj             = self.pool.get('res.users')
        partner_id           = user_obj.browse(cr,1,uid).partner_id
        online_confirm       = partner_id.reg_online
        if online_confirm:
            return True
        return False

    def _get_reg_exist(self, cr, uid, context=None):
        user_obj             = self.pool.get('res.users')
        partner_id           = user_obj.browse(cr,1,uid).partner_id
        reg                  = partner_id.reg
        return reg

    def _get_inv_registation_paid(self, cr, uid, context=None):
        user_obj             = self.pool.get('res.users')
        inv_obj              = self.pool.get('account.invoice')
        partner_id           = user_obj.browse(cr,1,uid).partner_id
        reg                  = partner_id.reg
        origin               = 'Pendaftaran '+str(reg)
        inv_exist            = inv_obj.search(cr,1,[('origin','=',origin)])
        if inv_exist :
            inv_state = inv_obj.browse(cr,uid,inv_exist[0]).state
            if inv_state == 'paid' :
                return True
        return False

    def _get_tpa_done(self, cr, uid, context=None):
        user_obj             = self.pool.get('res.users')
        #survey_obj           = self.pool.get('survey.survey')
        answer_obj           = self.pool.get('survey.user_input')
        # tpa                  = survey_obj.search(cr,1,[('res_model','=','TPA')])
        # if tpa :        
        partner_id           = user_obj.browse(cr,1,uid).partner_id
        answer_exist         = answer_obj.search(cr,1,[('partner_id','=',partner_id.id),('state','=','done')])
        if answer_exist :
                return True
        return False

    def _get_manipulasi_skor(self, cr, uid, context=None):
        user_obj             = self.pool.get('res.users')

        answer_obj           = self.pool.get('survey.user_input')    
        partner_id           = user_obj.browse(cr,1,uid).partner_id
        answer_exist         = answer_obj.search(cr,1,[('partner_id','=',partner_id.id),('state','=','done')])
        if answer_exist :
            skor = answer_obj.browse(cr,1,answer_exist[0]).quizz_score
            if skor < 60 :
                skor = 60
            return skor
        return 0        

    no_reg              = fields.Char('No. Pendaftaran')
    confirm             = fields.Boolean('Confirm?')
    is_confirm_text     = fields.Text('Result',default=is_confirm)
    not_confirm_text    = fields.Text('Result',default=not_confirm)
    sudah_tpa           = fields.Boolean('Sudah TPA?')
    skor_manipulasi_tpa = fields.Float('Skor')
    registration_paid   = fields.Boolean('Sudah Bayar TPA?')

    _defaults = {
        'no_reg': _get_reg_exist,
        'confirm': _get_confirm_online,
        'registration_paid':_get_inv_registation_paid,
        'sudah_tpa':_get_tpa_done,
        'skor_manipulasi_tpa':_get_manipulasi_skor,
    }

    def action_start_survey_from_registration(self, cr, uid, ids, context=None):
        ''' Open the website page with the survey form '''
        survey_obj = self.pool.get('survey.survey')
        tpa = survey_obj.search(cr,1,[('res_model','=','TPA')])
        if not tpa :
            raise except_orm(_('Not Found !'), _("Data TPA belum ada, silahkan hubungi bagian akademik !"))
        trail = ""
        context = dict(context or {}, relative_url=True)
        if 'survey_token' in context:
            trail = "/" + context['survey_token']
        return {
            'type': 'ir.actions.act_url',
            'name': "Start TPA",
            'target': 'self',
            'url': survey_obj.read(cr, uid, tpa, ['public_url'], context=context)[0]['public_url'] + trail
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
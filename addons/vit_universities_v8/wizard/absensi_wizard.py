# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
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
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning as UserError

class absensi_wizard(models.TransientModel):
    _name = "absensi.wizard"

    tahun_akademik_id = fields.Many2one('academic.year', 'Tahun Akademik', required=True)
    semester_id = fields.Many2one('master.semester', 'Semester',domain="[('name','>',2)]",required=True)

    @api.multi
    def create_absensi(self):
        
        jadwal_obj          = self.env['master.jadwal']
        tahun_akademik_id   = self.tahun_akademik_id.id
        semester_id         = self.semester_id.id 

        jadwal_ids          = jadwal_obj.search([('is_active','=',True),('tahun_ajaran_id','=',tahun_akademik_id),('semester_id','=',semester_id)])
        if not jadwal_ids :
            raise UserError(_('Error! \
                                     Tidak ditemukan jadwal dengan parameter tersebut'))

        absensi_obj          = self.env['absensi']    
        attendee_ids = []
        for absen in jadwal_ids:
            # cek jika jadwal sudah ada dan sudah confirm
            absensi_exist = absensi_obj.search([('employee_id','=',absen.employee_id.id),
                                                ('semester_id','=',absen.semester_id.id),
                                                ('mata_kuliah_id','=',absen.mata_kuliah_id.id),
                                                ('tahun_ajaran_id','=',absen.tahun_ajaran_id.id),
                                                ('fakultas_id','=',absen.fakultas_id.id),
                                                ('prodi_id','=',absen.prodi_id.id),
                                                ('konsentrasi_id','=',absen.konsentrasi_id.id),])
            if not absensi_exist :
                #import pdb;pdb.set_trace()
                self._cr.execute("""select rp.id from res_partner rp
                                left join operasional_krs_mahasiswa okm on okm.partner_id = rp.id
                                left join operasional_krs_detail_mahasiswa okdm on okm.id = okdm.krs_mhs_id 
                                where okdm.jadwal_id = %s"""%(absen.id,))
                dpt = self._cr.fetchall()     
                if dpt :
                    mhs_ids = map(lambda x: x[0], dpt)

                    res = []
                    for ms in mhs_ids:
                        res.append([0,0,{'partner_id': ms}])                       

                    absensi_obj.create({'employee_id'       :absen.employee_id.id,
                                        'semester_id'       :absen.semester_id.id,
                                        'mata_kuliah_id'    :absen.mata_kuliah_id.id,
                                        'tahun_ajaran_id'   :absen.tahun_ajaran_id.id,
                                        'fakultas_id'       :absen.fakultas_id.id,
                                        'prodi_id'          :absen.prodi_id.id,
                                        'konsentrasi_id'    :absen.konsentrasi_id.id,
                                        'state'             :'draft',
                                        'absensi_ids'       :res,
                                        'absensi_nilai_ids' :res})

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

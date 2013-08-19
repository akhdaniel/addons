# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################
# Generated by the OpenERP plugin for Dia !
from osv import fields,osv
SUPPLIER_STATES =[('draft','Baru'),
    ('verify','Verify'),('active','Active'),
    ('reject','Reject'), ('blacklist','Blacklisted')]

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    def action_draft(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':SUPPLIER_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':SUPPLIER_STATES[1][0]},context=context)

    def action_approve(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':SUPPLIER_STATES[2][0]},context=context)

    def action_reject(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':SUPPLIER_STATES[3][0]},context=context)

    def action_blacklist(self,cr,uid,ids,context=None): 
        return self.write(cr,uid,ids,{'state':SUPPLIER_STATES[4][0]},context=context)    

    _columns = {
        'no': fields.char('Nomor', size=100,readonly=True),

        #'businessType' : fields.many2one('eproc.business_type','Business Type'),
        #'subBusinessType' : fields.many2one('eproc.sub_business_type','Sub Business Type'),
        'city':fields.many2one('eproc.city','City'),
        'contactPerson' : fields.char('Contact Person',size=300),
        'contactPersonEmail' : fields.char('Contact Person Email',size=300),
        'contactPersonAddress' : fields.char('Contact Person Address',size=300),
        'contactPersonMobileNo' : fields.char('Contact Person Mobile No',size=300),
        
        'defaultWhtRate' : fields.char('Default WHT Rate',size=300),
        
        'bankName' : fields.char('Bank Name',size=300),
        'bankAccountNo' : fields.char('Bank Account No',size=300),
        'bankAccountName' : fields.char('Bank Account Name',size=300),
        'bankAccountType' : fields.char('Bank Account Type',size=300),

      #  'state' : fields.selection(SUPPLIER_STATES,'Status', readonly=True ),

        'ijin_usaha_ids':  fields.one2many('eproc.ijin_usaha','partner_id','Ijin Usaha'),
        'pemilik_ids':     fields.one2many('eproc.pemilik','partner_id','Pemilik Perusahaan'),
        'pengurus_ids':    fields.one2many('eproc.pengurus','partner_id','Pengurus Perusahaan'),
        'tenaga_ahli_ids': fields.one2many('eproc.tenaga_ahli','partner_id','Tenaga Ahli'),
        'pengalaman_ids':  fields.one2many('eproc.pengalaman','partner_id','Pengalaman'),
        'peralatan_ids':   fields.one2many('eproc.peralatan','partner_id','Peralatan'),
        'neraca_ids':      fields.one2many('eproc.neraca','partner_id','Neraca'),
        'bukti_pajak_ids': fields.one2many('eproc.bukti_pajak','partner_id','Bukti Pajak'),
        'akta_perusahaan_ids': fields.one2many('eproc.akta_perusahaan','partner_id','Akta Perusahaan'),
        'user_id': fields.many2one('res.users','Registered By')
    }
    _defaults = {
       # 'state': SUPPLIER_STATES[0][0],
        'user_id': lambda obj, cr, uid, context: uid,
        'no': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'res.partner'),
        }
    
res_partner()


class eproc_business_type(osv.osv):
    _name = 'eproc.business_type'

    _columns = {
        'name': fields.char('Tipe Bisnis', size=300),
        'sub_business_type': fields.one2many('eproc.sub_business_type','business_type','Sub Tipe Bisnis')
    }
eproc_business_type()

class eproc_sub_business_type(osv.osv):
    _name = 'eproc.sub_business_type'
    
    _columns = {
        'name': fields.char('Sub Tipe Bisnis', size=300),
        'business_type': fields.many2one('eproc.business_type','Tipe Bisnis')
    }
eproc_sub_business_type()


class eproc_city(osv.osv):
    _name = 'eproc.city'
    _columns = {
        'name': fields.char('Nama', size=300),
        'state_id': fields.many2one('res.country.state')
    }
eproc_city()


class eproc_status(osv.osv):
    _name = 'eproc.status'
    _columns = {
        'name': fields.char('Nama',size=300),
    }
eproc_status()



class eproc_ijin_usaha(osv.osv):
    _rec_name = 'nomor'
    _name = 'eproc.ijin_usaha'
    _columns = {
        'masterIjinUsaha' : fields.many2one('eproc.master_ijin_usaha','Ijin Usaha'), 
        'nomor' : fields.char('Nomor',size=100),
        'berlakuSampai' : fields.date('Berlaku Sampai'),
        'instansiPemberi' : fields.char('Instansi Pemberi', size=100),
        'filename' : fields.binary('Bukti Dokumen'),
        'kualifikasi':fields.many2one('eproc.master_kualifikasi','Kualifikasi'),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_ijin_usaha()

class eproc_pemilik(osv.osv):
    _name = 'eproc.pemilik'
    _columns = {
        'name': fields.char('Nama',size=300),
        'ktp' : fields.char('KTP',size=300),
        'alamat' : fields.char('Alamat',size=300),
        'saham' : fields.integer('Jumlah Lembar Saham'),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_pemilik()

class eproc_pengurus(osv.osv):
    _name = 'eproc.pengurus'
    _columns = {
        'name': fields.char('Nama',size=300),
        'ktp' : fields.char('KTP',size=300),
        'alamat' : fields.char('Alamat',size=300),
        'jabatan': fields.char('Jabatan',size=300),
        'mulai' : fields.date('Tanggal Mulai'),
        'sampai' :fields.date('Tanggal Selesai'),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_pengurus()

class eproc_tenaga_ahli(osv.osv):
    _name = 'eproc.tenaga_ahli'
    _columns = {
        'name': fields.char('Nama',size=300),
        'partner_id': fields.many2one('res.partner','Supplier'),
        'tanggalLahir' : fields.date('Tanggal Lahir'),
        'pendidikanTerakhir' : fields.char('Pendidikan Terakhir',size=300),
        'tahunPengalamanKerja' : fields.char('Tahun Pengalaman Kerja',size=4),
        'profesi' : fields.char('Profesi',size=300), 
        'email' : fields.char('email',size=300),
        'wargaNegara' : fields.char('Warga Negara',size=300),
        'jabatan' : fields.char('Jabatan',size=300),
        'statusPegawai' : fields.char('Status Pegawai',size=300),

        'pengalaman_kerja' : fields.one2many('eproc.tenaga_ahli_pengalaman_kerja','tahun','Pengalaman Kerja'),
        'pendidikan' : fields.one2many('eproc.tenaga_ahli_pendidikan','tenaga_ahli','Pendidikan yang Relevan'),
        'sertifikat' : fields.one2many('eproc.tenaga_ahli_sertifikat','tenaga_ahli','Sertifikat Pendukung'),
        'bahasa' : fields.one2many('eproc.tenaga_ahli_bahasa','tenaga_ahli','Bahasa Asing Yang Dikuasai'),
    }
eproc_tenaga_ahli()

class eproc_tenaga_ahli_pengalaman_kerja(osv.osv):
    _name = 'eproc.tenaga_ahli_pengalaman_kerja'
    _columns = {
        'name': fields.char('Nama',size=300),
        'tahun': fields.integer('Tahun Pengalaman Kerja',size=4),
        'tenaga_ahli': fields.many2one('eproc.tenaga_ahli',''),
    }
eproc_tenaga_ahli_pengalaman_kerja()


class eproc_tenaga_ahli_pendidikan(osv.osv):
    _name = 'eproc.tenaga_ahli_pendidikan'
    _columns = {
        'name': fields.char('Nama',size=300),
        'tahun': fields.char('Tahun Lulus',size=4),
        'tenaga_ahli': fields.many2one('eproc.tenaga_ahli',''),
    }
eproc_tenaga_ahli_pendidikan()


class eproc_tenaga_ahli_sertifikat(osv.osv):
    _name = 'eproc.tenaga_ahli_sertifikat'
    _columns = {
        'name': fields.char('Nama',size=300),
        'tahun': fields.char('Tahun',size=4),
        'tenaga_ahli': fields.many2one('eproc.tenaga_ahli',''),
    }
eproc_tenaga_ahli_sertifikat()


class eproc_tenaga_ahli_bahasa(osv.osv):
    _name = 'eproc.tenaga_ahli_bahasa'
    _columns = {
        'name': fields.char('Nama',size=300),
        'tenaga_ahli': fields.many2one('eproc.tenaga_ahli',''),
    }
eproc_tenaga_ahli_bahasa()

class eproc_peralatan(osv.osv):
    _name = 'eproc.peralatan'
    _columns = {
        'name' : fields.char('Nama Peralatan',size=200),
        'jumlah' : fields.integer('Jumlah',size=200),
        'kapasitas' : fields.char('Kapasitas',size=200),
        'merk' : fields.char('Merk',size=200),
        'type' : fields.char('Type',size=200),
        'tahunPembuatan' : fields.char('Tahun  Pembuatan',size=4),
        'kondisi' : fields.char('Kondisi',size=200),
        'lokasiSekarang' : fields.char('Lokasi  Sekarang',size=200),
        'buktiKepemilikan' : fields.char('Bukti Kepemilikan',size=200),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_peralatan()

class eproc_pengalaman(osv.osv):
    _name = 'eproc.pengalaman'
    _columns = {
        'name' : fields.char('Nama Pekerjaan',size=200),
        'lokasi' : fields.char('Lokasi',size=200),
        'instansiPemberi' : fields.char('Instansi Pemberi',size=200),
        'alamatInstansi' : fields.char('Alamat Instansi',size=200),
        'telponInstansi' : fields.char('Telpon Instansi',size=200),
        'tanggalKontrak' : fields.date('Tanggal Kontrak',size=200),
        'selesaiKontrak' : fields.date('Selesai Kontrak',size=200),
        'nomorKontrak' : fields.char('Nomor Kontrak',size=200),
        'nilai' : fields.integer('Nilai',size=200),
        'tanggalPelaksanaan' : fields.date('Tanggal Pelaksanaan'),
        'tanggalSerahTerima' : fields.date('Tanggal Serah Terima'),
        'prosentasePelaksanaan' : fields.float('Persentase Pelaksanaan'),

        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_pengalaman()


class eproc_neraca(osv.osv):
    _rec_name = 'tahun'
    _name = 'eproc.neraca'
    _columns = {
        'tahun' : fields.char('Tahun'),
        'tanggal' : fields.date('Tanggal'),
        'aktivaTetap' : fields.float('Aktiva Tetap'),
        'aktivaLancar' : fields.float('Aktiva Lancar'),
        'aktivaLainnya' : fields.float('Aktiva Lainnya'),
        'hutangJangkaPanjang' : fields.float('Hutang Jangka Panjang'),
        'hutangJangkaPendek' : fields.float('Hutang Jangka Pendek'),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_neraca()

class eproc_bukti_pajak(osv.osv):
    _rec_name = 'nomor'
    _name = 'eproc.bukti_pajak'
    _columns = {
        'masterPajak' : fields.many2one('eproc.master_pajak','Master Pajak'),
        'nomor' : fields.char('Nomor',size=200),
        'tanggal' : fields.date('Tanggal'),
        'masaTahun' : fields.char('Masa Tahun',size=4),
        'masaBulan' : fields.char('Masa Bulan',size=200),
        'filename' : fields.binary('Filename',size=200,required=True),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_bukti_pajak()

class eproc_master_pajak(osv.osv):
    _name = 'eproc.master_pajak'
    _columns = {
        'name': fields.char('Nama',size=300),
    }
eproc_master_pajak()


class eproc_akta_perusahaan(osv.osv):
    _rec_name = 'nomor'
    _name = 'eproc.akta_perusahaan'
    _columns = {
        'nomor' : fields.char('Nomor',size=200),
        'tanggalSurat' : fields.date('Tanggal Surat',size=200),
        'notaris' : fields.char('Notaris',size=200),
        'dokumenName' : fields.char('Nama Dokumen',size=200),
        'dokumenFileName' : fields.binary('File Dokumen',size=200),
        'jenis' : fields.selection([('pendirian','Pendirian'),('perubahan', 'Perubahan')], 'Jenis Akta'),
        'partner_id': fields.many2one('res.partner','Supplier'),
    }
eproc_akta_perusahaan()


class eproc_master_ijin_usaha(osv.osv):
    _name = 'eproc.master_ijin_usaha'
    _columns = {
        'name': fields.char('Nama',size=300),
    }
eproc_master_ijin_usaha()


class eproc_master_kualifikasi(osv.osv):
    _name = 'eproc.master_kualifikasi'
    _columns = {
        'name': fields.char('Nama',size=300),
    }
eproc_master_kualifikasi()


from openerp.osv import fields, osv
from openerp import tools
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

import sets
import logging
_logger = logging.getLogger(__name__)

class res_partner_calon_mhs (osv.osv):
	_name = "res.partner.calon.mhs"

	_columns = {
		'name'				:fields.char('Nama',size=160),
		'reg'				:fields.char('No. Pendaftaran',readonly=True,size=34),
		'jenis_kelamin'		:fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
		'tempat_lahir'		:fields.char('Tempat Lahir'),
		'tanggal_lahir'		:fields.date('Tanggal Lahir'),                  
		'fakultas_id'		:fields.many2one('master.fakultas',string='Fakultas',),
		'jurusan_id'		:fields.many2one('master.jurusan',string='Jurusan',domain="[('fakultas_id','=',fakultas_id)]"),
		'prodi_id'			:fields.many2one('master.prodi',string='Program Studi',domain="[('jurusan_id','=',jurusan_id)]"),
		'konsentrasi_id' 	:fields.many2one('master.konsentrasi','Konsentrasi'),
		'tahun_ajaran_id'	:fields.many2one('academic.year',string='Tahun Akademik'),               
		'tgl_lulus'			:fields.date('Tanggal Lulus'),
		'no_formulir'		:fields.char('No Formulir Ujian'),
		'tgl_ujian'			:fields.date('Tanggal Ujian'),
		'nilai_ujian'		:fields.float('Nilai Ujian'),
		'batas_nilai'		:fields.float('Batas Nilai Kelulusan',readonly=True),
		'status_pernikahan'	:fields.selection([('belum','Belum Menikah'),('menikah','Menikah'),('janda','Janda'),('duda','Duda')],'Status Pernikahan'),
		'agama'				:fields.selection([('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')],'Agama'),
		'tgl_daftar'		:fields.date('Tanggal Daftar',readonly=True),
		'nilai_beasiswa'	:fields.float('Rata-Rata Nilai SMA/Sederajat'),
		'is_beasiswa' 		:fields.boolean('Penerima Beasiswa',readonly=True),
		'user_id'			:fields.many2one('res.users','User',readonly=True),
		'date_move'			:fields.date('Date Move',readonly=True),
		'state'				:fields.selection([('lulus','Lulus'),('gagal','Gagal')],'Status',readonly=True),
				}

res_partner_calon_mhs()



class res_partner(osv.osv):
	_inherit = 'res.partner'

	def action_move_calon(self, cr, uid, context=None):
		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_action_move_calon(cr, uid, active_ids, context)


	def actual_action_move_calon(self, cr, uid, ids, context=None):
		calon_obj = self.pool.get('res.partner.calon.mhs')
		konv_obj = self.pool.get('akademik.konversi')
		inv_obj = self.pool.get('account.invoice')
		usr_obj = self.pool.get('res.users')
		i = len(ids)
		for res in self.browse(cr,uid, ids, context):
			if res.status_mahasiswa != 'calon':
				raise osv.except_osv(_('Error !'),_("Data dengan nama %s berstatus %s, yang dapat di pindah hanya data yang berstatus calon mahasiswa saja!")%(res.name,res.status_mahasiswa) )
			calon_obj.create(cr,uid,{'reg'				:res.reg,
									'name'				:res.name,
									'jenis_kelamin'		:res.jenis_kelamin or False,
									'tempat_lahir'		:res.tempat_lahir or False,
									'tanggal_lahir'		:res.tanggal_lahir or False,                  
									'fakultas_id'		:res.fakultas_id.id,
									'prodi_id'			:res.prodi_id.id,
									'tahun_ajaran_id'	:res.tahun_ajaran_id.id,                
									'tgl_lulus'			:res.tgl_lulus or False,
									'no_formulir'		:res.no_formulir or False,
									'tgl_ujian'			:res.tgl_ujian or False,
									'nilai_ujian'		:res.nilai_ujian or False,
									'batas_nilai'		:res.batas_nilai or False,
									'status_pernikahan'	:res.status_pernikahan or False,
									'agama'				:res.agama or False,
									'tgl_daftar'		:res.tgl_daftar or False,
									'nilai_beasiswa'	:res.nilai_beasiswa or False,
									'is_beasiswa' 		:res.is_beasiswa,
									'konsentrasi_id'	:res.konsentrasi_id.id,
									'date_move'			:time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
									'user_id'			:uid,
									'state'				:'gagal'},
									context=context)
			# karena terlalu banyak relasi jadi ga bisa sembarangan di hapus (relasi ke konversi, keuangan, user, dll)
			mhs_konv_exist = konv_obj.search(cr,uid,[('partner_id','=',res.id)],context=context)
			if mhs_konv_exist :
				raise osv.except_osv(_('Error !'),_("Data dengan nama %s , tidak bisa di move karena ada proses di konversi!")%(res.name) )
			mhs_inv_exist = inv_obj.search(cr,uid,[('partner_id','=',res.id)],context=context)
			if mhs_inv_exist :
				raise osv.except_osv(_('Error !'),_("Data dengan nama %s , tidak bisa di move karena ada proses di Keuangan/Invoice!")%(res.name) )
			# karena terlalu banyak relasi jadi ga bisa sembarangan di hapus (relasi ke konversi, keuangan, user, dll)
			# self.unlink(cr,uid,[res.id],context=context)		
			self.write(cr,uid,res.id,{'active':False},context=context)							
			cr.commit()
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_universities_v8', 'partner_tree_view3')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s partners moved' % (i) )}, 
			'name' : _('Calon Mahasiswa (Temp)'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'res.partner',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{}",
			'nodestroy': False,
		}
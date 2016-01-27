from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class absensi(osv.osv):
	_name = 'absensi'

	def create(self, cr, uid, vals, context=None):
		ajaran = vals['tahun_ajaran_id']
		fakultas = vals['fakultas_id']
		prodi = vals['prodi_id']
		semester = vals['semester_id']	
		matakuliah = vals['mata_kuliah_id']	
		jad_obj = self.pool.get('absensi')
		jad_id = jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),
			('semester_id','=',semester),
			('mata_kuliah_id','=',matakuliah)])

		if jad_id != [] :
			raise osv.except_osv(_('Error!'), _('Absensi tersebut sudah ada!'))

		return super(absensi, self).create(cr, uid, vals, context=context)   

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if context is None:
			context = {}
		ids = []
		if name:
			ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
		if not ids:
			ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
		return self.name_get(cr, user, ids, context)

	_columns = {
		'name'  : fields.char('Kode',size=30,required=True,readonly=True, states={'open': [('readonly', False)]}),
		'mata_kuliah_id' :fields.many2one('master.matakuliah',string='Matakuliah',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'state':fields.selection([('open','Open'),('close','Closed')],'State',readonly=True, states={'open': [('readonly', False)]}),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,readonly=True, states={'open': [('readonly', False)]}), 
		'employee_id' :fields.many2one('hr.employee','Dosen', domain="[('is_dosen','=',True)]",required=True,readonly=True, states={'open': [('readonly', False)]}),
		'sesi':fields.integer('Total Sesi',required=True,readonly=True, states={'open': [('readonly', False)]}),
		
		'kurikulum_id':fields.many2one('master.kurikulum',"Kurikulum",readonly=True, states={'open': [('readonly', False)]}),
		'absensi_ids' : fields.one2many('absensi.detail','absensi_id','Mahasiswa',readonly=True, states={'open': [('readonly', False)]}),

			}
			
	_defaults= {
		'state':'open',

		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'absensi'), 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode Absensi tidak boleh sama')]

	def open_absensi(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'open'},context=context)
			for det in ct.absensi_ids:
				self.pool.get('absensi.detail').write(cr,uid,det.id,{'state':'open'},context=context)
		return True	

	def close_absensi(self,cr,uid,ids,context=None):
		krs_obj = self.pool.get('operasional.krs')
		for ct in self.browse(cr,uid,ids):
			tahun_ajaran = ct.tahun_ajaran_id.id
			fakultas = ct.fakultas_id.id
			prodi = ct.prodi_id.id
			semester = ct.semester_id.id
			matakuliah = ct.mata_kuliah_id.id
			self.write(cr,uid,ct.id,{'state':'close'},context=context)
			for det in ct.absensi_ids:
				mahasiswa = det.partner_id.id
				tugas = det.tugas
				uts   = det.uts
				uas   = det.uas
				#import pdb;pdb.set_trace()
				s1_h = 0 #H
				s1_s = 0 #sakit
				s1_a = 0 #alpha
				if det.absensi_1 == 'H':
					s1_h = 1
				elif det.absensi_1 == 'S':
					s1_s = 1
				else:
					s1_a = 1

				s2_h = 0 #H
				s2_s = 0 #sakit
				s2_a = 0 #alpha
				if det.absensi_2 == 'H':
					s2_h = 1
				elif det.absensi_2 == 'S':
					s2_s = 1
				else:
					s2_a = 1

				s3_h = 0 #H
				s3_s = 0 #sakit
				s3_a = 0 #alpha
				if det.absensi_3 == 'H':
					s3_h = 1
				elif det.absensi_3 == 'S':
					s3_s = 1
				else:
					s3_a = 1

				s4_h = 0 #H
				s4_s = 0 #sakit
				s4_a = 0 #alpha
				if det.absensi_4 == 'H':
					s4_h = 1
				elif det.absensi_4 == 'S':
					s4_s = 1
				else:
					s4_a = 1

				s5_h = 0 #H
				s5_s = 0 #sakit
				s5_a = 0 #alpha
				if det.absensi_5 == 'H':
					s5_h = 1
				elif det.absensi_5 == 'S':
					s5_s = 1
				else:
					s5_a = 1

				s6_h = 0 #H
				s6_s = 0 #sakit
				s6_a = 0 #alpha
				if det.absensi_6 == 'H':
					s6_h = 1
				elif det.absensi_6 == 'S':
					s6_s = 1
				else:
					s6_a = 1

				s6_h = 0 #H
				s6_s = 0 #sakit
				s6_a = 0 #alpha
				if det.absensi_6 == 'H':
					s6_h = 1
				elif det.absensi_6 == 'S':
					s6_s = 1
				else:
					s6_a = 1

				s6_h = 0 #H
				s6_s = 0 #sakit
				s6_a = 0 #alpha
				if det.absensi_6 == 'H':
					s6_h = 1
				elif det.absensi_6 == 'S':
					s6_s = 1
				else:
					s6_a = 1

				s7_h = 0 #H
				s7_s = 0 #sakit
				s7_a = 0 #alpha
				if det.absensi_7 == 'H':
					s7_h = 1
				elif det.absensi_7 == 'S':
					s7_s = 1
				else:
					s7_a = 1

				s8_h = 0 #H
				s8_s = 0 #sakit
				s8_a = 0 #alpha
				if det.absensi_8 == 'H':
					s8_h = 1
				elif det.absensi_8 == 'S':
					s8_s = 1
				else:
					s8_a = 1

				s9_h = 0 #H
				s9_s = 0 #sakit
				s9_a = 0 #alpha
				if det.absensi_9 == 'H':
					s9_h = 1
				elif det.absensi_9 == 'S':
					s9_s = 1
				else:
					s9_a = 1

				s10_h = 0 #H
				s10_s = 0 #sakit
				s10_a = 0 #alpha
				if det.absensi_10 == 'H':
					s10_h = 1
				elif det.absensi_10 == 'S':
					s10_s = 1
				else:
					s10_a = 1

				s11_h = 0 #H
				s11_s = 0 #sakit
				s11_a = 0 #alpha
				if det.absensi_11 == 'H':
					s11_h = 1
				elif det.absensi_11 == 'S':
					s11_s = 1
				else:
					s11_a = 1

				s12_h = 0 #H
				s12_s = 0 #sakit
				s12_a = 0 #alpha
				if det.absensi_12 == 'H':
					s12_h = 1
				elif det.absensi_12 == 'S':
					s12_s = 1
				else:
					s12_a = 1

				s13_h = 0 #H
				s13_s = 0 #sakit
				s12_a = 0 #alpha
				if det.absensi_13 == 'H':
					s13_h = 1
				elif det.absensi_13 == 'S':
					s13_s = 1
				else:
					s13_a = 1

				s13_h = 0 #H
				s13_s = 0 #sakit
				s13_a = 0 #alpha
				if det.absensi_13 == 'H':
					s13_h = 1
				elif det.absensi_13 == 'S':
					s13_s = 1
				else:
					s13_a = 1

				s14_h = 0 #H
				s14_s = 0 #sakit
				s14_a = 0 #alpha
				if det.absensi_14 == 'H':
					s14_h = 1
				elif det.absensi_14 == 'S':
					s14_s = 1
				else:
					s14_a = 1

				s15_h = 0 #H
				s15_s = 0 #sakit
				s15_a = 0 #alpha
				if det.absensi_15 == 'H':
					s15_h = 1
				elif det.absensi_15 == 'S':
					s15_s = 1
				else:
					s15_a = 1

				s16_h = 0 #H
				s16_s = 0 #sakit
				s16_a = 0 #alpha
				if det.absensi_16 == 'H':
					s16_h = 1
				elif det.absensi_16 == 'S':
					s16_s = 1
				else:
					s16_a = 1

				s17_h = 0 #H
				s17_s = 0 #sakit
				s17_a = 0 #alpha
				if det.absensi_17 == 'H':
					s17_h = 1
				elif det.absensi_17 == 'S':
					s17_s = 1
				else:
					s17_a = 1

				s18_h = 0 #H
				s18_s = 0 #sakit
				s18_a = 0 #alpha
				if det.absensi_18 == 'H':
					s18_h = 1
				elif det.absensi_18 == 'S':
					s18_s = 1
				else:
					s18_a = 1

				s19_h = 0 #H
				s19_s = 0 #sakit
				s19_a = 0 #alpha
				if det.absensi_19 == 'H':
					s19_h = 1
				elif det.absensi_19 == 'S':
					s19_s = 1
				else:
					s19_a = 1

				s20_h = 0 #H
				s20_s = 0 #sakit
				s20_a = 0 #alpha
				if det.absensi_20 == 'H':
					s20_h = 1
				elif det.absensi_20 == 'S':
					s20_s = 1
				else:
					s20_a = 1

				s21_h = 0 #H
				s21_s = 0 #sakit
				s21_a = 0 #alpha
				if det.absensi_21 == 'H':
					s21_h = 1
				elif det.absensi_21 == 'S':
					s21_s = 1
				else:
					s21_a = 1																																																																																										

				s22_h = 0 #H
				s22_s = 0 #sakit
				s22_a = 0 #alpha
				if det.absensi_22 == 'H':
					s22_h = 1
				elif det.absensi_22 == 'S':
					s22_s = 1
				else:
					s22_a = 1

				s23_h = 0 #H
				s23_s = 0 #sakit
				s23_a = 0 #alpha
				if det.absensi_23 == 'H':
					s23_h = 1
				elif det.absensi_23 == 'S':
					s23_s = 1
				else:
					s23_a = 1

				s24_h = 0 #H
				s24_s = 0 #sakit
				s24_a = 0 #alpha
				if det.absensi_24 == 'H':
					s24_h = 1
				elif det.absensi_24 == 'S':
					s24_s = 1
				else:
					s24_a = 1

				s24_h = 0 #H
				s24_s = 0 #sakit
				s24_a = 0 #alpha
				if det.absensi_24 == 'H':
					s24_h = 1
				elif det.absensi_24 == 'S':
					s24_s = 1
				else:
					s24_a = 1

				s25_h = 0 #H
				s25_s = 0 #sakit
				s25_a = 0 #alpha
				if det.absensi_25 == 'H':
					s25_h = 1
				elif det.absensi_25 == 'S':
					s25_s = 1
				else:
					s25_a = 1

				s26_h = 0 #H
				s26_s = 0 #sakit
				s26_a = 0 #alpha
				if det.absensi_26 == 'H':
					s26_h = 1
				elif det.absensi_26 == 'S':
					s26_s = 1
				else:
					s26_a = 1

				s27_h = 0 #H
				s27_s = 0 #sakit
				s27_a = 0 #alpha
				if det.absensi_27 == 'H':
					s27_h = 1
				elif det.absensi_27 == 'S':
					s27_s = 1
				else:
					s27_a = 1

				s28_h = 0 #H
				s28_s = 0 #sakit
				s28_a = 0 #alpha
				if det.absensi_28 == 'H':
					s28_h = 1
				elif det.absensi_28 == 'S':
					s28_s = 1
				else:
					s28_a = 1

				s29_h = 0 #H
				s29_s = 0 #sakit
				s29_a = 0 #alpha
				if det.absensi_29 == 'H':
					s29_h = 1
				elif det.absensi_29 == 'S':
					s29_s = 1
				else:
					s29_a = 1

				s30_h = 0 #H
				s30_s = 0 #sakit
				s30_a = 0 #alpha
				if det.absensi_30 == 'H':
					s30_h = 1
				elif det.absensi_30 == 'S':
					s30_s = 1
				else:
					s30_a = 1

				# total_hadir = s1_h + s2_h + s3_h + s4_h + s5_h + s6_h + s7_h + s8_h + s9_h + s10_h + s11_h + s12_h + s13_h + s14_h + s15_h + s16_h + s17_h + s18_h + s19_h + s20_h + s21_h + s22_h + s23_h + s24_h + s25_h + s26_h + s27_h + s28_h + s29_h + s30_h	
				# total_izin = s1_s + s2_s + s3_s + s4_s + s5_s + s6_s + s7_s + s8_s + s9_s + s10_s +	s11_s + s12_s + s13_s + s14_s + s15_s + s16_s + s17_s + s18_s + s19_s + s20_s + s21_s + s22_s + s23_s + s24_s + s25_s + s26_s + s27_s + s28_s + s29_s + s20_s
				# total_alpha = s1_a + s2_a + s3_a + s4_a + s5_a + s6_a + s7_a + s8_a + s9_a + s10_a + s11_a + s12_a + s13_a + s14_a + s15_a + s16_a + s17_a + s18_a + s19_a + s20_a + s21_a + s22_a + s23_a + s24_a + s25_a + s26_a + s27_a + s28_a + s29_a + s30_a			 		  																																																																
				
				total_hadir = s1_h + s2_h + s3_h + s4_h + s5_h + s6_h + s7_h + s8_h + s9_h + s10_h + s11_h + s12_h + s13_h + s14_h
				total_izin = s1_s + s2_s + s3_s + s4_s + s5_s + s6_s + s7_s + s8_s + s9_s + s10_s +	s11_s + s12_s + s13_s + s14_s 
				total_alpha = s1_a + s2_a + s3_a + s4_a + s5_a + s6_a + s7_a + s8_a + s9_a + s10_a + s11_a + s12_a + s13_a + s14_a		 		  																																																																


				krs_exist = krs_obj.search(cr,uid,[('tahun_ajaran_id','=',tahun_ajaran),
													('fakultas_id','=',fakultas),
													('prodi_id','=',prodi),
													('semester_id','=',semester),
													('partner_id','=',mahasiswa)],context=context)
				if krs_exist :
					browse_krs = krs_obj.browse(cr,uid,krs_exist[0])
					for dtl in browse_krs.krs_detail_ids:
						if dtl.mata_kuliah_id.id == matakuliah :
							self.pool.get('operasional.krs_detail').write(cr,uid,dtl.id,{'hadir'	:total_hadir,
																						 'izin'		:total_izin,
																						 'alpha'	:total_alpha,
																						 'tugas'	:tugas,
																						 'uts'		:uts,
																						 'uas'		:uas,})
							break

				self.pool.get('absensi.detail').write(cr,uid,det.id,{'state':'close'},context=context)			
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in un active"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state == 'close':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus open'))
		return super(absensi, self).unlink(cr, uid, ids, context=context)

	def onchange_kelas(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, prodi_id,kelas_id,context=None):

		results = {}
		if not kelas_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','Mahasiswa'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('fakultas_id','=',fakultas_id),
			('prodi_id','=',prodi_id),
			('kelas_id','=',kelas_id)], context=context)

		#import pdb;pdb.set_trace()
		if par_ids :
			res = []
			for mhs in par_ids:
				res.append([0,0,{'partner_id': mhs,'state':'open'}])	
			results = {
				'value' : {
					'absensi_ids' : res,
				}
			}
		return results

absensi()


class absensi_detail(osv.osv):
	_name = "absensi.detail"

	_columns = {
		'absensi_id' 	: fields.many2one('absensi','Jadwal'),
		'partner_id' 	: fields.many2one('res.partner','Mahasiswa',domain="[('status_mahasiswa','=','Mahasiswa')]",required=True),
		'absensi_1'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'1'),
		'absensi_2'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'2'),
		'absensi_3'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'3'),
		'absensi_4'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'4'),
		'absensi_5'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'5'),
		'absensi_6'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'6'),
		'absensi_7'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'7'),
		'absensi_8'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'8'),
		'absensi_9'		:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'9'),
		'absensi_10'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'10'),
		'absensi_11'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'11'),
		'absensi_12'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'12'),
		'absensi_13'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'13'),
		'absensi_14'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'14'),
		'absensi_15'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'15'),
		'absensi_16'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'16'),
		'absensi_17'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'17'),
		'absensi_18'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'18'),
		'absensi_19'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'19'),
		'absensi_20'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'20'),
		'absensi_21'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'21'),
		'absensi_22'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'22'),
		'absensi_23'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'23'),
		'absensi_24'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'24'),
		'absensi_25'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'25'),
		'absensi_26'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'26'),
		'absensi_27'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'27'),
		'absensi_28'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'28'),
		'absensi_29'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'29'),
		'absensi_30'	:fields.selection([('H','Hadir'),('S','Izin'),('A','Alpha')],'30'),
		'tugas'			:fields.float('Tugas'),
		'uts'			:fields.float('UTS'),
		'uas'			:fields.float('UAS'),		
		'note'			:fields.char('Ket.'),
		'state':fields.selection([('open','Open'),('close','Close')],'State'),
	}
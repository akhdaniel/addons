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
		konsentrasi = vals['konsentrasi_id']
		semester = vals['semester_id']	
		matakuliah = vals['mata_kuliah_id']	
		jad_obj = self.pool.get('absensi')
		jad_id = jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
										('fakultas_id','=',fakultas),
										('prodi_id','=',prodi),
										('konsentrasi_id','=',konsentrasi),
										('semester_id','=',semester),
										('mata_kuliah_id','=',matakuliah)])

		if jad_id != [] :
			raise osv.except_osv(_('Error!'), _('Absensi tersebut sudah ada!'))

		return super(absensi, self).create(cr, uid, vals, context=context)   

	def write(self, cr, uid, ids, vals, context=None):
		if context is None:
			context = {}
		#import pdb;pdb.set_trace()
		if 'absensi_ids' in vals:
			absen1 = False ; absen2 = False ; absen3 = False ; absen4 = False ; absen5 = False ; absen6 = False ; absen7 = False
			absen8 = False ; absen9 = False ; absen10 = False ; absen11 = False ; absen12 = False ; absen13 = False ; absen14 = False
			for absen in vals['absensi_ids']:
				if absen[2] : # True
					if 'absensi_1' in absen[2] :
						absen1 = str(datetime.now())
					if 'absensi_2' in absen[2] :
						absen2 = str(datetime.now())
					if 'absensi_3' in absen[2] :
						absen3 = str(datetime.now())
					if 'absensi_4' in absen[2] :
						absen4 = str(datetime.now())
					if 'absensi_5' in absen[2] :
						absen5 = str(datetime.now())
					if 'absensi_6' in absen[2] :
						absen6 = str(datetime.now())
					if 'absensi_7' in absen[2] :
						absen7 = str(datetime.now())
					if 'absensi_8' in absen[2] :
						absen8 = str(datetime.now())	
					if 'absensi_9' in absen[2] :
						absen9 = str(datetime.now())
					if 'absensi_10' in absen[2] :
						absen10 = str(datetime.now())
					if 'absensi_11' in absen[2] :
						absen11 = str(datetime.now())
					if 'absensi_12' in absen[2] :
						absen12 = str(datetime.now())												
					if 'absensi_13' in absen[2] :
						absen13 = str(datetime.now())
					if 'absensi_14' in absen[2] :
						absen14 = str(datetime.now())
			if absen1 != False or absen2 != False or absen3 != False or absen4 != False or absen5 != False or absen6 != False or absen7 != False or absen8 != False or absen9 != False or absen10 != False or absen11 != False or absen12 != False or absen13 != False or absen14 != False :
				data = [[0,0,{'history_absensi_1'	: absen1,
								'history_absensi_2'	: absen2,
								'history_absensi_3'	: absen3,
								'history_absensi_4'	: absen4,
								'history_absensi_5'	: absen5,
								'history_absensi_6'	: absen6,
								'history_absensi_7'	: absen7,
								'history_absensi_8'	: absen8,
								'history_absensi_9'	: absen9,
								'history_absensi_10': absen10,
								'history_absensi_11': absen11,
								'history_absensi_12': absen12,
								'history_absensi_13': absen13,
								'history_absensi_14': absen14,
								}]] 
				vals.update({'history_absensi_ids': data})

		return super(absensi, self).write(cr, uid, ids, vals, context=context)

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
		'name'  : fields.char('Kode',size=30,required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'mata_kuliah_id' :fields.many2one('master.matakuliah',string='Matakuliah',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'state':fields.selection([('draft','Draft'),('open','Open'),('close','Closed')],'State',readonly=True, states={'draft': [('readonly', False)]}),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=False,readonly=True, states={'draft': [('readonly', False)]}), 
		'employee_id' :fields.many2one('hr.employee','Dosen', domain="[('is_dosen','=',True)]",required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'sesi':fields.integer('Total Pertemuan',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'konsentrasi_id': fields.many2one('master.konsentrasi','Konsentrasi',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'kurikulum_id':fields.many2one('master.kurikulum',"Kurikulum",readonly=True, states={'draft': [('readonly', False)]}),
		'absensi_ids' : fields.one2many('absensi.detail','absensi_id','Mahasiswa'),
		'history_absensi_ids' : fields.one2many('absensi.history','absensi_id','Histoty',readonly=True),
		'absensi_nilai_ids' : fields.one2many('absensi.detail.nilai','absensi_id','Mahasiswa'),
		#param persentase nilai
		'ulangan' 		: fields.float('Ulangan (%)',readonly=True, states={'open': [('readonly', False)]}),
		'quiz' 		    : fields.float('Quiz (%)',readonly=True, states={'open': [('readonly', False)]}),
		'presentasi' 	: fields.float('Presentasi (%)',readonly=True, states={'open': [('readonly', False)]}),
		'quiz' 		: fields.float('Quiz (%)',readonly=True, states={'open': [('readonly', False)]}),
		'lainnya'		: fields.float('Lainnya (%)',readonly=True, states={'open': [('readonly', False)]}),		
		'absensi' : fields.float('Absensi (%)',readonly=True, states={'open': [('readonly', False)]}),
		'tugas' : fields.float('Tugas (%)',readonly=True, states={'open': [('readonly', False)]}),
		'uts' : fields.float('UTS (%)',readonly=True, states={'open': [('readonly', False)]}),
		'uas' : fields.float('UAS (%)',readonly=True, states={'open': [('readonly', False)]}),
		'user_id' : fields.many2one('res.users','User',readonly=True, ),

			}
			
	_defaults= {
		'state':'draft',
		'sesi':14,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'absensi'),
		'user_id': lambda obj, cr, uid, context: uid, 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode Absensi tidak boleh sama')]


	def query_mahasiswa_by_pengajuan_krs(self,cr,uid,ids,context=None):
		jadwal_obj = self.pool.get('master.jadwal')
		for ct in self.browse(cr,uid,ids):
			#import pdb;pdb.set_trace()
			jadwal_exist = jadwal_obj.search(cr,uid,[('employee_id','=',ct.employee_id.id),
														('tahun_ajaran_id','=',ct.tahun_ajaran_id.id),
														('fakultas_id','=',ct.fakultas_id.id),
														('prodi_id','=',ct.prodi_id.id),
														('is_active','=',True),
														('mata_kuliah_id','=',ct.mata_kuliah_id.id),
														('semester_id','=',ct.semester_id.id)])
			if jadwal_exist :
				jadwal_exist = jadwal_exist+ [0]# tambah id 0 karena jika hasil search tdk buleh satu id
				cr.execute("""select rp.id from res_partner rp
								left join operasional_krs_mahasiswa okm on okm.partner_id = rp.id
								left join operasional_krs_detail_mahasiswa okdm on okm.id = okdm.krs_mhs_id 
								where okdm.jadwal_id in %s"""%(tuple(jadwal_exist),))
				dpt = cr.fetchall()		
				if dpt :
					mhs_ids = map(lambda x: x[0], dpt)

					res = []
					for ms in mhs_ids:
						res.append([0,0,{'partner_id': ms}])	
					sql = "delete from absensi_detail where absensi_id=%s" % (ct.id)
					cr.execute(sql)
					sql = "delete from absensi_detail_nilai where absensi_id=%s" % (ct.id)
					cr.execute(sql)						
					self.write(cr,uid,ct.id,{'absensi_ids':res,
											'absensi_nilai_ids':res})
		return True	

	def open_absensi(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,1,ct.id,{'state':'open'},context=context)
			for det in ct.absensi_ids:
				self.pool.get('absensi.detail').write(cr,1,det.id,{'state':'open'},context=context)
		return True	

	def cancel_absensi(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,1,ct.id,{'state':'draft'},context=context)
			for det in ct.absensi_ids:
				self.pool.get('absensi.detail').write(cr,1,det.id,{'state':'draft'},context=context)
		return True	

	def close_absensi(self,cr,uid,ids,context=None):
		krs_obj = self.pool.get('operasional.krs')
		for ct in self.browse(cr,uid,ids):
			tahun_ajaran = ct.tahun_ajaran_id.id
			fakultas = ct.fakultas_id.id
			prodi = ct.prodi_id.id
			konsentrasi = ct.konsentrasi_id.id
			semester = ct.semester_id.id
			matakuliah = ct.mata_kuliah_id.id
			#import pdb;pdb.set_trace()
			for det in ct.absensi_ids:
				mahasiswa = det.partner_id.id
				total_hadir = det.percentage
				krs_exist = krs_obj.search(cr,1,[('tahun_ajaran_id','=',tahun_ajaran),
													('fakultas_id','=',fakultas),
													('prodi_id','=',prodi),
													('konsentrasi_id','=',konsentrasi),
													('semester_id','=',semester),
													('partner_id','=',mahasiswa)],context=context)
				if krs_exist :
					browse_krs = krs_obj.browse(cr,1,krs_exist[0])
					for dtl in browse_krs.krs_detail_ids:
						if dtl.mata_kuliah_id.id == matakuliah :
							self.pool.get('operasional.krs_detail').write(cr,uid,dtl.id,{'absensi'	:total_hadir})
							break
				self.pool.get('absensi.detail').write(cr,uid,det.id,{'state':'close'},context=context)
			for det in ct.absensi_nilai_ids:
				mahasiswa 	= det.partner_id.id
				tugas 		= det.tugas
				uts   		= det.uts
				uas   		= det.uas
				ulangan 	= det.ulangan
				presentasi  = det.presentasi
				quiz   		= det.quiz
				lainnya 	= det.lainnya

				krs_exist = krs_obj.search(cr,uid,[('tahun_ajaran_id','=',tahun_ajaran),
													('fakultas_id','=',fakultas),
													('prodi_id','=',prodi),
													('konsentrasi_id','=',konsentrasi),
													('semester_id','=',semester),
													('partner_id','=',mahasiswa)],context=context)
				if krs_exist :
					browse_krs = krs_obj.browse(cr,uid,krs_exist[0])
					for dtl in browse_krs.krs_detail_ids:
						if dtl.mata_kuliah_id.id == matakuliah :
							self.pool.get('operasional.krs_detail').write(cr,uid,dtl.id,{'tugas'	:tugas,
																						 'uts'		:uts,
																						 'uas'		:uas,
																						 'ulangan'	:ulangan,
																						 'presentasi':presentasi,
																						 'quiz'		:quiz,
																						 'lainnya'	:lainnya})
							break

				self.pool.get('absensi.detail.nilai').write(cr,uid,det.id,{'state':'close'},context=context)
			self.write(cr,uid,ct.id,{'state':'close'},context=context)			
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in un active"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state == 'close':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus open'))
		return super(absensi, self).unlink(cr, uid, ids, context=context)

	def onchange_kelas(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, prodi_id,kelas_id,konsentrasi_id, context=None):

		results = {}
		if not kelas_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','Mahasiswa'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('fakultas_id','=',fakultas_id),
			('konsentrasi_id','=',konsentrasi_id),
			('prodi_id','=',prodi_id),
			('kelas_id','=',kelas_id)], context=context)

		
		if par_ids :
			res = []
			for mhs in par_ids:
				res.append([0,0,{'partner_id': mhs,'state':'open'}])	
			results = {
				'value' : {
					'absensi_ids' : res,
					'absensi_nilai_ids':res,
				}
			}
		return results

absensi()


class absensi_detail(osv.osv):
	_name = "absensi.detail"

	def get_percentage_absen(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}
		
		for det in self.browse(cr,uid,ids):
			s1_h = 0
			if det.absensi_1:
				s1_h = 1

			s2_h = 0 #H
			if det.absensi_2:
				s2_h = 1

			s3_h = 0 #H
			if det.absensi_3:
				s3_h = 1

			s4_h = 0 #H
			if det.absensi_4:
				s4_h = 1

			s5_h = 0 #H
			if det.absensi_5:
				s5_h = 1

			s6_h = 0 #H
			if det.absensi_6:
				s6_h = 1

			s6_h = 0 #H
			if det.absensi_6:
				s6_h = 1

			s6_h = 0 #H
			if det.absensi_6:
				s6_h = 1

			s7_h = 0 #H
			if det.absensi_7:
				s7_h = 1

			s8_h = 0 #H
			if det.absensi_8:
				s8_h = 1

			s9_h = 0 #H
			if det.absensi_9:
				s9_h = 1

			s10_h = 0 #H
			if det.absensi_10:
				s10_h = 1

			s11_h = 0 #H
			if det.absensi_11:
				s11_h = 1

			s12_h = 0 #H
			if det.absensi_12:
				s12_h = 1

			s13_h = 0 #H
			if det.absensi_13:
				s13_h = 1


			s13_h = 0 #H
			if det.absensi_13:
				s13_h = 1

			s14_h = 0
			if det.absensi_14:
				s14_h = 1

			
			total_hadir = s1_h + s2_h + s3_h + s4_h + s5_h + s6_h + s7_h + s8_h + s9_h + s10_h + s11_h + s12_h + s13_h + s14_h
			percent = (float(total_hadir)/14)*100
			result[det.id] = percent
		return result	

	_columns = {
		'absensi_id' 	: fields.many2one('absensi','Jadwal'),
		'partner_id' 	: fields.many2one('res.partner','Mahasiswa',domain="[('status_mahasiswa','=','Mahasiswa')]",required=True),
		'absensi_1'		:fields.boolean('1'),
		'absensi_2'		:fields.boolean('2'),
		'absensi_3'		:fields.boolean('3'),
		'absensi_4'		:fields.boolean('4'),
		'absensi_5'		:fields.boolean('5'),
		'absensi_6'		:fields.boolean('6'),
		'absensi_7'		:fields.boolean('7'),
		'absensi_8'		:fields.boolean('8'),
		'absensi_9'		:fields.boolean('9'),
		'absensi_10'	:fields.boolean('10'),
		'absensi_11'	:fields.boolean('11'),
		'absensi_12'	:fields.boolean('12'),
		'absensi_13'	:fields.boolean('13'),
		'absensi_14'	:fields.boolean('14'),				
		'percentage'	:fields.function(get_percentage_absen,type='float',string='(%)',store=True),
		'state':fields.selection([('draft','Draft'),('open','Open'),('close','Close')],'State'),
	}

class absensi_detail_nilai(osv.osv):
	_name = "absensi.detail.nilai"

	_columns = {
		'absensi_id' 	: fields.many2one('absensi','Jadwal'),
		'partner_id' 	: fields.many2one('res.partner','Mahasiswa',domain="[('status_mahasiswa','=','Mahasiswa')]",required=True),	
		'tugas'			: fields.float('Tugas'),
		'ulangan' 		: fields.float('Ulangan'),
		'presentasi' 	: fields.float('Presentasi'),
		'quiz' 			: fields.float('Quiz'),
		'uts'			: fields.float('UTS'),
		'uas'			: fields.float('UAS'),
		'lainnya'		: fields.float('Lainnya'),		
		'state':fields.selection([('draft','Draft'),('open','Open'),('close','Close')],'State'),
	}

class absensi_history (osv.osv):
	_name = "absensi.history"	

	_columns = {
		'absensi_id' 			:fields.many2one('absensi','Absensi ID'),
		'history_absensi_1'		:fields.datetime('Sesi 1',readonly=True),
		'history_absensi_2'		:fields.datetime('Sesi 2',readonly=True),
		'history_absensi_3'		:fields.datetime('Sesi 3',readonly=True),
		'history_absensi_4'		:fields.datetime('Sesi 4',readonly=True),
		'history_absensi_5'		:fields.datetime('Sesi 5',readonly=True),
		'history_absensi_6'		:fields.datetime('Sesi 6',readonly=True),
		'history_absensi_7'		:fields.datetime('Sesi 7',readonly=True),
		'history_absensi_8'		:fields.datetime('Sesi 8',readonly=True),
		'history_absensi_9'		:fields.datetime('Sesi 9',readonly=True),
		'history_absensi_10'	:fields.datetime('Sesi 10',readonly=True),
		'history_absensi_11'	:fields.datetime('Sesi 11',readonly=True),
		'history_absensi_12'	:fields.datetime('Sesi 12',readonly=True),
		'history_absensi_13'	:fields.datetime('Sesi 13',readonly=True),
		'history_absensi_14'	:fields.datetime('Sesi 14',readonly=True),
	}	
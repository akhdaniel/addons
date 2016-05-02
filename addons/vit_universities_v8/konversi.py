from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import date, datetime, timedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class konversi(osv.Model):
	_name = 'akademik.konversi'

	# fungsi notifikasi konversi
	def convertion_notification(self, cr, uid, ids, user_id):
		#import pdb;pdb.set_trace()
		for conv in self.browse(cr,uid,ids) :
			state = conv.state
			if state == 'waiting' :
				state = 'waiting approval'
			body_html = 'Hallo '+str(user_id.name)+', Dokumen konversi dengan kode '+ str(conv.name)+' ( '+str(conv.partner_id.name)+' ) '+'masih berstatus '+str(state)+', silahkan untuk ditindaklanjuti !'			
			# create notifikasi ke email
			mail 		= self.pool.get('mail.mail')
			notif_mail 	= mail.create(cr,uid,{'subject' 		: 'Konversi Mahasiswa Baru ISTN',
												'email_from'	: user_id.company_id.email,
												'email_to' 		: user_id.partner_id.email,
												#'email_cc'		: 
												'recipient_ids' : [(6, 0, [conv.partner_id.id])],
												'notification' 	: True,
												'body_html'		: body_html,
												})	
		return notif_mail	

	# fungsi notifikasi konversi
	def convertion_notification_with_cc(self, cr, uid, ids, user_id, cc):
		#import pdb;pdb.set_trace()
		for conv in self.browse(cr,uid,ids) :
			state = conv.state
			if state == 'waiting' :
				state = 'waiting approval'
			body_html = 'Hallo '+str(user_id.name)+', Dokumen konversi dengan kode '+ str(conv.name)+' ( '+str(conv.partner_id.name)+' ) '+'masih berstatus '+str(state)+', silahkan untuk ditindaklanjuti !'			
			# create notifikasi ke email
			mail 		= self.pool.get('mail.mail')
			notif_mail 	= mail.create(cr,uid,{'subject' 		: 'Konversi Mahasiswa Baru ISTN',
												'email_from'	: user_id.company_id.email,
												'email_to' 		: user_id.partner_id.email,
												'email_cc'		: cc,
												'recipient_ids' : [(6, 0, [conv.partner_id.id])],
												'notification' 	: True,
												'body_html'		: body_html,
												})	
		return notif_mail


	_columns = {
		'name' 				: fields.char('Kode Konversi',size=36,required = True,readonly=True, ),
		'partner_id' 		: fields.many2one('res.partner','Calon Mahasiswa',required=True, domain="[('status_mahasiswa','=','Mahasiswa')]",),
		'semester_id'		: fields.many2one('master.semester','Semester Mulai',required=True,),
		# 'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,readonly=True, states={'draft': [('readonly', False)]}),

		'asal_univ_id'		: fields.many2one('res.partner','Asal Universitas',required=True, ),
		'asal_fakultas_id'	: fields.many2one('master.fakultas','Asal Fakultas',required=True, ),
		'asal_prodi_id'		: fields.many2one('master.prodi','Asal Program Studi',required=True, ),

		'fakultas_id'		: fields.many2one('master.fakultas','Fakultas',required=True, ),
		'prodi_id'			: fields.many2one('master.prodi','Program Studi', required=True,),
		'tahun_ajaran_id'	: fields.many2one('academic.year','Angkatan', required=True, ),
		'status'			: fields.selection([('draft','Draft'),('waiting','Waiting Approval'),('cancel','Canceled'),('refuse','Refused'),('confirm','Confirmed')],'Status',),
		# tambah field status karena field state error
		# File "/opt/openerp/odoo-8.0/openerp/fields.py", line 1388, in convert_to_cache
		# raise ValueError("Wrong value for %s: %r" % (self, value))
		# ValueError: Wrong value for akademik.konversi.state: 1

		'state'				: fields.selection([('draft','Draft'),('waiting','Waiting Approval'),('confirm','Confirmed'),('cancel','Canceled'),('refuse','Refused'),('done','Done')],'Status',),
		'notes' 			: fields.text('Alasan',required=True, ),
		'user_id'			: fields.many2one('res.users', 'User',readonly=True),
		'date'				: fields.datetime('Tanggal Registrasi',readonly=True,),
		'create_date'		: fields.datetime('Tanggal Permohonan',readonly=True,),
		'confirm_date'		: fields.datetime('Tanggal Confirm',readonly=True,),
		'approve_date'		: fields.datetime('Tanggal Approve',readonly=True,),
		'done_date'			: fields.datetime('Tanggal Aktivasi Mahasiswa',readonly=True,),
		'krs_done'			: fields.boolean('KRS Done',readonly=True,),

		'matakuliah_ids' 	: fields.one2many('akademik.konversi.mk','konversi_id','Mata Kuliah', ondelete="cascade" ,),

		'total_mk_asal'		: fields.integer('Total Matakuliah Asal',),
		'total_mk_tujuan'	: fields.integer('Total Matakuliah Tujuan',),
		'total_sks_asal'	: fields.integer('Total SKS Asal',),
		'total_sks_tujuan'	: fields.integer('Total SKS Tujuan',),		
	}

	_defaults = {  
		#'state':'draft',
		'status':'draft',
		'user_id':lambda obj, cr, uid, context: uid,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'akademik.konversi'), 
	}
			
	_sql_constraints = [('name_uniq', 'unique(name)','Kode akademik.konversi tidak boleh sama')]

	def onchange_partner(self, cr, uid, ids, tahun_ajaran_id, fakultas_id,prodi_id,partner_id, context=None):
		results = {}
		if not partner_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [('id','=',partner_id)], context=context)

		#import pdb;pdb.set_trace()
		par_id = par_obj.browse(cr,uid,par_ids,context=context)[0]
		tahun_ajaran_id = par_id.tahun_ajaran_id.id
		fakultas_id = par_id.fakultas_id.id
		# jurusan_id = par_id.jurusan_id.id
		prodi_id = par_id.prodi_id.id

		results = {
			'value' : {
				'tahun_ajaran_id' : tahun_ajaran_id,
				'fakultas_id' : fakultas_id,
				'prodi_id' : prodi_id,
			}
		}
		return results 

	def onchange_konversi(self,cr, uid, ids, matakuliah_ids,total_mk_asal,total_mk_tujuan,total_sks_asal,total_sks_tujuan, context=None):
		#
		context = context or {}
		if not matakuliah_ids:
			matakuliah_ids = []
		
		res = {
			'matakuliah_ids': [],
		}
		
		matakuliah_ids = matakuliah_ids
		matakuliah_ids = self.resolve_2many_commands(cr, uid, 'matakuliah_ids', matakuliah_ids, ['asal_matakuliah_id','matakuliah_id','asal_sks','sks'], context)

		total_asal_sks = 0
		total_asal_mk = 0
		total_sks = 0
		total_mk = 0		
		for mk in matakuliah_ids:
			asal_mkul 	= mk.get('asal_matakuliah_id',False)
			asal_sks  	= mk.get('asal_sks',0)
			mkul 		= mk.get('matakuliah_id',False)
			sks  		= mk.get('sks',0)
			total_asal_sks  += asal_sks
			total_sks  += sks
			if mkul :
				total_mk += 1
			if asal_mkul :
				total_asal_mk += 1

		res.update({'total_mk_asal': total_asal_mk,
					'total_mk_tujuan': total_mk,
					'total_sks_asal': total_asal_sks,
					'total_sks_tujuan':total_sks})
		
		return {
			'value': res
		}

	def confirm(self,cr,uid,ids,context=None):
		konv_obj = self.pool.get('akademik.konversi.mapping')
		partner_obj = self.pool.get('res.partner')
		for ct in self.browse(cr,uid,ids):
			if not ct.asal_univ_id or not ct.asal_fakultas_id or not ct.asal_prodi_id:	
				raise osv.except_osv(_('Error!'),
								_('Universitas/Fakultas/Prodi asal harus diisi!'))		
			if not ct.matakuliah_ids:
				raise osv.except_osv(_('Error!'),
								_('Data Matakuliah harus diisi!'))
			asal_prodi = ct.asal_prodi_id.id
			prodi = ct.prodi_id.id																			
			for mk in ct.matakuliah_ids:
				mk_asal = mk.asal_matakuliah_id.id
				mk_tujuan = mk.matakuliah_id.id
				asal_smt = mk.asal_semester_id.id
				smt = mk.semester_id.id				
				# cari a pasang MK ini di master mapping
				exist = konv_obj.search(cr,uid,[#('asal_prodi_id','=',asal_prodi),
												('asal_matakuliah_id','=',mk_asal),
												#('prodi_id','=',prodi),
												('matakuliah_id','=',mk_tujuan)])
				if not exist and mk_tujuan and smt:
					#create master mapping

					konv_obj.create(cr,uid,{'kode':str(mk.asal_matakuliah_id.kode)+str(mk.matakuliah_id.kode),
											'asal_prodi_id':asal_prodi,
											'asal_semester_id':asal_smt,
											'asal_matakuliah_id':mk_asal,
											'prodi_id':prodi,
											'semester_id':smt,
											'matakuliah_id':mk_tujuan},context=context)
			self.write(cr,uid,ct.id,{'status'		: 'waiting',
									'confirm_date'	: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
									},context=context)
			partner_id = partner_obj.search(cr,uid,[('id','=',ct.partner_id.id)])
			if partner_id:
				partner_obj.write(cr,uid,partner_id[0],{'asal_sks_diakui':ct.total_sks_tujuan})
		return True	

	def approve(self,cr,uid,ids,context=None):
		#import pdb;pdb.set_trace()
		calon_obj = self.pool.get('res.partner.calon.mhs')
		kur_obj = self.pool.get('master.kurikulum')
		studi_obj = self.pool.get('operasional.krs')
		studi_detail_obj = self.pool.get('operasional.krs_detail')
		for ct in self.browse(cr,uid,ids):

			t_id = ct.tahun_ajaran_id.date_start
			t_tuple =  tuple(t_id)
			t_id_final = t_tuple[2]+t_tuple[3]#ambil 2 digit paling belakang dari tahun saja	
			f_id = partner.fakultas_id.kode	
			p_id = partner.prodi_id.kode
			lokasi = partner.alamat_id.kode
			t_pend = partner.type_pendaftaran
			if t_pend == 'ganjil' :
				pend = '1'
			else:
				pend = '2'

			if p_id.find(".") != -1:
				j = p_id.split(".")
				p_id = j[1]	

			smt_daftar = ct.semester_id.id
			st = ct.partner_id.status_mahasiswa
			jp_id = ct.partner_id.jenis_pendaftaran_id.code

			se = self.pool.get('ir.sequence').get(cr, uid, 'seq.npm.partner') or '/'

			# sql = "select count(*) from res_partner where jenis_pendaftaran_id=%s and jurusan_id=%s and tahun_ajaran_id=%s" % (
			sql = "select count(*) from res_partner where jenis_pendaftaran_id=%s and prodi_id=%s and tahun_ajaran_id=%s" % (
				ct.partner_id.jenis_pendaftaran_id.id, 
				ct.prodi_id.id, 
				ct.tahun_ajaran_id.id)
			cr.execute(sql)
			# import pdb; pdb.set_trace()
			hasil = cr.fetchone()
			if hasil and hasil[0] != None:
				se = "%03d" % (hasil[0] + 1)
			else:
				se = "001"	
			npm = t_id_final +pend+ f_id+p_id +lokasi+ jp_id + se

			#create data calon yang lulus tersebut ke tabel res.partner.calon.mhs agar ada history terpisah
			calon_obj.create(cr,uid,{'reg'				:ct.partner_id.reg,
									'name'				:ct.partner_id.name,
									'jenis_kelamin'		:ct.partner_id.jenis_kelamin or False,
									'tempat_lahir'		:ct.partner_id.tempat_lahir or False,
									'tanggal_lahir'		:ct.partner_id.tanggal_lahir or False,                  
									'fakultas_id'		:ct.partner_id.fakultas_id.id,
									'prodi_id'			:ct.partner_id.prodi_id.id,
									'tahun_ajaran_id'	:ct.partner_id.tahun_ajaran_id.id,                
									'tgl_lulus'			:ct.partner_id.tgl_lulus or False,
									'no_formulir'		:ct.partner_id.no_formulir or False,
									'tgl_ujian'			:ct.partner_id.tgl_ujian or False,
									'nilai_ujian'		:ct.partner_id.nilai_ujian or False,
									'batas_nilai'		:0,
									'status_pernikahan'	:ct.partner_id.status_pernikahan or False,
									'agama'				:ct.partner_id.agama or False,
									'tgl_daftar'		:ct.partner_id.tgl_daftar or False,
									'nilai_beasiswa'	:ct.partner_id.nilai_beasiswa or False,
									'is_beasiswa' 		:False,
									'state'				:'lulus',
									'date_move'			:time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
									'user_id'			:uid},									
									context=context)

			self.pool.get('res.partner').write(cr,uid,ct.partner_id.id,{'npm':npm,'status_mahasiswa':'Mahasiswa'},context=context)

			#cari matakuliah yg akan di masukan pada master kurikulum		
			kur_ids = kur_obj.search(cr, uid, [
				('tahun_ajaran_id','=',ct.tahun_ajaran_id.id),
				('prodi_id','=',ct.prodi_id.id),
				('state','=','confirm'),
				('semester_id','=',smt_daftar)], context=context)
			if not kur_ids:
				raise osv.except_osv(_('Error!'),
								_('Tidak ada kurikulum yang cocok untuk konversi ini!'))	

			
			smes = 1
			for xr in range(1,smt_daftar):
				cr.execute('''select
							matakuliah_id,sks,nilai,nilai_a
						from
							akademik_konversi_mk
						where
							konversi_id = %s and semester_id = %s''',(ct.id,xr))
				res = cr.fetchall()
				mk_ids = map(lambda x: x[0], res) # atau  [i for (i,) in res]

				#create KHS Detail
				khs_ids = []
				for det in res:	

					khs_ids.append((0,0,{
										'mata_kuliah_id'	: det[0],
										'sks'				: det[1],
										'tugas'				: det[2],
										'ulangan'			: det[2],
										'uts'				: det[2],
										'uas'				: det[2],
										'state'				: 'done',
										'is_konversi'		: True,
										}))	
				#create KHS
				#import pdb;pdb.set_trace()
				khs_id = studi_obj.create(cr,uid,{'kode'		: str(npm)+'-'+str(xr),
											'partner_id'		: ct.partner_id.id,
											'npm'				: npm,
											'semester_id'		: xr,
											'tahun_ajaran_id'	: ct.tahun_ajaran_id.id,
											'fakultas_id'		: ct.fakultas_id.id,
											'prodi_id'			: ct.prodi_id.id,
											'user_id'			: uid,
											'kurikulum_id'		: kur_ids[0],
											'krs_detail_ids'	: khs_ids,
											'state'				: 'done'})

			#create KRS detailnya
			kur_id = kur_obj.browse(cr,uid,kur_ids,context=context)[0].kurikulum_detail_ids
			mk_kurikulum = []
			for kur in kur_id:
				mk_kurikulum.append(kur.id)
		
			#cari matakuliah apa saja yg sdh di tempuh di smt sebelumnya
			cr.execute("""SELECT okd.id, okd.mata_kuliah_id
							FROM operasional_krs_detail okd
							LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
							WHERE ok.partner_id = %s
							AND ok.state <> 'draft'"""%(ct.partner_id.id))
			dpt = cr.fetchall()
			
			total_mk_ids = []
			for x in dpt:
				total_mk_ids.append(x[1])
			#import pdb;pdb.set_trace()
			#filter matakuliah yg benar-benar belum di tempuh
			mk_baru_ids =set(mk_kurikulum).difference(total_mk_ids)

			krs_ids = []
			for kur in mk_baru_ids:
				krs_ids.append((0,0,{
									'mata_kuliah_id'	: kur,
									'sks'				: det[1],
									'state'				: 'draft'
									}))																	
			#create KRS berjalan
			studi_obj.create(cr,uid,{'kode'				: str(npm)+'-'+str(smt_daftar),
									'partner_id'		: ct.partner_id.id,
									'npm'				: npm,
									'semester_id'		: smt_daftar,
									'tahun_ajaran_id'	: ct.tahun_ajaran_id.id,
									'fakultas_id'		: ct.fakultas_id.id,
									'prodi_id'			: ct.prodi_id.id,
									'user_id'			: uid,
									'kurikulum_id'		: kur_ids[0],
									'krs_detail_ids'	: krs_ids,
									},context=context)	
			self.write(cr,uid,ct.id,{'status'		:'confirm',
									'krs_done'		: True,
									'approve_date' 	: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),},context=context)
		return True	

	def cancel(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'status':'cancel'},context=context)
		return True	

	def set_draft(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'status':'draft'},context=context)
		return True	

	def refuse(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'status':'refuse'},context=context)
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.status != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(konversi, self).unlink(cr, uid, ids, context=context)


	####################################################################################################
	# Cron Job untuk kirim notif email ke group
	####################################################################################################
	def cron_notif_email_konversi(self, cr, uid, ids=None,context=None):
		#import pdb;pdb.set_trace()
		groups_obj = self.pool.get('res.groups')
		users_obj = self.pool.get('res.users')

		now = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
		now_check = datetime.strptime(now,'%Y-%m-%d %H:%M:%S')
		hari_2 = now_check - timedelta(hours=48)
		hari_3 = now_check - timedelta(hours=72)
		hari_4 = now_check - timedelta(hours=96)

		users_prodi  	= groups_obj.search(cr,uid,[('name','ilike','Staff Prodi')], context=context)
		users_dekan  	= groups_obj.search(cr,uid,[('name','ilike','Staff Dekan')], context=context)
		users_kabaak  	= groups_obj.search(cr,uid,[('name','ilike','Kepala BAAK')], context=context)
		users_dirbaak  	= groups_obj.search(cr,uid,[('name','ilike','Direktur BAAK')], context=context)
		users_rektor  	= groups_obj.search(cr,uid,[('name','ilike','Rektor')], context=context)

		conv_draft_exist4 = self.search(cr,uid,[('create_date','<=',str(hari_4)),('state','in',('draft','waiting'))])
		if conv_draft_exist4 :	
			for conv in conv_draft_exist4 :
				if users_dirbaak :
					users_ids = groups_obj.browse(cr,uid,users_dirbaak[0])
					if users_ids.users :
						for usr in users_ids.users :
							cc = False
							if users_rektor :
								cc = users_obj.browse(cr,uid,users_rektor[0]).partner_id.email
							self.convertion_notification_with_cc(cr, uid, [conv], usr, cc)

		conv_draft_exist3 = self.search(cr,uid,[('create_date','>',str(hari_4)),('create_date','<=',str(hari_3)),('state','in',('draft','waiting'))])
		if conv_draft_exist3 :	
			for conv in conv_draft_exist3 :
				if users_dekan :
					users_ids = groups_obj.browse(cr,uid,users_dekan[0])
					if users_ids.users :
						for usr in users_ids.users :
							if usr.fakultas_id.id == self.browse(cr,uid,conv).fakultas_id.id :
								self.convertion_notification_with_cc(cr, uid, [conv], usr, usr.partner_id.email)

		conv_draft_exist2 = self.search(cr,uid,[('create_date','>',str(hari_3)),('state','in',('draft','waiting'))])
		if conv_draft_exist2 :	
			for conv in conv_draft_exist2 :
				if users_dekan :
					users_ids = groups_obj.browse(cr,uid,users_prodi[0])
					if users_ids.users :
						for usr in users_ids.users :
							self.convertion_notification(cr, uid, [conv], usr)

		conv_waiting_exist4 = self.search(cr,uid,[('create_date','<=',str(hari_4)),('state','in',('draft','waiting'))])
		if conv_waiting_exist4 :	
			for conv in conv_waiting_exist4 :
				if users_dirbaak :
					users_ids = groups_obj.browse(cr,uid,users_dirbaak[0])
					if users_ids.users :
						for usr in users_ids.users :
							cc = False
							if users_rektor :
								cc = users_obj.browse(cr,uid,users_rektor[0]).partner_id.email
							self.convertion_notification_with_cc(cr, uid, [conv], usr, cc)

		conv_waiting_exist3 = self.search(cr,uid,[('create_date','>',str(hari_4)),('create_date','<=',str(hari_3)),('state','in',('draft','waiting'))])
		if conv_waiting_exist3 :	
			for conv in conv_waiting_exist3 :
				if users_dekan :
					users_ids = groups_obj.browse(cr,uid,users_dekan[0])
					if users_ids.users :
						for usr in users_ids.users :
							if usr.fakultas_id.id == self.browse(cr,uid,conv).fakultas_id.id :
								self.convertion_notification_with_cc(cr, uid, [conv], usr, usr.partner_id.email)

		conv_waiting_exist2 = self.search(cr,uid,[('create_date','>',str(hari_3)),('state','in',('draft','waiting'))])
		if conv_waiting_exist2 :	
			for conv in conv_waiting_exist2 :
				if users_dekan :
					users_ids = groups_obj.browse(cr,uid,users_prodi[0])
					if users_ids.users :
						for usr in users_ids.users :
							self.convertion_notification(cr, uid, [conv], usr)

		return True

			
konversi()



class akademik_konversi_mk(osv.osv):
	_name 		= "akademik.konversi.mk"
	_columns 	= {
		'konversi_id' 			: fields.many2one('akademik.konversi', 'Konversi'),
		'asal_matakuliah_id' 	: fields.many2one('akademik.konversi.master_asal_mk', 'Nama Matakuliah',required=True),
		'asal_semester_id'		: fields.many2one('master.semester', 'Semester',required=True),
		'asal_sks'				: fields.integer('SKS',required=True),
		'asal_nilai'			: fields.float('Nilai',required=True),
		'asal_nilai_a'			: fields.char('Nilai 2',required=True),		
		'matakuliah_id' 		: fields.many2one('master.matakuliah', 'Nama Matakuliah'),
		'semester_id'			: fields.many2one('master.semester', 'Semester'),
		'sks'					: fields.integer('SKS'),
		'nilai'					: fields.float('Nilai'),
		'nilai_a'				: fields.char('Nilai 2'),
	}


	def onchange_asal_matakuliah(self, cr, uid, ids, konversi_id,asal_matakuliah_id,asal_semester_id,asal_sks,asal_nilai,asal_nilai_a, context=None):
		#import pdb;pdb.set_trace()
		konv_obj = self.pool.get('akademik.konversi.mapping')
		map_id = konv_obj.search(cr,uid,[('asal_matakuliah_id','=',asal_matakuliah_id)])
		sks = 0
		mk = False
		smt = False
		if map_id:
			mapping = konv_obj.browse(cr,uid,map_id[0])
			mk = mapping.matakuliah_id.id
			sks = mapping.matakuliah_id.sks
			smt = mapping.semester_id.id

		val = {
			'matakuliah_id': mk,
			'sks': sks,
			'semester_id' : smt,
			'nilai' : asal_nilai or 0,
			'nilai_a': asal_nilai_a or False,
			}

		return {'value': val}


class master_asal_mk(osv.Model):
	_name = 'akademik.konversi.master_asal_mk'
	_rec_name= 'nama'


	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		ids = []
		if name:
			ids = self.search(cr, user, ['|','|',('nama', operator, name),('kode', operator, name),('kode_dikti', operator, name)] + args, limit=limit)
		else:
			ids = self.search(cr, user, args, context=context, limit=limit)
		return self.name_get(cr, user, ids, context=context)


	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['nama', 'kode'], context=context)
		res = []
		for record in reads:
			name = record['nama']
			if record['kode']:
				name = '['+record['kode'] +']'+ ' ' + name
			res.append((record['id'], name))
		return res

	_columns = {
		'kode' 			: fields.char('Kode', 128,required = True),
		'nama' 			: fields.char('Nama',required = True),
		'kode_dikti' 	: fields.char('Kode DIKTI', size=28,required = True),
		'sks'			: fields.char('SKS',required = True),
		'prodi_id'		: fields.many2one('master.prodi','Program Studi'),
		'jenjang_id'	: fields.many2one('master.jenjang','Jejang'),
	}

master_asal_mk()



class master_mapping(osv.Model):
	_name = 'akademik.konversi.mapping'
	_rec_name = 'kode'

	_columns = {
		'kode' 				:fields.char('Kode', 128,required = True),
		'prodi_id' 			: fields.many2one('master.prodi','Program Studi Tujuan'),
		'matakuliah_id'  	: fields.many2one('master.matakuliah', 'MK Tujuan'),
		'asal_matakuliah_id': fields.many2one('akademik.konversi.master_asal_mk', 'MK Asal'),
		'asal_prodi_id' 	: fields.many2one('master.prodi','Program Studi Asal'),
		'asal_semester_id'	: fields.many2one('master.semester','Semester Asal'),
		'semester_id'		: fields.many2one('master.semester','Semester Tujuan'),		
	}

master_asal_mk()


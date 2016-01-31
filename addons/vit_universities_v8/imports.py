from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


################################################################
# konversi tanggal dari mm/dd/yy ke yyyy-mm-dd
# jika yy > min2000 dan yy < max2000 
#	tambah 2000
# else
#	tambah 1900 
#
# misal 02/10/89 ===> 1989-02-10
#       02/10/02 ===> 2002-02-10
################################################################
def format_tanggal(min2000, max2000, input_date):
	#09/24/87
	#01234567
	t = int(input_date[6:8])
	if t>min2000 and t<max2000: 
		t = 2000 + t
	else: # 
		t = 1900 + t 
	tgl = "%s-%s-%s" % ( t , input_date[:2], input_date[3:5])
	return tgl 

################################################################
# class import table matakuliah TBKMK.csv
# masuk ke master_matakuliah
#          master_kurikulum
################################################################
class import_mk(osv.osv):
	_name 		= "akademik.import_mk"
	_columns 	= {
		"thsmstbkmk"	: fields.char("THSMSTBKMK,C,5"),
		"kdptitbkmk"	: fields.char("KDPTITBKMK,C,6"),
		"kdjentbkmk"	: fields.char("KDJENTBKMK,C,1"),
		"kode_prodi"	: fields.char("KODE PRODI"),
		"tahun_ajaran"	: fields.char("TAHUN AJARAN"),
		"kdpsttbkmk"	: fields.char("KDPSTTBKMK,C,5"),
		"kdkmktbkmk"	: fields.char("KDKMKTBKMK,C,10"),
		"nakmktbkmk"	: fields.char("NAKMKTBKMK,C,40"),
		"sksmktbkmk"	: fields.char("SKSMKTBKMK,N,2,0"),
		"skstmtbkmk"	: fields.char("SKSTMTBKMK,N,2,0"),
		"sksprtbkmk"	: fields.char("SKSPRTBKMK,N,2,0"),
		"skslptbkmk"	: fields.char("SKSLPTBKMK,N,2,0"),
		"semestbkmk"	: fields.char("SEMESTBKMK,C,2"),
		"kdkeltbkmk"	: fields.char("KDKELTBKMK,C,1"),
		"kdkurtbkmk"	: fields.char("KDKURTBKMK,C,1"),
		"kdwpltbkmk"	: fields.char("KDWPLTBKMK,C,1"),
		"nodostbkmk"	: fields.char("NODOSTBKMK,C,10"),
		"jenjatbkmk"	: fields.char("JENJATBKMK,C,1"),
		"proditbkmk"	: fields.char("PRODITBKMK,C,5"),
		"stkmktbkmk"	: fields.char("STKMKTBKMK,C,1"),
		"slbustbkmk"	: fields.char("SLBUSTBKMK,C,1"),
		"sappptbkmk"	: fields.char("SAPPPTBKMK,C,1"),
		"bhnajtbkmk"	: fields.char("BHNAJTBKMK,C,1"),
		"diktttbkmk"	: fields.char("DIKTTTBKMK,C,1"),
		"is_processed"	: fields.boolean("Is Processed"),
	}

	def get_prodi_id(self, cr, uid, prodi_prima_id, context=None):
		# import pdb; pdb.set_trace()
		mapping 	= self.pool.get('akademik.prodi.map')
		prodi 		= self.pool.get('master.prodi')
		ids 		= mapping.search(cr, uid, [('prodi_prima_id','=',prodi_prima_id)], context=context)
		if ids :
			m = mapping.browse(cr, uid, ids[0] , context=context)
			prodi_id = prodi.search(cr, uid, [('kode','=', m.prodi_kode )], context=context)
			prodi_data = prodi.browse(cr, uid, prodi_id[0], context=context)
			return prodi_data
		else:
			return None

	def get_prodi(self, cr, uid, kode_prodi, context=None):
		# import pdb; pdb.set_trace()
		prodi_obj		= self.pool.get('master.prodi')
		ids = prodi_obj.search(cr, uid, [('kode','=', kode_prodi )], context=context)
		if ids :
			prodi_data = prodi_obj.browse(cr, uid, ids[0], context=context)
			return prodi_data
		else:
			return None

	def get_semester_id(self, cr, uid, semester_name, context=None):
		semester = self.pool.get('master.semester')
		ids = semester.search(cr, uid, [('name','=',semester_name)], context=context)
		if ids :
			m = semester.browse(cr, uid, ids[0] , context=context)
			return m
		else:
			return None

	def get_tahun_ajaran_id(self, cr, uid, tahun, context=None):
		tahun_ajaran = self.pool.get('academic.year')
		ids = tahun_ajaran.search(cr, uid, [('code','=',tahun)], context=context)
		if ids :
			m = tahun_ajaran.browse(cr, uid, ids[0] , context=context)
			return m
		else:
			return None

	def get_mk_id(self, cr, uid, kode_mk, prodi_id, rec, context=None):
		mk_obj = self.pool.get('master.matakuliah')
		mk_ids = mk_obj.search(cr, uid, [('kode','=',kode_mk)], context=context)

		if mk_ids :
			m = mk_obj.browse(cr, uid, mk_ids[0] , context=context)
			return m
		else:
			data = {
				'kode' 			: kode_mk,
				'kode_dikti'	: rec.kdkmktbkmk,
				'nama'			: rec.nakmktbkmk,
				'sks' 			: rec.sksmktbkmk,
				'jenis' 		: 'mk_umum',
				'prodi_id'		: prodi_id.id
			}
			new_mk = mk_obj.create(cr, uid, data, context=context)
			m = mk_obj.browse(cr, uid, new_mk , context=context)
			return m


	def action_import_mk(self, cr, uid, context=None):
		##########################################################
		# id line import_mk yang diselect
		##########################################################
		active_ids = context and context.get("active_ids", False)
		if not context:
			context = {}

		kur_obj = self.pool.get('master.kurikulum')

		ids = self.search(cr, uid, [('is_processed','=',False)], context=context)
		# ids = active_ids

		semester_lama 	= ""
		kd_prodi_lama   = ""

		cr.execute('delete from master_kurikulum')

		# import pdb; pdb.set_trace()
		mk_ids 		= []
		kur_id 		= None

		for rec in self.browse(cr, uid, ids, context=context):

			# tahun 		= rec.thsmstbkmk[:4]
			# tahun 		= 2000 + int(rec.kdkmktbkmk[1:2])
			tahun 			= rec.tahun_ajaran
			tahun_ajaran = self.get_tahun_ajaran_id(cr, uid, tahun, context=context)
			if not tahun_ajaran:
				raise osv.except_osv(_('Error'),_("no tahun_ajaran %s") % (tahun) ) 

			# prodi_prima_id = rec.kdpsttbkmk
			# prodi_id 	= self.get_prodi_id(cr, uid, prodi_prima_id, context=context)
			kode_prodi = rec.kode_prodi
			prodi_id 	= self.get_prodi(cr, uid, kode_prodi, context=context)
			if prodi_id:
				fakultas_id = prodi_id.fakultas_id
			else:
				fakultas_id = None
				print _("no prodi kode %s") % (kode_prodi)
				continue
				# raise osv.except_osv(_('Error'),_("no prodi with ID prima %s") % (prodi_prima_id) ) 

			kode_mk 	= rec.kdkmktbkmk
			nama 		= rec.nakmktbkmk
			sks 		= rec.sksmktbkmk
			semester 	= self.get_semester_id(cr, uid, rec.semestbkmk, context=context)
			if not semester:
				raise osv.except_osv(_('Error'),_("no semester %s") % (rec.semestbkmk) ) 


			if prodi_id.kode != kd_prodi_lama or semester.id != semester_lama:
				if kd_prodi_lama != "" and semester_lama != "":
					# import pdb; pdb.set_trace()

					if mk_ids:
						data = {
							'kurikulum_detail_ids'	: [(6,0, mk_ids) ] , 
							'total_sks'				: 1,
							'total_mk_ids' 			: None,
							'total_sks2'			: 1	
						}
						kur_obj.write(cr, uid, kur_id, data, context=context)
					mk_ids 		= []
					kur_id 		= None


				data={
					'name' 				: self.pool.get('ir.sequence').get(cr, uid, 'master.kurikulum'),
					'fakultas_id'		: fakultas_id.id,
					'prodi_id'			: prodi_id.id,
					'semester_id'		: semester.id,
					'max_sks'			: 30,
					'min_ip'			: 2,
					'tahun_ajaran_id'	: tahun_ajaran.id,
					'state'				: 'draft'
				}
				kur_id = kur_obj.create(cr, uid, data, context=context)

				mk_data = self.get_mk_id(cr, uid, kode_mk, prodi_id, rec, context=context)
				if mk_data:
					mk_ids.append( mk_data.id ) 
				else:
					print "not found MK %s " % (kode_mk)
					continue

			else:

				mk_data = self.get_mk_id(cr, uid, kode_mk, prodi_id, rec, context=context)
				if mk_data:
					mk_ids.append( mk_data.id ) 
				else:
					print "not found MK %s " % (kode_mk)
					continue

			semester_lama 	= semester.id
			kd_prodi_lama   = prodi_id.kode

			self.write(cr, uid, rec.id, {'is_processed':True}, context=context)

		return


################################################################
# class import table mahasiswa MSMHS.csv
# masuk ke res_partner
#          operasional_krs
################################################################
class import_mhs(osv.osv):
	_name 		= "akademik.import_mhs"
	_columns 	= {
		"kdptimsmhs"			: fields.char("KDPTIMSMHS,C,6"),
		"kdjenmsmhs"			: fields.char("KDJENMSMHS,C,1"),
		"kdpstmsmhs"			: fields.char("KDPSTMSMHS,C,5"),
		"nimhsmsmhs"			: fields.char("NIMHSMSMHS,C,15"),
		"nmmhsmsmhs"			: fields.char("NMMHSMSMHS,C,30"),
		"shiftmsmhs"			: fields.char("SHIFTMSMHS,C,1"),
		"tplhrmsmhs"			: fields.char("TPLHRMSMHS,C,20"),
		"tglhrmsmhs"			: fields.char("TGLHRMSMHS,D"),
		"kdjekmsmhs"			: fields.char("KDJEKMSMHS,C,1"),
		"tahunmsmhs"			: fields.char("TAHUNMSMHS,C,4"),
		"smawlmsmhs"			: fields.char("SMAWLMSMHS,C,5"),
		"btstumsmhs"			: fields.char("BTSTUMSMHS,C,5"),
		"assmamsmhs"			: fields.char("ASSMAMSMHS,C,2"),
		"tgmskmsmhs"			: fields.char("TGMSKMSMHS,D"),
		"tgllsmsmhs"			: fields.char("TGLLSMSMHS,D"),
		"stmhsmsmhs"			: fields.char("STMHSMSMHS,C,1"),
		"stpidmsmhs"			: fields.char("STPIDMSMHS,C,1"),
		"sksdimsmhs"			: fields.char("SKSDIMSMHS,N,3,0"),
		"asnimmsmhs"			: fields.char("ASNIMMSMHS,C,15"),
		"asptimsmhs"			: fields.char("ASPTIMSMHS,C,6"),
		"asjenmsmhs"			: fields.char("ASJENMSMHS,C,1"),
		"aspstmsmhs"			: fields.char("ASPSTMSMHS,C,5"),
		"bistumsmhs"			: fields.char("BISTUMSMHS,C,1"),
		"peksbmsmhs"			: fields.char("PEKSBMSMHS,C,1"),
		"nmpekmsmhs"			: fields.char("NMPEKMSMHS,C,40"),
		"ptpekmsmhs"			: fields.char("PTPEKMSMHS,C,6"),
		"pspekmsmhs"			: fields.char("PSPEKMSMHS,C,5"),
		"noprmmsmhs"			: fields.char("NOPRMMSMHS,C,10"),
		"nokp1msmhs"			: fields.char("NOKP1MSMHS,C,10"),
		"nokp2msmhs"			: fields.char("NOKP2MSMHS,C,10"),
		"nokp3msmhs"			: fields.char("NOKP3MSMHS,C,10"),
		"nokp4msmhs"			: fields.char("NOKP4MSMHS,C,10"),
		"is_processed"			: fields.boolean("Is Processed"),
	}

	##########################################################
	# import ke tabel mahasiswa
	##########################################################
	def action_import_mhs(self, cr, uid, context=None):
		active_ids = context and context.get("active_ids", False)
		if not context:
			context = {}

		mhs_obj = self.pool.get('res.partner')
		prodi_obj = self.pool.get('master.prodi')
		tahun_obj = self.pool.get('academic.year')
		semester_obj = self.pool.get('master.semester')
		jp_obj = self.pool.get('akademik.jenis_pendaftaran')

		jp_baru = jp_obj.find_by_name(cr, uid, "Baru", context=context)

		ids = self.search(cr, uid, [('id','in', active_ids),('is_processed','=',False)], context=context)
		for rec in self.browse(cr, uid, ids, context=context):
			
			#50110339
			#01234
			kode_prodi = rec.nimhsmsmhs[2:4]
			prodi = prodi_obj.find_by_kode(cr, uid, kode_prodi, context=context)

			t = int(rec.nimhsmsmhs[:2])
			if t > 0 and t < 15:
				thn = t + 2000
			else:
				thn = t + 1900
			tahun = tahun_obj.find_by_code(cr, uid, thn, context=context)

			semester = semester_obj.find_by_name(cr, uid, "1", context=context)


			if rec.tglhrmsmhs:
				tgl_lahir = format_tanggal(0,2,rec.tglhrmsmhs)
			else:
				tgl_lahir = False

			if rec.tgllsmsmhs:
				tgl_lulus = format_tanggal(0,15,rec.tgllsmsmhs)
			else:
				tgl_lulus = False


			data = {
				'name'				: rec.nmmhsmsmhs,
				'npm' 				: rec.nimhsmsmhs,
				'reg'				: '',
				'jenis_kelamin'		: rec.kdjekmsmhs,
				'tempat_lahir'		: rec.tplhrmsmhs,
				'tanggal_lahir'		: tgl_lahir,
				'status_mahasiswa'	: 'Mahasiswa',
				'is_mahasiswa' 		: True,
				'status_aktivitas'	: 'A',
				'jenis_pendaftaran_id': jp_baru.id,
				'prodi_id'			: prodi.id,
				'fakultas_id'		: prodi.fakultas_id.id,
				'tahun_ajaran_id'	: tahun.id,
				'semester_id'		: semester.id,
				'tgl_lulus'			: tgl_lulus
			}

			mhs_id = mhs_obj.create(cr, uid, data, context=context)

		self.write(cr, uid, ids, {'is_processed': True} , context=context)

		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_universities_v8', 'partner_tree_view2')
		view_id = view_ref and view_ref[1] or False,		
		return {
			'name' : _('Mahasiswa View'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'res.partner',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			# 'domain' : "[('state','=','draft')]",
			#'context': "{'default_state':'open'}",#
			'nodestroy': False,
		}


################################################################
# class import table nilai mahasiswa  TRNLP.csv
# masuk ke res_partner
#          operasional_krs
################################################################
class import_nlm(osv.osv):
	_name 		= "akademik.import_nlm"
	_columns 	= {
		"thsmstrnlm"			: fields.char("THSMSTRNLM,C,5"),
		"kdptitrnlm"			: fields.char("KDPTITRNLM,C,6"),
		"kdjentrnlm"			: fields.char("KDJENTRNLM,C,1"),
		"kdpsttrnlm"			: fields.char("KDPSTTRNLM,C,5"),
		"nimhstrnlm"			: fields.char("NIMHSTRNLM,C,15"),
		"kdkmktrnlm"			: fields.char("KDKMKTRNLM,C,10"),
		"nlakhtrnlm"			: fields.char("NLAKHTRNLM,C,2"),
		"bobottrnlm"			: fields.char("BOBOTTRNLM,N,4,2"),
		"is_processed"			: fields.boolean("Is Processed"),
	}

	def action_import_nlm(self, cr, uid, context=None):
		##########################################################
		# id line import_nlm yang diselect
		##########################################################
		active_ids = context and context.get("active_ids", False)
		if not context:
			context = {}

		ids = self.search(cr, uid, [('is_processed','=',False)], context=context)
		# for rec in self.browse(cr, uid, ids, context=context):
		# 	return


		return


################################################################
# class import table lulusan mahasiswa TRLSM.csv 
# update ke res_partner status : Lulus / DO / Cuti
################################################################
class import_lsm(osv.osv):
	_name 		= "akademik.import_lsm"
	_columns 	= {
		"thsmstrlsm"				: fields.char("THSMSTRLSM,C,5"),
		"kdptitrlsm"				: fields.char("KDPTITRLSM,C,6"),
		"kdjentrlsm"				: fields.char("KDJENTRLSM,C,1"),
		"kdpsttrlsm"				: fields.char("KDPSTTRLSM,C,5"),
		"nimhstrlsm"				: fields.char("NIMHSTRLSM,C,15"),
		"stmhstrlsm"				: fields.char("STMHSTRLSM,C,1"),
		"tgllstrlsm"				: fields.char("TGLLSTRLSM,D"),
		"skstttrlsm"				: fields.char("SKSTTTRLSM,N,3,0"),
		"nlipktrlsm"				: fields.char("NLIPKTRLSM,N,4,2"),
		"noskrtrlsm"				: fields.char("NOSKRTRLSM,C,30"),
		"tglretrlsm"				: fields.char("TGLRETRLSM,D"),
		"noijatrlsm"				: fields.char("NOIJATRLSM,C,40"),
		"stllstrlsm"				: fields.char("STLLSTRLSM,C,1"),
		"jnllstrlsm"				: fields.char("JNLLSTRLSM,C,1"),
		"blawltrlsm"				: fields.char("BLAWLTRLSM,C,6"),
		"blakhtrlsm"				: fields.char("BLAKHTRLSM,C,6"),
		"nods1trlsm"				: fields.char("NODS1TRLSM,C,10"),
		"nods2trlsm"				: fields.char("NODS2TRLSM,C,10"),
		"nods3trlsm"				: fields.char("NODS3TRLSM,C,10"),
		"nods4trlsm"				: fields.char("NODS4TRLSM,C,10"),
		"nods5trlsm"				: fields.char("NODS5TRLSM,C,10"),
		"is_processed"			: fields.boolean("Is Processed"),
	}

	def action_import_lsm(self, cr, uid, context=None):
		##########################################################
		# id line import_lsm yang diselect
		##########################################################
		active_ids = context and context.get("active_ids", False)
		if not context:
			context = {}

		ids = self.search(cr, uid, [('is_processed','=',False)], context=context)
		# for rec in self.browse(cr, uid, ids, context=context):
		# 	return


		return
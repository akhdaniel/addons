from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

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

	def get_mk_id(self, cr, uid, kode_mk, context=None):
		mk_obj = self.pool.get('master.matakuliah')
		mk_ids = mk_obj.search(cr, uid, [('kode','=',kode_mk)], context=context)

		if mk_ids :
			m = mk_obj.browse(cr, uid, mk_ids[0] , context=context)
			return m
		else:
			return None


	def action_import_mk(self, cr, uid, context=None):
		##########################################################
		# id line import_mk yang diselect
		##########################################################
		active_ids = context and context.get("active_ids", False)
		if not context:
			context = {}

		kur_obj = self.pool.get('master.kurikulum')

		ids = self.search(cr, uid, [('is_processed','=',False)], context=context)

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

				mk_data = self.get_mk_id(cr, uid, kode_mk, context=context)
				if mk_data:
					mk_ids.append( mk_data.id ) 
				else:
					print "not found MK %s " % (kode_mk)
					continue

			else:

				mk_data = self.get_mk_id(cr, uid, kode_mk, context=context)
				if mk_data:
					mk_ids.append( mk_data.id ) 
				else:
					print "not found MK %s " % (kode_mk)
					continue

			semester_lama 	= semester.id
			kd_prodi_lama   = prodi_id.kode

		return

class prodi_map(osv.osv):
	_name = "akademik.prodi.map"
	_columns = {
		'prodi_prima_id' 	: fields.char("ID Prodi Prima"),
		'prodi_kode'		: fields.char('Kode Prodi'),
		'name'				: fields.char('Nama Prodi'),
	}
from datetime import datetime
from datetime import date
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from time import strptime
from time import strftime
from openerp.tools.translate import _

class job(osv.osv):
	_name 		= 'hr.job'
	_inherit	= 'hr.job'

	###########################################################################
	########################## fungsi untuk status ############################ 
	
	def set_recruit(self, cr, uid, ids, context=None):
		for job in self.browse(cr, uid, ids, context=context):
			no_of_recruitment = job.no_of_recruitment == 0 and 1 or job.no_of_recruitment
			self.write(cr, uid, [job.id], {'state': 'recruit', 'no_of_recruitment': no_of_recruitment, 'status_rec': 'filter'}, context=context)
		return True

	def set_open(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {
			'state': 'open',
			'no_of_recruitment': 0,
			'no_of_hired_employee': 0,
			'status_rec': 'done'  
		}, context=context)
		return True

	#########################################################################

	###############################################################
	############ fungsi untuk memfilter calon pelamar #############
	###############################################################

	def seleksi_pelamar(self,cr,uid,ids, context=None) :
		per =self.browse(cr,uid,ids,context)[0]
		
		job_name = per.name
		job_pengalaman = per.pengalaman
		job_kelamin = per.kelamin
		job_domisili = per.tempat_lahir_id.name
		job_umr = per.usia
		job_sts_prk = per.sts_prk
		job_pend = per.type_id.id      

		job_b_name = per.bol_name
		job_b_pengalaman = per.bol_pengalaman
		job_b_kelamin = per.bol_kelamin
		job_b_domisili = per.bol_tempat_lahir_id
		job_b_umr = per.bol_usia
		job_b_status = per.bol_sts_prk
		job_b_pend = per.bol_type_id

		#browse stage rectruitment
		partner = self.pool.get('hr.recruitment.stage')
		pero = partner.search(cr,uid,[])
		pers = partner.browse(cr,uid,pero,context)[0]

		filt = [('stage_id','=','Initial Qualification')]
		partner = self.pool.get('hr.applicant')
		
		perok = partner.search(cr,uid,[('app_id','=',job_name),(pers.id,'=',1)])
		for tt in partner.browse(cr,uid,perok) :			
			partner.write(cr,uid,perok,{'app_id' : False},context=context)

		if job_b_pengalaman :
			filt.append(('pengalaman','>=',job_pengalaman))
		if job_b_kelamin :
			filt.append(('jen_kel','=',job_kelamin))
		if job_b_domisili :
			filt.append(('kab_id','=',job_domisili))
		if job_b_umr :
			filt.append(('age','<=',job_umr))
		if job_b_status :
			filt.append(('status','=',job_sts_prk))
		# if job_b_pend :
		# 	filt.append(('type_id','=',job_pend))

		pero = partner.search(cr,uid,filt)
		if job_b_name == False :
			for xux in partner.browse(cr,uid,pero):
				if job_b_pend :
					if per.type_id.sequence <= xux.type_id.sequence :
						partner.write(cr,uid,[xux.id],{'app_id':per.id, 'department_id':per.department_id.id},context=context)
				else :
					partner.write(cr,uid,[xux.id],{'app_id':per.id, 'department_id':per.department_id.id},context=context)
		elif job_b_name :
			ada = partner.browse(cr,uid,pero)
			for rr in ada:
				if rr.job_id.name == job_name :
					partner.write(cr,uid,[rr.id],{'app_id':rr.job_id.id,'dep_app':rr.department_id.id}, context=context) 			
		self.write(cr,uid,ids,{'status_rec':'execute'},context=context)
		return True
	
	################################################################################                                    

	################################################################################
	######### pindahkan pelamar dari initial qualifikasi ke wawancara 1 ############
	################################################################################
		
	def execute(self,cr, uid,ids, context=None):
		hasil=self.browse(cr,uid,ids,context)[0]
		obj_app=self.pool.get('hr.applicant')
		execute = hasil.applicant_ids
		if execute == False :
			raise osv.except_osv(_('Peringatan!'),_('Pelamar Tidak Boleh Kosong.'))
			
		# search Stage
		n = 1000 #bilangan maksimal
		stage_rec=self.pool.get('hr.recruitment.stage')  
		stage_src=stage_rec.search(cr,uid,[])     
		stage_brw=stage_rec.browse(cr,uid,stage_src,context)	
		for src_stg in stage_brw :
			if src_stg.department_id.id == hasil.department_id.id or src_stg.department_id.id == False :
				seq = src_stg.sequence
				if seq > 0 and seq < n and seq != 1 :
					n = src_stg.sequence  
					nn = src_stg.id
		for applicant in execute :
			obj_app.write(cr,uid,[applicant.id],{'stage_id':nn ,'job_id': hasil.id,'department_id':hasil.department_id.id },context=context)
		self.write(cr,uid,ids,{'status_rec':'done'},context=context)
		return True
	
	_columns = {
		'pengalaman':fields.integer('Pengalaman (min-th)',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
		'usia':fields.selection([('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31'),('32','32'),('33','33'),('34','34'),('35','35'),('36','36'),('37','37'),('38','38'),('39','39'),('40','40'),('41','41'),('42','42'),('43','43'),('44','44'),('45','45'),('46','46'),('47','47'),('48','48'),('49','49'),('50','50')],string='Usia (max)',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
		'sts_prk':fields.selection([('single','Single'),('menikah','Menikah')],string='Status Pernikahan',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
		'kelamin':fields.selection([('L','Pria'),('W','Wanita')],string='Jenis Kelamin',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
		#'domisili_id':fields.many2one('hr_recruit.kota','Domisili',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),    
		'tempat_lahir_id':fields.many2one('hr_recruit.kota','Domisili',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}), 
		'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
		#'jurusan_ids':fields.one2many('hr_recruit.jurusan_detail','permohonan_recruit_id','Jurusan',states={'verify':[('readonly',True)], 'in_progress':[('readonly',True)]}),
		
		'status_rec' :fields.char('status rec',readonly=True),

		'bol_name' :fields.boolean('Name'),
		'bol_pengalaman':fields.boolean('Pengalaman'),
		'bol_usia':fields.boolean('Usia'),
		'bol_kelamin':fields.boolean('Jenis Kelamin'),
		'bol_sts_prk':fields.boolean('Status Pernikahan'),
		'bol_domisili':fields.boolean('Domisili'),
		'bol_tempat_lahir_id':fields.boolean('Tempat Lahir'),
		'bol_type_id':fields.boolean('Pendidikan'),
		'applicant_ids':fields.one2many('hr.applicant','app_id','Daftar Pelamar'),
	}

class hr_applicant(osv.osv):
	_name = "hr.applicant"
	_inherit = "hr.applicant"

	_columns = {
		'app_id':fields.many2one('hr.job','Applicant Id'),
	}
hr_applicant()
